from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from mfp_bibliography.moondb_claims import (
    MOONDB_TRANSFORMATION_ID,
    MoonDBProvenance,
    adapt_moondb_claims,
    build_validation_report,
    load_moondb_provenance,
    load_policy,
    read_claims_csv,
)
from mfp_bibliography.source_claims import validate_claim

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_MOONDB = REPO_ROOT / "data" / "raw" / "moondb" / "all_emf_and_curated.tsv"
FIXTURE_MOONDB = REPO_ROOT / "data" / "fixtures" / "moondb" / "sample.tsv"
POLICY_PATH = REPO_ROOT / "configs" / "source_claim_policy_v0.1.yaml"
CLAIMS_CSV = REPO_ROOT / "data" / "interim" / "source_claims_moondb.csv"
REPORT_JSON = REPO_ROOT / "data" / "interim" / "source_claims_moondb_validation_report.json"

FIXTURE_PROVENANCE = MoonDBProvenance(
    source_version="unknown",
    retrieved_at="unknown",
    raw_file_path="data/fixtures/moondb/sample.tsv",
    raw_sha256="0" * 64,
    raw_row_count=3,
)


def _write_tsv(path: Path, rows: list[tuple[str, str]]) -> None:
    lines = ["#UniProtKB_ac\tUniProtKB_ac\ttype"]
    lines.extend(f"{uniprot}\t{uniprot}\t{claim_type}" for uniprot, claim_type in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_adapter_maps_fixture_rows_through_policy() -> None:
    policy = load_policy(POLICY_PATH)
    claims = adapt_moondb_claims(FIXTURE_MOONDB, policy, FIXTURE_PROVENANCE)

    assert len(claims) == 3
    by_uniprot = {claim["uniprot_id"]: claim for claim in claims}
    assert by_uniprot["Q86VP1"]["operational_status"] == "predicted"
    assert by_uniprot["Q8WUM4"]["operational_status"] == "predicted"
    assert by_uniprot["P06744"]["operational_status"] == "curated"
    assert by_uniprot["P06744"]["primary_target_eligible"] is True
    assert by_uniprot["Q86VP1"]["primary_target_eligible"] is False
    assert all(claim["control_eligible"] is False for claim in claims)
    assert all(claim["raw_claim_field"] == "type" for claim in claims)
    assert by_uniprot["P06744"]["raw_claim_value"] == "Curated"
    for claim in claims:
        validate_claim(claim)


def test_row_identity_and_provenance_fields() -> None:
    policy = load_policy(POLICY_PATH)
    claims = adapt_moondb_claims(FIXTURE_MOONDB, policy, FIXTURE_PROVENANCE)

    assert [claim["raw_row_or_url"] for claim in claims] == ["row:2", "row:3", "row:4"]
    assert [claim["source_record_id"] for claim in claims] == [
        "moondb_row_2",
        "moondb_row_3",
        "moondb_row_4",
    ]
    for claim in claims:
        assert claim["raw_file_path"] == FIXTURE_PROVENANCE.raw_file_path
        assert claim["source_version"] == "unknown"
        assert claim["retrieved_at"] == "unknown"
        assert claim["transformation_id"] == MOONDB_TRANSFORMATION_ID


def test_duplicates_are_preserved(tmp_path: Path) -> None:
    raw_path = tmp_path / "duplicates.tsv"
    _write_tsv(raw_path, [("P12345", "Curated"), ("P12345", "Curated")])
    policy = load_policy(POLICY_PATH)
    provenance = MoonDBProvenance(
        source_version="unknown",
        retrieved_at="unknown",
        raw_file_path=str(raw_path),
        raw_sha256="0" * 64,
        raw_row_count=2,
    )

    claims = adapt_moondb_claims(raw_path, policy, provenance)

    assert len(claims) == 2
    assert claims[0]["uniprot_id"] == claims[1]["uniprot_id"] == "P12345"
    assert claims[0]["claim_id"] != claims[1]["claim_id"]
    assert claims[0]["raw_row_or_url"] == "row:2"
    assert claims[1]["raw_row_or_url"] == "row:3"
    for claim in claims:
        validate_claim(claim)


def test_unmapped_value_resolves_to_unresolved(tmp_path: Path) -> None:
    raw_path = tmp_path / "unmapped.tsv"
    _write_tsv(raw_path, [("P99999", "Unclear")])
    policy = load_policy(POLICY_PATH)
    provenance = MoonDBProvenance(
        source_version="unknown",
        retrieved_at="unknown",
        raw_file_path=str(raw_path),
        raw_sha256="0" * 64,
        raw_row_count=1,
    )

    claim = adapt_moondb_claims(raw_path, policy, provenance)[0]

    assert claim["operational_status"] == "unresolved"
    assert claim["raw_claim_value"] == "Unclear"
    assert claim["primary_target_eligible"] is False
    assert claim["control_eligible"] is False
    validate_claim(claim)


def test_rejects_policy_claim_field_outside_permitted_raw_fields() -> None:
    policy = load_policy(POLICY_PATH)
    policy["source_mappings"]["SRC_MOONDB"]["field"] = "Models"

    with pytest.raises(ValueError):
        adapt_moondb_claims(FIXTURE_MOONDB, policy, FIXTURE_PROVENANCE)


def test_real_artifact_reconciles_with_manifest_counts() -> None:
    policy = load_policy(POLICY_PATH)
    provenance = load_moondb_provenance(REPO_ROOT)
    claims = adapt_moondb_claims(RAW_MOONDB, policy, provenance)
    report = build_validation_report(claims, RAW_MOONDB, provenance)

    assert len(claims) == 351
    assert report["counts_by_raw_type"] == {"Curated": 62, "Predicted": 289}
    assert report["counts_by_operational_status"] == {"curated": 62, "predicted": 289}
    assert report["primary_target_eligible_count"] == 62
    assert report["checks"]["raw_sha256_matches_manifest"] is True
    assert report["reconciliation_ok"] is True


def test_committed_artifact_reconciles_and_is_reproducible() -> None:
    policy = load_policy(POLICY_PATH)
    provenance = load_moondb_provenance(REPO_ROOT)
    regenerated = adapt_moondb_claims(RAW_MOONDB, policy, provenance)

    committed = read_claims_csv(CLAIMS_CSV)
    assert len(committed) == 351
    assert committed == regenerated
    for claim in committed:
        validate_claim(claim)

    report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    assert report["claim_count"] == 351
    assert report["counts_by_raw_type"] == {"Curated": 62, "Predicted": 289}
    assert report["counts_by_operational_status"] == {"curated": 62, "predicted": 289}
    assert report["reconciliation_ok"] is True


def test_build_script_reproduces_committed_artifact(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_source_claims_moondb.py",
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    reproduced = (tmp_path / "source_claims_moondb.csv").read_text(encoding="utf-8")
    assert reproduced == CLAIMS_CSV.read_text(encoding="utf-8")
    report = json.loads((tmp_path / "source_claims_moondb_validation_report.json").read_text(encoding="utf-8"))
    assert report["reconciliation_ok"] is True
