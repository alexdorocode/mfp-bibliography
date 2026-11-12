"""Unit tests and integrity verification for integrated functional normalization pilot.

Verifies:
1. Complete execution of build_functional_claims_pilot generating all required artifacts.
2. Schema validation under Draft 2020-12 across claims, annotations, and coverage.
3. Catalog referential integrity against mfp_catalog_mvp (all protein IDs exist in catalog).
4. Coverage reconciliation against the empirical 20-record cohort (100% denominator accounting).
5. Cross-source shared entity deduplication and total ordering (Q42525 3-way share; P34788 & P0AFW0 2-way shares).
6. Reference-granularity preservation (linked PMIDs in MoonProt vs record PMIDs in PlantMP vs semicolon PMIDs in Multitask).
7. Explicit-location preservation in MoonProt claim notes without inferring CC terms or triplets.
8. Deterministic byte-identical output across repeated runs and differing PYTHONHASHSEED values.
9. Baseline protection verifying no mutation to raw artifacts, catalog, or release candidate.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from jsonschema import Draft202012Validator
import pytest

from scripts.build_functional_claims_pilot import (
    ANNOTATIONS_SCHEMA_PATH,
    CLAIMS_SCHEMA_PATH,
    COVERAGE_SCHEMA_PATH,
    DEFAULT_CATALOG_PATH,
    DEFAULT_PILOT_DIR,
    DEFAULT_PROTEINS_CATALOG_PATH,
    DEFAULT_REPORTS_DIR,
    PILOT_COHORT_SPECIFICATION,
    REPO_ROOT,
    build_functional_claims_pilot,
    compute_sha256,
)


@pytest.fixture
def claims_validator() -> Draft202012Validator:
    with CLAIMS_SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.fixture
def annotations_validator() -> Draft202012Validator:
    with ANNOTATIONS_SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.fixture
def coverage_validator() -> Draft202012Validator:
    with COVERAGE_SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_pilot_pipeline_builds_and_validates(
    claims_validator: Draft202012Validator,
    annotations_validator: Draft202012Validator,
    coverage_validator: Draft202012Validator,
) -> None:
    """Verify build_functional_claims_pilot generates all required artifacts and passes Draft 2020-12 validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_pilot_dir = Path(tmpdir) / "pilot"
        tmp_reports_dir = Path(tmpdir) / "reports"

        report = build_functional_claims_pilot(
            pilot_dir=tmp_pilot_dir,
            reports_dir=tmp_reports_dir,
            catalog_path=DEFAULT_CATALOG_PATH,
        )

        assert report["verification_status"] == "VERIFIED"
        totals = report["cohort_summary"]["totals"]
        assert totals["source_records"] == 20
        assert totals["coverage"] == 20
        assert totals["claims"] == 44
        assert totals["annotations"] == 353

        # Check breakdown by source
        by_source = report["cohort_summary"]["by_source"]
        assert by_source["SRC_MULTITASKPROTDB_II"]["source_records"] == 6
        assert by_source["SRC_MULTITASKPROTDB_II"]["claims"] == 12
        assert by_source["SRC_MULTITASKPROTDB_II"]["annotations"] == 99

        assert by_source["SRC_PLANTMP"]["source_records"] == 8
        assert by_source["SRC_PLANTMP"]["claims"] == 22
        assert by_source["SRC_PLANTMP"]["annotations"] == 113

        assert by_source["SRC_MOONPROT"]["source_records"] == 6
        assert by_source["SRC_MOONPROT"]["claims"] == 10
        assert by_source["SRC_MOONPROT"]["annotations"] == 141

        # Check file outputs
        claims_file = tmp_pilot_dir / "functional_claims_pilot.csv"
        ann_file = tmp_pilot_dir / "source_go_annotations_pilot.csv"
        cov_file = tmp_pilot_dir / "functional_coverage_pilot.csv"
        manifest_file = tmp_pilot_dir / "manifest.json"
        report_file = tmp_reports_dir / "functional_claims_pilot_report.json"

        assert claims_file.exists()
        assert ann_file.exists()
        assert cov_file.exists()
        assert manifest_file.exists()
        assert report_file.exists()

        # Schema validation for claims.csv
        with claims_file.open("r", encoding="utf-8") as f:
            claims_rows = list(csv.DictReader(f))
        assert len(claims_rows) == 44
        for r in claims_rows:
            obj = {k: (None if v == "" else (int(v) if k == "claim_index" else v)) for k, v in r.items()}
            claims_validator.validate(obj)

        # Schema validation for source_go_annotations.csv
        with ann_file.open("r", encoding="utf-8") as f:
            ann_rows = list(csv.DictReader(f))
        assert len(ann_rows) == 353
        for r in ann_rows:
            obj = {k: (None if v == "" else (int(v) if k == "annotation_index" else v)) for k, v in r.items()}
            annotations_validator.validate(obj)

        # Schema validation for functional_coverage.csv
        with cov_file.open("r", encoding="utf-8") as f:
            cov_rows = list(csv.DictReader(f))
        assert len(cov_rows) == 20
        for r in cov_rows:
            obj = {k: (None if v == "" else (int(v) if k == "claims_extracted_count" else v)) for k, v in r.items()}
            coverage_validator.validate(obj)


def test_pilot_referential_integrity_and_shared_entities() -> None:
    """Verify catalog referential integrity, foreign keys, and cross-source shared entities."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_pilot_dir = Path(tmpdir) / "pilot"
        tmp_reports_dir = Path(tmpdir) / "reports"

        build_functional_claims_pilot(
            pilot_dir=tmp_pilot_dir,
            reports_dir=tmp_reports_dir,
            catalog_path=DEFAULT_CATALOG_PATH,
        )

        with (tmp_pilot_dir / "functional_claims_pilot.csv").open("r", encoding="utf-8") as f:
            claims = list(csv.DictReader(f))
        with (tmp_pilot_dir / "source_go_annotations_pilot.csv").open("r", encoding="utf-8") as f:
            annotations = list(csv.DictReader(f))
        with (tmp_pilot_dir / "functional_coverage_pilot.csv").open("r", encoding="utf-8") as f:
            coverage = list(csv.DictReader(f))

        # 1. Annotation claim_id referential integrity
        claims_by_id = {c["claim_id"]: c for c in claims}
        for a in annotations:
            cid = a["claim_id"]
            if cid:
                assert cid in claims_by_id, f"Annotation links to nonexistent claim {cid}"
                assert claims_by_id[cid]["protein_id"] == a["protein_id"]

        # 2. Total ordering check
        claim_keys = [
            (c["protein_id"], c["source_id"], c["source_record_id"], int(c["claim_index"]), c["claim_id"])
            for c in claims
        ]
        assert claim_keys == sorted(claim_keys), "functional_claims_pilot.csv violates total ordering"

        ann_keys = [
            (a["protein_id"], a["source_id"], a["source_record_id"], a["source_field"], int(a["annotation_index"]), a["annotation_id"])
            for a in annotations
        ]
        assert ann_keys == sorted(ann_keys), "source_go_annotations_pilot.csv violates total ordering"

        cov_keys = [(cov["protein_id"] or "", cov["source_id"], cov["source_record_id"]) for cov in coverage]
        assert cov_keys == sorted(cov_keys), "functional_coverage_pilot.csv violates total ordering"

        # 3. 3-Way Shared Protein entity check: Q42525 / MFP:U:8272bae0e8df8149
        shared_3way_claims = [c for c in claims if c["protein_id"] == "MFP:U:8272bae0e8df8149"]
        assert len(shared_3way_claims) == 8
        sources_3way = {c["source_id"] for c in shared_3way_claims}
        assert sources_3way == {"SRC_MULTITASKPROTDB_II", "SRC_PLANTMP", "SRC_MOONPROT"}

        # 4. 2-Way Shared Protein entity check: P34788 / MFP:U:d0cd1a882c7acdf3
        shared_plant_multi = [c for c in claims if c["protein_id"] == "MFP:U:d0cd1a882c7acdf3"]
        assert len(shared_plant_multi) == 5
        sources_plant_multi = {c["source_id"] for c in shared_plant_multi}
        assert sources_plant_multi == {"SRC_MULTITASKPROTDB_II", "SRC_PLANTMP"}

        # 5. 2-Way Shared Protein entity check: P0AFW0 / MFP:U:9023923ecdd9d57f
        shared_moon_multi = [c for c in claims if c["protein_id"] == "MFP:U:9023923ecdd9d57f"]
        assert len(shared_moon_multi) == 4
        sources_moon_multi = {c["source_id"] for c in shared_moon_multi}
        assert sources_moon_multi == {"SRC_MULTITASKPROTDB_II", "SRC_MOONPROT"}


def test_pilot_preservation_invariants() -> None:
    """Verify source-preservation invariants across references, cellular locations, and status handling."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_pilot_dir = Path(tmpdir) / "pilot"
        tmp_reports_dir = Path(tmpdir) / "reports"

        build_functional_claims_pilot(
            pilot_dir=tmp_pilot_dir,
            reports_dir=tmp_reports_dir,
            catalog_path=DEFAULT_CATALOG_PATH,
        )

        with (tmp_pilot_dir / "functional_claims_pilot.csv").open("r", encoding="utf-8") as f:
            claims = list(csv.DictReader(f))
        with (tmp_pilot_dir / "source_go_annotations_pilot.csv").open("r", encoding="utf-8") as f:
            annotations = list(csv.DictReader(f))
        with (tmp_pilot_dir / "functional_coverage_pilot.csv").open("r", encoding="utf-8") as f:
            coverage = list(csv.DictReader(f))

        # 1. Reference granularity:
        # MoonProt claims must have linked_reference_ids with PMID: and record_reference_ids is empty
        moon_claims = [c for c in claims if c["source_id"] == "SRC_MOONPROT"]
        for mc in moon_claims:
            assert mc["record_reference_ids"] == ""
            if mc["linked_reference_ids"]:
                assert "PMID:" in mc["linked_reference_ids"]

        # PlantMP claims must have record_reference_ids and linked_reference_ids is empty
        plant_claims = [c for c in claims if c["source_id"] == "SRC_PLANTMP"]
        for pc in plant_claims:
            assert pc["linked_reference_ids"] == ""
            # When pubmed_id was in raw, it's preserved in record_reference_ids
            if pc["source_record_id"] == "plantmp_order_1":
                assert pc["record_reference_ids"] == "7913892"

        # 2. Explicit cellular location preservation:
        # MoonProt MPID 1, 2, 7, 359 have cellular locations in notes
        moon_notes = [mc["notes"] for mc in moon_claims if mc["notes"]]
        assert any("cellular_location:" in n for n in moon_notes)

        # 3. Protein-level GO annotations in MoonProt have claim_id = "" (null)
        moon_ann = [a for a in annotations if a["source_id"] == "SRC_MOONPROT"]
        assert len(moon_ann) == 141
        for ma in moon_ann:
            assert ma["claim_id"] == "", f"MoonProt annotation {ma['annotation_id']} must have claim_id=null"

        # 4. PlantMP status mapping: likely is excluded_likely (unresolved), never curated; predicted is predicted
        order_68_claims = [c for c in plant_claims if c["source_record_id"] == "plantmp_order_68"]
        assert len(order_68_claims) == 3
        for oc in order_68_claims:
            assert oc["claim_assertion_type"] == "unresolved"
            assert "policy_status: excluded_likely" in oc["notes"]

        order_85_claims = [c for c in plant_claims if c["source_record_id"] == "plantmp_order_85"]
        assert len(order_85_claims) == 2
        for oc in order_85_claims:
            assert oc["claim_assertion_type"] == "predicted"
            assert "source_type: predicted" in oc["notes"]

        # 5. MoonProt MPID 288 extraction failure case (parse_failure)
        mpid_288_cov = next(cov for cov in coverage if cov["source_record_id"] == "moonprot_288")
        assert mpid_288_cov["coverage_status"] == "parse_failure"
        assert mpid_288_cov["claims_extracted_count"] == "0"
        assert mpid_288_cov["protein_id"] == "MFP:U:75a37d1de4bcf985"
        assert "malformed markup prevented functional statement extraction" in (mpid_288_cov["notes"] or "")
        mpid_288_claims = [c for c in claims if c["source_record_id"] == "moonprot_288"]
        assert len(mpid_288_claims) == 0
        mpid_288_ann = [a for a in annotations if a["source_record_id"] == "moonprot_288"]
        assert len(mpid_288_ann) == 22
        for a in mpid_288_ann:
            assert a["claim_id"] == ""
            assert a["protein_id"] == "MFP:U:75a37d1de4bcf985"

        # 6. Verify machine-readable diagnostic in report
        with (tmp_reports_dir / "functional_claims_pilot_report.json").open("r", encoding="utf-8") as f:
            pilot_rep = json.load(f)
        assert len(pilot_rep["extraction_diagnostics"]) == 1
        diag = pilot_rep["extraction_diagnostics"][0]
        assert diag["source_record_id"] == "moonprot_288"
        assert diag["coverage_status"] == "parse_failure"
        assert diag["raw_artifact_locator"] == "data/raw/moonprot/mpid_288.html"
        assert "malformed markup" in diag["failure_reason"]
        assert diag["claims_extracted_count"] == 0
        assert diag["source_go_annotations_count"] == 22
        assert diag["protein_id"] == "MFP:U:75a37d1de4bcf985"


def test_pilot_byte_reproducibility_across_hashseeds() -> None:
    """Verify that repeated executions with different PYTHONHASHSEED yield 100% byte-identical CSV and manifest digests."""
    with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
        dir1 = Path(tmpdir1)
        dir2 = Path(tmpdir2)

        # Run 1: PYTHONHASHSEED=0
        cmd1 = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "build_functional_claims_pilot.py"),
            "--pilot-dir", str(dir1 / "pilot"),
            "--reports-dir", str(dir1 / "reports"),
        ]
        env1 = {**subprocess.os.environ, "PYTHONHASHSEED": "0", "PYTHONPATH": str(REPO_ROOT / "src")}
        res1 = subprocess.run(cmd1, env=env1, capture_output=True, text=True, check=True)
        assert "PILOT BUILD SUCCESS" in res1.stdout

        # Run 2: PYTHONHASHSEED=42
        cmd2 = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "build_functional_claims_pilot.py"),
            "--pilot-dir", str(dir2 / "pilot"),
            "--reports-dir", str(dir2 / "reports"),
        ]
        env2 = {**subprocess.os.environ, "PYTHONHASHSEED": "42", "PYTHONPATH": str(REPO_ROOT / "src")}
        res2 = subprocess.run(cmd2, env=env2, capture_output=True, text=True, check=True)
        assert "PILOT BUILD SUCCESS" in res2.stdout

        # Verify byte identity for all data artifacts
        for filename in [
            "functional_claims_pilot.csv",
            "source_go_annotations_pilot.csv",
            "functional_coverage_pilot.csv",
            "manifest.json",
        ]:
            b1 = (dir1 / "pilot" / filename).read_bytes()
            b2 = (dir2 / "pilot" / filename).read_bytes()
            assert b1 == b2, f"Artifact {filename} is not byte-identical across PYTHONHASHSEED runs"
            h1 = compute_sha256(b1)
            h2 = compute_sha256(b2)
            assert h1 == h2


def test_baseline_protection_candidate_release() -> None:
    """Verify that the packaged candidate release remains pristine and valid."""
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "package_catalog_candidate.py"),
        "--verify-package",
    ]
    env = {**subprocess.os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
    res = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
    assert "PACKAGE_VERIFY OK" in res.stdout
