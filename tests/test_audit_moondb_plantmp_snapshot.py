"""Tests for audit_moondb_plantmp_snapshot.py quality audit script."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_csv(data: list[dict[str, Any]], path: Path) -> str:
    """Write data to CSV and return SHA-256."""
    if not data:
        return ""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(data[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)
    
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def make_effective_status_record(
    uniprot_id: str,
    effective_status: str,
    source_ids: list[str] = None,
    claim_ids: list[str] = None,
    status_set: list[str] = None,
    has_curated: bool = False,
    has_predicted: bool = False,
    has_excluded_likely: bool = False,
    claim_count: int = 1,
    source_count: int = 1,
) -> dict[str, Any]:
    return {
        "uniprot_id": uniprot_id,
        "effective_status": effective_status,
        "source_ids": ";".join(source_ids or ["SRC_TEST"]),
        "claim_ids": ";".join(claim_ids or ["C1"]),
        "status_set": ";".join(status_set or [effective_status]),
        "has_curated_claim": str(has_curated),
        "has_predicted_claim": str(has_predicted),
        "has_excluded_likely_claim": str(has_excluded_likely),
        "has_unresolved_claim": "false",
        "claim_count": claim_count,
        "source_count": source_count,
        "aggregation_policy_id": "TEST_POLICY",
        "transformation_id": "test_transform",
        "record_status": "valid",
        "notes": "",
    }


def make_source_claim(claim_id: str, source_id: str, uniprot_id: str, status: str) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "source_id": source_id,
        "source_record_id": f"{source_id}_row",
        "uniprot_id": uniprot_id,
        "protein_name_raw": "",
        "organism_raw": "",
        "raw_claim_field": "type",
        "raw_claim_value": status,
        "operational_status": status,
        "primary_target_eligible": str(status == "curated").lower(),
        "control_eligible": "false",
        "raw_file_path": "test.csv",
        "raw_row_or_url": "row:1",
        "source_version": "test_v0",
        "retrieved_at": "unknown",
        "transformation_id": "test_transform",
        "record_status": "valid",
        "notes": "",
    }


class TestAuditWithSyntheticData:
    """Test audit with synthetic fixtures."""

    def test_one_claim_per_id(self, tmp_path: Path) -> None:
        """Test audit with one claim per UniProt ID."""
        # Create synthetic CSV files
        effective_status_csv = tmp_path / "effective_status.csv"
        snapshot_manifest = tmp_path / "snapshot_manifest.json"
        moondb_claims = tmp_path / "source_claims_moondb.csv"
        plantmp_claims = tmp_path / "source_claims_plantmp.csv"
        
        # Write effective status CSV
        records = [
            make_effective_status_record("P0001", "curated"),
            make_effective_status_record("P0002", "predicted"),
            make_effective_status_record("P0003", "excluded_likely"),
        ]
        write_csv(records, effective_status_csv)
        
        # Write snapshot manifest
        manifest = {
            "aggregation_policy_id": "TEST_POLICY",
            "transformation_id": "test_transform",
        }
        with open(snapshot_manifest, "w") as f:
            json.dump(manifest, f)
        
        # Write source claims (one per ID)
        moondb_data = [
            make_source_claim("MD:001", "SRC_MOONDB", "P0001", "curated"),
        ]
        plantmp_data = [
            make_source_claim("PM:001", "SRC_PLANTMP", "P0002", "predicted"),
            make_source_claim("PM:002", "SRC_PLANTMP", "P0003", "excluded_likely"),
        ]
        write_csv(moondb_data, moondb_claims)
        write_csv(plantmp_data, plantmp_claims)
        
        # Import and run audit functions
        import sys
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from audit_moondb_plantmp_snapshot import (
            read_effective_status_csv,
            read_source_claims,
            analyze_snapshot,
            write_json_audit,
            write_md_audit,
        )
        
        # Override paths
        import audit_moondb_plantmp_snapshot as audit_module
        audit_module.EFFECTIVE_STATUS_CSV = effective_status_csv
        audit_module.SNAPSHOT_MANIFEST = snapshot_manifest
        audit_module.MOONDB_CLAIMS = moondb_claims
        audit_module.PLANTMP_CLAIMS = plantmp_claims
        
        records = read_effective_status_csv(effective_status_csv)
        moondb_claim_list = read_source_claims(moondb_claims)
        plantmp_claim_list = read_source_claims(plantmp_claims)
        all_claims = moondb_claim_list + plantmp_claim_list
        
        audit = analyze_snapshot(records, all_claims)
        
        assert audit["record_count"] == 3
        assert audit["effective_status_counts"]["curated"] == 1
        assert audit["effective_status_counts"]["predicted"] == 1
        assert audit["effective_status_counts"]["excluded_likely"] == 1

    def test_multiple_sources_same_id(self, tmp_path: Path) -> None:
        """Test audit with multiple sources for same UniProt ID."""
        effective_status_csv = tmp_path / "effective_status.csv"
        snapshot_manifest = tmp_path / "snapshot_manifest.json"
        moondb_claims = tmp_path / "source_claims_moondb.csv"
        plantmp_claims = tmp_path / "source_claims_plantmp.csv"
        
        records = [
            make_effective_status_record(
                "P0001", "curated",
                source_ids=["SRC_MOONDB", "SRC_PLANTMP"],
                claim_ids=["MD:001", "PM:001"],
                status_set=["curated"],
                has_curated=True,
                claim_count=2,
                source_count=2,
            ),
        ]
        write_csv(records, effective_status_csv)
        
        manifest = {"aggregation_policy_id": "TEST", "transformation_id": "test"}
        with open(snapshot_manifest, "w") as f:
            json.dump(manifest, f)
        
        moondb_data = [make_source_claim("MD:001", "SRC_MOONDB", "P0001", "curated")]
        plantmp_data = [make_source_claim("PM:001", "SRC_PLANTMP", "P0001", "curated")]
        write_csv(moondb_data, moondb_claims)
        write_csv(plantmp_data, plantmp_claims)
        
        import sys
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from audit_moondb_plantmp_snapshot import (
            read_effective_status_csv,
            read_source_claims,
            analyze_snapshot,
        )
        
        records = read_effective_status_csv(effective_status_csv)
        moondb_claim_list = read_source_claims(moondb_claims)
        plantmp_claim_list = read_source_claims(plantmp_claims)
        all_claims = moondb_claim_list + plantmp_claim_list
        
        audit = analyze_snapshot(records, all_claims)
        
        assert audit["record_count"] == 1
        assert audit["ids_by_source_count"]["multiple_sources"] == 1
        assert audit["ids_by_source_count"]["one_source"] == 0

    def test_duplicate_claims(self, tmp_path: Path) -> None:
        """Test audit with source-local duplicate claims."""
        effective_status_csv = tmp_path / "effective_status.csv"
        snapshot_manifest = tmp_path / "snapshot_manifest.json"
        moondb_claims = tmp_path / "source_claims_moondb.csv"
        plantmp_claims = tmp_path / "source_claims_plantmp.csv"
        
        records = [
            make_effective_status_record(
                "P0001", "curated",
                claim_count=2,
                source_count=1,
                has_curated=True,
            ),
        ]
        write_csv(records, effective_status_csv)
        
        manifest = {"aggregation_policy_id": "TEST", "transformation_id": "test"}
        with open(snapshot_manifest, "w") as f:
            json.dump(manifest, f)
        
        # Two claims for same (source, uniprot)
        moondb_data = [
            make_source_claim("MD:001", "SRC_MOONDB", "P0001", "curated"),
            make_source_claim("MD:002", "SRC_MOONDB", "P0001", "curated"),
        ]
        plantmp_data: list[dict[str, Any]] = []
        write_csv(moondb_data, moondb_claims)
        # Write empty CSV with header for plantmp
        with open(plantmp_claims, "w", encoding="utf-8", newline="") as f:
            f.write("")
        
        import sys
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from audit_moondb_plantmp_snapshot import (
            read_effective_status_csv,
            read_source_claims,
            analyze_snapshot,
        )
        
        records = read_effective_status_csv(effective_status_csv)
        moondb_claim_list = read_source_claims(moondb_claims)
        plantmp_claim_list = read_source_claims(plantmp_claims)
        all_claims = moondb_claim_list + plantmp_claim_list
        
        audit = analyze_snapshot(records, all_claims)
        
        assert audit["source_local_duplicate_count"] == 1
        assert len(audit["source_local_duplicate_details"]) == 1
        assert audit["source_local_duplicate_details"][0]["source_id"] == "SRC_MOONDB"
        assert audit["source_local_duplicate_details"][0]["uniprot_id"] == "P0001"

    def test_excluded_likely_with_stronger(self, tmp_path: Path) -> None:
        """Test audit with excluded_likely coexisting with curated."""
        effective_status_csv = tmp_path / "effective_status.csv"
        snapshot_manifest = tmp_path / "snapshot_manifest.json"
        moondb_claims = tmp_path / "source_claims_moondb.csv"
        plantmp_claims = tmp_path / "source_claims_plantmp.csv"
        
        records = [
            make_effective_status_record(
                "P0001", "curated",
                status_set=["curated", "excluded_likely"],
                has_curated=True,
                has_excluded_likely=True,
            ),
        ]
        write_csv(records, effective_status_csv)
        
        manifest = {"aggregation_policy_id": "TEST", "transformation_id": "test"}
        with open(snapshot_manifest, "w") as f:
            json.dump(manifest, f)
        
        moondb_data = [
            make_source_claim("MD:001", "SRC_MOONDB", "P0001", "curated"),
            make_source_claim("MD:002", "SRC_MOONDB", "P0001", "excluded_likely"),
        ]
        plantmp_data: list[dict[str, Any]] = []
        write_csv(moondb_data, moondb_claims)
        # Write empty CSV with header for plantmp
        with open(plantmp_claims, "w", encoding="utf-8", newline="") as f:
            f.write("")
        
        import sys
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from audit_moondb_plantmp_snapshot import (
            read_effective_status_csv,
            read_source_claims,
            analyze_snapshot,
        )
        
        records = read_effective_status_csv(effective_status_csv)
        moondb_claim_list = read_source_claims(moondb_claims)
        plantmp_claim_list = read_source_claims(plantmp_claims)
        all_claims = moondb_claim_list + plantmp_claim_list
        
        audit = analyze_snapshot(records, all_claims)
        
        assert audit["excluded_likely_with_stronger_count"] == 1

    def test_predicted_only(self, tmp_path: Path) -> None:
        """Test audit with predicted-only IDs."""
        effective_status_csv = tmp_path / "effective_status.csv"
        snapshot_manifest = tmp_path / "snapshot_manifest.json"
        moondb_claims = tmp_path / "source_claims_moondb.csv"
        plantmp_claims = tmp_path / "source_claims_plantmp.csv"
        
        records = [
            make_effective_status_record("P0001", "predicted", has_predicted=True),
            make_effective_status_record("P0002", "predicted", has_predicted=True),
        ]
        write_csv(records, effective_status_csv)
        
        manifest = {"aggregation_policy_id": "TEST", "transformation_id": "test"}
        with open(snapshot_manifest, "w") as f:
            json.dump(manifest, f)
        
        moondb_data = [
            make_source_claim("MD:001", "SRC_MOONDB", "P0001", "predicted"),
            make_source_claim("MD:002", "SRC_MOONDB", "P0002", "predicted"),
        ]
        plantmp_data: list[dict[str, Any]] = []
        write_csv(moondb_data, moondb_claims)
        # Write empty CSV with header for plantmp
        with open(plantmp_claims, "w", encoding="utf-8", newline="") as f:
            f.write("")
        
        import sys
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from audit_moondb_plantmp_snapshot import (
            read_effective_status_csv,
            read_source_claims,
            analyze_snapshot,
        )
        
        records = read_effective_status_csv(effective_status_csv)
        moondb_claim_list = read_source_claims(moondb_claims)
        plantmp_claim_list = read_source_claims(plantmp_claims)
        all_claims = moondb_claim_list + plantmp_claim_list
        
        audit = analyze_snapshot(records, all_claims)
        
        assert audit["predicted_ids_count"] == 2
        assert "P0001" in audit["predicted_ids"]
        assert "P0002" in audit["predicted_ids"]

    def test_deterministic_output(self, tmp_path: Path) -> None:
        """Test that audit output is deterministic."""
        effective_status_csv = tmp_path / "effective_status.csv"
        snapshot_manifest = tmp_path / "snapshot_manifest.json"
        moondb_claims = tmp_path / "source_claims_moondb.csv"
        plantmp_claims = tmp_path / "source_claims_plantmp.csv"
        
        records = [
            make_effective_status_record("P0001", "curated"),
            make_effective_status_record("P0002", "predicted"),
        ]
        write_csv(records, effective_status_csv)
        
        manifest = {"aggregation_policy_id": "TEST", "transformation_id": "test"}
        with open(snapshot_manifest, "w") as f:
            json.dump(manifest, f)
        
        moondb_data = [
            make_source_claim("MD:001", "SRC_MOONDB", "P0001", "curated"),
            make_source_claim("MD:002", "SRC_MOONDB", "P0002", "predicted"),
        ]
        plantmp_data: list[dict[str, Any]] = []
        write_csv(moondb_data, moondb_claims)
        # Write empty CSV with header for plantmp
        with open(plantmp_claims, "w", encoding="utf-8", newline="") as f:
            f.write("")
        
        import sys
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from audit_moondb_plantmp_snapshot import (
            read_effective_status_csv,
            read_source_claims,
            analyze_snapshot,
            write_json_audit,
            write_md_audit,
            compute_sha256,
        )
        import audit_moondb_plantmp_snapshot as audit_module
        audit_module.EFFECTIVE_STATUS_CSV = effective_status_csv
        audit_module.SNAPSHOT_MANIFEST = snapshot_manifest
        audit_module.MOONDB_CLAIMS = moondb_claims
        audit_module.PLANTMP_CLAIMS = plantmp_claims
        audit_module.AUDIT_JSON_PATH = tmp_path / "audit.json"
        audit_module.AUDIT_MD_PATH = tmp_path / "audit.md"
        
        # Run twice
        records = read_effective_status_csv(effective_status_csv)
        moondb_claim_list = read_source_claims(moondb_claims)
        plantmp_claim_list = read_source_claims(plantmp_claims)
        all_claims = moondb_claim_list + plantmp_claim_list
        
        audit1 = analyze_snapshot(records, all_claims)
        audit1_json_sha = write_json_audit(audit1, tmp_path / "audit1.json")
        
        # Reset timestamp to avoid difference
        audit1["audit_metadata"]["generated_at"] = "2024-01-01T00:00:00+00:00"
        audit2 = analyze_snapshot(records, all_claims)
        audit2["audit_metadata"]["generated_at"] = "2024-01-01T00:00:00+00:00"
        
        # Compare audit dicts (excluding generated_at which we controlled)
        audit1_json_sha = write_json_audit(audit1, tmp_path / "audit1.json")
        audit2_json_sha = write_json_audit(audit2, tmp_path / "audit2.json")
        
        assert audit1_json_sha == audit2_json_sha
