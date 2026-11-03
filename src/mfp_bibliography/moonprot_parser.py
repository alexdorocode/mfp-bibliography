"""Pure offline parser for local MoonProt HTML fixtures (MFPB_0_11_MOONPROT_OFFLINE_PARSER).

Extracts `MoonProt ID`, `UniProt ID`, and `Name(s)` from local HTML fixture
files by locating fields through their visible labels, never by fixed table
row positions. This module contains no network, HTTP client, scraper, retry,
or acquisition code and must never contact MoonProt or any external URL.

The parser assigns no policy status and creates no source claims. Missing
`uniprot_id`/`protein_name` are reported explicitly on the record; a missing
MoonProt ID, duplicated labels, malformed HTML, and an MPID conflict raise
typed parse errors.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

CONTRACT_ID = "MFPB_0_11_MOONPROT_OFFLINE_PARSER"
MOONPROT_SOURCE_ID = "SRC_MOONPROT"
MOONPROT_URL_PATTERN = "http://www.moonlightingproteins.org/protein_detail/?mpid={id}"
PLANNED_MPID_RANGE = (1, 706)

LABEL_MOONPROT_ID = "MoonProt ID"
LABEL_UNIPROT_ID = "UniProt ID"
LABEL_NAMES = "Name(s)"
TARGET_LABELS = (LABEL_MOONPROT_ID, LABEL_UNIPROT_ID, LABEL_NAMES)

FIELD_UNIPROT_ID = "uniprot_id"
FIELD_PROTEIN_NAME = "protein_name"


class MoonProtParseError(Exception):
    """Base class for typed MoonProt fixture parse errors."""


class MoonProtMalformedHtmlError(MoonProtParseError):
    """The fixture does not contain a parseable label/value table."""

    def __init__(self, message: str, *, table_found: bool, row_count: int) -> None:
        super().__init__(message)
        self.table_found = table_found
        self.row_count = row_count


class MoonProtDuplicateLabelError(MoonProtParseError):
    """A target label appears more than once in the fixture."""

    def __init__(self, duplicates: dict[str, list[str]]) -> None:
        rendered = ", ".join(
            f"{label!r} -> {[value for value in values]}"
            for label, values in sorted(duplicates.items())
        )
        super().__init__(f"Duplicate target labels found: {rendered}")
        self.duplicates = duplicates


class MoonProtMissingMpidError(MoonProtParseError):
    """The MoonProt ID field is absent or empty."""

    def __init__(self, *, label_present: bool, value: str) -> None:
        if label_present:
            message = f"{LABEL_MOONPROT_ID!r} label present but its value is empty."
        else:
            message = f"{LABEL_MOONPROT_ID!r} label not found in the fixture."
        super().__init__(message)
        self.label_present = label_present
        self.value = value


class MoonProtMpidConflictError(MoonProtParseError):
    """The parsed MoonProt ID conflicts with the expected input ID."""

    def __init__(self, *, parsed_mpid: str, expected_mpid: str) -> None:
        super().__init__(
            f"Parsed MoonProt ID {parsed_mpid!r} conflicts with expected ID {expected_mpid!r}."
        )
        self.parsed_mpid = parsed_mpid
        self.expected_mpid = expected_mpid


class MoonProtKnownAbsentError(MoonProtParseError):
    """The page explicitly indicates the requested MoonProt ID is absent/not found.
    
    Detection is based on:
    1. Exact absence phrases in <title>, <h1>, or <h2> elements; OR
    2. Documented soft-404 template signature from captured MPID 103 response.
    """

    # Absence phrases checked ONLY in title/h1/h2 element text (case-insensitive)
    ABSENT_PHRASES = frozenset({
        "no entry found",
        "entry not found",
        "no such protein",
        "protein not found",
        "page not found",
        "not found",
        "this record does not exist",
        "moonprot id not found",
        "no details available",
    })
    
    # Documented soft-404 template signature from MPID 103 capture:
    # HTML contains <h1>Protein Detail</h1> and <p>No entry found for MoonProt ID
    SOFT_404_SIGNATURE = frozenset({
        "<h1>protein detail</h1>",
        "<p>no entry found for moonprot id",
    })

    def __init__(self, message: str, *, absent_marker: str) -> None:
        super().__init__(message)
        self.absent_marker = absent_marker


@dataclass(frozen=True)
class MoonProtFunctionDetail:
    """Detailed function section parsed from a MoonProt fixture."""

    function_index: int
    description: str | None = None
    references_raw: str | None = None
    pmids: tuple[str, ...] = ()
    ec_number: str | None = None
    cellular_location: str | None = None


@dataclass(frozen=True)
class MoonProtRecord:
    """Structured extraction result from one MoonProt fixture."""

    moonprot_id: str
    uniprot_id: str | None
    protein_name: str | None
    missing_fields: tuple[str, ...] = ()
    field_text: dict[str, str] = field(default_factory=dict)
    raw_go_terms: str | None = None
    functions: tuple[MoonProtFunctionDetail, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "moonprot_id": self.moonprot_id,
            "uniprot_id": self.uniprot_id,
            "protein_name": self.protein_name,
            "missing_fields": list(self.missing_fields),
            "field_text": dict(self.field_text),
        }


def _extract_principal_text(html_text: str) -> str:
    """Extract concatenated text from <title>, <h1>, and <h2> elements.
    
    Returns all text content from these principal elements, joined with spaces,
    in lowercase for case-insensitive matching.
    """
    class PrincipalTextExtractor(HTMLParser):
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.text_parts: list[str] = []
            self._in_target = False
            
        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if tag in ("title", "h1", "h2"):
                self._in_target = True
                
        def handle_endtag(self, tag: str) -> None:
            if tag in ("title", "h1", "h2"):
                self._in_target = False
                
        def handle_data(self, data: str) -> None:
            if self._in_target:
                self.text_parts.append(data)
    
    parser = PrincipalTextExtractor()
    parser.feed(html_text)
    parser.close()
    return " ".join(parser.text_parts).lower()


def _check_soft_404_signature(html_text: str) -> bool:
    """Check for documented soft-404 template signature from MPID 103 capture.
    
    Matches the exact structural signature: presence of both
    <h1>Protein Detail</h1> and <p>No entry found for MoonProt ID in the raw HTML.
    Uses case-insensitive matching on the raw HTML tags.
    """
    lower_html = html_text.lower()
    for sig in MoonProtKnownAbsentError.SOFT_404_SIGNATURE:
        if sig not in lower_html:
            return False
    return True


class _MoonProtTableParser(HTMLParser):
    """Collect label/value rows from every <tr> in the document.

    Cells are <th>/<td> elements; a row with at least two cells becomes a
    candidate (label, value) pair where the label is the first cell and the
    value is the remaining cell text joined with single spaces. Cell text is
    preserved as-is except for minimal end trimming; character references are
    decoded by HTMLParser.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.table_found = False
        self.rows: list[tuple[str, str]] = []
        self._in_cell = False
        self._cell_chunks: list[str] = []
        self._row_cells: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self.table_found = True
        elif tag in ("td", "th"):
            self._in_cell = True
            self._cell_chunks = []

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._in_cell:
            self._row_cells.append("".join(self._cell_chunks).strip())
            self._in_cell = False
        elif tag == "tr":
            if len(self._row_cells) >= 2:
                label = self._row_cells[0]
                value = " ".join(self._row_cells[1:]).strip()
                self.rows.append((label, value))
            self._row_cells = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_chunks.append(data)


def parse_moonprot_html(
    html_text: str, expected_mpid: str | int | None = None
) -> MoonProtRecord:
    """Parse one MoonProt protein-detail HTML page text into a record.

    Fields are located by visible labels; row order is irrelevant. Missing
    `uniprot_id`/`protein_name` are reported through `missing_fields` on the
    returned record. Raises MoonProtMalformedHtmlError, MoonProtDuplicateLabelError,
    MoonProtMissingMpidError, MoonProtMpidConflictError, or MoonProtKnownAbsentError on failure.
    """
    # Check for known absent: first try principal elements (title/h1/h2)
    # Sort phrases by length (longest first) to match most specific first
    principal_text = _extract_principal_text(html_text)
    for phrase in sorted(MoonProtKnownAbsentError.ABSENT_PHRASES, key=len, reverse=True):
        if phrase in principal_text:
            raise MoonProtKnownAbsentError(
                f"Page contains absent phrase in title/h1/h2: {phrase!r}",
                absent_marker=phrase,
            )
    
    # If not found in principal elements, check documented soft-404 signature
    if _check_soft_404_signature(html_text):
        raise MoonProtKnownAbsentError(
            "Page matches documented soft-404 template signature",
            absent_marker="soft_404_template",
        )
    
    parser = _MoonProtTableParser()
    parser.feed(html_text)
    parser.close()

    if not parser.rows:
        raise MoonProtMalformedHtmlError(
            "Fixture contains no table rows to parse.",
            table_found=parser.table_found,
            row_count=len(parser.rows),
        )

    observed: dict[str, list[str]] = {}
    for label, value in parser.rows:
        if label in TARGET_LABELS:
            observed.setdefault(label, []).append(value)

    duplicates = {label: values for label, values in observed.items() if len(values) > 1}
    if duplicates:
        raise MoonProtDuplicateLabelError(duplicates)

    field_text = {label: observed.get(label, [""])[0] for label in TARGET_LABELS}

    if not field_text[LABEL_MOONPROT_ID]:
        raise MoonProtMissingMpidError(
            label_present=LABEL_MOONPROT_ID in observed,
            value=field_text[LABEL_MOONPROT_ID],
        )

    if expected_mpid is not None:
        expected = str(expected_mpid).strip()
        if field_text[LABEL_MOONPROT_ID] != expected:
            raise MoonProtMpidConflictError(
                parsed_mpid=field_text[LABEL_MOONPROT_ID],
                expected_mpid=expected,
            )

    uniprot_id = field_text[LABEL_UNIPROT_ID] or None
    protein_name = field_text[LABEL_NAMES] or None
    missing_fields = tuple(
        name
        for name, value in ((FIELD_UNIPROT_ID, uniprot_id), (FIELD_PROTEIN_NAME, protein_name))
        if value is None
    )

    raw_go_terms: str | None = None
    functions: list[MoonProtFunctionDetail] = []
    current_func: dict[str, Any] | None = None

    for label, value in parser.rows:
        if label == "GO terms":
            raw_go_terms = value.strip() or None
        elif label == "Function description":
            if current_func is not None:
                functions.append(MoonProtFunctionDetail(**current_func))
            current_func = {
                "function_index": len(functions) + 1,
                "description": value.strip() or None,
                "references_raw": None,
                "pmids": (),
                "ec_number": None,
                "cellular_location": None,
            }
        elif current_func is not None:
            if label == "References for function":
                current_func["references_raw"] = value.strip() or None
                pmids = re.findall(r"pubmed/(\d+)|PMID:\s*(\d+)", value, re.IGNORECASE)
                extracted_pmids = tuple(p[0] or p[1] for p in pmids)
                current_func["pmids"] = extracted_pmids
            elif label == "E.C. number":
                current_func["ec_number"] = value.strip() or None
            elif label == "Cellular location of function":
                current_func["cellular_location"] = value.strip() or None

    if current_func is not None:
        functions.append(MoonProtFunctionDetail(**current_func))

    return MoonProtRecord(
        moonprot_id=field_text[LABEL_MOONPROT_ID],
        uniprot_id=uniprot_id,
        protein_name=protein_name,
        missing_fields=missing_fields,
        field_text=field_text,
        raw_go_terms=raw_go_terms,
        functions=tuple(functions),
    )


def parse_moonprot_fixture(
    fixture_path: str | Path, expected_mpid: str | int | None = None
) -> MoonProtRecord:
    """Parse a local MoonProt HTML fixture file (never a URL)."""
    path = Path(fixture_path)
    return parse_moonprot_html(path.read_text(encoding="utf-8"), expected_mpid=expected_mpid)
