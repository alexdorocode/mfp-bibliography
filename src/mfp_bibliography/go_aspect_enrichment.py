"""GO Aspect Metadata Enrichment Engine.

Task PIL-04.1A: Minimum GO-aspect metadata enrichment for source annotations.
Maps standardized Gene Ontology namespaces (BP, CC, MF) from an immutable
pinned ontology snapshot while strictly preserving source-native provenance.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from jsonschema import Draft202012Validator

GO_ID_REGEX = re.compile(r"^GO:[0-9]{7}$")

NAMESPACE_TO_ASPECT = {
    "biological_process": "BP",
    "cellular_component": "CC",
    "molecular_function": "MF",
}

DERIVED_COLUMNS = [
    "annotation_id",
    "protein_id",
    "source_id",
    "source_record_id",
    "claim_id",
    "annotation_index",
    "raw_annotation_text",
    "source_go_id",
    "source_declared_aspect",
    "resolved_go_id",
    "derived_aspect",
    "mapping_status",
    "replaced_by_go_id",
    "consider_go_ids",
    "term_name_resolved",
    "ontology_version",
    "ontology_sha256",
    "notes",
]


@dataclass(frozen=True)
class TermRecord:
    """Represents a parsed Term record from an OBO ontology."""

    id: str
    name: Optional[str] = None
    namespace: Optional[str] = None
    is_obsolete: bool = False
    alt_ids: Tuple[str, ...] = ()
    replaced_by: Optional[str] = None
    consider: Tuple[str, ...] = ()


@dataclass(frozen=True)
class OntologySnapshot:
    """Immutable parsed ontology snapshot with cryptographic verification."""

    terms: Dict[str, TermRecord]
    alt_map: Dict[str, str]
    format_version: str
    data_version: str
    source_path: str
    sha256_digest: str

    def get_term(self, go_id: str) -> Optional[TermRecord]:
        """Lookup primary term by GO ID."""
        return self.terms.get(go_id)

    def resolve_alt_id(self, alt_id: str) -> Optional[str]:
        """Resolve alternate identifier to canonical primary ID."""
        return self.alt_map.get(alt_id)


def compute_file_sha256(path: Union[str, Path]) -> str:
    """Compute cryptographic SHA-256 digest of a local file."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def parse_obo_ontology(
    obo_path: Union[str, Path],
    expected_sha256: Optional[str] = None,
) -> OntologySnapshot:
    """Parse an OBO 1.2 file into an OntologySnapshot with digest verification."""
    path = Path(obo_path)
    if not path.is_file():
        raise FileNotFoundError(f"Ontology file does not exist: {path}")

    actual_sha256 = compute_file_sha256(path)
    if expected_sha256 is not None and actual_sha256.lower() != expected_sha256.lower():
        raise ValueError(
            f"Ontology digest mismatch for {path}: expected {expected_sha256}, got {actual_sha256}"
        )

    terms: Dict[str, TermRecord] = {}
    alt_map: Dict[str, str] = {}
    format_version = "1.2"
    data_version = "unknown"

    current_term_id: Optional[str] = None
    current_name: Optional[str] = None
    current_namespace: Optional[str] = None
    current_is_obsolete = False
    current_alt_ids: List[str] = []
    current_replaced_by: Optional[str] = None
    current_consider: List[str] = []
    in_term = False

    def _flush_current_term() -> None:
        nonlocal current_term_id, current_name, current_namespace, current_is_obsolete
        nonlocal current_alt_ids, current_replaced_by, current_consider
        if current_term_id is not None:
            rec = TermRecord(
                id=current_term_id,
                name=current_name,
                namespace=current_namespace,
                is_obsolete=current_is_obsolete,
                alt_ids=tuple(current_alt_ids),
                replaced_by=current_replaced_by,
                consider=tuple(current_consider),
            )
            terms[current_term_id] = rec
            for aid in current_alt_ids:
                alt_map[aid] = current_term_id
        current_term_id = None
        current_name = None
        current_namespace = None
        current_is_obsolete = False
        current_alt_ids = []
        current_replaced_by = None
        current_consider = []

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line == "[Term]":
                if in_term:
                    _flush_current_term()
                in_term = True
                continue
            elif line.startswith("[") and line.endswith("]"):
                if in_term:
                    _flush_current_term()
                in_term = False
                continue

            if not in_term:
                if line.startswith("format-version:"):
                    format_version = line.split(":", 1)[1].strip()
                elif line.startswith("data-version:"):
                    data_version = line.split(":", 1)[1].strip()
            else:
                if line.startswith("id:"):
                    current_term_id = line.split(":", 1)[1].strip()
                elif line.startswith("name:"):
                    current_name = line.split(":", 1)[1].strip()
                elif line.startswith("namespace:"):
                    current_namespace = line.split(":", 1)[1].strip()
                elif line == "is_obsolete: true":
                    current_is_obsolete = True
                elif line.startswith("alt_id:"):
                    current_alt_ids.append(line.split(":", 1)[1].strip())
                elif line.startswith("replaced_by:"):
                    current_replaced_by = line.split(":", 1)[1].strip()
                elif line.startswith("consider:"):
                    current_consider.append(line.split(":", 1)[1].strip())

        if in_term:
            _flush_current_term()

    return OntologySnapshot(
        terms=terms,
        alt_map=alt_map,
        format_version=format_version,
        data_version=data_version,
        source_path=str(path.resolve()),
        sha256_digest=actual_sha256,
    )


def enrich_annotation_row(
    row: Dict[str, Any],
    ontology: OntologySnapshot,
) -> Dict[str, Any]:
    """Map a single source annotation row against the ontology snapshot.

    Enforces conservative mapping semantics:
    - Retains original source annotation identity, go_id, and declared aspect.
    - Resolves active primary identifiers to namespace/aspect.
    - Resolves secondary alt_ids to primary identifier without mutating source_go_id.
    - Records obsolescence with replaced_by and consider metadata; does NOT substitute
      replacement identifiers or treat obsolete terms as active.
    - Identifies malformed and unknown terms explicitly.
    - Preserves both source and ontology aspects upon conflict, flagging the mismatch.
    """
    annotation_id = str(row["annotation_id"]).strip()
    protein_id = str(row["protein_id"]).strip()
    source_id = str(row["source_id"]).strip()
    source_record_id = str(row["source_record_id"]).strip()

    claim_id_raw = row.get("claim_id")
    claim_id = str(claim_id_raw).strip() if claim_id_raw and str(claim_id_raw).strip() else None

    annotation_index = int(row["annotation_index"])
    raw_annotation_text = str(row.get("raw_annotation_text", "")).strip()

    source_go_id = str(row.get("go_id", "")).strip()

    source_aspect_raw = row.get("go_aspect")
    source_declared_aspect = (
        str(source_aspect_raw).strip()
        if source_aspect_raw is not None and str(source_aspect_raw).strip()
        else None
    )

    resolved_go_id: Optional[str] = None
    derived_aspect: Optional[str] = None
    mapping_status: str
    replaced_by_go_id: Optional[str] = None
    consider_go_ids: Optional[str] = None
    term_name_resolved: Optional[str] = None
    notes: Optional[str] = None

    # Check for malformed identifier
    if not GO_ID_REGEX.match(source_go_id):
        mapping_status = "unresolved_malformed_id"
        notes = f"Source identifier '{source_go_id}' does not match standard pattern ^GO:[0-9]{{7}}$"
    elif source_go_id in ontology.terms:
        term = ontology.terms[source_go_id]
        term_name_resolved = term.name

        if term.is_obsolete:
            # Rule C: Record obsolescence and replaced_by / consider metadata.
            # Do NOT automatically substitute replacement identifier as resolved_go_id.
            # Do NOT assign derived_aspect to obsolete terms in this increment.
            resolved_go_id = None
            derived_aspect = None
            replaced_by_go_id = term.replaced_by
            consider_go_ids = ";".join(term.consider) if term.consider else None

            if term.replaced_by:
                mapping_status = "obsolete_replaced_by"
                notes = (
                    f"Obsolete term with replaced_by metadata '{term.replaced_by}' "
                    f"in ontology {ontology.data_version}; replacement not automatically substituted"
                )
            else:
                mapping_status = "obsolete_unreplaced"
                notes = (
                    f"Obsolete term without direct replacement in ontology {ontology.data_version}"
                    + (f"; consider suggestions: {consider_go_ids}" if consider_go_ids else "")
                )
        else:
            # Active primary identifier
            resolved_go_id = term.id
            raw_ns = term.namespace or ""
            mapped_asp = NAMESPACE_TO_ASPECT.get(raw_ns)

            # Rule E: Source / ontology aspect conflict check
            if (
                source_declared_aspect in ("BP", "CC", "MF")
                and mapped_asp is not None
                and source_declared_aspect != mapped_asp
            ):
                mapping_status = "conflict_source_ontology_aspect_mismatch"
                derived_aspect = mapped_asp
                notes = (
                    f"Conflict: source declared aspect '{source_declared_aspect}' "
                    f"differs from ontology namespace '{raw_ns}' ({mapped_asp})"
                )
            else:
                mapping_status = "resolved_primary"
                derived_aspect = mapped_asp
                if source_declared_aspect in ("BP", "CC", "MF"):
                    notes = f"Source aspect '{source_declared_aspect}' verified against ontology namespace '{raw_ns}'"
                elif source_declared_aspect == "unassigned":
                    notes = f"Unassigned source aspect enriched to '{mapped_asp}' from namespace '{raw_ns}'"
                else:
                    notes = f"Undeclared source aspect enriched to '{mapped_asp}' from namespace '{raw_ns}'"

    elif source_go_id in ontology.alt_map:
        # Rule B: Alternate identifier resolved to primary
        prim_id = ontology.alt_map[source_go_id]
        term = ontology.terms[prim_id]
        resolved_go_id = prim_id
        term_name_resolved = term.name
        raw_ns = term.namespace or ""
        mapped_asp = NAMESPACE_TO_ASPECT.get(raw_ns)

        if (
            source_declared_aspect in ("BP", "CC", "MF")
            and mapped_asp is not None
            and source_declared_aspect != mapped_asp
        ):
            mapping_status = "conflict_source_ontology_aspect_mismatch"
            derived_aspect = mapped_asp
            notes = (
                f"Conflict on alt_id '{source_go_id}' -> primary '{prim_id}': "
                f"source declared '{source_declared_aspect}' vs ontology '{raw_ns}' ({mapped_asp})"
            )
        else:
            mapping_status = "resolved_secondary_alt_id"
            derived_aspect = mapped_asp
            notes = f"Resolved secondary alt_id '{source_go_id}' to active primary '{prim_id}' ({mapped_asp})"
    else:
        # Rule D: Unknown identifier
        mapping_status = "unresolved_unknown_id"
        notes = f"Identifier '{source_go_id}' not found in ontology snapshot {ontology.data_version}"

    return {
        "annotation_id": annotation_id,
        "protein_id": protein_id,
        "source_id": source_id,
        "source_record_id": source_record_id,
        "claim_id": claim_id,
        "annotation_index": annotation_index,
        "raw_annotation_text": raw_annotation_text,
        "source_go_id": source_go_id,
        "source_declared_aspect": source_declared_aspect,
        "resolved_go_id": resolved_go_id,
        "derived_aspect": derived_aspect,
        "mapping_status": mapping_status,
        "replaced_by_go_id": replaced_by_go_id,
        "consider_go_ids": consider_go_ids,
        "term_name_resolved": term_name_resolved,
        "ontology_version": ontology.data_version,
        "ontology_sha256": ontology.sha256_digest,
        "notes": notes,
    }


def enrich_source_go_annotations_file(
    input_csv_path: Union[str, Path],
    ontology: OntologySnapshot,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Process all rows from source_go_annotations_pilot.csv and emit derived rows."""
    p = Path(input_csv_path)
    if not p.is_file():
        raise FileNotFoundError(f"Input file not found: {p}")

    input_sha256 = compute_file_sha256(p)
    derived_rows: List[Dict[str, Any]] = []

    status_counts: Dict[str, int] = {}
    source_counts: Dict[str, int] = {}
    aspect_counts: Dict[str, int] = {}

    with open(p, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            derived = enrich_annotation_row(row, ontology)
            derived_rows.append(derived)

            st = derived["mapping_status"]
            status_counts[st] = status_counts.get(st, 0) + 1

            src = derived["source_id"]
            source_counts[src] = source_counts.get(src, 0) + 1

            asp = derived["derived_aspect"] or "null"
            aspect_counts[asp] = aspect_counts.get(asp, 0) + 1

    summary = {
        "total_input_rows": len(derived_rows),
        "input_sha256": input_sha256,
        "ontology_version": ontology.data_version,
        "ontology_sha256": ontology.sha256_digest,
        "status_distribution": status_counts,
        "source_distribution": source_counts,
        "derived_aspect_distribution": aspect_counts,
    }

    return derived_rows, summary


def validate_derived_rows_against_schema(
    rows: List[Dict[str, Any]],
    schema_path: Union[str, Path],
) -> None:
    """Validate in-memory derived row dicts against Draft 2020-12 JSON schema."""
    p = Path(schema_path)
    if not p.is_file():
        raise FileNotFoundError(f"Schema not found: {p}")

    with open(p, "r", encoding="utf-8") as f:
        schema = json.load(f)

    validator = Draft202012Validator(schema)
    for idx, r in enumerate(rows):
        errors = list(validator.iter_errors(r))
        if errors:
            first_err = errors[0]
            raise ValueError(
                f"Row {idx} ({r.get('annotation_id')}) failed schema validation at {list(first_err.path)}: {first_err.message}"
            )


def write_derived_source_go_aspects_csv(
    rows: List[Dict[str, Any]],
    output_path: Union[str, Path],
) -> str:
    """Write derived rows to CSV with deterministic formatting. Returns SHA-256."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with open(p, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=DERIVED_COLUMNS,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()
        for r in rows:
            # Format row for CSV: None -> empty string
            row_clean = {k: ("" if r.get(k) is None else str(r[k])) for k in DERIVED_COLUMNS}
            writer.writerow(row_clean)

    return compute_file_sha256(p)
