# MoonProt Maintainer Contact Draft

## Purpose
Request confirmation of responsible access pattern for MoonProt MPIDs 4-706 for academic/research use.

## Context
- **Project**: mfp-bibliography (Multifunctional Protein Bibliography)
- **Smoke test completed**: MPIDs 1-3 only, validated and documented
- **Bulk acquisition blocked**: MPIDs 4-706 pending maintainer guidance
- **Local snapshot**: MoonDB+PlantMP effective-status artifact is reproducible (463 claims → 461 IDs; curated=124, predicted=326, excluded_likely=11)
- **No MoonProt data included** in current snapshot

## Request
We seek explicit confirmation and guidance before proceeding with any access to MoonProt MPIDs 4-706.

### Specific Questions
1. Is controlled sequential retrieval of MPIDs 4-706 for academic research acceptable?
2. Is there a preferred export/download mechanism or API we should use instead of web requests?
3. What is the recommended rate limit and request pattern?
4. What guidance applies to data use, redistribution, citation, and licensing for MoonProt content?

## Requested Fields Only
- MoonProt ID
- UniProt ID
- Name(s)

These are the only fields we need to extract. No additional data is required.

## Scope
- **Target range**: MPIDs 4 through 706 (703 entries)
- **Access pattern**: Sequential requests only, never concurrent
- **Volume**: Approximately 703 individual protein-detail page requests

## Access Pattern Assurances
- **Sequential only**: Never concurrent requests
- **Polite delay**: Will implement minimum delay between requests (configurable, default 10 seconds)
- **User-Agent**: Will use honest identifier: `mfp-bibliography/0.1 (contact: <curator email>)`
- **Robots.txt**: Will check and respect `robots.txt` before every request
- **No credentials**: No request for credentials or special access
- **Rate limiting**: Will respect any stated rate limits and implement stricter limits if requested

## Data Use Assurances
- **Academic/research use only**: Non-commercial research project
- **No redistribution**: Will not redistribute MoonProt content without explicit permission
- **Citation**: Will cite MoonProt appropriately if results are published
- **Compliance**: Will follow all applicable terms and license requirements

## Implementation Assurances
- **Controlled acquisition**: Will implement controlled, sequential acquisition only
- **No bulk scraping**: Bulk scraping will not proceed without maintainer guidance
- **Preferred mechanisms**: Willing to use any preferred download/API/export if available
- **Validation**: Will validate all fetched data against expected structure

## Smoke Test Status
- **Completed**: MPIDs 1-3 acquired and validated
- **Validated**: Raw HTML, artifact index, checksums, results, and error log all valid
- **No issues**: No parser errors, no blocks, no redirects

## Decision Paths
We will follow one of three documented paths based on your response:
1. **Approved with conditions**: Proceed with specified rate limits and conditions
2. **Preferred official export/API**: Use official mechanism instead of web requests
3. **No response / access not confirmed**: No bulk acquisition will proceed

No action will be taken until we receive your guidance.

## Contact Information
- **Project**: mfp-bibliography
- **Status**: Awaiting maintainer confirmation before any bulk acquisition for MPIDs 4-706
- **Next step**: Manual outreach via project website contact form or published email
