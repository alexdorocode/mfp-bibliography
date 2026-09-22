from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path

import yaml

from mfp_bibliography.validation import validate_repository


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "configs" / "source_claim_policy_v0.1.yaml"
CHECKSUMS_PATH = REPO_ROOT / "data" / "manifests" / "file_checksums.sha256"
RAW_MOONDB = REPO_ROOT / "data" / "raw" / "moondb" / "all_emf_and_curated.tsv"
RAW_PLANTMP = REPO_ROOT / "data" / "raw" / "plantmp" / "PlantMP_all.csv"


def load_policy() -> dict:
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


def resolve_status(policy: dict, source_id: str, raw_value: str | None) -> str:
    """Resolve an operational status per the declarative policy."""
    default = policy["default_status"]
    if raw_value is None or str(raw_value).strip() == "":
        return default
    mapping = policy["source_mappings"].get(source_id, {})
    return mapping.get("value_map", {}).get(raw_value, default)


def observed_moondb_types() -> set[str]:
    with RAW_MOONDB.open(encoding="utf-8", newline="") as handle:
        rows = csv.reader(handle, delimiter="\t")
        next(rows)
        return {row[2] for row in rows if row}


def observed_plantmp_types() -> set[str]:
    with RAW_PLANTMP.open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        return {row["type"] for row in rows}


class TestSourceClaimPolicy:
    def test_policy_identity_and_vocabulary(self) -> None:
        policy = load_policy()
        assert policy["policy_id"] == "MFPB_0_7_SOURCE_CLAIM_POLICY_V0"
        assert policy["version"] == "0.1"
        assert set(policy["status_vocabulary"]) == {
            "curated",
            "predicted",
            "excluded_likely",
            "unresolved",
        }
        assert policy["default_status"] == "unresolved"

    def test_moondb_observed_values_map_exactly_once(self) -> None:
        policy = load_policy()
        value_map = policy["source_mappings"]["SRC_MOONDB"]["value_map"]
        assert policy["source_mappings"]["SRC_MOONDB"]["field"] == "type"
        assert set(value_map) == observed_moondb_types()
        assert set(value_map.values()) <= set(policy["status_vocabulary"])

    def test_plantmp_observed_values_map_exactly_once(self) -> None:
        policy = load_policy()
        value_map = policy["source_mappings"]["SRC_PLANTMP"]["value_map"]
        assert policy["source_mappings"]["SRC_PLANTMP"]["field"] == "type"
        assert set(value_map) == observed_plantmp_types()
        assert set(value_map.values()) <= set(policy["status_vocabulary"])

    def test_expected_mappings(self) -> None:
        policy = load_policy()
        assert resolve_status(policy, "SRC_MOONDB", "Curated") == "curated"
        assert resolve_status(policy, "SRC_MOONDB", "Predicted") == "predicted"
        assert resolve_status(policy, "SRC_PLANTMP", "confirmed") == "curated"
        assert resolve_status(policy, "SRC_PLANTMP", "likely") == "excluded_likely"
        assert resolve_status(policy, "SRC_PLANTMP", "predicted") == "predicted"

    def test_unknown_and_missing_values_map_to_unresolved(self) -> None:
        policy = load_policy()
        assert resolve_status(policy, "SRC_MOONDB", "whatever") == "unresolved"
        assert resolve_status(policy, "SRC_PLANTMP", None) == "unresolved"
        assert resolve_status(policy, "SRC_PLANTMP", "") == "unresolved"
        assert resolve_status(policy, "SRC_MOONDB", None) == "unresolved"

    def test_no_mapping_for_multitaskprotdb_ii_models(self) -> None:
        policy = load_policy()
        assert "SRC_MULTITASKPROTDB_II" not in policy["source_mappings"]
        assert "Models" in policy["excluded_fields"]["SRC_MULTITASKPROTDB_II"]
        for value in ("Phyre", "ITasser"):
            assert resolve_status(policy, "SRC_MULTITASKPROTDB_II", value) == "unresolved"

    def test_multifacetedprotdb_remains_unresolved(self) -> None:
        policy = load_policy()
        assert "SRC_MULTIFACETEDPROTDB" in policy["unmapped_sources"]
        assert "SRC_MULTIFACETEDPROTDB" not in policy["source_mappings"]
        assert resolve_status(policy, "SRC_MULTIFACETEDPROTDB", "any") == "unresolved"

    def test_precedence_order_is_total_over_vocabulary(self) -> None:
        policy = load_policy()
        assert policy["precedence"] == [
            "curated",
            "predicted",
            "excluded_likely",
            "unresolved",
        ]
        assert set(policy["precedence"]) == set(policy["status_vocabulary"])

    def test_raw_checksums_unchanged(self) -> None:
        for line in CHECKSUMS_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            expected, relative_path = line.split("  ", 1)
            digest = hashlib.sha256((REPO_ROOT / relative_path).read_bytes()).hexdigest()
            assert digest == expected, f"Checksum mismatch for {relative_path}"


class TestRawDirectoryHygiene:
    def test_repository_has_no_lock_files(self) -> None:
        result = validate_repository(REPO_ROOT)
        names = {check["name"]: check for check in result["checks"]}
        assert names["raw_directory_hygiene"]["ok"] is True

    def test_hygiene_check_rejects_lock_files(self, tmp_path) -> None:
        copied = tmp_path / "repo"
        shutil.copytree(REPO_ROOT, copied)
        (copied / "data" / "raw" / "plantmp" / ".~lock.PlantMP MySQL.xlsx#").write_text(
            "", encoding="utf-8"
        )

        result = validate_repository(copied)
        assert result["ok"] is False
        names = {check["name"]: check for check in result["checks"]}
        assert names["raw_directory_hygiene"]["ok"] is False
