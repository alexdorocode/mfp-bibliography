"""MoonProt smoke-acquisition client with injected transport (MPIDs 1, 2, 3 only).

Implements the contract in docs/acquisition-protocols/moonprot.md and
docs/acquisition-protocols/moonprot-artifact-index.md:

- only MPIDs 1, 2, 3 may be requested; anything else is rejected before any
  transport call;
- sequential execution with a minimum delay between any two requests;
- a configurable honest User-Agent and a 15-second default timeout;
- at most one retry per MPID with a minimum 30-second backoff;
- the robots.txt gate is checked through the same transport before every
  protein request;
- raw response bytes are persisted verbatim to
  ``data/raw/moonprot/mpid_{id}.html`` only after the full persistence gate
  passes: robots/terms allow, successful HTTP status, no unexpected redirect,
  acceptable HTML content type, no CAPTCHA/block/JS-challenge marker, and a
  parser success with the expected MPID;
- per-file provenance is appended to ``data/raw/moonprot/artifact_index.csv``
  and ``data/manifests/file_checksums.sha256``; extracted results go to
  ``data/interim/moonprot_smoke_results.csv``;
- failures are recorded in ``data/interim/moonprot_smoke_error_log.csv`` and
  execution stops immediately on any protocol stop condition.

The client never constructs a real transport implicitly: a transport must be
injected. ``UrllibTransport`` exists for the future approved execution only;
it is never used by tests or by the CLI dry-run mode.

Batch client (MFPB_0_16_BATCH_CLIENT):
- Accepts explicit MPID lists and inclusive ranges only;
- Hard maximum per invocation: 100 MPIDs;
- Rejects IDs outside 1..706;
- Rejects any request for an ID already present in data/raw/moonprot/;
- Default batch is forbidden; user must explicitly pass IDs/range;
- Sequential-only behavior, one request at a time;
- Preserves all contract values from smoke client;
- Stop-on-error by default; optional --continue-on-error mode.
"""

from __future__ import annotations

import csv
import hashlib
import re
import time
import urllib.error
import urllib.request
import urllib.robotparser
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mfp_bibliography.moonprot_parser import (
    MOONPROT_URL_PATTERN,
    MoonProtKnownAbsentError,
    MoonProtParseError,
    parse_moonprot_html,
)

CONTRACT_ID = "MFPB_0_12_MOONPROT_SMOKE_CLIENT"
ALLOWED_MPIDS = (1, 2, 3)
MOONPROT_HOST = "http://www.moonlightingproteins.org"
ROBOTS_URL = f"{MOONPROT_HOST}/robots.txt"
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
BLOCK_MARKERS = (
    "captcha",
    "access denied",
    "permission denied",
    "blocked",
    "cloudflare",
    "ddos protection",
    "javascript challenge",
    "verify you are human",
)
REQUIRED_HTML_CONTENT_TYPE = "text/html"

INDEX_HEADER = (
    "mpid",
    "url",
    "retrieved_at",
    "http_status",
    "content_type",
    "raw_file_path",
    "sha256",
    "file_size_bytes",
    "parser_status",
    "missing_fields",
)
ERROR_LOG_HEADER = (
    "mpid",
    "url",
    "error_type",
    "detail",
    "http_status",
    "attempted_at",
)
ABSENT_LOG_HEADER = (
    "mpid",
    "url",
    "http_status",
    "absent_marker",
    "detected_at",
)
SMOKE_RESULT_HEADER = ("mpid", "uniprot_id", "protein_name")

DEFAULT_TIMEOUT_SECONDS = 15.0
DEFAULT_DELAY_SECONDS = 10.0
DEFAULT_MAX_RETRIES = 1
DEFAULT_RETRY_BACKOFF_SECONDS = 30.0


class TransportError(Exception):
    """The injected transport failed to deliver a response (timeout, I/O)."""


@dataclass(frozen=True)
class TransportResponse:
    """One HTTP response as returned by a transport (no redirect following)."""

    status_code: int
    headers: Mapping[str, str]
    body: bytes
    final_url: str | None = None


class Transport:
    """Minimal transport interface; real or fake implementations are injected."""

    def get(
        self, url: str, *, user_agent: str, timeout_seconds: float
    ) -> TransportResponse:
        raise NotImplementedError


@dataclass(frozen=True)
class MoonProtSmokeConfig:
    """Configuration for one smoke run; paths are resolved under ``root``."""

    user_agent: str
    root: Path
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    delay_seconds: float = DEFAULT_DELAY_SECONDS
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff_seconds: float = DEFAULT_RETRY_BACKOFF_SECONDS

    def __post_init__(self) -> None:
        if not self.user_agent.strip():
            raise ValueError("user_agent must be a non-empty, honest identifier")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.delay_seconds < 0:
            raise ValueError("delay_seconds must be non-negative")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds must be non-negative")

    @property
    def raw_dir(self) -> Path:
        return self.root / "data" / "raw" / "moonprot"

    def raw_path(self, mpid: int) -> Path:
        return self.raw_dir / f"mpid_{mpid}.html"

    @property
    def artifact_index_path(self) -> Path:
        return self.raw_dir / "artifact_index.csv"

    @property
    def checksums_path(self) -> Path:
        return self.root / "data" / "manifests" / "file_checksums.sha256"

    @property
    def smoke_result_path(self) -> Path:
        return self.root / "data" / "interim" / "moonprot_smoke_results.csv"

    @property
    def error_log_path(self) -> Path:
        return self.root / "data" / "interim" / "moonprot_smoke_error_log.csv"

    @property
    def absent_log_path(self) -> Path:
        return self.root / "data" / "interim" / "moonprot_absent_log.csv"


@dataclass(frozen=True)
class SmokeMpidOutcome:
    mpid: int
    status: str  # "acquired", "stopped", "skipped"
    error_type: str | None = None
    detail: str | None = None
    http_status: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "mpid": self.mpid,
            "status": self.status,
            "error_type": self.error_type,
            "detail": self.detail,
            "http_status": self.http_status,
        }


@dataclass(frozen=True)
class SmokeRunReport:
    requested: tuple[int, ...]
    outcomes: tuple[SmokeMpidOutcome, ...] = field(default_factory=tuple)
    stopped: bool = False
    stop_reason: str | None = None

    @property
    def acquired_mpids(self) -> tuple[int, ...]:
        return tuple(outcome.mpid for outcome in self.outcomes if outcome.status == "acquired")

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested": list(self.requested),
            "outcomes": [outcome.to_dict() for outcome in self.outcomes],
            "stopped": self.stopped,
            "stop_reason": self.stop_reason,
            "acquired_mpids": list(self.acquired_mpids),
        }


class _GateStop(Exception):
    """Internal: a protocol stop condition was reached for one MPID."""

    def __init__(self, error_type: str, detail: str, http_status: int | None = None) -> None:
        super().__init__(detail)
        self.error_type = error_type
        self.detail = detail
        self.http_status = http_status


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def protein_url(mpid: int) -> str:
    return MOONPROT_URL_PATTERN.format(id=mpid)


class MoonProtSmokeClient:
    """Sequential, transport-injected smoke client for MPIDs 1, 2, 3."""

    def __init__(
        self,
        config: MoonProtSmokeConfig,
        transport: Transport,
        *,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._config = config
        self._transport = transport
        self._sleeper = sleeper
        self._clock = clock
        self._last_request_at: float | None = None

    # -- public API ---------------------------------------------------------

    def run(self, mpids: Iterable[int | str]) -> SmokeRunReport:
        """Acquire the given MPIDs sequentially, stopping on any stop condition.

        Non-integer MPID values raise ``ValueError``. Integer MPIDs outside
        ``{1, 2, 3}`` are rejected before any transport call, recorded in the
        error log, and stop the run.
        """
        requested = tuple(int(mpid) for mpid in mpids)
        # Ensure error log always exists with header (even on successful runs)
        self._init_csv(self._config.error_log_path, ERROR_LOG_HEADER)
        out_of_scope = [mpid for mpid in requested if mpid not in ALLOWED_MPIDS]
        if out_of_scope:
            for mpid in out_of_scope:
                self._log_error(
                    mpid,
                    protein_url(mpid),
                    "mpid_out_of_scope",
                    f"MPID {mpid} is outside the approved scope {{1, 2, 3}}",
                    None,
                )
            return SmokeRunReport(
                requested=requested,
                outcomes=tuple(
                    SmokeMpidOutcome(
                        mpid,
                        "stopped" if mpid == out_of_scope[0] else "skipped",
                        error_type="mpid_out_of_scope" if mpid == out_of_scope[0] else None,
                    )
                    for mpid in requested
                ),
                stopped=True,
                stop_reason="mpid_out_of_scope",
            )

        outcomes: list[SmokeMpidOutcome] = []
        stop: _GateStop | None = None
        for mpid in requested:
            if stop is not None:
                outcomes.append(SmokeMpidOutcome(mpid, "skipped"))
                continue
            try:
                self._acquire(mpid)
            except _GateStop as gate:
                stop = gate
                self._gate_to_error_log(mpid, gate)
                outcomes.append(
                    SmokeMpidOutcome(mpid, "stopped", gate.error_type, gate.detail, gate.http_status)
                )
            else:
                outcomes.append(SmokeMpidOutcome(mpid, "acquired"))
        if stop is not None:
            return SmokeRunReport(
                requested=requested,
                outcomes=tuple(outcomes),
                stopped=True,
                stop_reason=stop.error_type,
            )
        return SmokeRunReport(requested=requested, outcomes=tuple(outcomes))

    # -- acquisition pipeline ----------------------------------------------

    def _acquire(self, mpid: int) -> None:
        url = protein_url(mpid)
        raw_path = self._config.raw_path(mpid)
        if raw_path.exists():
            raise _GateStop(
                "raw_file_exists",
                f"Raw file already exists and is append-only: {raw_path}",
            )

        if not self._robots_allows(url):
            raise _GateStop(
                "robots_disallow",
                f"robots.txt disallows fetching {url}",
            )

        response = self._fetch_with_retry(url)
        self._validate_response(url, response)

        decoded = response.body.decode("utf-8", errors="replace")
        lowered = decoded.lower()
        for marker in BLOCK_MARKERS:
            if marker in lowered:
                raise _GateStop(
                    "block_or_challenge",
                    f"Response body contains a block/challenge marker: {marker!r}",
                    response.status_code,
                )

        try:
            record = parse_moonprot_html(decoded, expected_mpid=mpid)
        except MoonProtParseError as exc:
            raise _GateStop(
                "parser_error",
                f"Parser rejected the fetched page: {exc}",
                response.status_code,
            ) from exc

        self._persist(mpid, url, response, record)

    def _robots_allows(self, url: str) -> bool:
        response = self._request(ROBOTS_URL)
        if response.status_code in (404, 410):
            return True
        if not 200 <= response.status_code < 300:
            raise _GateStop(
                "robots_unavailable",
                f"robots.txt could not be retrieved (HTTP {response.status_code})",
                response.status_code,
            )
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(response.body.decode("utf-8", errors="replace").splitlines())
        return parser.can_fetch(self._config.user_agent, url)

    def _fetch_with_retry(self, url: str) -> TransportResponse:
        attempts = 0
        while True:
            attempts += 1
            try:
                response = self._request(url)
            except TransportError as exc:
                if attempts <= self._config.max_retries:
                    self._sleeper(self._config.retry_backoff_seconds)
                    continue
                raise _GateStop(
                    "transport_error",
                    f"Transport failed after {attempts} attempt(s): {exc}",
                ) from exc
            if response.status_code in REDIRECT_STATUSES or (
                response.final_url is not None and response.final_url != url
            ):
                raise _GateStop(
                    "unexpected_redirect",
                    f"Unexpected redirect for {url} (HTTP {response.status_code})",
                    response.status_code,
                )
            if 200 <= response.status_code < 300:
                return response
            if attempts <= self._config.max_retries:
                self._sleeper(self._config.retry_backoff_seconds)
                continue
            raise _GateStop(
                "http_error",
                f"HTTP {response.status_code} persisted after {attempts} attempt(s)",
                response.status_code,
            )

    def _validate_response(self, url: str, response: TransportResponse) -> None:
        content_type = ""
        for name, value in response.headers.items():
            if name.lower() == "content-type":
                content_type = value
                break
        if REQUIRED_HTML_CONTENT_TYPE not in content_type.lower():
            raise _GateStop(
                "content_type_rejected",
                f"Unacceptable content type for {url}: {content_type!r}",
                response.status_code,
            )

    def _persist(self, mpid: int, url: str, response: TransportResponse, record: Any) -> None:
        config = self._config
        raw_path = config.raw_path(mpid)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(response.body)

        sha256 = hashlib.sha256(response.body).hexdigest()
        rel_raw = raw_path.relative_to(config.root).as_posix()
        content_type = ""
        for name, value in response.headers.items():
            if name.lower() == "content-type":
                content_type = value
                break

        self._append_csv_row(
            config.artifact_index_path,
            INDEX_HEADER,
            (
                str(mpid),
                url,
                _utc_now_iso(),
                str(response.status_code),
                content_type,
                rel_raw,
                sha256,
                str(len(response.body)),
                "ok",
                ";".join(record.missing_fields),
            ),
        )

        config.checksums_path.parent.mkdir(parents=True, exist_ok=True)
        with config.checksums_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{sha256}  {rel_raw}\n")

        self._append_csv_row(
            config.smoke_result_path,
            SMOKE_RESULT_HEADER,
            (str(mpid), record.uniprot_id or "", record.protein_name or ""),
        )

    # -- error log -----------------------------------------------------------

    def _log_error(
        self,
        mpid: int | str,
        url: str,
        error_type: str,
        detail: str,
        http_status: int | None,
    ) -> None:
        path = self._config.error_log_path
        self._append_csv_row(
            path,
            ERROR_LOG_HEADER,
            (
                str(mpid),
                url,
                error_type,
                detail,
                "" if http_status is None else str(http_status),
                _utc_now_iso(),
            ),
        )

    def _gate_to_error_log(self, mpid: int, gate: _GateStop) -> None:
        self._log_error(mpid, protein_url(mpid), gate.error_type, gate.detail, gate.http_status)

    # -- transport plumbing --------------------------------------------------

    def _request(self, url: str) -> TransportResponse:
        if self._last_request_at is not None:
            elapsed = self._clock() - self._last_request_at
            wait = self._config.delay_seconds - elapsed
            if wait > 0:
                self._sleeper(wait)
        response = self._transport.get(
            url,
            user_agent=self._config.user_agent,
            timeout_seconds=self._config.timeout_seconds,
        )
        self._last_request_at = self._clock()
        return response

    @staticmethod
    def _init_csv(path: Path, header: tuple[str, ...]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        needs_header = not path.exists() or path.stat().st_size == 0
        if needs_header:
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(header)

    @staticmethod
    def _append_csv_row(path: Path, header: tuple[str, ...], row: tuple[str, ...]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        needs_header = not path.exists() or path.stat().st_size == 0
        with path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            if needs_header:
                writer.writerow(header)
            writer.writerow(row)


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Return 3xx responses as-is instead of following redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


class UrllibTransport(Transport):
    """Real HTTP transport for the future approved execution only.

    Follows no redirects (3xx responses are returned as-is) and converts
    transport-level failures into ``TransportError``. It is never invoked by
    tests or by the CLI dry-run mode.
    """

    def __init__(self) -> None:
        self._opener = urllib.request.build_opener(_NoRedirectHandler)

    def get(
        self, url: str, *, user_agent: str, timeout_seconds: float
    ) -> TransportResponse:
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})
        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                return TransportResponse(
                    status_code=response.status,
                    headers={name: value for name, value in response.headers.items()},
                    body=response.read(),
                    final_url=response.geturl(),
                )
        except urllib.error.HTTPError as exc:
            return TransportResponse(
                status_code=exc.code,
                headers={name: value for name, value in exc.headers.items()},
                body=exc.read(),
                final_url=None,
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise TransportError(str(exc)) from exc


# -- Batch Client (MFPB_0_16_BATCH_CLIENT) -------------------------------------

BATCH_CONTRACT_ID = "MFPB_0_16_BATCH_CLIENT"
BATCH_ALLOWED_MPID_RANGE = (1, 706)
MAX_BATCH_SIZE = 100


@dataclass(frozen=True)
class MoonProtBatchConfig:
    """Configuration for batch acquisition; extends smoke config with batch limits."""

    user_agent: str
    root: Path
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    delay_seconds: float = DEFAULT_DELAY_SECONDS
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff_seconds: float = DEFAULT_RETRY_BACKOFF_SECONDS
    continue_on_error: bool = False

    def __post_init__(self) -> None:
        if not self.user_agent.strip():
            raise ValueError("user_agent must be a non-empty, honest identifier")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.delay_seconds < 0:
            raise ValueError("delay_seconds must be non-negative")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds must be non-negative")

    @property
    def raw_dir(self) -> Path:
        return self.root / "data" / "raw" / "moonprot"

    def raw_path(self, mpid: int) -> Path:
        return self.raw_dir / f"mpid_{mpid}.html"

    @property
    def artifact_index_path(self) -> Path:
        return self.raw_dir / "artifact_index.csv"

    @property
    def checksums_path(self) -> Path:
        return self.root / "data" / "manifests" / "file_checksums.sha256"

    @property
    def smoke_result_path(self) -> Path:
        return self.root / "data" / "interim" / "moonprot_smoke_results.csv"

    @property
    def error_log_path(self) -> Path:
        return self.root / "data" / "interim" / "moonprot_smoke_error_log.csv"

    @property
    def absent_log_path(self) -> Path:
        return self.root / "data" / "interim" / "moonprot_absent_log.csv"


@dataclass(frozen=True)
class BatchMpidOutcome:
    mpid: int
    status: str  # "acquired", "known_absent", "stopped", "skipped"
    error_type: str | None = None
    detail: str | None = None
    http_status: int | None = None
    absent_marker: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "mpid": self.mpid,
            "status": self.status,
            "error_type": self.error_type,
            "detail": self.detail,
            "http_status": self.http_status,
        }
        if self.absent_marker is not None:
            result["absent_marker"] = self.absent_marker
        return result


@dataclass(frozen=True)
class BatchRunReport:
    requested: tuple[int, ...]
    outcomes: tuple[BatchMpidOutcome, ...] = field(default_factory=tuple)
    stopped: bool = False
    stop_reason: str | None = None

    @property
    def acquired_mpids(self) -> tuple[int, ...]:
        return tuple(outcome.mpid for outcome in self.outcomes if outcome.status == "acquired")

    @property
    def known_absent_mpids(self) -> tuple[int, ...]:
        return tuple(outcome.mpid for outcome in self.outcomes if outcome.status == "known_absent")

    @property
    def stopped_mpids(self) -> tuple[int, ...]:
        return tuple(outcome.mpid for outcome in self.outcomes if outcome.status == "stopped")

    @property
    def skipped_mpids(self) -> tuple[int, ...]:
        return tuple(outcome.mpid for outcome in self.outcomes if outcome.status == "skipped")

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested": list(self.requested),
            "outcomes": [outcome.to_dict() for outcome in self.outcomes],
            "stopped": self.stopped,
            "stop_reason": self.stop_reason,
            "acquired_mpids": list(self.acquired_mpids),
            "known_absent_mpids": list(self.known_absent_mpids),
            "stopped_mpids": list(self.stopped_mpids),
            "skipped_mpids": list(self.skipped_mpids),
        }


class _BatchGateStop(Exception):
    """Internal: a protocol stop condition was reached for one MPID in batch mode."""

    def __init__(self, error_type: str, detail: str, http_status: int | None = None) -> None:
        super().__init__(detail)
        self.error_type = error_type
        self.detail = detail
        self.http_status = http_status


class _KnownAbsentStop(Exception):
    """Internal: the MPID was detected as known absent."""

    def __init__(self, mpid: int, url: str, http_status: int, absent_marker: str) -> None:
        super().__init__(f"MPID {mpid} is known absent")
        self.mpid = mpid
        self.url = url
        self.http_status = http_status
        self.absent_marker = absent_marker


class MoonProtBatchClient:
    """Controlled batch client for explicit MPID lists in range 1..706.
    
    Hard limits:
    - Maximum 100 MPIDs per invocation
    - MPIDs must be in range 1..706
    - Rejects any MPID already present in data/raw/moonprot/
    - Sequential-only, one request at a time
    - Stop-on-error by default (continue_on_error=False)
    """

    def __init__(
        self,
        config: MoonProtBatchConfig,
        transport: Transport,
        *,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._config = config
        self._transport = transport
        self._sleeper = sleeper
        self._clock = clock
        self._last_request_at: float | None = None

    def _resolve_mpids(self, mpids: Iterable[int | str]) -> tuple[int, ...]:
        """Resolve MPID list from explicit IDs and ranges."""
        resolved: list[int] = []
        for item in mpids:
            item_str = str(item)
            if ".." in item_str:
                # Range notation
                parts = item_str.split("..")
                if len(parts) != 2:
                    raise ValueError(f"Invalid range format: {item_str}")
                try:
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())
                except ValueError:
                    raise ValueError(f"Invalid range endpoints: {item_str}")
                if start > end:
                    raise ValueError(f"Invalid range: start {start} > end {end}")
                resolved.extend(range(start, end + 1))
            else:
                resolved.append(int(item_str))
        return tuple(resolved)

    def _validate_batch_params(self, mpids: tuple[int, ...]) -> tuple[list[int], list[str]]:
        """Validate batch parameters. Returns (valid_mpids, errors)."""
        errors: list[str] = []
        valid: list[int] = []
        
        # Check batch size
        if len(mpids) > MAX_BATCH_SIZE:
            errors.append(f"Batch size {len(mpids)} exceeds maximum of {MAX_BATCH_SIZE}")
            return valid, errors
        
        # Check for default batch (empty)
        if len(mpids) == 0:
            errors.append("Default batch is forbidden; must explicitly pass IDs or range")
            return valid, errors
        
        # Check each MPID
        absent_log_path = self._config.absent_log_path
        absent_mpids = self._load_absent_mpids(absent_log_path) if absent_log_path.exists() else set()
        
        for mpid in mpids:
            # Check range
            if not (BATCH_ALLOWED_MPID_RANGE[0] <= mpid <= BATCH_ALLOWED_MPID_RANGE[1]):
                errors.append(f"MPID {mpid} is outside allowed range {BATCH_ALLOWED_MPID_RANGE[0]}..{BATCH_ALLOWED_MPID_RANGE[1]}")
                continue
            
            # Check if already acquired
            raw_path = self._config.raw_path(mpid)
            if raw_path.exists():
                errors.append(f"MPID {mpid} already exists at {raw_path}")
                continue
            
            # Check if already known absent
            if mpid in absent_mpids:
                errors.append(f"MPID {mpid} already known absent")
                continue
            
            valid.append(mpid)
        
        return valid, errors
    
    @staticmethod
    def _load_absent_mpids(path: Path) -> set[int]:
        """Load set of MPIDs from the absent log."""
        if not path.exists():
            return set()
        mpids = set()
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    mpids.add(int(row["mpid"]))
                except (ValueError, KeyError):
                    continue
        return mpids

    def run(self, mpids: Iterable[int | str]) -> BatchRunReport:
        """Acquire the given MPIDs sequentially in batch mode.
        
        Accepts explicit IDs and inclusive ranges (e.g., "1..5").
        Hard maximum of 100 MPIDs per invocation.
        Rejects IDs outside 1..706.
        Rejects any request for an ID already present in data/raw/moonprot/.
        Sequential-only, one request at a time.
        Stop-on-error by default.
        """
        # Resolve ranges
        try:
            resolved_mpids = self._resolve_mpids(mpids)
        except ValueError as e:
            # Log validation error
            self._init_csv(self._config.error_log_path, ERROR_LOG_HEADER)
            self._log_error(
                "range_parse_error",
                "range_parse_error",
                "range_parse_error",
                str(e),
                None,
            )
            return BatchRunReport(
                requested=(),
                outcomes=(),
                stopped=True,
                stop_reason="range_parse_error",
            )
        
        # Ensure error log always exists with header
        self._init_csv(self._config.error_log_path, ERROR_LOG_HEADER)
        
        # Validate batch parameters
        valid_mpids, errors = self._validate_batch_params(resolved_mpids)
        
        if errors:
            # Log all validation errors
            for error in errors:
                self._log_error(
                    "validation_error",
                    "validation_error",
                    "validation_error",
                    error,
                    None,
                )
            
            # Create error mapping: for invalid MPIDs, map to their specific error
            # For valid MPIDs (if any passed validation), they won't have errors
            error_map: dict[int, str] = {}
            invalid_mpids = [mpid for mpid in resolved_mpids if mpid not in valid_mpids]
            
            # Try to map errors to specific invalid MPIDs
            for error in errors:
                # Extract MPID from error message if present
                for mpid in invalid_mpids:
                    if str(mpid) in error:
                        error_map[mpid] = error
                        break
            
            # For any invalid MPIDs without a specific error, use the first error
            for mpid in invalid_mpids:
                if mpid not in error_map and errors:
                    error_map[mpid] = errors[0]
            
            outcomes = []
            for idx, mpid in enumerate(resolved_mpids):
                if mpid in invalid_mpids:
                    if idx == 0:
                        outcomes.append(BatchMpidOutcome(mpid, "stopped", "validation_error", error_map.get(mpid, errors[0]), None))
                    else:
                        outcomes.append(BatchMpidOutcome(mpid, "skipped", "validation_error", error_map.get(mpid, errors[0]), None))
                else:
                    # Valid MPID but we have validation errors for other MPIDs
                    if idx == 0:
                        outcomes.append(BatchMpidOutcome(mpid, "stopped", "validation_error", errors[0], None))
                    else:
                        outcomes.append(BatchMpidOutcome(mpid, "skipped", "validation_error", errors[0], None))
            
            return BatchRunReport(
                requested=resolved_mpids,
                outcomes=tuple(outcomes),
                stopped=True,
                stop_reason="validation_error",
            )
        
        # Ensure absent log always exists with header
        self._init_csv(self._config.absent_log_path, ABSENT_LOG_HEADER)
        
        outcomes: list[BatchMpidOutcome] = []
        stop: _BatchGateStop | None = None
        processed_count = 0
        
        for mpid in valid_mpids:
            if stop is not None and not self._config.continue_on_error:
                outcomes.append(BatchMpidOutcome(mpid, "skipped"))
                continue
            try:
                self._acquire(mpid)
            except _KnownAbsentStop as absent:
                # Log the absent record
                self._log_absent(
                    absent.mpid,
                    absent.url,
                    absent.http_status,
                    absent.absent_marker,
                )
                outcomes.append(
                    BatchMpidOutcome(
                        mpid, "known_absent", error_type=None, detail=None,
                        http_status=absent.http_status, absent_marker=absent.absent_marker
                    )
                )
            except _GateStop as gate:
                stop = _BatchGateStop(gate.error_type, gate.detail, gate.http_status)
                self._gate_to_error_log(mpid, gate)
                outcomes.append(
                    BatchMpidOutcome(mpid, "stopped", gate.error_type, gate.detail, gate.http_status)
                )
                if not self._config.continue_on_error:
                    # Add remaining MPIDs as skipped
                    processed_count += 1
                    remaining = valid_mpids[processed_count:]
                    for remaining_mpid in remaining:
                        outcomes.append(BatchMpidOutcome(remaining_mpid, "skipped"))
                    break
            else:
                outcomes.append(BatchMpidOutcome(mpid, "acquired"))
            
            processed_count += 1
        
        if stop is not None and not self._config.continue_on_error:
            return BatchRunReport(
                requested=resolved_mpids,
                outcomes=tuple(outcomes),
                stopped=True,
                stop_reason=stop.error_type,
            )
        return BatchRunReport(requested=resolved_mpids, outcomes=tuple(outcomes))

    # -- Reuse smoke client methods -------------------------------------------------
    
    def _acquire(self, mpid: int) -> None:
        """Acquire a single MPID (reuses smoke client logic)."""
        url = protein_url(mpid)
        raw_path = self._config.raw_path(mpid)
        if raw_path.exists():
            raise _GateStop(
                "raw_file_exists",
                f"Raw file already exists and is append-only: {raw_path}",
            )

        if not self._robots_allows(url):
            raise _GateStop(
                "robots_disallow",
                f"robots.txt disallows fetching {url}",
            )

        response = self._fetch_with_retry(url)
        self._validate_response(url, response)

        decoded = response.body.decode("utf-8", errors="replace")
        lowered = decoded.lower()
        for marker in BLOCK_MARKERS:
            if marker in lowered:
                raise _GateStop(
                    "block_or_challenge",
                    f"Response body contains a block/challenge marker: {marker!r}",
                    response.status_code,
                )

        try:
            record = parse_moonprot_html(decoded, expected_mpid=mpid)
        except MoonProtKnownAbsentError as exc:
            raise _KnownAbsentStop(mpid, url, response.status_code, exc.absent_marker) from exc
        except MoonProtParseError as exc:
            raise _GateStop(
                "parser_error",
                f"Parser rejected the fetched page: {exc}",
                response.status_code,
            ) from exc

        self._persist(mpid, url, response, record)

    def _robots_allows(self, url: str) -> bool:
        response = self._request(ROBOTS_URL)
        if response.status_code in (404, 410):
            return True
        if not 200 <= response.status_code < 300:
            raise _GateStop(
                "robots_unavailable",
                f"robots.txt could not be retrieved (HTTP {response.status_code})",
                response.status_code,
            )
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(response.body.decode("utf-8", errors="replace").splitlines())
        return parser.can_fetch(self._config.user_agent, url)

    def _fetch_with_retry(self, url: str) -> TransportResponse:
        attempts = 0
        while True:
            attempts += 1
            try:
                response = self._request(url)
            except TransportError as exc:
                if attempts <= self._config.max_retries:
                    self._sleeper(self._config.retry_backoff_seconds)
                    continue
                raise _GateStop(
                    "transport_error",
                    f"Transport failed after {attempts} attempt(s): {exc}",
                ) from exc
            if response.status_code in REDIRECT_STATUSES or (
                response.final_url is not None and response.final_url != url
            ):
                raise _GateStop(
                    "unexpected_redirect",
                    f"Unexpected redirect for {url} (HTTP {response.status_code})",
                    response.status_code,
                )
            if 200 <= response.status_code < 300:
                return response
            if attempts <= self._config.max_retries:
                self._sleeper(self._config.retry_backoff_seconds)
                continue
            raise _GateStop(
                "http_error",
                f"HTTP {response.status_code} persisted after {attempts} attempt(s)",
                response.status_code,
            )

    def _validate_response(self, url: str, response: TransportResponse) -> None:
        content_type = ""
        for name, value in response.headers.items():
            if name.lower() == "content-type":
                content_type = value
                break
        if REQUIRED_HTML_CONTENT_TYPE not in content_type.lower():
            raise _GateStop(
                "content_type_rejected",
                f"Unacceptable content type for {url}: {content_type!r}",
                response.status_code,
            )

    def _persist(self, mpid: int, url: str, response: TransportResponse, record: Any) -> None:
        config = self._config
        raw_path = config.raw_path(mpid)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(response.body)

        sha256 = hashlib.sha256(response.body).hexdigest()
        rel_raw = raw_path.relative_to(config.root).as_posix()
        content_type = ""
        for name, value in response.headers.items():
            if name.lower() == "content-type":
                content_type = value
                break

        self._append_csv_row(
            config.artifact_index_path,
            INDEX_HEADER,
            (
                str(mpid),
                url,
                _utc_now_iso(),
                str(response.status_code),
                content_type,
                rel_raw,
                sha256,
                str(len(response.body)),
                "ok",
                ";".join(record.missing_fields),
            ),
        )

        config.checksums_path.parent.mkdir(parents=True, exist_ok=True)
        with config.checksums_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{sha256}  {rel_raw}\n")

        self._append_csv_row(
            config.smoke_result_path,
            SMOKE_RESULT_HEADER,
            (str(mpid), record.uniprot_id or "", record.protein_name or ""),
        )

    def _log_error(
        self,
        mpid: int | str,
        url: str,
        error_type: str,
        detail: str,
        http_status: int | None,
    ) -> None:
        path = self._config.error_log_path
        self._append_csv_row(
            path,
            ERROR_LOG_HEADER,
            (
                str(mpid),
                url,
                error_type,
                detail,
                "" if http_status is None else str(http_status),
                _utc_now_iso(),
            ),
        )

    def _gate_to_error_log(self, mpid: int, gate: _GateStop) -> None:
        self._log_error(mpid, protein_url(mpid), gate.error_type, gate.detail, gate.http_status)

    def _log_absent(
        self,
        mpid: int,
        url: str,
        http_status: int,
        absent_marker: str,
    ) -> None:
        path = self._config.absent_log_path
        self._append_csv_row(
            path,
            ABSENT_LOG_HEADER,
            (
                str(mpid),
                url,
                str(http_status),
                absent_marker,
                _utc_now_iso(),
            ),
        )

    def _request(self, url: str) -> TransportResponse:
        if self._last_request_at is not None:
            elapsed = self._clock() - self._last_request_at
            wait = self._config.delay_seconds - elapsed
            if wait > 0:
                self._sleeper(wait)
        response = self._transport.get(
            url,
            user_agent=self._config.user_agent,
            timeout_seconds=self._config.timeout_seconds,
        )
        self._last_request_at = self._clock()
        return response

    @staticmethod
    def _init_csv(path: Path, header: tuple[str, ...]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        needs_header = not path.exists() or path.stat().st_size == 0
        if needs_header:
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(header)

    @staticmethod
    def _append_csv_row(path: Path, header: tuple[str, ...], row: tuple[str, ...]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        needs_header = not path.exists() or path.stat().st_size == 0
        with path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            if needs_header:
                writer.writerow(header)
            writer.writerow(row)
