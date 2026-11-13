"""Validation and invariant checking for raw QuickGO exports from MFP_QuickV1.

Stages P1-P2: Bounded validation for raw annotations and denominator coverage fixtures.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from jsonschema import Draft202012Validator, ValidationError


EXPECTED_COHORT: Tuple[str, ...] = (
    "Q42525",
    "Q9Y3E5",
    "P0AFW0",
    "P34788",
    "P78007",
    "P24228",
    "A0A0H3CDS3",
    "E6KMA1",
)

PMID_PATTERN = re.compile(r"^[0-9]+$")
GO_REF_PATTERN = re.compile(r"^GO_REF:[0-9]{7}$")
GO_ID_PATTERN = re.compile(r"^GO:[0-9]{7}$")


class QuickGORawValidationError(ValueError):
    """Raised when raw QuickGO export fails schema or invariant validation."""


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_schema(schema_path: Path) -> dict[str, Any]:
    """Load JSON Schema from disk with UTF-8 encoding."""
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_validator(schema_path: Path) -> Draft202012Validator:
    """Build and verify a Draft 2020-12 validator."""
    schema = load_schema(schema_path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def parse_csv_value(val: str) -> Optional[str]:
    """Parse raw CSV string, mapping empty string to None."""
    val = val.strip()
    return val if val != "" else None


def read_raw_annotations_csv(csv_path: Path) -> List[Dict[str, Any]]:
    """Read raw annotations CSV, converting types and empty strings to None."""
    rows: List[Dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected_fields = [
            "database_annotation_id",
            "accession",
            "database_protein_id",
            "go_id",
            "raw_category",
            "evidence_code",
            "publication_id",
        ]
        if reader.fieldnames != expected_fields:
            raise QuickGORawValidationError(
                f"Annotations CSV headers {reader.fieldnames} do not match expected {expected_fields}"
            )
        for i, row in enumerate(reader, start=1):
            raw_id = row["database_annotation_id"].strip()
            try:
                db_id = int(raw_id)
            except ValueError:
                raise QuickGORawValidationError(
                    f"Row {i}: invalid non-integer database_annotation_id '{raw_id}'"
                )
            rows.append(
                {
                    "database_annotation_id": db_id,
                    "accession": row["accession"].strip(),
                    "database_protein_id": row["database_protein_id"].strip(),
                    "go_id": row["go_id"].strip(),
                    "raw_category": row["raw_category"].strip(),
                    "evidence_code": row["evidence_code"].strip(),
                    "publication_id": parse_csv_value(row["publication_id"]),
                }
            )
    return rows


def read_raw_coverage_csv(csv_path: Path) -> List[Dict[str, Any]]:
    """Read raw coverage CSV, converting types and empty strings to None."""
    rows: List[Dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected_fields = [
            "accession",
            "database_protein_id",
            "quickgo_coverage_status",
            "identity_review_status",
            "stored_annotation_rows",
            "distinct_go_terms",
            "notes",
        ]
        if reader.fieldnames != expected_fields:
            raise QuickGORawValidationError(
                f"Coverage CSV headers {reader.fieldnames} do not match expected {expected_fields}"
            )
        for i, row in enumerate(reader, start=1):
            try:
                stored_rows = int(row["stored_annotation_rows"].strip())
                distinct_terms = int(row["distinct_go_terms"].strip())
            except ValueError:
                raise QuickGORawValidationError(
                    f"Row {i}: stored_annotation_rows or distinct_go_terms is not an integer"
                )
            rows.append(
                {
                    "accession": row["accession"].strip(),
                    "database_protein_id": parse_csv_value(row["database_protein_id"]),
                    "quickgo_coverage_status": row["quickgo_coverage_status"].strip(),
                    "identity_review_status": row["identity_review_status"].strip(),
                    "stored_annotation_rows": stored_rows,
                    "distinct_go_terms": distinct_terms,
                    "notes": parse_csv_value(row["notes"]),
                }
            )
    return rows


def validate_raw_annotations_schema(
    rows: List[Dict[str, Any]], validator: Draft202012Validator
) -> None:
    """Validate all rows in raw annotations against the schema."""
    for i, row in enumerate(rows, start=1):
        errors = list(validator.iter_errors(row))
        if errors:
            msg = "; ".join(e.message for e in errors)
            raise QuickGORawValidationError(
                f"Raw annotations row {i} failed schema validation: {msg} | Row: {row}"
            )


def validate_raw_coverage_schema(
    rows: List[Dict[str, Any]], validator: Draft202012Validator
) -> None:
    """Validate all rows in raw coverage against the schema."""
    for i, row in enumerate(rows, start=1):
        errors = list(validator.iter_errors(row))
        if errors:
            msg = "; ".join(e.message for e in errors)
            raise QuickGORawValidationError(
                f"Raw coverage row {i} failed schema validation: {msg} | Row: {row}"
            )


def validate_raw_annotations_invariants(
    rows: List[Dict[str, Any]], allowed_cohort: Tuple[str, ...] = EXPECTED_COHORT
) -> Dict[str, Any]:
    """Verify dataset-level invariants on raw annotations."""
    seen_db_ids: Set[int] = set()
    seen_tuples: Set[Tuple[str, str, str, Optional[str]]] = set()
    pmid_count = 0
    go_ref_count = 0
    null_ref_count = 0

    for i, row in enumerate(rows, start=1):
        db_id = row["database_annotation_id"]
        if db_id in seen_db_ids:
            raise QuickGORawValidationError(
                f"Duplicate database_annotation_id {db_id} at row {i}"
            )
        seen_db_ids.add(db_id)

        acc = row["accession"]
        if acc not in allowed_cohort:
            raise QuickGORawValidationError(
                f"Row {i} accession '{acc}' is not in allowed cohort {allowed_cohort}"
            )

        pub_id = row["publication_id"]
        if pub_id is None:
            null_ref_count += 1
        elif PMID_PATTERN.match(pub_id):
            pmid_count += 1
        elif GO_REF_PATTERN.match(pub_id):
            go_ref_count += 1
        else:
            raise QuickGORawValidationError(
                f"Row {i}: unexpected publication_id format '{pub_id}'"
            )

        # Check tuple uniqueness: (accession, go_id, evidence_code, publication_id)
        tpl = (acc, row["go_id"], row["evidence_code"], pub_id)
        if tpl in seen_tuples:
            raise QuickGORawValidationError(
                f"Duplicate annotation tuple (accession, go_id, evidence_code, publication_id) {tpl} at row {i}"
            )
        seen_tuples.add(tpl)

    return {
        "total_rows": len(rows),
        "distinct_db_ids": len(seen_db_ids),
        "pmid_rows": pmid_count,
        "go_ref_rows": go_ref_count,
        "null_ref_rows": null_ref_count,
    }


def validate_raw_coverage_invariants(
    rows: List[Dict[str, Any]], expected_cohort: Tuple[str, ...] = EXPECTED_COHORT
) -> Dict[str, Any]:
    """Verify dataset-level invariants on raw coverage."""
    if len(rows) != len(expected_cohort):
        raise QuickGORawValidationError(
            f"Coverage row count {len(rows)} does not match cohort size {len(expected_cohort)}"
        )

    seen_accessions: List[str] = [r["accession"] for r in rows]
    if len(set(seen_accessions)) != len(rows):
        raise QuickGORawValidationError(
            f"Duplicate accessions in coverage export: {seen_accessions}"
        )

    expected_set = set(expected_cohort)
    actual_set = set(seen_accessions)
    if expected_set != actual_set:
        missing = expected_set - actual_set
        extra = actual_set - expected_set
        raise QuickGORawValidationError(
            f"Coverage accessions mismatch. Missing: {missing}, Extra: {extra}"
        )

    status_counts: Dict[str, int] = {}
    for r in rows:
        acc = r["accession"]
        cov_status = r["quickgo_coverage_status"]
        id_status = r["identity_review_status"]
        status_counts[cov_status] = status_counts.get(cov_status, 0) + 1

        # Check P34788 taxonomic discrepancy flag
        if acc == "P34788":
            if id_status != "flagged_taxonomic_discrepancy":
                raise QuickGORawValidationError(
                    f"P34788 must have identity_review_status 'flagged_taxonomic_discrepancy', got '{id_status}'"
                )
        else:
            if id_status != "no_discrepancy_noted":
                raise QuickGORawValidationError(
                    f"{acc} must have identity_review_status 'no_discrepancy_noted', got '{id_status}'"
                )

    return {
        "total_coverage_rows": len(rows),
        "status_counts": status_counts,
    }


def validate_cross_file_consistency(
    annotation_rows: List[Dict[str, Any]], coverage_rows: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Verify cross-file consistency between annotations and denominator coverage."""
    # Group annotations by accession
    acc_annotations: Dict[str, List[Dict[str, Any]]] = {}
    for r in annotation_rows:
        acc = r["accession"]
        acc_annotations.setdefault(acc, []).append(r)

    coverage_map = {r["accession"]: r for r in coverage_rows}

    # Every accession in annotations must exist in coverage
    for acc in acc_annotations:
        if acc not in coverage_map:
            raise QuickGORawValidationError(
                f"Accession '{acc}' found in annotations but absent from coverage"
            )
        cov = coverage_map[acc]
        if cov["quickgo_coverage_status"] != "annotations_available":
            raise QuickGORawValidationError(
                f"Accession '{acc}' has annotations but coverage_status is '{cov['quickgo_coverage_status']}'"
            )

    # Check each coverage record
    reconciliation_details: Dict[str, Dict[str, Any]] = {}
    for acc, cov in coverage_map.items():
        cov_status = cov["quickgo_coverage_status"]
        stored_rows = cov["stored_annotation_rows"]
        distinct_terms = cov["distinct_go_terms"]
        actual_ann_rows = acc_annotations.get(acc, [])
        actual_row_count = len(actual_ann_rows)
        actual_distinct_go = len(set(r["go_id"] for r in actual_ann_rows))

        if cov_status == "annotations_available":
            if actual_row_count == 0:
                raise QuickGORawValidationError(
                    f"Accession '{acc}' marked 'annotations_available' but has 0 annotation rows"
                )
            if actual_row_count != stored_rows:
                raise QuickGORawValidationError(
                    f"Accession '{acc}' annotation row count mismatch: coverage claims {stored_rows}, actual is {actual_row_count}"
                )
            if actual_distinct_go != distinct_terms:
                raise QuickGORawValidationError(
                    f"Accession '{acc}' distinct GO count mismatch: coverage claims {distinct_terms}, actual is {actual_distinct_go}"
                )
        else:
            if actual_row_count != 0:
                raise QuickGORawValidationError(
                    f"Accession '{acc}' marked '{cov_status}' but has {actual_row_count} annotation rows"
                )
            if stored_rows != 0 or distinct_terms != 0:
                raise QuickGORawValidationError(
                    f"Accession '{acc}' marked '{cov_status}' but stored_rows={stored_rows}, distinct_terms={distinct_terms}"
                )

        reconciliation_details[acc] = {
            "quickgo_coverage_status": cov_status,
            "identity_review_status": cov["identity_review_status"],
            "annotation_rows": actual_row_count,
            "distinct_go_terms": actual_distinct_go,
        }

    return reconciliation_details


def validate_export_pair(
    annotations_csv: Path,
    coverage_csv: Path,
    annotations_schema: Path,
    coverage_schema: Path,
) -> Dict[str, Any]:
    """Execute complete validation of the exported raw fixture pair."""
    ann_validator = build_validator(annotations_schema)
    cov_validator = build_validator(coverage_schema)

    ann_rows = read_raw_annotations_csv(annotations_csv)
    cov_rows = read_raw_coverage_csv(coverage_csv)

    validate_raw_annotations_schema(ann_rows, ann_validator)
    validate_raw_coverage_schema(cov_rows, cov_validator)

    ann_stats = validate_raw_annotations_invariants(ann_rows)
    cov_stats = validate_raw_coverage_invariants(cov_rows)
    recon = validate_cross_file_consistency(ann_rows, cov_rows)

    return {
        "annotations_sha256": compute_sha256(annotations_csv),
        "coverage_sha256": compute_sha256(coverage_csv),
        "annotation_stats": ann_stats,
        "coverage_stats": cov_stats,
        "reconciliation": recon,
    }
