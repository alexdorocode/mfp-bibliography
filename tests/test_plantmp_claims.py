from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from mfp_bibliography.plantmp_claims import (
    PLANTMP_TRANSFORMATION_ID,
    PlantMPProvenance,
    adapt_plantmp_claims,
    build_validation_report,
    load_plantmp_provenance,
    load_policy,
)
from mfp_bibliography.source_claims import read_claims_csv, validate_claim

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_PLANTMP = REPO_ROOT / "data" / "raw" / "plantmp" / "PlantMP_all.csv"
FIXTURE_PLANTMP = REPO_ROOT / "data" / "fixtures" / "plantmp" / "sample.csv"
POLICY_PATH = REPO_ROOT / "configs" / "source_claim_policy_v0.1.yaml"
CLAIMS_CSV = REPO_ROOT / "data" / "interim" / "source_claims_plantmp.csv"
REPORT_JSON = REPO_ROOT / "data" / "interim" / "source_claims_plantmp_validation_report.json"

FIXTURE_PROVENANCE = PlantMPProvenance(
    source_version="unknown",
    retrieved_at="unknown",
    raw_file_path="data/fixtures/plantmp/sample.csv",
    raw_sha256="0" * 64,
    raw_row_count=3,
)

_CSV_COLUMNS = [
    "order",
    "protein name, gene",
    "uniport_id",
    "canonical_function_bp",
    "canonical_function_mf",
    "moonlighting_function_bp",
    "moonlighting_function_mf",
    "go_canonical_bp",
    "go_canonical_mf",
    "go_moonlighting_bp",
    "go_moonlighting_mf",
    "plant_species",
    "pubmed_id",
    "type",
]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in _CSV_COLUMNS})


def _tmp_provenance(raw_path: Path, row_count: int) -> PlantMPProvenance:
    return PlantMPProvenance(
        source_version="unknown",
        retrieved_at="unknown",
        raw_file_path=str(raw_path),
        raw_sha256="0" * 64,
        raw_row_count=row_count,
    )


def test_adapter_maps_fixture_rows_through_policy() -> None:
    policy = load_policy(POLICY_PATH)
    claims = adapt_plantmp_claims(FIXTURE_PLANTMP, policy, FIXTURE_PROVENANCE)

    assert len(claims) == 3
    by_order = {claim["source_record_id"]: claim for claim in claims}
    assert by_order["plantmp_order_1"]["operational_status"] == "curated"
    assert by_order["plantmp_order_1"]["primary_target_eligible"] is True
    assert by_order["plantmp_order_2"]["operational_status"] == "excluded_likely"
    assert by_order["plantmp_order_2"]["primary_target_eligible"] is False
    assert by_order["plantmp_order_3"]["operational_status"] == "predicted"
    assert by_order["plantmp_order_3"]["primary_target_eligible"] is False
    assert all(claim["control_eligible"] is False for claim in claims)
    assert all(claim["raw_claim_field"] == "type" for claim in claims)
    assert by_order["plantmp_order_1"]["raw_claim_value"] == "confirmed"
    for claim in claims:
        validate_claim(claim)


def test_raw_protein_name_and_organism_retained() -> None:
    policy = load_policy(POLICY_PATH)
    claims = adapt_plantmp_claims(FIXTURE_PLANTMP, policy, FIXTURE_PROVENANCE)

    by_order = {claim["source_record_id"]: claim for claim in claims}
    assert by_order["plantmp_order_1"]["protein_name_raw"] == "Protein A, GENE1"
    assert by_order["plantmp_order_1"]["organism_raw"] == "Arabidopsis thaliana"
    assert by_order["plantmp_order_2"]["protein_name_raw"] == "Protein B, GENE2"


def test_row_identity_and_provenance_fields() -> None:
    policy = load_policy(POLICY_PATH)
    claims = adapt_plantmp_claims(FIXTURE_PLANTMP, policy, FIXTURE_PROVENANCE)

    assert [claim["raw_row_or_url"] for claim in claims] == ["order:1", "order:2", "order:3"]
    for claim in claims:
        assert claim["raw_file_path"] == FIXTURE_PROVENANCE.raw_file_path
        assert claim["source_version"] == "unknown"
        assert claim["retrieved_at"] == "unknown"
        assert claim["transformation_id"] == PLANTMP_TRANSFORMATION_ID
        assert claim["raw_claim_value"] in {"confirmed", "likely", "predicted"}


def test_duplicate_uniprot_rows_are_preserved(tmp_path: Path) -> None:
    raw_path = tmp_path / "duplicates.csv"
    _write_csv(
        raw_path,
        [
            {"order": "1", "uniport_id": "Q8VYA3", "plant_species": "Arabidopsis thaliana", "type": "confirmed"},
            {"order": "2", "uniport_id": "Q8VYA3", "plant_species": "Arabidopsis thaliana", "type": "predicted"},
        ],
    )
    policy = load_policy(POLICY_PATH)
    provenance = _tmp_provenance(raw_path, 2)

    claims = adapt_plantmp_claims(raw_path, policy, provenance)

    assert len(claims) == 2
    assert [claim["uniprot_id"] for claim in claims] == ["Q8VYA3", "Q8VYA3"]
    assert claims[0]["claim_id"] != claims[1]["claim_id"]
    assert claims[0]["operational_status"] == "curated"
    assert claims[1]["operational_status"] == "predicted"
    for claim in claims:
        validate_claim(claim)


def test_missing_and_unmapped_type_resolve_to_unresolved(tmp_path: Path) -> None:
    raw_path = tmp_path / "types.csv"
    _write_csv(
        raw_path,
        [
            {"order": "1", "uniport_id": "P11111", "type": ""},
            {"order": "2", "uniport_id": "P22222", "type": "hypothetical"},
        ],
    )
    policy = load_policy(POLICY_PATH)
    provenance = _tmp_provenance(raw_path, 2)

    claims = adapt_plantmp_claims(raw_path, policy, provenance)

    assert [claim["operational_status"] for claim in claims] == [
        "unresolved",
        "unresolved",
    ]
    assert claims[0]["raw_claim_value"] == "unknown"
    assert claims[1]["raw_claim_value"] == "hypothetical"
    assert all(claim["primary_target_eligible"] is False for claim in claims)
    for claim in claims:
        validate_claim(claim)


def test_rejects_policy_claim_field_outside_permitted_raw_fields() -> None:
    policy = load_policy(POLICY_PATH)
    policy["source_mappings"]["SRC_PLANTMP"]["field"] = "Models"

    with pytest.raises(ValueError):
        adapt_plantmp_claims(FIXTURE_PLANTMP, policy, FIXTURE_PROVENANCE)


def test_real_artifact_reconciles_with_manifest_counts() -> None:
    policy = load_policy(POLICY_PATH)
    provenance = load_plantmp_provenance(REPO_ROOT)
    claims = adapt_plantmp_claims(RAW_PLANTMP, policy, provenance)
    report = build_validation_report(claims, RAW_PLANTMP, provenance, policy)

    assert len(claims) == 112
    assert report["counts_by_raw_type"] == {"confirmed": 62, "likely": 12, "predicted": 38}
    assert report["counts_by_operational_status"] == {
        "curated": 62,
        "excluded_likely": 12,
        "predicted": 38,
    }
    assert report["primary_target_eligible_count"] == 62
    assert report["checks"]["raw_sha256_matches_manifest"] is True
    assert report["checks"]["status_matches_policy"] is True
    assert report["reconciliation_ok"] is True

    duplicate_claims = [c for c in claims if c["uniprot_id"] in {"Q8VYA3", "F4I9D5"}]
    assert len(duplicate_claims) == 4
    assert len({c["claim_id"] for c in duplicate_claims}) == 4


def test_committed_artifact_reconciles_and_is_reproducible() -> None:
    policy = load_policy(POLICY_PATH)
    provenance = load_plantmp_provenance(REPO_ROOT)
    regenerated = adapt_plantmp_claims(RAW_PLANTMP, policy, provenance)

    committed = read_claims_csv(CLAIMS_CSV)
    assert len(committed) == 112
    assert committed == regenerated
    for claim in committed:
        validate_claim(claim)

    report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    assert report["claim_count"] == 112
    assert report["counts_by_raw_type"] == {"confirmed": 62, "likely": 12, "predicted": 38}
    assert report["counts_by_operational_status"] == {
        "curated": 62,
        "excluded_likely": 12,
        "predicted": 38,
    }
    assert report["reconciliation_ok"] is True


def test_build_script_reproduces_committed_artifact(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_source_claims_plantmp.py",
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    reproduced = (tmp_path / "source_claims_plantmp.csv").read_text(encoding="utf-8")
    assert reproduced == CLAIMS_CSV.read_text(encoding="utf-8")
    report = json.loads(
        (tmp_path / "source_claims_plantmp_validation_report.json").read_text(encoding="utf-8")
    )
    assert report["reconciliation_ok"] is True
