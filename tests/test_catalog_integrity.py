"""Integrity validation and evidence-based summary metrics for the MVP catalog."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp"
CLAIMS = {
    "moondb": REPO_ROOT / "data" / "interim" / "source_claims_moondb.csv",
    "plantmp": REPO_ROOT / "data" / "interim" / "source_claims_plantmp.csv",
}
ABSENT_LOG = REPO_ROOT / "data" / "interim" / "moonprot_absent_log.csv"


def _load_build_module():
    spec = importlib.util.spec_from_file_location(
        "build_mfp_catalog_mvp", REPO_ROOT / "scripts" / "build_mfp_catalog_mvp.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_mfp_catalog_mvp"] = module
    spec.loader.exec_module(module)
    return module


build = _load_build_module()


def make_record(source="SRC_MOONDB", record_id="r1", uniprot_id="P00001",
                claim_id="c1", mpid=None, protein_id=None, source_status="valid",
                coverage_status="valid"):
    if protein_id is None:
        if uniprot_id:
            protein_id = build.make_protein_id_uniprot(uniprot_id)
        else:
            protein_id = build.make_protein_id_fallback(source, claim_id or record_id)
    return build.SourceRecord(
        source_name=source, source_record_id=record_id, protein_id=protein_id,
        source_status=source_status, coverage_status=coverage_status,
        uniprot_id=uniprot_id, claim_id=claim_id, mpid=mpid,
    )


def make_identifier(record, namespace="UniProt", value="P00001"):
    return build.Identifier(
        protein_id=record.protein_id, identifier_namespace=namespace,
        identifier_value=value, source_name=record.source_name,
        source_record_id=record.source_record_id,
    )


def make_assertion(record, assertion_type="source_status"):
    return build.Assertion(
        protein_id=record.protein_id, source_name=record.source_name,
        source_record_id=record.source_record_id, assertion_type=assertion_type,
        assertion_value=record.source_status,
    )


class TestIntegrityDetection:
    """Synthetic inconsistent inputs are detected by validate_catalog_integrity."""

    def _validate(self, records, identifiers=(), assertions=(), expected_counts=None):
        entities = build.assign_protein_ids(records)
        return build.validate_catalog_integrity(
            list(records), entities, list(identifiers), list(assertions),
            expected_counts or {r.source_name: 0 for r in records},
        )

    def test_clean_fixture_produces_no_errors(self):
        records = [make_record(record_id="r1", uniprot_id="P00001"),
                   make_record(source="SRC_PLANTMP", record_id="r2", uniprot_id="P00001")]
        errors = self._validate(records, expected_counts={"SRC_MOONDB": 1, "SRC_PLANTMP": 1})
        assert errors == []

    def test_orphan_foreign_key_detected(self):
        records = [make_record()]
        ghost = build.Identifier(
            protein_id="MFP:U:deadbeefdeadbeef", identifier_namespace="UniProt",
            identifier_value="P99999", source_name="SRC_MOONDB", source_record_id="r1",
        )
        errors = self._validate(records, identifiers=[ghost])
        assert any("unknown protein" in e for e in errors)

    def test_duplicate_primary_key_detected(self):
        records = [make_record(record_id="r1"), make_record(record_id="r1", uniprot_id="P00002")]
        errors = self._validate(records)
        assert any("duplicate source record key" in e for e in errors)

    def test_conflicting_identifiers_detected(self):
        r1 = make_record(record_id="r1", uniprot_id="P00001")
        r2 = make_record(record_id="r2", uniprot_id="P00002")
        conflicting = [make_identifier(r1, value="P00001"), make_identifier(r2, value="P00001")]
        errors = self._validate([r1, r2], identifiers=conflicting)
        assert any("conflicting identifier" in e for e in errors)

    def test_distinct_identity_keys_sharing_one_protein_id_detected(self):
        records = [make_record(record_id="r1", uniprot_id="P00001", protein_id="MFP:U:0000000000000001"),
                   make_record(record_id="r2", uniprot_id="P00002", protein_id="MFP:U:0000000000000001")]
        entities = {r.protein_id: build.ProteinEntity(protein_id=r.protein_id) for r in records}
        errors = build.validate_catalog_integrity(
            records, entities, [make_identifier(r) for r in records],
            [make_assertion(r) for r in records], {"SRC_MOONDB": 2},
        )
        assert any("distinct identity keys" in e for e in errors)

    def test_source_record_lost_in_build_detected(self):
        records = [make_record(record_id="r1")]
        errors = self._validate(records, expected_counts={"SRC_MOONDB": 2})
        assert any("not conserved" in e for e in errors)

    def test_protein_without_source_record_detected(self):
        records = [make_record()]
        entities = build.assign_protein_ids(records)
        entities["MFP:U:cafebabecafebabe"] = build.ProteinEntity(
            protein_id="MFP:U:cafebabecafebabe")
        errors = build.validate_catalog_integrity(
            records, entities, [make_identifier(records[0])], [make_assertion(records[0])],
            {"SRC_MOONDB": 1},
        )
        assert any("has no source record" in e for e in errors)


class TestSummaryMetrics:
    """Metrics are computed from rows, not hard-coded."""

    def test_duplicate_identifier_count(self):
        r1 = make_record()
        identifiers = [make_identifier(r1), make_identifier(r1)]
        metrics = build.compute_summary_metrics([r1], identifiers)
        assert metrics["duplicate_identifier_count"] == 1

    def test_conflicting_identifier_count(self):
        r1 = make_record(record_id="r1", uniprot_id="P00001")
        r2 = make_record(record_id="r2", uniprot_id="P00002")
        identifiers = [make_identifier(r1, value="P00001"), make_identifier(r2, value="P00001")]
        metrics = build.compute_summary_metrics([r1, r2], identifiers)
        assert metrics["conflicting_identifier_count"] == 1

    def test_fallback_records_are_not_unresolved(self):
        fallback = make_record(record_id="r1", uniprot_id=None, claim_id="c1")
        metrics = build.compute_summary_metrics([fallback], [make_identifier(
            fallback, namespace="SRC_MOONDB_record_id", value="r1")])
        assert metrics["fallback_identity_records"] == 1
        assert metrics["unresolved_identity_records"] == 0

    def test_unresolved_only_without_any_key(self):
        unresolved = make_record(record_id="", uniprot_id=None, claim_id="",
                                protein_id="MFP:F:SRC_MOONDB:0000000000000000")
        metrics = build.compute_summary_metrics([unresolved], [])
        assert metrics["unresolved_identity_records"] == 1

    def test_legitimate_acquired_protein_without_uniprot_keeps_fallback_id(self):
        """Coverage-only exclusion must not ban valid fallback identities."""
        acquired = make_record(source="SRC_MOONPROT", record_id="moonprot_9",
                               uniprot_id=None, mpid="9", claim_id=None,
                               protein_id=build.make_protein_id_fallback("SRC_MOONPROT", "MPID_9"))
        entities = build.assign_protein_ids([acquired])
        assert len(entities) == 1
        entity = entities[acquired.protein_id]
        assert entity.protein_id.startswith("MFP:F:SRC_MOONPROT:")
        assert entity.protein_id == build.make_protein_id_fallback("SRC_MOONPROT", "MPID_9")
        errors = build.validate_catalog_integrity(
            [acquired], entities,
            [make_identifier(acquired, namespace="SRC_MOONPROT_record_id", value="moonprot_9")],
            [make_assertion(acquired)], {"SRC_MOONPROT": 1},
        )
        assert errors == []

    def test_acquired_moonprot_records_carry_raw_provenance(self):
        """Every acquired MoonProt record must retain raw_path and raw_sha256."""
        with open(OUTPUT_DIR / "mfp_source_records.csv", newline="") as f:
            for row in csv.DictReader(f):
                if row["source_name"] == "SRC_MOONPROT":
                    assert row["raw_path"], f"missing raw_path for {row['source_record_id']}"
                    assert row["raw_sha256"], f"missing raw_sha256 for {row['source_record_id']}"


def _make_sandbox(tmp_path):
    sandbox = tmp_path / "repo"
    (sandbox / "scripts").mkdir(parents=True)
    (sandbox / "data" / "interim").mkdir(parents=True)
    (sandbox / "data" / "raw").mkdir(parents=True)
    shutil.copy(REPO_ROOT / "scripts" / "build_mfp_catalog_mvp.py",
                sandbox / "scripts" / "build_mfp_catalog_mvp.py")
    shutil.copytree(REPO_ROOT / "src", sandbox / "src", ignore=shutil.ignore_patterns("__pycache__"))
    for claims in CLAIMS.values():
        shutil.copy(claims, sandbox / "data" / "interim" / claims.name)
    if ABSENT_LOG.exists():
        shutil.copy(ABSENT_LOG, sandbox / "data" / "interim" / ABSENT_LOG.name)
    manifest_dir = sandbox / "data" / "manifests"
    manifest_dir.mkdir()
    shutil.copy(REPO_ROOT / "data" / "manifests" / "source_manifest.csv", manifest_dir / "source_manifest.csv")
    (sandbox / "data/raw/moondb").mkdir()
    shutil.copy(REPO_ROOT / "data/raw/moondb/all_emf_and_curated.tsv",
                sandbox / "data/raw/moondb/all_emf_and_curated.tsv")
    (sandbox / "data/raw/plantmp").mkdir()
    shutil.copy(REPO_ROOT / "data/raw/plantmp/PlantMP_all.csv",
                sandbox / "data/raw/plantmp/PlantMP_all.csv")
    shutil.copytree(REPO_ROOT / "data" / "raw" / "moonprot", sandbox / "data" / "raw" / "moonprot")
    (sandbox / "data/raw/multifacetedprotdb").mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO_ROOT / "data/raw/multifacetedprotdb/MultifacetedProtDB_data.json",
                sandbox / "data/raw/multifacetedprotdb/MultifacetedProtDB_data.json")
    shutil.copy(REPO_ROOT / "data/interim/source_records_multifacetedprotdb.csv",
                sandbox / "data/interim/source_records_multifacetedprotdb.csv")
    (sandbox / "data/raw/multitaskprotdb-ii").mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO_ROOT / "data/raw/multitaskprotdb-ii/proteins.csv",
                sandbox / "data/raw/multitaskprotdb-ii/proteins.csv")
    shutil.copy(REPO_ROOT / "data/interim/source_records_multitaskprotdb_ii.csv",
                sandbox / "data/interim/source_records_multitaskprotdb_ii.csv")
    return sandbox


def _run_build(sandbox):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(sandbox / "src")
    return subprocess.run(
        [sys.executable, str(sandbox / "scripts" / "build_mfp_catalog_mvp.py")],
        env=env, capture_output=True, text=True,
    )


def _repo_output_state():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(OUTPUT_DIR.iterdir()) if p.is_file()}


class TestIsolatedBuild:
    """The real build runs in a sandbox and never touches repository outputs."""

    def test_real_build_in_temp_dir_matches_repo_summary(self, tmp_path):
        before = _repo_output_state()
        sandbox = _make_sandbox(tmp_path)
        result = _run_build(sandbox)
        assert result.returncode == 0, result.stderr
        sandbox_summary = json.loads(
            (sandbox / "data" / "processed" / "mfp_catalog_mvp" / "summary.json").read_text())
        repo_summary = json.loads((OUTPUT_DIR / "summary.json").read_text())
        for key in ("source_record_count", "protein_entity_count", "exact_uniprot_merges",
                    "source_record_counts", "duplicate_identifier_count",
                    "conflicting_identifier_count", "unresolved_identity_records",
                    "fallback_identity_records"):
            assert sandbox_summary[key] == repo_summary[key], key
        assert _repo_output_state() == before

    def test_integrity_failure_blocks_outputs_and_exits_nonzero(self, tmp_path):
        sandbox = _make_sandbox(tmp_path)
        claims_path = sandbox / "data" / "interim" / "source_claims_moondb.csv"
        lines = claims_path.read_text().splitlines()
        # Duplicate one claims row -> duplicate source record primary key
        claims_path.write_text("\n".join([lines[0], lines[1], lines[1]] + lines[2:]) + "\n")
        result = _run_build(sandbox)
        assert result.returncode != 0
        assert "integrity" in result.stderr
        out_dir = sandbox / "data" / "processed" / "mfp_catalog_mvp"
        assert not out_dir.exists() or not any(out_dir.iterdir()), "outputs published despite failure"
