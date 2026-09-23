# MoonProt Acquisition Protocol (Planned)

Status: planned contract only. No scraper implementation or execution in this repository state.

## Offline parser status (MFPB_0_11_MOONPROT_OFFLINE_PARSER)

- **Implemented**: a pure, offline HTML parser for local fixtures only,
  `src/mfp_bibliography/moonprot_parser.py`, with the fixture CLI
  `scripts/parse_moonprot_fixture.py`.
- **Guarantees**: fields are located by visible labels (`MoonProt ID`,
  `UniProt ID`, `Name(s)`), never by fixed table row positions; raw label/value
  text is preserved after minimal whitespace trimming; missing `uniprot_id` or
  `Name(s)` are reported explicitly on the record; malformed HTML, duplicate
  labels, a missing MoonProt ID, and an MPID conflicting with the expected
  input ID raise typed parse errors.
- **Out of scope**: the parser assigns no policy status and creates no source
  claims.

## Acquisition gate (explicit)

The parser and CLI contain **no network, HTTP client, scraper, retry, or
acquisition code** and never contact MoonProt or any external URL. Real
acquisition remains a **future task only**, gated behind source-policy review
plus inspection of `robots.txt`, terms, access restrictions, and rate limits.
Until that gate is passed, only local fixtures under
`data/fixtures/moonprot/` may be parsed.

## Planned target

- URL pattern: `http://www.moonlightingproteins.org/protein_detail/?mpid={id}`
- Full inclusive ID range (future, reference only): `mpid=1..706`
- Target fields: `UniProt ID`, `Name(s)`
- Expected extraction output format: `uniprot_id,name`

## Smoke scope (only approved execution scope)

- MPIDs `1`, `2`, `3` only. Any request outside `1,2,3` is a stop condition.
- The full `1..706` range remains out of scope until a separate review.

## Raw artifact layout

- One raw file per MPID: `data/raw/moonprot/mpid_{id}.html` (e.g.
  `mpid_1.html`), containing the response bytes **verbatim**, written once,
  append-only per ADR-002 (never edited in place).
- Raw files are written only through the persistence gate below; no partial or
  failed-response bodies are ever persisted.
- Per-file provenance lives exclusively in
  `data/raw/moonprot/artifact_index.csv`, specified in
  `moonprot-artifact-index.md`.

## Source manifest mapping

- The source manifest keeps **one row per source**: `SRC_MOONPROT` represents
  the acquisition batch only (method, acquisition window, aggregate notes).
- Per-file provenance (URL, checksum, HTTP status, parser status) lives
  exclusively in `artifact_index.csv`; it is never duplicated into the source
  manifest.
- The manifest schema is unchanged in this increment; no `SRC_MOONPROT` row
  exists yet.

## Error logging requirements

Store a separate error log with exactly these fields:
- `mpid`
- `url`
- `error_type`
- `detail`
- `http_status`
- `attempted_at`

The error log file at `data/interim/moonprot_smoke_error_log.csv` **must always
 exist** after a run, even on complete success (header-only).
`http_status` is empty when not applicable (e.g. robots gate, timeout,
parser error). Every failed or skipped attempt produces one error-log record.

## Compliance and access constraints

Before implementation/execution, inspect and respect applicable `robots.txt`, terms, access restrictions, and rate limits.

## Execution requirements (first version)

- **Sequential requests only**: never concurrent.
- **Delay**: minimum 10 seconds between any two requests.
- **User-Agent**: required, honest (identifies this project and a contact),
  configurable; no spoofing of browser identifiers.
- **Timeout**: 15 seconds per request.
- **Retry**: at most 1 retry per MPID.
- **Backoff**: minimum 30 seconds before any retry.
- No silent failures: every attempt is reflected in the error log or the
  artifact index.

## Persistence gate (verbatim bytes only after all pass)

Raw response bytes are persisted only after, in order:

1. The `robots.txt`/terms gate passes for the target URL.
2. The HTTP response is successful.
3. There is no unexpected redirect.
4. The content type is acceptable HTML.
5. The offline parser succeeds with the expected MPID.

Any failure means nothing is written to `data/raw/`; the attempt goes to the
error log only.

## Stop conditions (execution halts immediately)

- `robots.txt` or terms disallow access.
- A CAPTCHA, block, or JavaScript challenge page is detected.
- An unexpected redirect or unacceptable content type is received.
- HTTP 4xx/5xx persists after the single allowed retry.
- A typed parser error occurs on a fetched page.
- The raw file `data/raw/moonprot/mpid_{id}.html` already exists.
- Any request would target an MPID outside `1,2,3`.

## Parsing constraints

The HTML parser must identify fields by labels, not fixed row positions.

## Testing requirements

- Local HTML fixtures are mandatory.
- Mock network errors are mandatory.
- Normal test runs must not perform real-network requests.

## Approval gate

MoonProt scraping is an approved **future task only** after source-policy review.
