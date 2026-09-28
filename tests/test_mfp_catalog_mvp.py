"""Tests for MFP Catalog MVP build."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
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
        assert "SRC_MULTIFACETEDPROTDB" in sources
        assert "SRC_MULTITASKPROTDB_II" in sources

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
        
        # 351 MoonDB + 112 PlantMP + 702 MoonProt + 1103 MultifacetedProtDB
        # + 694 MultitaskProtDB-II = 2962.
        # Known-absent/unresolved MPIDs are coverage-only, never source records.
        assert len(rows) == 2962

    def test_moonprot_source_record_count(self, output_dir):
        path = output_dir / "mfp_source_records.csv"
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            moonprot_rows = [r for r in reader if r["source_name"] == "SRC_MOONPROT"]
        # 702 acquired only; MPID 103 (known absent) is coverage-only
        assert len(moonprot_rows) == 702

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
        # 2322 UniProt-resolved entities across five sources
        assert len(rows) == 2322

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


class TestProteinIdScheme:
    """Tests for the deterministic protein ID scheme (MFPB_PROTEIN_ID_V1)."""

    def test_accession_variants_share_id(self):
        from mfp_bibliography.normalization import make_protein_id_uniprot
        assert make_protein_id_uniprot("P12345") == make_protein_id_uniprot(" p12345 ")
        assert make_protein_id_uniprot("P12345") == make_protein_id_uniprot("P12345 isoform")

    def test_distinct_accessions_get_distinct_ids(self):
        from mfp_bibliography.normalization import make_protein_id_uniprot
        accessions = ["P12345", "P12346", "P1234S", "Q86VP1", "Q86VP2", "O00101", "O00102"]
        ids = [make_protein_id_uniprot(a) for a in accessions]
        assert len(set(ids)) == len(accessions)

    def test_id_format_matches_scheme(self):
        import re
        from mfp_bibliography.normalization import make_protein_id_fallback, make_protein_id_uniprot
        up_pattern = re.compile(r"^MFP:U:[0-9a-f]{16}$")
        fb_pattern = re.compile(r"^MFP:F:SRC_[A-Z0-9]+:[0-9a-f]{16}$")
        assert up_pattern.match(make_protein_id_uniprot("P12345"))
        assert fb_pattern.match(make_protein_id_fallback("SRC_MOONDB", "claim_1"))
        assert fb_pattern.match(make_protein_id_fallback("SRC_MOONPROT", "MPID_103"))

    def test_scheme_digest_is_version_pinned(self):
        import hashlib
        from mfp_bibliography.normalization import (
            PROTEIN_ID_DIGEST_LENGTH, PROTEIN_ID_SCHEME_VERSION, make_protein_id_uniprot,
            normalize_uniprot_accession,
        )
        canonical = normalize_uniprot_accession("p12345")
        digest = hashlib.sha256(
            f"{PROTEIN_ID_SCHEME_VERSION}::uniprot::{canonical}".encode("utf-8")
        ).hexdigest()[:PROTEIN_ID_DIGEST_LENGTH]
        assert make_protein_id_uniprot("p12345") == f"MFP:U:{digest}"

    def test_fallback_ids_are_source_scoped_and_stable(self):
        from mfp_bibliography.normalization import make_protein_id_fallback, make_protein_id_uniprot
        first = make_protein_id_fallback("SRC_MOONDB", "claim_1")
        assert first == make_protein_id_fallback("SRC_MOONDB", "claim_1")
        assert first != make_protein_id_fallback("SRC_PLANTMP", "claim_1")
        assert first != make_protein_id_uniprot("claim_1")


class TestCatalogReferentialIntegrity:
    """Cross-file integrity of protein_id after the ID migration."""

    def _read(self, name):
        with open(OUTPUT_DIR / name, "r", newline="") as f:
            return list(csv.DictReader(f))

    def test_every_source_record_maps_to_exactly_one_protein_row(self):
        proteins = {row["protein_id"] for row in self._read("mfp_proteins.csv")}
        records = self._read("mfp_source_records.csv")
        assert len(proteins) == len(self._read("mfp_proteins.csv"))
        for row in records:
            assert row["protein_id"] in proteins

    def test_no_orphan_protein_ids_in_identifiers(self):
        proteins = {row["protein_id"] for row in self._read("mfp_proteins.csv")}
        for row in self._read("mfp_identifiers.csv"):
            assert row["protein_id"] in proteins

    def test_no_orphan_protein_ids_in_assertions(self):
        proteins = {row["protein_id"] for row in self._read("mfp_proteins.csv")}
        for row in self._read("mfp_assertions.csv"):
            assert row["protein_id"] in proteins

    def test_no_duplicate_entity_ids_for_distinct_canonical_keys(self):
        proteins = self._read("mfp_proteins.csv")
        seen_ids = {}
        for row in proteins:
            key = row["protein_id"]
            assert key not in seen_ids, f"Duplicate protein_id: {key}"
            seen_ids[key] = row["canonical_uniprot_accession"]
        by_accession = {}
        for row in proteins:
            accession = row["canonical_uniprot_accession"]
            if accession:
                assert accession not in by_accession, f"Two entities for {accession}"
                by_accession[accession] = row["protein_id"]


class TestCrossProcessDeterminism:
    """The build must not depend on Python's process-local hash seed."""

    @staticmethod
    def _run_build(seed):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "build_mfp_catalog_mvp.py")],
            cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=True,
        )

    @staticmethod
    def _output_checksums():
        return {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(OUTPUT_DIR.iterdir()) if p.is_file()
        }

    def test_builds_byte_identical_under_different_hash_seeds(self):
        self._run_build("1")
        first = self._output_checksums()
        self._run_build("42")
        second = self._output_checksums()
        assert first == second


class TestCoverageOnlyMpids:
    """Known-absent and unresolved MoonProt MPIDs must stay coverage-only."""

    def _coverage_only_mpids(self):
        with open(OUTPUT_DIR / "mfp_coverage.csv", "r", newline="") as f:
            return [row["mpid"] for row in csv.DictReader(f)
                    if row["status"] in ("known_absent", "unresolved")]

    def test_coverage_only_mpids_absent_from_source_records(self):
        coverage_only = set(self._coverage_only_mpids())
        assert "103" in coverage_only and {"542", "543", "626"} <= coverage_only
        with open(OUTPUT_DIR / "mfp_source_records.csv", "r", newline="") as f:
            for row in csv.DictReader(f):
                if row["source_name"] == "SRC_MOONPROT":
                    assert row["mpid"] not in coverage_only, f"coverage-only MPID {row['mpid']} in source records"
                    assert row["source_record_id"] != "moonprot_103"

    def test_coverage_only_mpids_absent_from_identifiers(self):
        coverage_only = set(self._coverage_only_mpids())
        with open(OUTPUT_DIR / "mfp_identifiers.csv", "r", newline="") as f:
            for row in csv.DictReader(f):
                assert row["identifier_value"] not in coverage_only, \
                    f"coverage-only MPID {row['identifier_value']} in identifiers"
                assert row["source_record_id"] != "moonprot_103"

    def test_coverage_only_mpids_absent_from_proteins_and_assertions(self):
        coverage_only = set(self._coverage_only_mpids())
        with open(OUTPUT_DIR / "mfp_proteins.csv", "r", newline="") as f:
            for row in csv.DictReader(f):
                assert row["protein_id"] not in {f"MFP:F:SRC_MOONPROT:{m}" for m in coverage_only}
        with open(OUTPUT_DIR / "mfp_assertions.csv", "r", newline="") as f:
            for row in csv.DictReader(f):
                assert row["source_record_id"] != "moonprot_103"

    def test_mpid_103_retained_in_coverage_with_absent_log_provenance(self):
        with open(OUTPUT_DIR / "mfp_coverage.csv", "r", newline="") as f:
            row = next(r for r in csv.DictReader(f) if r["mpid"] == "103")
        assert row["status"] == "known_absent"
        assert "absent log" in row["reason"]
        assert row["http_status"] == "200"

    def test_real_protein_ids_match_scheme(self):
        from mfp_bibliography.normalization import make_protein_id_uniprot
        with open(OUTPUT_DIR / "mfp_proteins.csv", "r", newline="") as f:
            for row in csv.DictReader(f):
                if row["canonical_uniprot_accession"]:
                    assert row["protein_id"] == make_protein_id_uniprot(row["canonical_uniprot_accession"])


class TestMultifacetedIntegration:
    """MultifacetedProtDB integration: identity, null status, raw-data preservation."""

    def _read(self, name):
        with open(OUTPUT_DIR / name, "r", newline="") as f:
            return list(csv.DictReader(f))

    def test_multifaceted_record_count(self):
        rows = [r for r in self._read("mfp_source_records.csv")
                if r["source_name"] == "SRC_MULTIFACETEDPROTDB"]
        assert len(rows) == 1103
        assert len({r["source_record_id"] for r in rows}) == 1103

    def test_overlap_accessions_share_protein_id_new_accessions_get_entities(self):
        from mfp_bibliography.normalization import make_protein_id_uniprot
        records = self._read("mfp_source_records.csv")
        proteins = {p["protein_id"]: p for p in self._read("mfp_proteins.csv")}
        mf = [r for r in records if r["source_name"] == "SRC_MULTIFACETEDPROTDB"]
        other = {r["uniprot_id"]: r["protein_id"] for r in records
                 if r["source_name"] != "SRC_MULTIFACETEDPROTDB" and r["uniprot_id"]}
        overlapping = [r for r in mf if r["uniprot_id"] in other]
        assert overlapping, "expected some accession overlap with existing sources"
        for r in overlapping:
            assert r["protein_id"] == other[r["uniprot_id"]]
            assert r["protein_id"] == make_protein_id_uniprot(r["uniprot_id"])
        # a genuinely new accession has its own entity
        fresh = [r for r in mf if r["uniprot_id"] not in other]
        assert fresh
        for r in fresh[:50]:
            assert r["protein_id"] in proteins
            assert proteins[r["protein_id"]]["canonical_uniprot_accession"] == r["uniprot_id"]

    def test_null_status_no_invented_claims(self):
        records = [r for r in self._read("mfp_source_records.csv")
                   if r["source_name"] == "SRC_MULTIFACETEDPROTDB"]
        assert all(r["source_status"] == "" for r in records)
        assert all(r["operational_status"] == "unresolved" for r in records)
        assertions = [a["assertion_type"] for a in self._read("mfp_assertions.csv")
                      if a["source_name"] == "SRC_MULTIFACETEDPROTDB"]
        assert set(assertions) == {"coverage_status", "protein_name", "uniprot_accession"}
        assert len(assertions) == 3 * len(records)

    def test_genes_and_annotation_preserved_from_interim(self):
        interim_path = REPO_ROOT / "data/interim/source_records_multifacetedprotdb.csv"
        with open(interim_path, newline="") as f:
            interim = {r["source_record_id"]: r for r in csv.DictReader(f)}
        for row in self._read("mfp_source_records.csv"):
            if row["source_name"] != "SRC_MULTIFACETEDPROTDB":
                continue
            source_row = interim[row["source_record_id"]]
            assert row["genes_raw"] == source_row["genes_raw"]
            assert row["annotation_raw"] == source_row["annotation_raw"]

    def test_stale_interim_input_rejected(self, tmp_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_mfp_catalog_mvp", REPO_ROOT / "scripts" / "build_mfp_catalog_mvp.py")
        build = importlib.util.module_from_spec(spec)
        sys.modules["build_mfp_catalog_mvp"] = build
        spec.loader.exec_module(build)
        with open(REPO_ROOT / "data/interim/source_records_multifacetedprotdb.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        for mutation, message in (
            ({"transformation_id": "stale_v9"}, "transformation_id"),
            ({"raw_file_sha256": "0" * 64}, "raw_file_sha256"),
            ({"raw_file_path": "data/raw/other.json"}, "raw_file_path"),
        ):
            stale = tmp_path / "stale.csv"
            with open(stale, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerow({**rows[0], **mutation})
            with pytest.raises(build.CatalogIntegrityError, match=message):
                build.load_multifacetedprotdb_records(records_path=stale)


class TestMultitaskIntegration:
    """MultitaskProtDB-II integration: row grain, null status, anomalies, provenance."""

    def _read(self, name):
        with open(OUTPUT_DIR / name, "r", newline="") as f:
            return list(csv.DictReader(f))

    def test_multitask_record_count_and_unique_ids(self):
        rows = [r for r in self._read("mfp_source_records.csv")
                if r["source_name"] == "SRC_MULTITASKPROTDB_II"]
        assert len(rows) == 694
        assert len({r["source_record_id"] for r in rows}) == 694

    def test_repeated_accessions_are_separate_observations_one_entity(self):
        from collections import Counter
        from mfp_bibliography.normalization import make_protein_id_uniprot
        rows = [r for r in self._read("mfp_source_records.csv")
                if r["source_name"] == "SRC_MULTITASKPROTDB_II"]
        counts = Counter(r["uniprot_id"] for r in rows)
        repeated = {a for a, c in counts.items() if c > 1}
        assert len(repeated) == 9
        assert sum(counts[a] - 1 for a in repeated) == 9
        for accession in repeated:
            same = [r for r in rows if r["uniprot_id"] == accession]
            assert len({r["source_record_id"] for r in same}) == len(same)
            assert len({r["protein_id"] for r in same}) == 1
            assert same[0]["protein_id"] == make_protein_id_uniprot(accession)

    def test_null_status_no_invented_claims(self):
        rows = [r for r in self._read("mfp_source_records.csv")
                if r["source_name"] == "SRC_MULTITASKPROTDB_II"]
        assert all(r["source_status"] == "" for r in rows)
        assert all(r["operational_status"] == "unresolved" for r in rows)
        assertion_types = {a["assertion_type"] for a in self._read("mfp_assertions.csv")
                          if a["source_name"] == "SRC_MULTITASKPROTDB_II"}
        assert assertion_types == {"coverage_status", "protein_name", "uniprot_accession"}

    def test_reference_anomalies_attached_to_original_rows(self):
        rows = [r for r in self._read("mfp_source_records.csv")
                if r["source_name"] == "SRC_MULTITASKPROTDB_II"]
        anomalies = {r["source_record_id"]: r for r in rows if r["reference_anomaly"]}
        assert set(anomalies) == {"multitaskprotdb_ii_row_239",
                                  "multitaskprotdb_ii_row_349",
                                  "multitaskprotdb_ii_row_422"}
        assert anomalies["multitaskprotdb_ii_row_239"]["reference_raw"].startswith("HIV-1")
        assert anomalies["multitaskprotdb_ii_row_422"]["reference_raw"] == "4ENL"
        assert anomalies["multitaskprotdb_ii_row_349"]["reference_raw"] == ""
        # nothing promoted to a verified PMID/DOI namespace
        assert anomalies["multitaskprotdb_ii_row_239"]["reference_article_like"] == "false"

    def test_go_and_metadata_preserved_verbatim(self):
        interim_path = REPO_ROOT / "data/interim/source_records_multitaskprotdb_ii.csv"
        with open(interim_path, newline="") as f:
            interim = {r["source_record_id"]: r for r in csv.DictReader(f)}
        rows = [r for r in self._read("mfp_source_records.csv")
                if r["source_name"] == "SRC_MULTITASKPROTDB_II"]
        for row in rows:
            source_row = interim[row["source_record_id"]]
            for field in ("go_raw", "go_moon_raw", "reference_raw", "canonical_function_raw",
                          "moonlighting_function_raw", "models_raw", "pdbs_raw"):
                assert row[field] == source_row[field]

    def test_stale_interim_input_rejected(self, tmp_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_mfp_catalog_mvp", REPO_ROOT / "scripts" / "build_mfp_catalog_mvp.py")
        build = importlib.util.module_from_spec(spec)
        sys.modules["build_mfp_catalog_mvp"] = build
        spec.loader.exec_module(build)
        with open(REPO_ROOT / "data/interim/source_records_multitaskprotdb_ii.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        for mutation, message in (
            ({"transformation_id": "stale_v9"}, "transformation_id"),
            ({"raw_file_sha256": "0" * 64}, "raw_file_sha256"),
            ({"raw_file_path": "data/raw/other.csv"}, "raw_file_path"),
        ):
            stale = tmp_path / "stale.csv"
            with open(stale, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerow({**rows[0], **mutation})
            with pytest.raises(build.CatalogIntegrityError, match=message):
                build.load_multitaskprotdb_ii_records(records_path=stale)
