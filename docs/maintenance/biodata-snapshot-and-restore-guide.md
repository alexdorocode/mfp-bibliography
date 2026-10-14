# BioData Snapshot & Restoration Guide

This operational guide provides step-by-step instructions for restoring and creating consistent point-in-time snapshots of the `BioData` PostgreSQL database used in the multifunctional protein (MFP) analytical pipeline.

---

## 1. Baseline Snapshot Information

The primary verified baseline snapshot of `BioData` is registered as follows:

| Property | Value |
|---|---|
| **Snapshot ID** | `biodata_mfp_snapshot_20261014` |
| **Created At (UTC)** | 2026-10-14 07:49:00 UTC |
| **Dump File Location** | [`data/snapshots/biodata_mfp_snapshot_20261014.dump`](../../data/snapshots/biodata_mfp_snapshot_20261014.dump) |
| **Manifest File** | [`releases/snapshots/biodata_mfp_snapshot_20261014.manifest.json`](../../releases/snapshots/biodata_mfp_snapshot_20261014.manifest.json) |
| **Format** | PostgreSQL Custom Dump (`-F c`, compressed) |
| **File Size** | 5,031,619 bytes (~4.8 MB) |
| **SHA-256 Checksum** | `be5dec2e16f08e4c72291b0f61e7804c82f72b4368d3ce0ac066592d315ea72b` |
| **Database Server** | PostgreSQL 16.13 (`pgvector/pgvector:pg16`) |
| **Docker Container** | `pgvectorsql` |

### Verified Table Row Counts

Every restore operation must match these exact counts:

| Table | Expected Row Count | Description |
|---|---|---|
| `accession` | **2,330** | Raw & secondary UniProt accession mappings |
| `protein` | **2,182** | Unified protein entities resolved by UniProt |
| `sequence` | **2,160** | Canonical amino acid sequences |
| `go_terms` | **9,376** | Unique Gene Ontology terms present in the cohort |
| `protein_go_term_annotation` | **96,186** | Persisted QuickGO annotations |
| `chain` | **0** | Unpopulated in this snapshot |

---

## 2. Restoration Procedures

All commands assume the host terminal is in `/home/alexdoro/repositories/mfp-bibliography` and Docker container `pgvectorsql` is running.

### Procedure A: Restore into an Isolated Database (Recommended)

Use this procedure to run experimental scripts, offline metric recalculations, or validation queries without touching the live `BioData` database.

```bash
# 1. Create a fresh target database inside the PostgreSQL container
docker exec pgvectorsql createdb -U usuario BioData_Restored

# 2. Copy the snapshot dump into the container /tmp
docker cp data/snapshots/biodata_mfp_snapshot_20261014.dump pgvectorsql:/tmp/restore.dump

# 3. Restore schema, tables, constraints, and data
docker exec pgvectorsql pg_restore -U usuario -d BioData_Restored --clean --if-exists -v /tmp/restore.dump

# 4. Clean up the temporary dump file inside the container
docker exec pgvectorsql rm -f /tmp/restore.dump

# 5. Verify row count reconciliation
docker exec pgvectorsql psql -U usuario -d BioData_Restored -c "
SELECT 'accession' AS table_name, COUNT(*) AS row_count FROM accession
UNION ALL SELECT 'protein', COUNT(*) FROM protein
UNION ALL SELECT 'sequence', COUNT(*) FROM sequence
UNION ALL SELECT 'go_terms', COUNT(*) FROM go_terms
UNION ALL SELECT 'protein_go_term_annotation', COUNT(*) FROM protein_go_term_annotation
UNION ALL SELECT 'chain', COUNT(*) FROM chain;
"
```

### Procedure B: Overwrite / Recover Live `BioData`

> [!CAUTION]
> This procedure will overwrite the current live `BioData` database. Ensure no active tasks or background workers are writing to the database before executing.

```bash
# 1. Copy the snapshot dump into the container /tmp
docker cp data/snapshots/biodata_mfp_snapshot_20261014.dump pgvectorsql:/tmp/restore.dump

# 2. Execute full clean restore
docker exec pgvectorsql pg_restore -U usuario -d BioData --clean --if-exists -v /tmp/restore.dump

# 3. Clean up the container temporary file
docker exec pgvectorsql rm -f /tmp/restore.dump

# 4. Run verification query
docker exec pgvectorsql psql -U usuario -d BioData -c "
SELECT 'accession' AS table_name, COUNT(*) AS row_count FROM accession
UNION ALL SELECT 'protein', COUNT(*) FROM protein
UNION ALL SELECT 'sequence', COUNT(*) FROM sequence
UNION ALL SELECT 'go_terms', COUNT(*) FROM go_terms
UNION ALL SELECT 'protein_go_term_annotation', COUNT(*) FROM protein_go_term_annotation
UNION ALL SELECT 'chain', COUNT(*) FROM chain;
"
```

---

## 3. How to Create a New Snapshot

When creating a new snapshot after a controlled extraction run:

```bash
# Set snapshot timestamp identifier
SNAPSHOT_DATE=$(date -u +%Y%m%d)
SNAPSHOT_NAME="biodata_mfp_snapshot_${SNAPSHOT_DATE}"

# 1. Perform a consistent, non-blocking custom pg_dump inside the container
docker exec pgvectorsql pg_dump -U usuario -d BioData -F c -b -v -f /tmp/${SNAPSHOT_NAME}.dump

# 2. Copy the dump out of the container to data/snapshots/
mkdir -p data/snapshots releases/snapshots
docker cp pgvectorsql:/tmp/${SNAPSHOT_NAME}.dump data/snapshots/${SNAPSHOT_NAME}.dump
docker exec pgvectorsql rm -f /tmp/${SNAPSHOT_NAME}.dump

# 3. Compute SHA-256 checksum
sha256sum data/snapshots/${SNAPSHOT_NAME}.dump > data/snapshots/${SNAPSHOT_NAME}.sha256
cat data/snapshots/${SNAPSHOT_NAME}.sha256

# 4. Verify restoration in an ephemeral test database
docker exec pgvectorsql createdb -U usuario ${SNAPSHOT_NAME}_test
docker cp data/snapshots/${SNAPSHOT_NAME}.dump pgvectorsql:/tmp/test_verify.dump
docker exec pgvectorsql pg_restore -U usuario -d ${SNAPSHOT_NAME}_test /tmp/test_verify.dump
docker exec pgvectorsql rm -f /tmp/test_verify.dump

# 5. Check row counts in the test database
docker exec pgvectorsql psql -U usuario -d ${SNAPSHOT_NAME}_test -c "
SELECT 'accession' AS table_name, COUNT(*) AS row_count FROM accession
UNION ALL SELECT 'protein', COUNT(*) FROM protein
UNION ALL SELECT 'sequence', COUNT(*) FROM sequence
UNION ALL SELECT 'go_terms', COUNT(*) FROM go_terms
UNION ALL SELECT 'protein_go_term_annotation', COUNT(*) FROM protein_go_term_annotation
UNION ALL SELECT 'chain', COUNT(*) FROM chain;
"

# 6. Drop ephemeral test database
docker exec pgvectorsql dropdb -U usuario ${SNAPSHOT_NAME}_test

# 7. Create/update the JSON manifest in releases/snapshots/
```

---

## 4. Verification Checksum Validation

To verify the integrity of the downloaded or archived dump file on any host:

```bash
sha256sum -c <<EOF
be5dec2e16f08e4c72291b0f61e7804c82f72b4368d3ce0ac066592d315ea72b  data/snapshots/biodata_mfp_snapshot_20261014.dump
EOF
```

Expected output:
```text
data/snapshots/biodata_mfp_snapshot_20261014.dump: OK
```

---

## 5. Related Documents

- Snapshot Manifest: [`releases/snapshots/biodata_mfp_snapshot_20261014.manifest.json`](../../releases/snapshots/biodata_mfp_snapshot_20261014.manifest.json)
- Extraction & Unification Audit: [`docs/audits/MFP_EXTRACTION_UNIFICATION_AUDIT.md`](../audits/MFP_EXTRACTION_UNIFICATION_AUDIT.md)
- Data Auditability Matrix: [`docs/audits/MFP_DATA_AUDITABILITY_MATRIX.md`](../audits/MFP_DATA_AUDITABILITY_MATRIX.md)
- MVP Roadmap: [`docs/experiments/MFP_BIBLIOGRAPHIC_MVP_ROADMAP.md`](../experiments/MFP_BIBLIOGRAPHIC_MVP_ROADMAP.md)

