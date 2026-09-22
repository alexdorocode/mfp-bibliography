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
- Inclusive ID range: `mpid=1..706`
- Target fields: `UniProt ID`, `Name(s)`
- Expected extraction output format: `uniprot_id,name`

## Error logging requirements

Store a separate error log with at least:
- `mpid`
- `url`
- `error_type`
- `detail`
- optional `http_status`

## Compliance and access constraints

Before implementation/execution, inspect and respect applicable `robots.txt`, terms, access restrictions, and rate limits.

## Execution and resilience requirements (first version)

- Sequential execution.
- Configurable User-Agent.
- Configurable timeout and retry policy.
- Exponential backoff and delay controls.
- No silent failures.

## Parsing constraints

The HTML parser must identify fields by labels, not fixed row positions.

## Testing requirements

- Local HTML fixtures are mandatory.
- Mock network errors are mandatory.
- Normal test runs must not perform real-network requests.

## Approval gate

MoonProt scraping is an approved **future task only** after source-policy review.
