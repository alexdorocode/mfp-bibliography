"""Unit tests for functional normalization module."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from mfp_bibliography.functional_normalization import (
    ProteinFacetsRecord,
    extract_cellular_components_from_text,
    format_go_id,
    join_terms,
    load_obo_aspects,
    normalize_moondb_record,
    normalize_moonprot_record,
    normalize_multitaskprotdb_ii_record,
    normalize_plantmp_record,
    parse_go_list,
    resolve_mono_source_record,
)
from mfp_bibliography.moonprot_parser import MoonProtFunctionDetail, MoonProtRecord


def test_format_go_id() -> None:
    assert format_go_id("GO:0005634") == "GO:0005634"
    assert format_go_id("5634") == "GO:0005634"
    assert format_go_id("0005634") == "GO:0005634"
    assert format_go_id("invalid") is None


def test_parse_go_list() -> None:
    text = "Terms include GO:0005634, 0005737 and also GO:0005634 repeated."
    terms = parse_go_list(text)
    assert terms == ["GO:0005634", "GO:0005737"]
    assert parse_go_list("") == []
    assert parse_go_list(None) == []


def test_join_terms() -> None:
    assert join_terms(["GO:0002", "GO:0001", "GO:0001"]) == "GO:0001; GO:0002"
    assert join_terms([]) == ""


def test_extract_cellular_components_from_text() -> None:
    text1 = "Condition: present in plasma membrane or cytoplasm"
    cc1 = extract_cellular_components_from_text(text1)
    assert "GO:0005886" in cc1  # plasma membrane
    assert "GO:0005737" in cc1  # cytoplasm

    text2 = "Condition: nuclear localisation upon stress"
    cc2 = extract_cellular_components_from_text(text2)
    assert "GO:0005634" in cc2  # nucleus

    text3 = "Condition: found in mitochondrial matrix"
    cc3 = extract_cellular_components_from_text(text3)
    assert "GO:0005739" in cc3  # mitochondrion

    text4 = "Condition: extracellular secretion in serum"
    cc4 = extract_cellular_components_from_text(text4)
    assert "GO:0005576" in cc4  # extracellular region

    assert extract_cellular_components_from_text("") == []
    assert extract_cellular_components_from_text(None) == []


def test_normalize_plantmp_record() -> None:
    row = {
        "order": "1",
        "uniport_id": "P12345",
        "canonical_function_bp": "photosynthesis",
        "go_canonical_bp": "GO:0015979",
        "go_canonical_mf": "GO:0016168",
        "moonlighting_function_bp": "transcription regulation",
        "go_moonlighting_bp": "GO:0006355",
        "go_moonlighting_mf": "GO:0003677",
        "pubmed_id": "12345678",
    }
    rec = normalize_plantmp_record(row)
    assert rec.canonical_uniprot_accession == "P12345"
    assert rec.source_name == "SRC_PLANTMP"
    assert rec.bp1 == "GO:0015979"
    assert rec.mf1 == "GO:0016168"
    assert rec.bp2 == "GO:0006355"
    assert rec.mf2 == "GO:0003677"
    assert rec.pmid2 == "12345678"
    assert rec.facet_status == "resolved"


def test_normalize_multitaskprotdb_ii_record() -> None:
    row = {
        "source_record_id": "row_1",
        "UniProt": "Q9Y265",
        "GO": "GO:0005840; C:ribosome; IEA.\nGO:0003735; F:structural constituent of ribosome; IEA.\nGO:0006412; P:translation; IEA.",
        "GO_Moon": "GO:0006355 biological_process\nGO:0003677 molecular_function",
        "Reference": "24681012",
        "Canonical_Function": "Ribosomal subunit protein",
        "Moonlighting_function": "Transcription regulator",
    }
    rec = normalize_multitaskprotdb_ii_record(row)
    assert rec.canonical_uniprot_accession == "Q9Y265"
    assert rec.source_name == "SRC_MULTITASKPROTDB_II"
    assert "GO:0006412" in rec.bp1
    assert "GO:0003735" in rec.mf1
    assert "GO:0005840" in rec.cc1
    assert "GO:0006355" in rec.bp2
    assert "GO:0003677" in rec.mf2
    assert rec.pmid2 == "24681012"
    assert rec.facet_status == "resolved"


def test_normalize_moonprot_record() -> None:
    f1 = MoonProtFunctionDetail(
        function_index=1,
        description="Glyceraldehyde-3-phosphate dehydrogenase",
        ec_number="1.2.1.12",
        pmids=("11111111",),
    )
    f2 = MoonProtFunctionDetail(
        function_index=2,
        description="Uracil DNA glycosylase",
        ec_number="3.2.2.27",
        pmids=("22222222",),
    )
    record = MoonProtRecord(
        moonprot_id="MP00001",
        uniprot_id="P04406",
        protein_name="GAPDH",
        raw_go_terms="GO:0006096",
        functions=(f1, f2),
    )
    ec2go = {
        "1.2.1.12": "GO:0004365",
        "3.2.2.27": "GO:0003906",
    }
    rec = normalize_moonprot_record(record, ec2go=ec2go)
    assert rec.canonical_uniprot_accession == "P04406"
    assert rec.source_name == "SRC_MOONPROT"
    assert rec.mf1 == "GO:0004365"
    assert rec.mf2 == "GO:0003906"
    assert rec.pmid1 == "11111111"
    assert rec.pmid2 == "22222222"
    assert "ec2go_mapped" in rec.resolution_sources
    assert rec.facet_status == "resolved"


def test_normalize_moondb_record_emf_dynamic_routing() -> None:
    # Test that terms are dynamically classified according to aspect lookup, not assumed to be BP
    emf_data = {
        "P00001": {
            "terms_1": {"GO:0001", "GO:0002"},  # GO:0001=BP, GO:0002=MF
            "terms_2": {"GO:0003", "GO:0004"},  # GO:0003=BP, GO:0004=CC
            "names_1": {"Process 1", "Activity 2"},
            "names_2": {"Process 3", "Component 4"},
        }
    }
    obo_aspects = {
        "GO:0001": "BP",
        "GO:0002": "MF",
        "GO:0003": "BP",
        "GO:0004": "CC",
    }
    rec = normalize_moondb_record(
        accession="P00001",
        source_record_id="moondb_P00001",
        emf_data=emf_data,
        obo_aspects=obo_aspects,
    )
    assert rec.canonical_uniprot_accession == "P00001"
    assert rec.source_name == "SRC_MOONDB"
    assert rec.bp1 == "GO:0001"
    assert rec.mf1 == "GO:0002"
    assert rec.bp2 == "GO:0003"
    assert rec.cc2 == "GO:0004"
    assert "Activity 2" in rec.func1_desc
    assert "Component 4" in rec.func2_desc
    assert rec.facet_status == "resolved"


def test_normalize_moondb_record_curated_with_conditions() -> None:
    manual_data = {
        "P00002": {
            "f1": "Canonical enzyme function. Condition: present in cytoplasm.",
            "f2": "Moonlighting transcription factor. Condition: nuclear localisation upon activation.",
            "pubs": ["12345678"],
            "cc1_terms": ["GO:0005737"],
            "cc2_terms": ["GO:0005634"],
            "species": "Homo sapiens",
        }
    }
    rec = normalize_moondb_record(
        accession="P00002",
        source_record_id="moondb_P00002",
        manual_data=manual_data,
    )
    assert rec.canonical_uniprot_accession == "P00002"
    assert rec.cc1 == "GO:0005737"
    assert rec.cc2 == "GO:0005634"
    assert rec.pmid2 == "12345678"
    assert rec.facet_status == "resolved"


def test_resolve_mono_source_record() -> None:
    rec = resolve_mono_source_record(
        source_name="SRC_MULTIFACETEDPROTDB",
        source_record_id="mono_001",
        accession="P99999",
    )
    assert rec.canonical_uniprot_accession == "P99999"
    assert rec.facet_status == "unassigned_mono_source"
    assert rec.bp1 == ""
    assert rec.bp2 == ""
    assert "unassigned per repository policy" in rec.notes
