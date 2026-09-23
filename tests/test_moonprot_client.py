from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

from mfp_bibliography.moonprot_client import (
    ALLOWED_MPIDS,
    BLOCK_MARKERS,
    CONTRACT_ID,
    DEFAULT_DELAY_SECONDS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    ERROR_LOG_HEADER,
    INDEX_HEADER,
    ROBOTS_URL,
    SMOKE_RESULT_HEADER,
    TransportError,
    TransportResponse,
    MoonProtSmokeClient,
    MoonProtSmokeConfig,
    protein_url,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
UA = "mfp-bibliography/0.1 (contact: curator@example.org)"


def protein_html(mpid: int, uniprot: str = "P12345", name: str = "Cytochrome c") -> bytes:
    return (
        "<html><body><table>"
        f"<tr><th>MoonProt ID</th><td>{mpid}</td></tr>"
        f"<tr><th>UniProt ID</th><td>{uniprot}</td></tr>"
        f"<tr><th>Name(s)</th><td>{name}</td></tr>"
        "</table></body></html>"
    ).encode("utf-8")


def robots_body(allow: bool = True) -> bytes:
    rule = "Allow: /" if allow else "Disallow: /"
    return f"User-agent: *\n{rule}\n".encode("utf-8")


def ok_response(body: bytes, content_type: str = "text/html; charset=utf-8") -> TransportResponse:
    return TransportResponse(200, {"Content-Type": content_type}, body)


def make_client(tmp_path: Path, routes: dict, **config_overrides) -> tuple[MoonProtSmokeClient, FakeTransport]:
    config = MoonProtSmokeConfig(
        user_agent=config_overrides.pop("user_agent", UA),
        root=tmp_path,
        delay_seconds=config_overrides.pop("delay_seconds", 0.0),
        retry_backoff_seconds=config_overrides.pop("retry_backoff_seconds", 0.0),
        **config_overrides,
    )
    transport = FakeTransport(routes)
    return MoonProtSmokeClient(config, transport), transport


class FakeTransport:
    """Transport fake: routes map URLs to a response, an exception, or a list
    of per-attempt responses/exceptions (consumed in order)."""

    def __init__(self, routes: dict) -> None:
        self.routes = routes
        self.calls: list[dict] = []

    def get(self, url: str, *, user_agent: str, timeout_seconds: float) -> TransportResponse:
        self.calls.append(
            {"url": url, "user_agent": user_agent, "timeout": timeout_seconds}
        )
        if url not in self.routes:
            raise AssertionError(f"unexpected URL requested: {url}")
        result = self.routes[url]
        if isinstance(result, list):
            result = result.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class FakeSleeper:
    def __init__(self) -> None:
        self.sleeps: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.sleeps.append(seconds)


def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return rows[0], rows[1:]


def test_contract_metadata() -> None:
    assert CONTRACT_ID == "MFPB_0_12_MOONPROT_SMOKE_CLIENT"
    assert ALLOWED_MPIDS == (1, 2, 3)
    assert DEFAULT_TIMEOUT_SECONDS == 15.0
    assert DEFAULT_DELAY_SECONDS == 10.0
    assert DEFAULT_MAX_RETRIES == 1
    assert DEFAULT_RETRY_BACKOFF_SECONDS == 30.0


def test_successful_acquisition_persists_byte_exact_artifacts(tmp_path: Path) -> None:
    body = protein_html(1, uniprot="P12345", name="Cytochrome c")
    client, transport = make_client(
        tmp_path,
        {ROBOTS_URL: ok_response(robots_body(allow=True)), protein_url(1): ok_response(body)},
    )

    report = client.run([1])

    assert [o.status for o in report.outcomes] == ["acquired"]
    assert report.stopped is False
    assert report.acquired_mpids == (1,)
    raw = tmp_path / "data" / "raw" / "moonprot" / "mpid_1.html"
    assert raw.read_bytes() == body  # verbatim bytes, no transformation

    sha = hashlib.sha256(body).hexdigest()
    header, rows = read_csv(tmp_path / "data" / "raw" / "moonprot" / "artifact_index.csv")
    assert header == list(INDEX_HEADER)
    assert len(rows) == 1
    row = rows[0]
    assert row[0] == "1"
    assert row[1] == protein_url(1)
    assert row[3] == "200"
    assert row[4] == "text/html; charset=utf-8"
    assert row[5] == "data/raw/moonprot/mpid_1.html"
    assert row[6] == sha
    assert row[7] == str(len(body))
    assert row[8] == "ok"
    assert row[9] == ""
    assert row[2]  # retrieved_at present

    checksums = (tmp_path / "data" / "manifests" / "file_checksums.sha256").read_text()
    assert checksums == f"{sha}  data/raw/moonprot/mpid_1.html\n"

    result_header, result_rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_results.csv")
    assert result_header == list(SMOKE_RESULT_HEADER)
    assert result_rows == [["1", "P12345", "Cytochrome c"]]

    # Error log must always exist with header (header-only on success)
    error_header, error_rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert error_header == list(ERROR_LOG_HEADER)
    assert error_rows == []
    # honest UA and configured timeout are passed through to every request
    assert all(call["user_agent"] == UA for call in transport.calls)
    assert all(call["timeout"] == 15.0 for call in transport.calls)


def test_robots_disallow_stops_before_protein_request(tmp_path: Path) -> None:
    client, transport = make_client(
        tmp_path,
        {ROBOTS_URL: ok_response(robots_body(allow=False))},
    )

    report = client.run([1, 2])

    assert report.stopped is True
    assert report.stop_reason == "robots_disallow"
    assert [o.status for o in report.outcomes] == ["stopped", "skipped"]
    protein_calls = [c for c in transport.calls if c["url"] == protein_url(1)]
    assert protein_calls == []  # robots gate blocks the protein request

    header, rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert header == list(ERROR_LOG_HEADER)
    assert len(rows) == 1
    assert rows[0][0] == "1"
    assert rows[0][2] == "robots_disallow"
    assert rows[0][4] == ""
    assert rows[0][5]  # attempted_at present
    assert not (tmp_path / "data" / "raw" / "moonprot" / "mpid_1.html").exists()


def test_robots_404_means_no_restrictions(tmp_path: Path) -> None:
    client, _ = make_client(
        tmp_path,
        {
            ROBOTS_URL: TransportResponse(404, {}, b"not found"),
            protein_url(1): ok_response(protein_html(1)),
        },
    )

    report = client.run([1])
    assert report.acquired_mpids == (1,)


def test_robots_unavailable_stops(tmp_path: Path) -> None:
    client, transport = make_client(
        tmp_path,
        {ROBOTS_URL: TransportResponse(500, {}, b"server error")},
    )

    report = client.run([1])

    assert report.stop_reason == "robots_unavailable"
    assert [c["url"] for c in transport.calls] == [ROBOTS_URL]
    header, rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert rows[0][2] == "robots_unavailable"


def test_delay_enforced_between_all_requests(tmp_path: Path) -> None:
    config = MoonProtSmokeConfig(user_agent=UA, root=tmp_path, delay_seconds=10.0)
    transport = FakeTransport(
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): ok_response(protein_html(1)),
        }
    )
    sleeper = FakeSleeper()
    client = MoonProtSmokeClient(config, transport, sleeper=sleeper, clock=lambda: 0.0)

    client.run([1])

    # robots -> protein request must be delayed by the full 10 seconds
    assert sleeper.sleeps == [10.0]
    assert len(transport.calls) == 2


def test_retry_backoff_and_max_one_retry(tmp_path: Path) -> None:
    config = MoonProtSmokeConfig(
        user_agent=UA, root=tmp_path, delay_seconds=0.0, retry_backoff_seconds=30.0
    )
    transport = FakeTransport(
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): [
                TransportResponse(500, {}, b"boom"),
                ok_response(protein_html(1)),
            ],
        }
    )
    sleeper = FakeSleeper()
    client = MoonProtSmokeClient(config, transport, sleeper=sleeper, clock=lambda: 0.0)

    report = client.run([1])

    assert report.acquired_mpids == (1,)
    protein_calls = [c for c in transport.calls if c["url"] == protein_url(1)]
    assert len(protein_calls) == 2  # one initial attempt + one retry, no more
    assert sleeper.sleeps == [30.0]  # 30-second backoff before the retry


def test_5xx_after_single_retry_stops(tmp_path: Path) -> None:
    client, transport = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): [
                TransportResponse(503, {}, b"a"),
                TransportResponse(503, {}, b"b"),
            ],
        },
    )

    report = client.run([1])

    assert report.stopped is True
    assert report.stop_reason == "http_error"
    protein_calls = [c for c in transport.calls if c["url"] == protein_url(1)]
    assert len(protein_calls) == 2
    header, rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert rows[0][2] == "http_error"
    assert rows[0][4] == "503"


def test_4xx_after_single_retry_stops(tmp_path: Path) -> None:
    client, _ = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(2): [TransportResponse(404, {}, b""), TransportResponse(404, {}, b"")],
        },
    )

    report = client.run([2])
    assert report.stop_reason == "http_error"
    header, rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert rows[0][4] == "404"


def test_transport_error_after_retry_stops(tmp_path: Path) -> None:
    client, _ = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): [TransportError("timed out"), TransportError("timed out")],
        },
    )

    report = client.run([1])
    assert report.stop_reason == "transport_error"
    assert not (tmp_path / "data" / "raw" / "moonprot" / "mpid_1.html").exists()


def test_redirect_rejected_without_retry(tmp_path: Path) -> None:
    client, transport = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): TransportResponse(
                302, {"Location": "http://example.org/elsewhere"}, b""
            ),
        },
    )

    report = client.run([1])

    assert report.stop_reason == "unexpected_redirect"
    protein_calls = [c for c in transport.calls if c["url"] == protein_url(1)]
    assert len(protein_calls) == 1  # redirects stop immediately, no retry
    header, rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert rows[0][2] == "unexpected_redirect"


def test_followed_redirect_detected_via_final_url(tmp_path: Path) -> None:
    client, _ = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): TransportResponse(
                200, {"Content-Type": "text/html"}, b"", final_url="http://other.example/x"
            ),
        },
    )

    report = client.run([1])
    assert report.stop_reason == "unexpected_redirect"


def test_non_html_content_type_rejected(tmp_path: Path) -> None:
    client, _ = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): ok_response(b'{"error": true}', content_type="application/json"),
        },
    )

    report = client.run([1])

    assert report.stop_reason == "content_type_rejected"
    assert not (tmp_path / "data" / "raw" / "moonprot" / "mpid_1.html").exists()
    header, rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert rows[0][2] == "content_type_rejected"


@pytest.mark.parametrize("marker", ["captcha", "Access Denied", "Cloudflare"])
def test_block_or_challenge_markers_stop(tmp_path: Path, marker: str) -> None:
    assert marker.lower() in BLOCK_MARKERS
    body = f"<html><body>{marker} page</body></html>".encode("utf-8")
    client, _ = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): ok_response(body),
        },
    )

    report = client.run([1])

    assert report.stop_reason == "block_or_challenge"
    assert not (tmp_path / "data" / "raw" / "moonprot" / "mpid_1.html").exists()


def test_parser_mpid_mismatch_stops_without_persisting(tmp_path: Path) -> None:
    client, _ = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): ok_response(protein_html(2)),  # page says MPID 2
        },
    )

    report = client.run([1])

    assert report.stop_reason == "parser_error"
    # persistence gate: nothing written although the bytes were fetched
    assert not (tmp_path / "data" / "raw" / "moonprot" / "mpid_1.html").exists()
    assert not (tmp_path / "data" / "raw" / "moonprot" / "artifact_index.csv").exists()
    header, rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert rows[0][2] == "parser_error"


def test_parser_malformed_page_stops(tmp_path: Path) -> None:
    client, _ = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): ok_response(b"<html><body><p>no table here</p></body></html>"),
        },
    )

    report = client.run([1])
    assert report.stop_reason == "parser_error"


def test_existing_raw_file_stops_before_any_request(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "moonprot" / "mpid_1.html"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"preexisting")

    client, transport = make_client(tmp_path, {ROBOTS_URL: ok_response(robots_body())})

    report = client.run([1, 2])

    assert report.stop_reason == "raw_file_exists"
    assert raw.read_bytes() == b"preexisting"  # untouched
    assert transport.calls == []  # stop happens before even the robots fetch
    header, rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert rows[0][2] == "raw_file_exists"


def test_out_of_scope_mpid_rejected_before_any_request(tmp_path: Path) -> None:
    client, transport = make_client(tmp_path, {})

    report = client.run([1, 4])

    assert report.stopped is True
    assert report.stop_reason == "mpid_out_of_scope"
    assert transport.calls == []  # rejected before any transport call
    header, rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert len(rows) == 1
    assert rows[0][0] == "4"
    assert rows[0][2] == "mpid_out_of_scope"


def test_sequential_multi_mpid_acquisition(tmp_path: Path) -> None:
    client, transport = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): ok_response(protein_html(1, "P1", "Alpha")),
            protein_url(2): ok_response(protein_html(2, "P2", "Beta")),
            protein_url(3): ok_response(protein_html(3, "P3", "Gamma")),
        },
    )

    report = client.run([1, 2, 3])

    assert report.acquired_mpids == (1, 2, 3)
    assert report.stopped is False
    urls = [call["url"] for call in transport.calls]
    # strict sequential order: robots, protein, robots, protein, ...
    assert urls == [
        ROBOTS_URL, protein_url(1),
        ROBOTS_URL, protein_url(2),
        ROBOTS_URL, protein_url(3),
    ]
    header, rows = read_csv(tmp_path / "data" / "raw" / "moonprot" / "artifact_index.csv")
    assert len(rows) == 3
    result_header, result_rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_results.csv")
    assert result_rows == [
        ["1", "P1", "Alpha"],
        ["2", "P2", "Beta"],
        ["3", "P3", "Gamma"],
    ]
    # Error log must always exist with header (header-only on success)
    error_header, error_rows = read_csv(tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv")
    assert error_header == list(ERROR_LOG_HEADER)
    assert error_rows == []


def test_no_real_http_during_execution_with_injected_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("real network access attempted")

    monkeypatch.setattr("urllib.request.urlopen", no_network)
    client, _ = make_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            protein_url(1): ok_response(protein_html(1)),
        },
    )

    report = client.run([1])  # full execution path with fake transport: no HTTP
    assert report.acquired_mpids == (1,)


def test_client_requires_injected_transport(tmp_path: Path) -> None:
    config = MoonProtSmokeConfig(user_agent=UA, root=tmp_path)
    with pytest.raises(TypeError):
        MoonProtSmokeClient(config)  # type: ignore[call-arg]


def test_config_rejects_blank_user_agent(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        MoonProtSmokeConfig(user_agent="   ", root=tmp_path)


def test_urllib_transport_is_never_used_by_client_by_default() -> None:
    # UrllibTransport exists only for the approved future execution; the client
    # has no default transport and never instantiates it on its own.
    import inspect

    source = inspect.getsource(MoonProtSmokeClient.__init__)
    assert "UrllibTransport" not in source


def test_cli_dry_run_makes_no_requests_and_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "acquire_moonprot_smoke.py"),
         "--mpid", "1", "--user-agent", UA],
        capture_output=True, text=True, env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0, result.stderr
    assert "DRY-RUN" in result.stdout
    assert "no requests will be made" in result.stdout
    assert protein_url(1) in result.stdout


def test_cli_rejects_out_of_scope_mpid() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "acquire_moonprot_smoke.py"),
         "--mpid", "4", "--user-agent", UA],
        capture_output=True, text=True, env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 2
    assert "outside the approved scope" in result.stdout


def test_cli_requires_user_agent() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "acquire_moonprot_smoke.py"),
         "--mpid", "1"],
        capture_output=True, text=True, env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 2
