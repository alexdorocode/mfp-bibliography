from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest

from mfp_bibliography.moonprot_client import (
    BATCH_ALLOWED_MPID_RANGE,
    BATCH_CONTRACT_ID,
    MAX_BATCH_SIZE,
    ERROR_LOG_HEADER,
    INDEX_HEADER,
    ROBOTS_URL,
    SMOKE_RESULT_HEADER,
    TransportError,
    TransportResponse,
    MoonProtBatchClient,
    MoonProtBatchConfig,
    BatchRunReport,
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


def make_batch_client(tmp_path: Path, routes: dict, **config_overrides) -> tuple[MoonProtBatchClient, FakeTransport]:
    config = MoonProtBatchConfig(
        user_agent=config_overrides.pop("user_agent", UA),
        root=tmp_path,
        delay_seconds=config_overrides.pop("delay_seconds", 0.0),
        retry_backoff_seconds=config_overrides.pop("retry_backoff_seconds", 0.0),
        continue_on_error=config_overrides.pop("continue_on_error", False),
        **config_overrides,
    )
    transport = FakeTransport(routes)
    return MoonProtBatchClient(config, transport), transport


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


# -- Contract metadata ----------------------------------------------------------


def test_batch_contract_metadata() -> None:
    assert BATCH_CONTRACT_ID == "MFPB_0_16_BATCH_CLIENT"
    assert BATCH_ALLOWED_MPID_RANGE == (1, 706)
    assert MAX_BATCH_SIZE == 20


# -- Configuration validation ---------------------------------------------------


def test_batch_config_defaults(tmp_path: Path) -> None:
    config = MoonProtBatchConfig(user_agent=UA, root=tmp_path)
    assert config.timeout_seconds == 15.0
    assert config.delay_seconds == 10.0
    assert config.max_retries == 1
    assert config.retry_backoff_seconds == 30.0
    assert config.continue_on_error is False


def test_batch_config_rejects_blank_user_agent(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        MoonProtBatchConfig(user_agent="   ", root=tmp_path)


def test_batch_config_accepts_continue_on_error(tmp_path: Path) -> None:
    config = MoonProtBatchConfig(user_agent=UA, root=tmp_path, continue_on_error=True)
    assert config.continue_on_error is True


# -- Range resolution ----------------------------------------------------------


def test_resolve_single_mpid(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    resolved = client._resolve_mpids(["5"])
    assert resolved == (5,)


def test_resolve_multiple_mpids(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    resolved = client._resolve_mpids(["1", "3", "5"])
    assert resolved == (1, 3, 5)


def test_resolve_range(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    resolved = client._resolve_mpids(["1..3"])
    assert resolved == (1, 2, 3)


def test_resolve_mixed_mpids_and_ranges(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    resolved = client._resolve_mpids(["1", "3..5", "7"])
    assert resolved == (1, 3, 4, 5, 7)


def test_resolve_range_with_whitespace(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    resolved = client._resolve_mpids([" 1 .. 3 "])
    assert resolved == (1, 2, 3)


def test_resolve_invalid_range_format(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    with pytest.raises(ValueError, match="Invalid range format"):
        client._resolve_mpids(["1..2..3"])


def test_resolve_invalid_range_endpoints(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    with pytest.raises(ValueError, match="Invalid range endpoints"):
        client._resolve_mpids(["a..b"])


def test_resolve_reversed_range(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    with pytest.raises(ValueError, match="start .* > end"):
        client._resolve_mpids(["5..1"])


# -- Batch parameter validation ------------------------------------------------


def test_batch_size_exceeds_maximum(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    mpids = tuple(range(1, 22))  # 21 MPIDs
    valid, errors = client._validate_batch_params(mpids)
    assert valid == []
    assert len(errors) == 1
    assert f"exceeds maximum of {MAX_BATCH_SIZE}" in errors[0]


def test_batch_mpid_outside_range(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    mpids = (0, 1, 707)
    valid, errors = client._validate_batch_params(mpids)
    assert valid == [1]
    assert len(errors) == 2
    assert "outside allowed range 1..706" in errors[0]
    assert "outside allowed range 1..706" in errors[1]


def test_batch_already_acquired_mpid(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "moonprot" / "mpid_1.html"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"preexisting")
    
    client, _ = make_batch_client(tmp_path, {})
    mpids = (1, 2, 3)
    valid, errors = client._validate_batch_params(mpids)
    assert valid == [2, 3]
    assert len(errors) == 1
    assert "already exists" in errors[0]


def test_batch_validation_all_valid(tmp_path: Path) -> None:
    client, _ = make_batch_client(tmp_path, {})
    mpids = (1, 2, 3)
    valid, errors = client._validate_batch_params(mpids)
    assert valid == [1, 2, 3]
    assert errors == []


# -- Batch execution ------------------------------------------------------------


def test_batch_successful_acquisition(tmp_path: Path) -> None:
    from mfp_bibliography.moonprot_parser import MOONPROT_URL_PATTERN
    client, transport = make_batch_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body(allow=True)),
            MOONPROT_URL_PATTERN.format(id=1): ok_response(protein_html(1)),
            MOONPROT_URL_PATTERN.format(id=2): ok_response(protein_html(2)),
        },
    )
    
    report = client.run(["1", "2"])
    
    assert report.requested == (1, 2)
    assert len(report.outcomes) == 2
    assert [o.status for o in report.outcomes] == ["acquired", "acquired"]
    assert report.stopped is False
    assert report.acquired_mpids == (1, 2)


def test_batch_stop_on_first_error_by_default(tmp_path: Path) -> None:
    from mfp_bibliography.moonprot_parser import MOONPROT_URL_PATTERN
    client, transport = make_batch_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body(allow=True)),
            MOONPROT_URL_PATTERN.format(id=1): ok_response(protein_html(1)),
            MOONPROT_URL_PATTERN.format(id=2): TransportResponse(500, {}, b"error"),
            MOONPROT_URL_PATTERN.format(id=3): ok_response(protein_html(3)),
        },
    )
    
    report = client.run(["1", "2", "3"])
    
    assert report.stopped is True
    assert report.stop_reason == "http_error"
    assert report.acquired_mpids == (1,)
    assert report.stopped_mpids == (2,)
    assert report.skipped_mpids == (3,)


def test_batch_continue_on_error_mode(tmp_path: Path) -> None:
    from mfp_bibliography.moonprot_parser import MOONPROT_URL_PATTERN
    client, transport = make_batch_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body(allow=True)),
            MOONPROT_URL_PATTERN.format(id=1): ok_response(protein_html(1)),
            MOONPROT_URL_PATTERN.format(id=2): TransportResponse(500, {}, b"error"),
            MOONPROT_URL_PATTERN.format(id=3): ok_response(protein_html(3)),
        },
        continue_on_error=True,
    )
    
    report = client.run(["1", "2", "3"])
    
    assert report.stopped is False
    assert report.acquired_mpids == (1, 3)
    assert report.stopped_mpids == (2,)
    assert report.skipped_mpids == ()


def test_batch_rejects_mpids_outside_1_706(tmp_path: Path) -> None:
    client, transport = make_batch_client(tmp_path, {})
    
    report = client.run(["0", "1", "707"])
    
    assert report.stopped is True
    assert report.stop_reason == "validation_error"
    # First is stopped, rest are skipped (all invalid)
    assert len(report.stopped_mpids) == 1
    assert len(report.skipped_mpids) == 2
    assert report.acquired_mpids == ()


def test_batch_rejects_already_acquired(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "moonprot" / "mpid_2.html"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"preexisting")
    
    client, transport = make_batch_client(tmp_path, {})
    
    report = client.run(["1", "2", "3"])
    
    assert report.stopped is True
    assert report.stop_reason == "validation_error"
    # Check that MPID 2 has the already exists error
    assert any("already exists" in outcome.detail for outcome in report.outcomes if outcome.detail)


def test_batch_range_validation(tmp_path: Path) -> None:
    from mfp_bibliography.moonprot_parser import MOONPROT_URL_PATTERN
    client, transport = make_batch_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body(allow=True)),
            MOONPROT_URL_PATTERN.format(id=1): ok_response(protein_html(1)),
            MOONPROT_URL_PATTERN.format(id=2): ok_response(protein_html(2)),
            MOONPROT_URL_PATTERN.format(id=3): ok_response(protein_html(3)),
        },
    )
    
    report = client.run(["1..3"])
    
    assert report.requested == (1, 2, 3)
    assert report.acquired_mpids == (1, 2, 3)


def test_batch_max_20_enforcement(tmp_path: Path) -> None:
    client, transport = make_batch_client(tmp_path, {})
    mpids = [str(i) for i in range(1, 22)]  # 21 MPIDs
    
    report = client.run(mpids)
    
    assert report.stopped is True
    assert report.stop_reason == "validation_error"
    # Check that the first outcome has the batch size error
    assert any(f"exceeds maximum of {MAX_BATCH_SIZE}" in outcome.detail for outcome in report.outcomes if outcome.detail)


def test_batch_sequential_order(tmp_path: Path) -> None:
    from mfp_bibliography.moonprot_parser import MOONPROT_URL_PATTERN
    client, transport = make_batch_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body(allow=True)),
            MOONPROT_URL_PATTERN.format(id=1): ok_response(protein_html(1)),
            MOONPROT_URL_PATTERN.format(id=2): ok_response(protein_html(2)),
            MOONPROT_URL_PATTERN.format(id=3): ok_response(protein_html(3)),
        },
    )
    
    client.run(["3", "1", "2"])
    
    urls = [call["url"] for call in transport.calls]
    # Should be in order: robots, 3, robots, 1, robots, 2
    assert urls[1] == MOONPROT_URL_PATTERN.format(id=3)
    assert urls[3] == MOONPROT_URL_PATTERN.format(id=1)
    assert urls[5] == MOONPROT_URL_PATTERN.format(id=2)


# -- Error logging ---------------------------------------------------------------


def test_batch_error_log_created_on_validation_error(tmp_path: Path) -> None:
    client, transport = make_batch_client(tmp_path, {})
    
    client.run(["707"])
    
    error_path = tmp_path / "data" / "interim" / "moonprot_smoke_error_log.csv"
    assert error_path.exists()
    header, rows = read_csv(error_path)
    assert header == list(ERROR_LOG_HEADER)
    assert len(rows) >= 1
    assert rows[0][2] == "validation_error"


# -- Persistence ----------------------------------------------------------------


def test_batch_persists_byte_exact_artifacts(tmp_path: Path) -> None:
    from mfp_bibliography.moonprot_parser import MOONPROT_URL_PATTERN
    body = protein_html(1, uniprot="P12345", name="Cytochrome c")
    client, transport = make_batch_client(
        tmp_path,
        {ROBOTS_URL: ok_response(robots_body(allow=True)), 
         MOONPROT_URL_PATTERN.format(id=1): ok_response(body)},
    )
    
    report = client.run(["1"])
    
    assert report.acquired_mpids == (1,)
    raw = tmp_path / "data" / "raw" / "moonprot" / "mpid_1.html"
    assert raw.read_bytes() == body
    
    # Check artifact index
    header, rows = read_csv(tmp_path / "data" / "raw" / "moonprot" / "artifact_index.csv")
    assert header == list(INDEX_HEADER)
    assert len(rows) == 1
    assert rows[0][0] == "1"


# -- CLI tests ----------------------------------------------------------------


def test_batch_cli_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "acquire_moonprot_batch.py"),
         "--mpid", "1", "--mpid", "2..3", "--user-agent", UA],
        capture_output=True, text=True, 
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0
    assert "DRY-RUN" in result.stdout
    assert "no requests will be made" in result.stdout


def test_batch_cli_rejects_out_of_range_mpid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "acquire_moonprot_batch.py"),
         "--mpid", "707", "--user-agent", UA, "--execute"],
        capture_output=True, text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    # Should fail because 707 is out of range
    assert result.returncode != 0


def test_batch_cli_requires_user_agent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "acquire_moonprot_batch.py"),
         "--mpid", "1"],
        capture_output=True, text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 2


def test_batch_cli_requires_mpid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "acquire_moonprot_batch.py"),
         "--user-agent", UA],
        capture_output=True, text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 2


# -- No real network ------------------------------------------------------------


def test_batch_client_no_real_http(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def no_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("real network access attempted")
    
    monkeypatch.setattr("urllib.request.urlopen", no_network)
    from mfp_bibliography.moonprot_parser import MOONPROT_URL_PATTERN
    client, _ = make_batch_client(
        tmp_path,
        {
            ROBOTS_URL: ok_response(robots_body()),
            MOONPROT_URL_PATTERN.format(id=1): ok_response(protein_html(1)),
        },
    )
    
    report = client.run(["1"])  # full execution path with fake transport: no HTTP
    assert report.acquired_mpids == (1,)
