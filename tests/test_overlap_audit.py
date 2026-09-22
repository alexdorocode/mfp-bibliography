from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from mfp_bibliography.overlap_audit import (
    CONTRACT_ID,
    MOONDB_SOURCE_ID,
    PLANTMP_SOURCE_ID,
    SIMULATED_STATUS_FIELD,
    build_overlap_audit,
    load_validated_claims,
    render_overlap_audit_markdown,
    simulated_effective_status,
)
from mfp_bibliography.provenance import sha256_file
from mfp_bibliography.schemas import RecordValidationError
from mfp_bibliography.source_claims import write_claims_csv

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "overlap"
MOONDB_CLAIMS = REPO_ROOT / "data" / "interim" / "source_claims_moondb.csv"
PLANTMP_CLAIMS = REPO_ROOT / "data" / "interim" / "source_claims_plantmp.csv"
REPORT_JSON = REPO_ROOT / "data" / "interim" / "reports" / "moondb_plantmp_overlap_audit.json"
REPORT_MD = REPO_ROOT / "data" / "interim" / "reports" / "moondb_plantmp_overlap_audit.md"


def _load_pair(scenario: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    moondb = load_validated_claims(FIXTURES / f"moondb_{scenario}.csv", MOONDB_SOURCE_ID)
    plantmp = load_validated_claims(FIXTURES / f"plantmp_{scenario}.csv", PLANTMP_SOURCE_ID)
    return moondb, plantmp


def test_no_overlap() -> None:
    moondb, plantmp = _load_pair("no_overlap")
    report = build_overlap_audit(moondb, plantmp)

    overlap = report["overlap"]
    assert overlap["shared_uniprot_count"] == 0
    assert overlap["shared_uniprot_ids"] == []
    assert overlap["moondb_exclusive_uniprot_ids"] == ["P10001"]
    assert overlap["plantmp_exclusive_uniprot_ids"] == ["Q10001"]
    assert overlap["status_combinations"] == {}
    assert overlap["curated_predicted_disagreements"]["count"] == 0
    assert report["simulated_precedence"]["by_shared_uniprot_id"] == {}


def test_curated_predicted_disagreement() -> None:
    moondb, plantmp = _load_pair("disagreement")
    report = build_overlap_audit(moondb, plantmp)

    disagreements = report["overlap"]["curated_predicted_disagreements"]
    assert disagreements["count"] == 2
    assert disagreements["uniprot_ids"] == ["P10002", "P10003"]
    assert disagreements["details"] == [
        {
            "uniprot_id": "P10002",
            MOONDB_SOURCE_ID: ["curated"],
            PLANTMP_SOURCE_ID: ["predicted"],
        },
        {
            "uniprot_id": "P10003",
            MOONDB_SOURCE_ID: ["predicted"],
            PLANTMP_SOURCE_ID: ["curated"],
        },
    ]
    assert report["overlap"]["status_combinations"] == {
        "SRC_MOONDB=curated|SRC_PLANTMP=curated": 1,
        "SRC_MOONDB=curated|SRC_PLANTMP=predicted": 1,
        "SRC_MOONDB=predicted|SRC_PLANTMP=curated": 1,
    }


def test_likely_plus_stronger_claim() -> None:
    moondb, plantmp = _load_pair("likely_plus_stronger")
    report = build_overlap_audit(moondb, plantmp)

    simulated = report["simulated_precedence"]["by_shared_uniprot_id"]
    assert simulated == {"P10005": "predicted", "P10006": "curated"}
    assert report["excluded_likely"]["count_by_source"] == {
        MOONDB_SOURCE_ID: 0,
        PLANTMP_SOURCE_ID: 2,
    }
    assert report["excluded_likely"]["uniprot_ids_by_source"][PLANTMP_SOURCE_ID] == [
        "P10005",
        "P10006",
    ]
    assert report["excluded_likely"]["shared_uniprot_ids"] == ["P10005", "P10006"]
    # excluded_likely against a stronger claim is not a curated/predicted disagreement
    assert report["overlap"]["curated_predicted_disagreements"]["count"] == 0


def test_duplicates_in_one_source() -> None:
    moondb, plantmp = _load_pair("duplicates")
    report = build_overlap_audit(moondb, plantmp)

    moondb_summary = report["per_source"][MOONDB_SOURCE_ID]
    assert moondb_summary["claim_count"] == 2
    assert moondb_summary["unique_uniprot_count"] == 1
    assert moondb_summary["duplicate_claim_count"] == 1
    assert moondb_summary["uniprot_ids_with_duplicate_claims"] == ["P10007"]
    assert report["per_source"][PLANTMP_SOURCE_ID]["duplicate_claim_count"] == 0
    # Both duplicate claims are preserved; the simulation takes the stronger one.
    assert report["simulated_precedence"]["counts_by_simulated_effective_status"] == {
        "curated": 2
    }


def test_blank_uniprot_id() -> None:
    moondb, plantmp = _load_pair("blank_id")
    report = build_overlap_audit(moondb, plantmp)

    missing = report["missing_or_blank_uniprot"]
    assert missing["claim_count_by_source"] == {MOONDB_SOURCE_ID: 1, PLANTMP_SOURCE_ID: 0}
    blank_claim_ids = [
        claim["claim_id"] for claim in moondb if not claim["uniprot_id"]
    ]
    assert missing["claim_ids_by_source"][MOONDB_SOURCE_ID] == blank_claim_ids
    assert missing["claim_ids_by_source"][PLANTMP_SOURCE_ID] == []
    # The blank claim is excluded from overlap keys and unique-ID counts.
    assert report["per_source"][MOONDB_SOURCE_ID]["unique_uniprot_count"] == 1
    assert report["overlap"]["moondb_exclusive_uniprot_ids"] == ["P10008"]


def test_simulated_effective_status_precedence() -> None:
    assert simulated_effective_status(["curated"]) == "curated"
    assert simulated_effective_status(["predicted", "curated"]) == "curated"
    assert simulated_effective_status(["excluded_likely", "predicted"]) == "predicted"
    assert simulated_effective_status(["unresolved", "excluded_likely"]) == "excluded_likely"
    assert simulated_effective_status(["unresolved"]) == "unresolved"


def test_invalid_claim_fails_contract_validation(tmp_path: Path) -> None:
    moondb, _ = _load_pair("no_overlap")
    bad_claim = dict(moondb[0])
    bad_claim["operational_status"] = "nmf"
    bad_path = tmp_path / "invalid_claims.csv"
    write_claims_csv([bad_claim], bad_path)

    with pytest.raises(RecordValidationError):
        load_validated_claims(bad_path, MOONDB_SOURCE_ID)


def test_wrong_source_id_is_rejected(tmp_path: Path) -> None:
    moondb, _ = _load_pair("no_overlap")
    wrong_source_path = tmp_path / "wrong_source.csv"
    write_claims_csv(moondb, wrong_source_path)

    with pytest.raises(ValueError):
        load_validated_claims(wrong_source_path, PLANTMP_SOURCE_ID)


def _assert_no_effective_status_key(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            assert key != "effective_status"
            _assert_no_effective_status_key(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_effective_status_key(item)


def test_no_effective_status_field_is_written() -> None:
    moondb, plantmp = _load_pair("disagreement")
    report = build_overlap_audit(moondb, plantmp)

    _assert_no_effective_status_key(report)
    assert SIMULATED_STATUS_FIELD == "simulated_effective_status"


def test_markdown_rendering_is_deterministic_and_labeled() -> None:
    moondb, plantmp = _load_pair("disagreement")
    report = build_overlap_audit(moondb, plantmp)

    first = render_overlap_audit_markdown(report)
    assert first == render_overlap_audit_markdown(report)
    assert CONTRACT_ID in first
    assert SIMULATED_STATUS_FIELD in first
    assert "P10002" in first


def test_real_inputs_audit_matches_committed_report() -> None:
    moondb = load_validated_claims(MOONDB_CLAIMS, MOONDB_SOURCE_ID)
    plantmp = load_validated_claims(PLANTMP_CLAIMS, PLANTMP_SOURCE_ID)
    report = build_overlap_audit(moondb, plantmp)

    assert report["contract_id"] == CONTRACT_ID
    assert report["per_source"][MOONDB_SOURCE_ID]["claim_count"] == 351
    assert report["per_source"][MOONDB_SOURCE_ID]["unique_uniprot_count"] == 351
    assert report["per_source"][MOONDB_SOURCE_ID]["duplicate_claim_count"] == 0
    assert report["per_source"][PLANTMP_SOURCE_ID]["claim_count"] == 112
    assert report["per_source"][PLANTMP_SOURCE_ID]["unique_uniprot_count"] == 110
    assert report["per_source"][PLANTMP_SOURCE_ID]["duplicate_claim_count"] == 2
    assert report["per_source"][PLANTMP_SOURCE_ID]["uniprot_ids_with_duplicate_claims"] == [
        "F4I9D5",
        "Q8VYA3",
    ]
    overlap = report["overlap"]
    assert overlap["shared_uniprot_count"] == 0
    assert overlap["moondb_exclusive_uniprot_count"] == 351
    assert overlap["plantmp_exclusive_uniprot_count"] == 110
    assert overlap["status_combinations"] == {}
    assert overlap["curated_predicted_disagreements"]["count"] == 0
    assert report["excluded_likely"]["count_by_source"] == {MOONDB_SOURCE_ID: 0, PLANTMP_SOURCE_ID: 12}
    assert report["missing_or_blank_uniprot"]["claim_count_by_source"] == {
        MOONDB_SOURCE_ID: 0,
        PLANTMP_SOURCE_ID: 0,
    }
    simulated = report["simulated_precedence"]
    assert simulated["unique_uniprot_count"] == 461
    assert simulated["counts_by_simulated_effective_status"] == {
        "curated": 124,
        "excluded_likely": 11,
        "predicted": 326,
    }

    committed = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    assert committed["contract_id"] == CONTRACT_ID
    assert committed["inputs"]["moondb_claims"]["sha256"] == sha256_file(MOONDB_CLAIMS)
    assert committed["inputs"]["plantmp_claims"]["sha256"] == sha256_file(PLANTMP_CLAIMS)
    for section in (
        "per_source",
        "overlap",
        "excluded_likely",
        "missing_or_blank_uniprot",
        "simulated_precedence",
    ):
        assert committed[section] == report[section]


def test_audit_script_reproduces_committed_report(tmp_path: Path) -> None:
    outputs: list[Path] = []
    for run in ("run1", "run2"):
        run_dir = tmp_path / run
        result = subprocess.run(
            [
                sys.executable,
                "scripts/audit_moondb_plantmp_overlap.py",
                "--output-dir",
                str(run_dir),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr
        outputs.append(run_dir)

    for filename in ("moondb_plantmp_overlap_audit.json", "moondb_plantmp_overlap_audit.md"):
        first = (outputs[0] / filename).read_text(encoding="utf-8")
        second = (outputs[1] / filename).read_text(encoding="utf-8")
        committed = (REPORT_JSON.parent / filename).read_text(encoding="utf-8")
        assert first == second
        assert first == committed
