# MoonProt Smoke Test Report

## Scope
- MPIDs: `1`, `2`, `3` only (approved smoke scope)

## Acquisition Date/Time
- MPID 1: 2026-09-22T15:13:45Z
- MPID 2: 2026-09-22T15:14:06Z
- MPID 3: 2026-09-22T15:14:26Z

## Artifacts Produced
- `data/raw/moonprot/mpid_1.html` (39474 bytes, SHA-256: `1a1a93f573f5d04b5541aa806057b694d258623ec2bbe6147f91dfe3dd13944c`)
- `data/raw/moonprot/mpid_2.html` (40568 bytes, SHA-256: `e74406e97535bc7eaf3d26b1f39fe11f329a8c88bda59bc5a132bdebda249db1`)
- `data/raw/moonprot/mpid_3.html` (44020 bytes, SHA-256: `e8575e20e97e7b08f56a4dd33ef99b5072ad8de85112f31d0c13dca767846713`)
- `data/raw/moonprot/artifact_index.csv` (per-file provenance)
- `data/interim/moonprot_smoke_results.csv` (extracted: mpid, uniprot_id, protein_name)
- `data/manifests/file_checksums.sha256` (SHA-256 checksums)
- `data/interim/moonprot_smoke_error_log.csv` (header-only, no errors)

## Parser and Integrity Results
- All three pages parsed successfully with expected MPIDs
- No typed parser errors
- SHA-256 checksums verified against manifest
- HTTP status: 200 for all requests
- Content type: `text/html; charset=UTF-8` for all responses
- No unexpected redirects, blocks, or CAPTCHA challenges detected

## Errors
- None observed

## Explicit Statement
This is **not** a bulk dataset and **not** a source-claims input. Smoke test only; no redistribution or bulk scraping occurred or is permitted without further approval.
