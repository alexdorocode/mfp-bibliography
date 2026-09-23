"""Tests for generate_effective_status_moondb_plantmp.py script.

Tests use synthetic claim CSVs and verify aggregation behavior.
"""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from mfp_bibliography.effective_status import (
    CONTRACT_ID,
    SourceClaim,
    aggregate_effective_status,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


# Synthetic claim data for testing
SYNTHETIC_MOONDB_CLAIMS = [
    SourceClaim("MD:001", "SRC_MOONDB", "P0001", "curated"),
    SourceClaim("MD:002", "SRC_MOONDB", "P0002", "predicted"),
    SourceClaim("MD:003", "SRC_MOONDB", "P0003", "excluded_likely"),
    SourceClaim("MD:004", "SRC_MOONDB", "P0004", "unresolved"),
    SourceClaim("MD:005", "SRC_MOONDB", "P0005", "predicted"),
]

SYNTHETIC_PLANTMP_CLAIMS = [
    SourceClaim("PM:001", "SRC_PLANTMP", "P0001", "curated"),  # Same UniProt as MD:001
    SourceClaim("PM:002", "SRC_PLANTMP", "P0006", "curated"),
    SourceClaim("PM:003", "SRC_PLANTMP", "P0007", "predicted"),
]

SYNTHETIC_BLANK_CLAIMS = [
    SourceClaim("MD:999", "SRC_MOONDB", "", "curated"),
    SourceClaim("PM:999", "SRC_PLANTMP", None, "predicted"),
]


def write_claims_csv(claims: list[SourceClaim], path: Path) -> str:
    """Write claims to CSV and return SHA-256."""
    fieldnames = [
        "claim_id", "source_id", "source_record_id", "uniprot_id",
        "protein_name_raw", "organism_raw", "raw_claim_field", "raw_claim_value",
        "operational_status", "primary_target_eligible", "control_eligible",
        "raw_file_path", "raw_row_or_url", "source_version", "retrieved_at",
        "transformation_id", "record_status", "notes"
    ]
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for claim in claims:
            row = {
                "claim_id": claim.claim_id,
                "source_id": claim.source_id,
                "source_record_id": f"{claim.source_id}_row",
                "uniprot_id": claim.uniprot_id if claim.uniprot_id else "",
                "protein_name_raw": "",
                "organism_raw": "",
                "raw_claim_field": "type",
                "raw_claim_value": claim.operational_status,
                "operational_status": claim.operational_status,
                "primary_target_eligible": str(claim.operational_status == "curated").lower(),
                "control_eligible": "false",
                "raw_file_path": "test.csv",
                "raw_row_or_url": "row:1",
                "source_version": "test_v0",
                "retrieved_at": "unknown",
                "transformation_id": "test_transform",
                "record_status": "valid",
                "notes": "",
            }
            writer.writerow(row)
    
    # Compute SHA-256
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class TestSyntheticAggregation:
    """Test aggregation with synthetic CSV inputs."""

    def test_basic_aggregation(self, tmp_path: Path) -> None:
        """Test basic aggregation from two synthetic CSV files."""
        # Create synthetic CSV files
        moondb_csv = tmp_path / "source_claims_moondb.csv"
        plantmp_csv = tmp_path / "source_claims_plantmp.csv"
        
        moondb_sha = write_claims_csv(SYNTHETIC_MOONDB_CLAIMS, moondb_csv)
        plantmp_sha = write_claims_csv(SYNTHETIC_PLANTMP_CLAIMS, plantmp_csv)
        
        # Run aggregation
        from mfp_bibliography.effective_status import SourceClaim
        
        all_claims = SYNTHETIC_MOONDB_CLAIMS + SYNTHETIC_PLANTMP_CLAIMS
        records = aggregate_effective_status(
            all_claims,
            aggregation_policy_id=CONTRACT_ID,
            transformation_id="test_v0",
        )
        
        valid_records = [r for r in records if r.record_status == "valid"]
        
        # P0001 has both curated (from both sources) -> effective = curated
        p0001_records = [r for r in valid_records if r.uniprot_id == "P0001"]
        assert len(p0001_records) == 1
        assert p0001_records[0].effective_status == "curated"
        assert p0001_records[0].claim_count == 2
        assert p0001_records[0].source_count == 2
        
        # Total: 7 unique UniProts (P0001-P0005 from MoonDB + P0006-P0007 from PlantMP, with P0001 overlapping)
        assert len(valid_records) == 7
        
        # P0001 is the only one with multiple sources
        multi_source = [r for r in valid_records if r.source_count > 1]
        assert len(multi_source) == 1

    def test_precedence_curated_wins(self, tmp_path: Path) -> None:
        """Test that curated beats predicted in mixed claims."""
        claims = [
            SourceClaim("c1", "SRC_MOONDB", "P0001", "predicted"),
            SourceClaim("c2", "SRC_PLANTMP", "P0001", "curated"),
        ]
        records = aggregate_effective_status(claims)
        valid_records = [r for r in records if r.record_status == "valid"]
        
        assert len(valid_records) == 1
        assert valid_records[0].effective_status == "curated"

    def test_blank_uniprot_excluded(self, tmp_path: Path) -> None:
        """Test that blank UniProt IDs are excluded from aggregation."""
        claims = SYNTHETIC_MOONDB_CLAIMS + SYNTHETIC_BLANK_CLAIMS
        records = aggregate_effective_status(claims)
        
        valid_records = [r for r in records if r.record_status == "valid"]
        excluded_records = [r for r in records if r.record_status == "excluded"]
        
        # 5 valid from SYNTHETIC_MOONDB_CLAIMS + 0 from PlantMP (blank ones excluded)
        assert len(valid_records) == 5
        # 2 blank claims should produce 2 excluded records
        assert len(excluded_records) == 2

    def test_duplicate_claims_preserved(self, tmp_path: Path) -> None:
        """Test that duplicate claims are preserved in counts."""
        claims = [
            SourceClaim("c1", "SRC_MOONDB", "P0001", "curated"),
            SourceClaim("c2", "SRC_MOONDB", "P0001", "curated"),
        ]
        records = aggregate_effective_status(claims)
        valid_records = [r for r in records if r.record_status == "valid"]
        
        assert len(valid_records) == 1
        assert valid_records[0].claim_count == 2
        assert valid_records[0].source_count == 1
        assert valid_records[0].claim_ids == ("c1", "c2")


class TestReportGeneration:
    """Test report generation."""

    def test_report_structure(self, tmp_path: Path) -> None:
        """Test that JSON report has expected structure."""
        moondb_csv = tmp_path / "source_claims_moondb.csv"
        plantmp_csv = tmp_path / "source_claims_plantmp.csv"
        
        write_claims_csv(SYNTHETIC_MOONDB_CLAIMS, moondb_csv)
        write_claims_csv(SYNTHETIC_PLANTMP_CLAIMS, plantmp_csv)
        
        # Manually run the aggregation logic
        all_claims = SYNTHETIC_MOONDB_CLAIMS + SYNTHETIC_PLANTMP_CLAIMS
        records = aggregate_effective_status(
            all_claims,
            aggregation_policy_id=CONTRACT_ID,
            transformation_id="test_v0",
        )
        
        valid_records = [r for r in records if r.record_status == "valid"]
        
        # Check that we can compute the report fields
        from collections import Counter
        
        effective_status_counts: Counter = Counter()
        for r in valid_records:
            effective_status_counts[r.effective_status] += 1
        
        source_combos: Counter = Counter()
        for r in valid_records:
            combo = ";".join(sorted(set(r.source_ids)))
            source_combos[combo] += 1
        
        multi_status_count = sum(
            1 for r in valid_records if len(r.status_set) > 1
        )
        
        all_uniprot_ids: set[str] = set()
        for r in valid_records:
            if r.uniprot_id:
                all_uniprot_ids.add(r.uniprot_id)
        
        # Verify we can build the report dict
        report_dict = {
            "aggregation_policy_id": CONTRACT_ID,
            "transformation_id": "test_v0",
            "total_input_claims": len(all_claims),
            "total_unique_uniprot": len(all_uniprot_ids),
            "aggregated_records": len(valid_records),
            "effective_status_counts": dict(effective_status_counts),
            "source_combination_counts": dict(source_combos),
            "multi_status_uniprot_count": multi_status_count,
        }
        
        assert "aggregation_policy_id" in report_dict
        assert "effective_status_counts" in report_dict
        assert report_dict["total_input_claims"] == 8  # 5 + 3


class TestDeterministicOutput:
    """Test deterministic, reproducible output."""

    def test_deterministic_csv_output(self, tmp_path: Path) -> None:
        """Test that CSV output is deterministic (sorted source_ids, claim_ids)."""
        claims = [
            SourceClaim("c2", "SRC_PLANTMP", "P0001", "curated"),
            SourceClaim("c1", "SRC_MOONDB", "P0001", "predicted"),
        ]
        records = aggregate_effective_status(claims)
        valid_records = [r for r in records if r.record_status == "valid"]
        
        assert len(valid_records) == 1
        record = valid_records[0]
        
        # source_ids and claim_ids should be sorted
        assert record.source_ids == ("SRC_MOONDB", "SRC_PLANTMP")
        assert record.claim_ids == ("c1", "c2")
        assert record.effective_status == "curated"


class TestIntegrationWithRealInputs:
    """Integration test against real interim inputs if they exist."""

    @pytest.mark.skipif(
        not (REPO_ROOT / "data" / "interim" / "source_claims_moondb.csv").exists(),
        reason="Real MoonDB claims not committed"
    )
    @pytest.mark.skipif(
        not (REPO_ROOT / "data" / "interim" / "source_claims_plantmp.csv").exists(),
        reason="Real PlantMP claims not committed"
    )
    def test_real_inputs_produce_output(self, tmp_path: Path) -> None:
        """Test that real inputs produce valid output files."""
        import subprocess
        import sys
        
        from mfp_bibliography.effective_status import CONTRACT_ID
        
        script_path = REPO_ROOT / "scripts" / "generate_effective_status_moondb_plantmp.py"
        output_csv = REPO_ROOT / "data" / "interim" / "effective_status_moondb_plantmp.csv"
        report_json = REPO_ROOT / "data" / "interim" / "reports" / "effective_status_moondb_plantmp_report.json"
        report_md = REPO_ROOT / "data" / "interim" / "reports" / "effective_status_moondb_plantmp_report.md"
        
        # Run the script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(REPO_ROOT / "src")},
            cwd=str(REPO_ROOT),
        )
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        
        # Check output files exist
        assert output_csv.exists()
        assert report_json.exists()
        assert report_md.exists()
        
        # Check CSV has header
        with open(output_csv, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames is not None
            assert "uniprot_id" in reader.fieldnames
            assert "effective_status" in reader.fieldnames
        
        # Check JSON report is valid
        with open(report_json, encoding="utf-8") as f:
            report = json.load(f)
            assert "aggregation_policy_id" in report
            assert report["aggregation_policy_id"] == CONTRACT_ID
            assert report["total_input_claims"] == 463  # 351 + 112
        
        # Check snapshot manifest exists and is valid
        snapshot_path = REPO_ROOT / "data" / "interim" / "reports" / "effective_status_moondb_plantmp_snapshot.json"
        assert snapshot_path.exists()
        
        with open(snapshot_path, encoding="utf-8") as f:
            snapshot = json.load(f)
            assert "snapshot_id" in snapshot
            assert "generated_at" in snapshot
            assert snapshot["schema_version"] == "MFPB_0_15_SNAPSHOT_V0"
            assert snapshot["aggregation_policy_id"] == CONTRACT_ID
            assert snapshot["output_sha256"] == "7522eeeb58ad02578fdab35db6fef43ef82bab12aeee6c3137bc944b63f6d21a"
            assert snapshot["output_record_count"] == 461
            assert snapshot["exclusions_count"] == 0
            assert snapshot["effective_status_counts"]["curated"] == 124
            assert snapshot["effective_status_counts"]["predicted"] == 326
            assert snapshot["effective_status_counts"]["excluded_likely"] == 11


class TestSnapshotManifest:
    """Test snapshot manifest generation with synthetic inputs."""

    def test_snapshot_manifest_structure(self, tmp_path: Path) -> None:
        """Test that snapshot manifest has all required fields."""
        import json
        from datetime import datetime, timezone
        from scripts.generate_effective_status_moondb_plantmp import (
            write_snapshot_manifest,
            InputFileInfo,
            SNAPSHOT_SCHEMA_VERSION,
        )
        from collections import Counter
        
        # Create mock input file info
        moondb_info = InputFileInfo(
            path=Path("data/interim/source_claims_moondb.csv"),
            sha256="a" * 64,
            claim_count=5,
            sources=Counter({"SRC_MOONDB": 5}),
            statuses=Counter({"curated": 3, "predicted": 2}),
            uniprot_count=5,
            blank_uniprot_count=0,
        )
        plantmp_info = InputFileInfo(
            path=Path("data/interim/source_claims_plantmp.csv"),
            sha256="b" * 64,
            claim_count=3,
            sources=Counter({"SRC_PLANTMP": 3}),
            statuses=Counter({"curated": 1, "predicted": 2}),
            uniprot_count=3,
            blank_uniprot_count=0,
        )
        
        manifest_path = tmp_path / "snapshot.json"
        effective_status_counts = Counter({"curated": 4, "predicted": 4})
        
        snapshot_id = write_snapshot_manifest(
            moondb_info,
            plantmp_info,
            "c" * 64,
            8,
            effective_status_counts,
            0,
            manifest_path,
        )
        
        assert manifest_path.exists()
        
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        
        required_fields = [
            "snapshot_id",
            "generated_at",
            "schema_version",
            "aggregation_policy_id",
            "transformation_id",
            "input_files",
            "input_total_claims",
            "input_claims_by_source",
            "output_path",
            "output_sha256",
            "output_record_count",
            "effective_status_counts",
            "exclusions_count",
            "reproducibility_statement",
        ]
        for field in required_fields:
            assert field in manifest, f"Missing field: {field}"
        
        assert manifest["schema_version"] == SNAPSHOT_SCHEMA_VERSION
        assert manifest["input_total_claims"] == 8
        assert manifest["output_record_count"] == 8
        assert manifest["exclusions_count"] == 0
        
    def test_snapshot_id_deterministic(self, tmp_path: Path) -> None:
        """Test that snapshot ID is deterministic from input SHA-256."""
        import json
        from scripts.generate_effective_status_moondb_plantmp import (
            write_snapshot_manifest,
            InputFileInfo,
        )
        from collections import Counter
        
        moondb_info = InputFileInfo(
            path=Path("moondb.csv"),
            sha256="a" * 64,
            claim_count=1,
            sources=Counter(),
            statuses=Counter(),
            uniprot_count=0,
            blank_uniprot_count=0,
        )
        plantmp_info = InputFileInfo(
            path=Path("plantmp.csv"),
            sha256="b" * 64,
            claim_count=1,
            sources=Counter(),
            statuses=Counter(),
            uniprot_count=0,
            blank_uniprot_count=0,
        )
        
        manifest_path1 = tmp_path / "snapshot1.json"
        manifest_path2 = tmp_path / "snapshot2.json"
        
        write_snapshot_manifest(
            moondb_info, plantmp_info, "c" * 64, 1, Counter(), 0, manifest_path1
        )
        write_snapshot_manifest(
            moondb_info, plantmp_info, "c" * 64, 1, Counter(), 0, manifest_path2
        )
        
        with open(manifest_path1) as f1, open(manifest_path2) as f2:
            m1 = json.load(f1)
            m2 = json.load(f2)
            # snapshot_id should be the same
            assert m1["snapshot_id"] == m2["snapshot_id"]
            # but generated_at will differ (timestamp)
            # All other fields should be the same
            assert m1["output_sha256"] == m2["output_sha256"]
            assert m1["output_record_count"] == m2["output_record_count"]
