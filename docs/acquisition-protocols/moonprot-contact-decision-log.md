# MoonProt Maintainer Contact Decision Log

## Contract ID
`MFPB_0_15_MOONDB_PLANTMP_DERIVED_SNAPSHOT` (contact package)

## Purpose
Track responses and decisions related to MoonProt maintainer contact for bulk acquisition approval.

## Log Format
Each entry must include the following fields (CSV-compatible format):

| Field | Description |
|-------|-------------|
| `date` | ISO 8601 date when the entry was created |
| `status` | Current status: `draft`, `sent`, `awaiting_response`, `approved_with_conditions`, `preferred_export_api`, `no_response`, `rejected` |
| `contact_channel` | How contact was/will be made: `email`, `web_form`, `github_issue`, `other` |
| `request_scope` | Scope of the request: `MPIDs 4-706`, `full_database`, `specific_subset` |
| `response_summary` | Brief summary of the response (or "N/A" if no response yet) |
| `access_decision` | Decision on access: `pending`, `approved`, `approved_with_conditions`, `use_export_api`, `denied`, `no_response` |
| `terms_decision` | Decision on terms/license: `pending`, `acceptable`, `acceptable_with_conditions`, `unacceptable`, `clarification_needed` |
| `rate_limit_decision` | Decision on rate limiting: `pending`, `specified_X_sec`, `use_export`, `follow_robots`, `no_limit_specified` |
| `next_action` | Next action required: `send_draft`, `await_response`, `implement_conditions`, `use_export_api`, `recontact`, `abandon`, `none` |
| `notes` | Additional notes, constraints, or details |

## Response Paths

### Path 1: Approved with Conditions
- **Status**: `approved_with_conditions`
- **Access Decision**: `approved_with_conditions`
- **Rate Limit Decision**: Specifies concrete limits (e.g., `specified_10_sec`)
- **Next Action**: `implement_conditions`
- **Notes**: Must include the specific conditions agreed upon

### Path 2: Preferred Official Export/API
- **Status**: `preferred_export_api`
- **Access Decision**: `use_export_api`
- **Terms Decision**: Typically `acceptable` or `acceptable_with_conditions`
- **Rate Limit Decision**: Typically `use_export` (not applicable for web requests)
- **Next Action**: `use_export_api`
- **Notes**: Must include URL, format, and access instructions for the export/API

### Path 3: No Response / Access Not Confirmed
- **Status**: `no_response` or `rejected`
- **Access Decision**: `no_response` or `denied`
- **Terms Decision**: `unacceptable` or `clarification_needed`
- **Rate Limit Decision**: `no_limit_specified`
- **Next Action**: `abandon`
- **Notes**: Must explain why bulk acquisition cannot proceed

## Initial Entry (Draft)

```csv
date,status,contact_channel,request_scope,response_summary,access_decision,terms_decision,rate_limit_decision,next_action,notes
2026-09-23,draft,N/A,MPIDs 4-706,N/A,pending,pending,pending,send_draft,"Draft prepared. Awaiting manual review and sending. Smoke test (MPIDs 1-3) complete and validated. No bulk acquisition until guidance received."
```

## Template for Future Entries

```csv
{date},{status},{contact_channel},{request_scope},{response_summary},{access_decision},{terms_decision},{rate_limit_decision},{next_action},"{notes}"
```

## Rules
- Only one entry may have `status` of `draft` at any time
- Once sent, the draft entry is archived and a new `sent` entry is created
- The `date` field uses YYYY-MM-DD format
- The `notes` field may contain quoted strings and semicolons
- Entries must be appended in chronological order
- No entries may be deleted or modified after creation

## Current Status
The draft contact package has been prepared and is awaiting manual review and sending.
No bulk acquisition will proceed until a response is received and logged.
