from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from mfp_bibliography.moonprot_parser import (
    CONTRACT_ID,
    LABEL_MOONPROT_ID,
    LABEL_NAMES,
    LABEL_UNIPROT_ID,
    PLANNED_MPID_RANGE,
    MOONPROT_URL_PATTERN,
    MoonProtDuplicateLabelError,
    MoonProtKnownAbsentError,
    MoonProtMalformedHtmlError,
    MoonProtMissingMpidError,
    MoonProtMpidConflictError,
    MoonProtParseError,
    MoonProtRecord,
    parse_moonprot_fixture,
    parse_moonprot_html,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "data" / "fixtures" / "moonprot"


def test_parser_contract_metadata() -> None:
    assert CONTRACT_ID == "MFPB_0_11_MOONPROT_OFFLINE_PARSER"
    assert MOONPROT_URL_PATTERN == "http://www.moonlightingproteins.org/protein_detail/?mpid={id}"
    assert PLANNED_MPID_RANGE == (1, 706)


def test_valid_record() -> None:
    record = parse_moonprot_fixture(FIXTURES / "mpid_1_valid.html", expected_mpid=1)

    assert isinstance(record, MoonProtRecord)
    assert record.moonprot_id == "1"
    assert record.uniprot_id == "P12345"
    assert record.protein_name == "Cytochrome c"
    assert record.missing_fields == ()
    assert record.field_text == {
        LABEL_MOONPROT_ID: "1",
        LABEL_UNIPROT_ID: "P12345",
        LABEL_NAMES: "Cytochrome c",
    }


def test_reordered_rows_are_parsed_by_label_not_position() -> None:
    record = parse_moonprot_fixture(FIXTURES / "mpid_2_reordered.html", expected_mpid=2)

    assert record.moonprot_id == "2"
    assert record.uniprot_id == "P60174"
    assert record.protein_name == "Hexokinase-1"
    assert record.missing_fields == ()


def test_missing_uniprot_id_is_reported_not_fatal() -> None:
    record = parse_moonprot_fixture(FIXTURES / "mpid_3_missing_uniprot.html")

    assert record.moonprot_id == "3"
    assert record.uniprot_id is None
    assert record.protein_name == "Triosephosphate isomerase"
    assert record.missing_fields == ("uniprot_id",)
    assert record.field_text[LABEL_UNIPROT_ID] == ""


def test_missing_name_is_reported_not_fatal() -> None:
    record = parse_moonprot_fixture(FIXTURES / "mpid_4_missing_name.html")

    assert record.moonprot_id == "4"
    assert record.uniprot_id == "P07327"
    assert record.protein_name is None
    assert record.missing_fields == ("protein_name",)
    assert record.field_text[LABEL_NAMES] == ""


def test_missing_moonprot_id_raises_typed_error() -> None:
    with pytest.raises(MoonProtMissingMpidError) as excinfo:
        parse_moonprot_fixture(FIXTURES / "mpid_5_missing_moonprot_id.html")

    assert excinfo.value.label_present is False
    assert isinstance(excinfo.value, MoonProtParseError)


def test_duplicate_labels_raise_typed_error() -> None:
    with pytest.raises(MoonProtDuplicateLabelError) as excinfo:
        parse_moonprot_fixture(FIXTURES / "mpid_6_duplicate_label.html")

    assert excinfo.value.duplicates == {LABEL_UNIPROT_ID: ["P04075", "P04075-2"]}
    assert isinstance(excinfo.value, MoonProtParseError)


def test_malformed_non_table_html_raises_typed_error() -> None:
    with pytest.raises(MoonProtMalformedHtmlError) as excinfo:
        parse_moonprot_fixture(FIXTURES / "mpid_7_malformed.html")

    assert excinfo.value.table_found is False
    assert excinfo.value.row_count == 0
    assert isinstance(excinfo.value, MoonProtParseError)

    with pytest.raises(MoonProtMalformedHtmlError) as empty_excinfo:
        parse_moonprot_html("<html><body><table></table></body></html>")
    assert empty_excinfo.value.table_found is True
    assert empty_excinfo.value.row_count == 0


def test_whitespace_and_entities_are_trimmed_and_decoded() -> None:
    record = parse_moonprot_fixture(FIXTURES / "mpid_8_whitespace_entities.html")

    assert record.moonprot_id == "8"
    assert record.uniprot_id == "P21397\xa0(human)"
    assert record.protein_name == "Aconitase\xa0& IPR\u2019s\n        (cytosolic)"
    assert record.missing_fields == ()


def test_conflicting_mpid_raises_typed_error() -> None:
    with pytest.raises(MoonProtMpidConflictError) as excinfo:
        parse_moonprot_fixture(FIXTURES / "mpid_9_conflicting.html", expected_mpid=42)

    assert excinfo.value.parsed_mpid == "9"
    assert excinfo.value.expected_mpid == "42"
    assert isinstance(excinfo.value, MoonProtParseError)

    # Matching expectation parses cleanly.
    record = parse_moonprot_fixture(FIXTURES / "mpid_9_conflicting.html", expected_mpid="9")
    assert record.moonprot_id == "9"


def test_parser_never_assigns_policy_status_or_claims() -> None:
    record = parse_moonprot_fixture(FIXTURES / "mpid_1_valid.html")

    assert record.to_dict().keys() == {
        "moonprot_id",
        "uniprot_id",
        "protein_name",
        "missing_fields",
        "field_text",
    }


def _parse_json_stream(text: str) -> list[dict]:
    decoder = json.JSONDecoder()
    objects: list[dict] = []
    position = 0
    while True:
        start = text.find("{", position)
        if start == -1:
            return objects
        obj, end = decoder.raw_decode(text, start)
        objects.append(obj)
        position = end


def test_fixture_cli_reports_records_and_typed_errors() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/parse_moonprot_fixture.py",
            "--expected-mpid",
            "1",
            str(FIXTURES / "mpid_1_valid.html"),
            str(FIXTURES / "mpid_6_duplicate_label.html"),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 1, result.stderr
    objects = _parse_json_stream(result.stdout)
    assert len(objects) == 2
    assert objects[0]["ok"] is True
    assert objects[0]["record"]["moonprot_id"] == "1"
    assert objects[1]["ok"] is False
    assert objects[1]["error_type"] == "MoonProtDuplicateLabelError"


def test_fixture_cli_is_reproducible() -> None:
    fixture = FIXTURES / "mpid_2_reordered.html"
    outputs = []
    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/parse_moonprot_fixture.py",
                "--expected-mpid",
                "2",
                str(fixture),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr
        outputs.append(result.stdout)
    assert outputs[0] == outputs[1]
    parsed = json.loads(outputs[0])
    assert parsed["contract_id"] == CONTRACT_ID
    assert parsed["ok"] is True
    assert parsed["record"]["moonprot_id"] == "2"


def test_known_absent_marker_no_entry_found() -> None:
    html = "<html><body><p>No entry found for MoonProt ID 103</p></body></html>"
    with pytest.raises(MoonProtKnownAbsentError) as excinfo:
        parse_moonprot_html(html, expected_mpid=103)
    assert excinfo.value.absent_marker == "no entry found"
    assert isinstance(excinfo.value, MoonProtParseError)


def test_known_absent_marker_no_such_protein() -> None:
    html = "<html><body><h1>No such protein</h1></body></html>"
    with pytest.raises(MoonProtKnownAbsentError) as excinfo:
        parse_moonprot_html(html, expected_mpid=999)
    assert excinfo.value.absent_marker == "no such protein"


def test_known_absent_marker_protein_not_found() -> None:
    html = "<html><body>Protein not found</body></html>"
    with pytest.raises(MoonProtKnownAbsentError) as excinfo:
        parse_moonprot_html(html, expected_mpid=1000)
    assert excinfo.value.absent_marker == "protein not found"


def test_known_absent_marker_this_record_does_not_exist() -> None:
    html = "<html><body>This record does not exist</body></html>"
    with pytest.raises(MoonProtKnownAbsentError) as excinfo:
        parse_moonprot_html(html, expected_mpid=1001)
    assert excinfo.value.absent_marker == "this record does not exist"


def test_known_absent_marker_case_insensitive() -> None:
    html = "<html><body><p>NO ENTRY FOUND for MoonProt ID 103</p></body></html>"
    with pytest.raises(MoonProtKnownAbsentError) as excinfo:
        parse_moonprot_html(html, expected_mpid=103)
    assert excinfo.value.absent_marker == "no entry found"


def test_table_less_200_without_absent_marker_still_raises_malformed() -> None:
    html = "<html><body><p>Some other error</p></body></html>"
    with pytest.raises(MoonProtMalformedHtmlError) as excinfo:
        parse_moonprot_html(html)
    assert excinfo.value.table_found is False
