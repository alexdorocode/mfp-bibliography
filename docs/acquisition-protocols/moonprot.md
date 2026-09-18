# MoonProt Acquisition Protocol (Planned)

Status: planned contract only. No scraper implementation or execution in this repository state.

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
