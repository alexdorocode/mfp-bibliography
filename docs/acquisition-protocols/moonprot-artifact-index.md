# MoonProt Artifact Index Specification

Status: contract only. No index data exists yet; the file
`data/raw/moonprot/artifact_index.csv` is created only by a future,
approved acquisition run.

## Purpose

`data/raw/moonprot/artifact_index.csv` is the **sole** per-file provenance
record for acquired MoonProt raw HTML files. The source manifest row
`SRC_MOONPROT` represents the acquisition batch only and never carries
per-file provenance.

## File contract

- CSV, UTF-8, one row per **successfully persisted** MPID, append-only per
  ADR-002 (rows are never edited or deleted).
- Header (exact, in order):

```
mpid,url,retrieved_at,http_status,content_type,raw_file_path,sha256,file_size_bytes,parser_status,missing_fields
```

- Failed attempts never appear here; they go to the MoonProt error log only.

## Field semantics

- `mpid`: the requested MoonProt ID (integer, e.g. `1`).
- `url`: the exact request URL.
- `retrieved_at`: ISO 8601 UTC timestamp of the successful response.
- `http_status`: HTTP status code of the successful response (e.g. `200`).
- `content_type`: the response `Content-Type` header value, verbatim.
- `raw_file_path`: repository-relative path, always
  `data/raw/moonprot/mpid_{id}.html`.
- `sha256`: SHA-256 of the persisted raw file bytes (hex).
- `file_size_bytes`: byte size of the persisted raw file.
- `parser_status`: `ok` (persistence requires the parser to have succeeded
  with the expected MPID); any parse failure prevents persistence and is
  error-logged instead.
- `missing_fields`: `;`-separated missing field names reported by the parser
  (e.g. `uniprot_id;protein_name`), empty if none.

## Consistency invariants

- Every row's `sha256` and `file_size_bytes` must match the referenced raw
  file exactly.
- No two rows may share an `mpid` or `raw_file_path`.
- Rows exist only for MPIDs within the approved scope (`1,2,3` for the smoke
  run).
