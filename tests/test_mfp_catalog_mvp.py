"""Tests for MFP Catalog MVP build."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "data" / "processed" / "mfp_catalog_mvp"


@pytest.fixture
def output_dir():
    """Ensure output directory exists."""
    assert OUTPUT_DIR.exists(), f"Output directory {OUTPUT_DIR} does not exist"
    return OUTPUT_DIR


class TestSourceRecords:
    """Tests for mfp_source_records.csv."""

    def test_source_records_file_exists(self, output_dir):
        path = output_dir / "mfp_source_records.csv"
        assert path.exists()

    def test_source_records_has_header(self, output_dir):
        path = output_dir / "mfp_source_records.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
        required = ["source_name", "source_record_id", "protein_id", "source_status",
                   "coverage_status"]
        for col in required:
            assert col in header, f"Missing column: {col}"

    def test_source_records_has_all_sources(self, output_dir):
        path = output_dir / "mfp_source_records.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            sources = set(row["source_name"] for row in reader)
        assert "SRC_MOONDB" in sources
        assert "SRC_PLANTMP" in sources
        assert "SRC_MOONPROT" in sources

    def test_every_source_record_has_provenance(self, output_dir):
        path = output_dir / "mfp_source_records.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Every record should have source_name and source_record_id
                assert row["source_name"].strip()
                assert row["source_record_id"].strip()

    def test_source_record_count_conserved(self, output_dir):
        """Total source records should match input counts."""
        path = output_dir / "mfp_source_records.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Should have 351 MoonDB + 112 PlantMP + 702 MoonProt acquired + 1 known_absent = 1166
        assert len(rows) == 1166

    def test_moonprot_source_record_count(self, output_dir):
        path = output_dir / "mfp_source_records.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            moonprot_rows = [r for r in reader if r["source_name"] == "SRC_MOONPROT"]
        # 702 acquired + 1 known_absent (MPID 103)
        assert len(moonprot_rows) == 703

    def test_moondb_source_record_count(self, output_dir):
        path = output_dir / "mfp_source_records.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            moondb_rows = [r for r in reader if r["source_name"] == "SRC_MOONDB"]
        assert len(moondb_rows) == 351

    def test_plantmp_source_record_count(self, output_dir):
        path = output_dir / "mfp_source_records.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            plantmp_rows = [r for r in reader if r["source_name"] == "SRC_PLANTMP"]
        assert len(plantmp_rows) == 112


class TestProteins:
    """Tests for mfp_proteins.csv."""

    def test_proteins_file_exists(self, output_dir):
        path = output_dir / "mfp_proteins.csv"
        assert path.exists()

    def test_proteins_has_header(self, output_dir):
        path = output_dir / "mfp_proteins.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
        required = ["protein_id", "canonical_uniprot_accession", "canonical_name",
                   "canonical_organism", "entity_status"]
        for col in required:
            assert col in header, f"Missing column: {col}"

    def test_proteins_count(self, output_dir):
        path = output_dir / "mfp_proteins.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Should have fewer entities than records due to merging
        assert len(rows) > 0
        # Should be around 1074 based on current data
        assert len(rows) == 1074

    def test_deterministic_protein_id_assignment(self, output_dir):
        """Same UniProt accession should always map to same protein_id."""
        path = output_dir / "mfp_source_records.csv"
        uniprot_to_pid = {}
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["uniprot_id"]:
                    up = row["uniprot_id"].strip().split(" ")[0].strip()
                    if up in uniprot_to_pid:
                        assert uniprot_to_pid[up] == row["protein_id"], \
                            f"UniProt {up} mapped to different protein_ids"
                    else:
                        uniprot_to_pid[up] = row["protein_id"]

    def test_no_name_only_merge(self, output_dir):
        """Protein entities should only be merged by UniProt accession, not name."""
        path = output_dir / "mfp_proteins.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # If there's a canonical_uniprot_accession, entity_status should be resolved
                # If not, it should be unresolved_identity
                if row["canonical_uniprot_accession"]:
                    assert row["entity_status"] == "resolved"
                else:
                    assert row["entity_status"] == "unresolved_identity"

    def test_exact_uniprot_merges(self, output_dir):
        """Verify exact UniProt merges are happening."""
        path = output_dir / "mfp_source_records.csv"
        uniprot_to_sources = {}
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["uniprot_id"]:
                    up = row["uniprot_id"].strip().split(" ")[0].strip().upper()
                    if up not in uniprot_to_sources:
                        uniprot_to_sources[up] = set()
                    uniprot_to_sources[up].add(row["source_name"])
        
        # Count UniProt accessions that appear in multiple sources
        exact_merges = sum(1 for sources in uniprot_to_sources.values() if len(sources) > 1)
        assert exact_merges >= 45  # From summary.json


class TestIdentifiers:
    """Tests for mfp_identifiers.csv."""

    def test_identifiers_file_exists(self, output_dir):
        path = output_dir / "mfp_identifiers.csv"
        assert path.exists()

    def test_identifiers_has_header(self, output_dir):
        path = output_dir / "mfp_identifiers.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
        required = ["protein_id", "identifier_namespace", "identifier_value",
                   "source_name", "source_record_id", "is_primary"]
        for col in required:
            assert col in header, f"Missing column: {col}"


class TestAssertions:
    """Tests for mfp_assertions.csv."""

    def test_assertions_file_exists(self, output_dir):
        path = output_dir / "mfp_assertions.csv"
        assert path.exists()

    def test_assertions_has_header(self, output_dir):
        path = output_dir / "mfp_assertions.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
        required = ["protein_id", "source_name", "source_record_id", "assertion_type",
                   "assertion_value", "evidence_tier"]
        for col in required:
            assert col in header, f"Missing column: {col}"


class TestCoverage:
    """Tests for mfp_coverage.csv."""

    def test_coverage_file_exists(self, output_dir):
        path = output_dir / "mfp_coverage.csv"
        assert path.exists()

    def test_coverage_has_706_rows(self, output_dir):
        """Coverage must have exactly 706 rows (MPIDs 1..706)."""
        path = output_dir / "mfp_coverage.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 706

    def test_coverage_has_correct_statuses(self, output_dir):
        path = output_dir / "mfp_coverage.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            statuses = set(row["status"] for row in reader)
        # Only acquired, known_absent, unresolved allowed
        assert statuses <= {"acquired", "known_absent", "unresolved"}

    def test_mpid_103_is_known_absent(self, output_dir):
        path = output_dir / "mfp_coverage.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["mpid"] == "103":
                    assert row["status"] == "known_absent"
                    return
        pytest.fail("MPID 103 not found in coverage")

    def test_unresolved_moonprot_ids_visible(self, output_dir):
        path = output_dir / "mfp_coverage.csv"
        unresolved = []
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["status"] == "unresolved":
                    unresolved.append(row["mpid"])
        # Should have 542, 543, 626
        assert "542" in unresolved
        assert "543" in unresolved
        assert "626" in unresolved

    def test_acquired_count(self, output_dir):
        path = output_dir / "mfp_coverage.csv"
        acquired = []
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["status"] == "acquired":
                    acquired.append(row["mpid"])
        # Should have 702 acquired MPIDs
        assert len(acquired) == 702

    def test_known_absent_count(self, output_dir):
        path = output_dir / "mfp_coverage.csv"
        known_absent = []
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["status"] == "known_absent":
                    known_absent.append(row["mpid"])
        # Should have 1 known absent (MPID 103)
        assert len(known_absent) == 1
        assert known_absent[0] == "103"

    def test_unresolved_count(self, output_dir):
        path = output_dir / "mfp_coverage.csv"
        unresolved = []
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["status"] == "unresolved":
                    unresolved.append(row["mpid"])
        # Should have 3 unresolved (542, 543, 626)
        assert len(unresolved) == 3


class TestSummary:
    """Tests for summary.json."""

    def test_summary_file_exists(self, output_dir):
        path = output_dir / "summary.json"
        assert path.exists()

    def test_summary_has_contract_id(self, output_dir):
        path = output_dir / "summary.json"
        with open(path, "r") as f:
            data = json.load(f)
        assert "mvp_contract_id" in data

    def test_summary_has_counts(self, output_dir):
        path = output_dir / "summary.json"
        with open(path, "r") as f:
            data = json.load(f)
        assert "source_record_count" in data
        assert "protein_entity_count" in data
        assert "exact_uniprot_merges" in data


class TestReadme:
    """Tests for README.md."""

    def test_readme_file_exists(self, output_dir):
        path = output_dir / "README.md"
        assert path.exists()

    def test_readme_has_scope(self, output_dir):
        path = output_dir / "README.md"
        content = path.read_text()
        assert "Scope" in content
        assert "NOT a machine-learning" in content or "NOT machine-learning" in content

    def test_readme_has_reproducibility(self, output_dir):
        path = output_dir / "README.md"
        content = path.read_text()
        assert "Reproducibility" in content
        assert "build_mfp_catalog_mvp.py" in content


class TestPrimaryKeys:
    """Tests for unique primary keys."""

    def test_source_records_unique_primary_key(self, output_dir):
        """Each source record should have unique (source_name, source_record_id)."""
        path = output_dir / "mfp_source_records.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            keys = []
            for row in reader:
                key = (row["source_name"], row["source_record_id"])
                assert key not in keys, f"Duplicate key: {key}"
                keys.append(key)

    def test_proteins_unique_primary_key(self, output_dir):
        """Each protein should have unique protein_id."""
        path = output_dir / "mfp_proteins.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            pids = []
            for row in reader:
                pid = row["protein_id"]
                assert pid not in pids, f"Duplicate protein_id: {pid}"
                pids.append(pid)

    def test_identifiers_unique_primary_key(self, output_dir):
        """Each identifier should have unique (protein_id, identifier_namespace, identifier_value, source_name, source_record_id)."""
        path = output_dir / "mfp_identifiers.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            keys = []
            for row in reader:
                key = (row["protein_id"], row["identifier_namespace"], 
                       row["identifier_value"], row["source_name"], row["source_record_id"])
                assert key not in keys, f"Duplicate identifier: {key}"
                keys.append(key)
