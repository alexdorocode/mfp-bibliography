"""Tests for MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0 effective status aggregation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mfp_bibliography.effective_status import (
    CONTRACT_ID,
    PRECEDENCE_ORDER,
    VALID_OPERATIONAL_STATUSES,
    EffectiveStatusRecord,
    SourceClaim,
    aggregate_effective_status,
)

# Load schema
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "data" / "curated" / "effective_status.schema.json"
with open(SCHEMA_PATH, encoding="utf-8") as f:
    SCHEMA = json.load(f)


def make_claim(claim_id: str, source_id: str, uniprot_id: str | None, status: str) -> SourceClaim:
    return SourceClaim(
        claim_id=claim_id,
        source_id=source_id,
        uniprot_id=uniprot_id,
        operational_status=status,
    )


class TestContractMetadata:
    def test_contract_id(self) -> None:
        assert CONTRACT_ID == "MFPB_0_13_EFFECTIVE_STATUS_CONTRACT_V0"

    def test_precedence_order(self) -> None:
        assert PRECEDENCE_ORDER == ("curated", "predicted", "excluded_likely", "unresolved")

    def test_valid_operational_statuses(self) -> None:
        assert VALID_OPERATIONAL_STATUSES == frozenset(PRECEDENCE_ORDER)


class TestOneClaimPerStatus:
    """Test single claim for each operational status."""

    @pytest.mark.parametrize("status", PRECEDENCE_ORDER)
    def test_single_claim_produces_expected_status(self, status: str) -> None:
        claims = [make_claim("c1", "s1", "P12345", status)]
        records = aggregate_effective_status(claims)

        assert len(records) == 1
        record = records[0]
        assert record.uniprot_id == "P12345"
        assert record.effective_status == status
        assert record.source_ids == ("s1",)
        assert record.claim_ids == ("c1",)
        assert record.status_set == (status,)
        assert record.claim_count == 1
        assert record.source_count == 1
        assert record.record_status == "valid"
        assert record.notes is None

        # Check boolean flags
        assert record.has_curated_claim == (status == "curated")
        assert record.has_predicted_claim == (status == "predicted")
        assert record.has_excluded_likely_claim == (status == "excluded_likely")
        assert record.has_unresolved_claim == (status == "unresolved")


class TestMixedCuratedPredicted:
    """Test mixed curated/predicted claims."""

    def test_curated_beats_predicted(self) -> None:
        claims = [
            make_claim("c1", "s1", "P12345", "predicted"),
            make_claim("c2", "s2", "P12345", "curated"),
        ]
        records = aggregate_effective_status(claims)

        assert len(records) == 1
        record = records[0]
        assert record.uniprot_id == "P12345"
        assert record.effective_status == "curated"
        assert record.has_curated_claim is True
        assert record.has_predicted_claim is True
        assert record.claim_count == 2
        assert record.source_count == 2

    def test_predicted_excluded_likely(self) -> None:
        claims = [
            make_claim("c1", "s1", "P12345", "predicted"),
            make_claim("c2", "s2", "P12345", "excluded_likely"),
        ]
        records = aggregate_effective_status(claims)

        assert len(records) == 1
        record = records[0]
        assert record.effective_status == "predicted"
        assert record.has_predicted_claim is True
        assert record.has_excluded_likely_claim is True


class TestUnresolvedOnly:
    def test_single_unresolved(self) -> None:
        claims = [make_claim("c1", "s1", "P12345", "unresolved")]
        records = aggregate_effective_status(claims)

        assert len(records) == 1
        assert records[0].effective_status == "unresolved"


class TestDuplicateClaims:
    def test_duplicates_preserved_in_counts(self) -> None:
        claims = [
            make_claim("c1", "s1", "P12345", "curated"),
            make_claim("c2", "s1", "P12345", "curated"),
        ]
        records = aggregate_effective_status(claims)

        assert len(records) == 1
        record = records[0]
        assert record.claim_count == 2
        assert record.source_count == 1
        assert record.claim_ids == ("c1", "c2")
        assert record.source_ids == ("s1", "s1")


class TestMultipleSources:
    def test_multiple_sources_same_uniprot(self) -> None:
        claims = [
            make_claim("c1", "SRC_MOONDB", "P12345", "curated"),
            make_claim("c2", "SRC_PLANTMP", "P12345", "predicted"),
        ]
        records = aggregate_effective_status(claims)

        assert len(records) == 1
        record = records[0]
        assert record.source_count == 2
        assert set(record.source_ids) == {"SRC_MOONDB", "SRC_PLANTMP"}
        assert record.effective_status == "curated"


class TestBlankUniprot:
    def test_blank_uniprot_produces_excluded_records(self) -> None:
        claims = [
            make_claim("c1", "s1", "", "curated"),
            make_claim("c2", "s2", None, "predicted"),
        ]
        records = aggregate_effective_status(claims)

        assert len(records) == 2
        for record in records:
            assert record.uniprot_id == ""
            assert record.record_status == "excluded"
            assert record.notes == "Blank/missing UniProt ID"

    def test_whitespace_uniprot_produces_excluded_records(self) -> None:
        claims = [make_claim("c1", "s1", "   ", "curated")]
        records = aggregate_effective_status(claims)

        assert len(records) == 1
        assert records[0].record_status == "excluded"


class TestDeterministicOrderIndependent:
    def test_order_independent_aggregation(self) -> None:
        claims1 = [
            make_claim("c1", "s1", "P12345", "predicted"),
            make_claim("c2", "s2", "P12345", "curated"),
        ]
        claims2 = [
            make_claim("c2", "s2", "P12345", "curated"),
            make_claim("c1", "s1", "P12345", "predicted"),
        ]

        records1 = aggregate_effective_status(claims1)
        records2 = aggregate_effective_status(claims2)

        assert len(records1) == len(records2) == 1
        # Compare to_dict outputs
        assert records1[0].to_dict() == records2[0].to_dict()

    def test_status_set_sorted_by_precedence(self) -> None:
        claims = [
            make_claim("c1", "s1", "P12345", "unresolved"),
            make_claim("c2", "s2", "P12345", "excluded_likely"),
            make_claim("c3", "s3", "P12345", "predicted"),
            make_claim("c4", "s4", "P12345", "curated"),
        ]
        records = aggregate_effective_status(claims)

        assert len(records) == 1
        # status_set should be sorted by precedence (highest first)
        assert records[0].status_set == ("curated", "predicted", "excluded_likely", "unresolved")


class TestValidation:
    def test_invalid_operational_status_raises(self) -> None:
        claims = [make_claim("c1", "s1", "P12345", "invalid_status")]
        with pytest.raises(ValueError, match="invalid operational_status"):
            aggregate_effective_status(claims)

    def test_empty_claim_id_raises(self) -> None:
        claims = [SourceClaim(claim_id="", source_id="s1", uniprot_id="P12345", operational_status="curated")]
        with pytest.raises(ValueError, match="empty claim_id"):
            aggregate_effective_status(claims)

    def test_empty_source_id_raises(self) -> None:
        claims = [SourceClaim(claim_id="c1", source_id="", uniprot_id="P12345", operational_status="curated")]
        with pytest.raises(ValueError, match="empty source_id"):
            aggregate_effective_status(claims)


class TestSchemaValidation:
    def test_record_matches_schema(self) -> None:
        import jsonschema

        claims = [
            make_claim("c1", "s1", "P12345", "curated"),
            make_claim("c2", "s2", "P12345", "predicted"),
        ]
        records = aggregate_effective_status(claims)
        record_dict = records[0].to_dict()

        jsonschema.validate(instance=record_dict, schema=SCHEMA)

    def test_all_status_records_match_schema(self) -> None:
        import jsonschema

        for status in PRECEDENCE_ORDER:
            claims = [make_claim("c1", "s1", "P12345", status)]
            records = aggregate_effective_status(claims)
            jsonschema.validate(instance=records[0].to_dict(), schema=SCHEMA)

    def test_excluded_record_matches_schema(self) -> None:
        import jsonschema

        claims = [make_claim("c1", "s1", "", "curated")]
        records = aggregate_effective_status(claims)
        jsonschema.validate(instance=records[0].to_dict(), schema=SCHEMA)


class TestRecordToDict:
    def test_to_dict_contains_all_fields(self) -> None:
        claims = [make_claim("c1", "s1", "P12345", "curated")]
        records = aggregate_effective_status(claims)
        record_dict = records[0].to_dict()

        expected_keys = {
            "uniprot_id",
            "effective_status",
            "source_ids",
            "claim_ids",
            "status_set",
            "has_curated_claim",
            "has_predicted_claim",
            "has_excluded_likely_claim",
            "has_unresolved_claim",
            "claim_count",
            "source_count",
            "aggregation_policy_id",
            "transformation_id",
            "record_status",
            "notes",
        }
        assert set(record_dict.keys()) == expected_keys


class TestEmptyInput:
    def test_empty_input_produces_empty_list(self) -> None:
        records = aggregate_effective_status([])
        assert records == []


class TestAggregationPolicyId:
    def test_custom_aggregation_policy_id(self) -> None:
        claims = [make_claim("c1", "s1", "P12345", "curated")]
        records = aggregate_effective_status(
            claims, aggregation_policy_id="custom_policy"
        )
        assert records[0].aggregation_policy_id == "custom_policy"

    def test_default_aggregation_policy_id(self) -> None:
        claims = [make_claim("c1", "s1", "P12345", "curated")]
        records = aggregate_effective_status(claims)
        assert records[0].aggregation_policy_id == CONTRACT_ID


class TestTransformationId:
    def test_custom_transformation_id(self) -> None:
        claims = [make_claim("c1", "s1", "P12345", "curated")]
        records = aggregate_effective_status(
            claims, transformation_id="custom_transform"
        )
        assert records[0].transformation_id == "custom_transform"
