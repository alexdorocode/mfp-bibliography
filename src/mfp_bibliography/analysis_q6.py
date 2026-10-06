"""Question 6 analysis: completeness of canonical protein fields.

Deterministic, stdlib-only aggregation over the packaged
`mfp_proteins.csv` of the packaged five-source candidate (see
docs/analysis/five-source-descriptive-study-plan.md, Q6).

Unit: protein entity. Denominator: the candidate manifest's
`protein_entity_count` (2,322 for this candidate), reconciled against the
derived row count. No source-record joins, no ignored inputs.

Semantics:
- A value is POPULATED iff it is not None and its stripped form is not
  empty; whitespace-only values count as empty.
- `canonical_name` and `canonical_organism` are REPRESENTATIVE values:
  the catalog builder deterministically selects the lexicographically
  smallest of the verbatim raw values supplied by any claiming record.
  They are NOT consensus and NOT source-confirmed truth.
- Entity-level field presence cannot be attributed to any one source (the
  packaged table carries no per-value provenance column); emptiness is
  dominated by source-dependent field supply and must NOT be read as
  source error, protein absence or negative evidence.
- `canonical_gene` and `taxonomy_id` are never populated by this builder
  (hard-coded empty) and are DEFERRED; their absence is not charted as
  missing source metadata.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from mfp_bibliography.analysis_q1 import (
    AnalysisError,
    sha256_file,
)


def load_manifest(candidate_dir: Path) -> dict:
    """Q6-specific manifest loader: entity count and packaged outputs only."""
    manifest_path = candidate_dir / "MANIFEST.json"
    if not manifest_path.is_file():
        raise AnalysisError(f"missing {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    if "protein_entity_count" not in manifest.get("measured_counts", {}):
        raise AnalysisError("MANIFEST.json measured_counts lacks protein_entity_count")
    if "packaged_outputs" not in manifest:
        raise AnalysisError("MANIFEST.json lacks packaged_outputs")
    return manifest

ANALYSIS_VERSION = "q6-canonical-completeness-v1"
INPUT_TABLE = "mfp_proteins.csv"
MEASURED_FIELDS = (
    "canonical_uniprot_accession",
    "entity_status",
    "canonical_name",
    "canonical_organism",
)
BAR_COLOR = "#0072B2"
EMPTY_COLOR = "#BBBBBB"
TEXT_COLOR = "#333333"


def verify_input(candidate_dir: Path, manifest: dict) -> str:
    """Enforce the packaged proteins-table hash before analysis."""
    path = candidate_dir / INPUT_TABLE
    if not path.is_file():
        raise AnalysisError(f"missing packaged input {INPUT_TABLE}")
    checksums_path = candidate_dir / "checksums.sha256"
    if not checksums_path.is_file():
        raise AnalysisError(f"missing {checksums_path}")
    listed: dict[str, str] = {}
    for line in checksums_path.read_text().splitlines():
        digest, name = line.split("  ", 1)
        listed[name] = digest
    actual = sha256_file(path)
    expected = manifest["packaged_outputs"].get(INPUT_TABLE, {}).get("sha256")
    if expected is None:
        raise AnalysisError(
            f"MANIFEST.json lacks packaged_outputs entry for {INPUT_TABLE}")
    if actual != expected:
        raise AnalysisError(
            f"input {INPUT_TABLE} hash mismatch: file is {actual}, "
            f"manifest says {expected}")
    if listed.get(INPUT_TABLE) != actual:
        raise AnalysisError(f"input {INPUT_TABLE} hash mismatch vs checksums.sha256")
    return actual


def _is_populated(value: str | None) -> bool:
    return value is not None and value.strip() != ""


def aggregate(candidate_dir: Path, manifest: dict) -> dict:
    """Populated/empty counts per measured field, with conservation checks."""
    with (candidate_dir / INPUT_TABLE).open(newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        rows = list(reader)
    missing_columns = [
        name for name in ("protein_id", *MEASURED_FIELDS) if name not in fieldnames]
    if missing_columns:
        raise AnalysisError(
            f"{INPUT_TABLE} lacks required columns: {', '.join(missing_columns)}")
    counts = manifest["measured_counts"]
    if len(rows) != counts["protein_entity_count"]:
        raise AnalysisError(
            f"derived protein entities {len(rows)} != manifest "
            f"protein_entity_count {counts['protein_entity_count']}")
    protein_ids = [row.get("protein_id") for row in rows]
    if len(set(protein_ids)) != len(protein_ids):
        raise AnalysisError("mfp_proteins.csv has duplicate protein_id values")

    field_rows = []
    for field in MEASURED_FIELDS:
        populated = sum(1 for row in rows if _is_populated(row.get(field)))
        empty = len(rows) - populated
        if populated + empty != len(rows):
            raise AnalysisError(
                f"conservation violated for {field}: {populated} + {empty} != "
                f"{len(rows)}")
        field_rows.append({
            "field": field,
            "populated": populated,
            "empty": empty,
            "denominator": len(rows),
            "percentage": f"{100.0 * populated / len(rows):.1f}",
        })
    return {
        "field_rows": field_rows,
        "protein_entity_count": len(rows),
    }


def render_csv(totals: dict) -> str:
    lines = ["field,populated,empty,denominator,percentage"]
    lines += [
        f'{row["field"]},{row["populated"]},{row["empty"]},'
        f'{row["denominator"]},{row["percentage"]}'
        for row in totals["field_rows"]]
    return "\n".join(lines) + "\n"


def render_svg(totals: dict, candidate_label: str) -> str:
    """Deterministic horizontal bars; populated vs empty, denominator stated."""
    width, height = 980, 380
    left, right, top, bottom = 300, 130, 96, 96
    plot_w = width - left - right
    row_h = 52
    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Q6: Completeness of canonical protein fields</title>',
        '<desc id="desc">Horizontal bars of populated versus empty values for four '
        'packaged protein-entity fields. The denominator is the protein entity '
        'count. Empty values reflect field supply, not protein absence.</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left - 280}" y="26" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="16" font-weight="bold" fill="{TEXT_COLOR}">Q6: Completeness '
        'of canonical protein fields</text>',
        f'<text x="{left - 280}" y="46" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">{candidate_label} '
        '— catalog packaging completeness; NOT evidence, protein presence or '
        'source quality</text>',
        f'<text x="{left - 280}" y="66" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">unit: protein entity; denominator '
        f'{totals["protein_entity_count"]} (stated in every row of the CSV); '
        'whitespace-only counts as empty</text>',
    ]
    for index, row in enumerate(totals["field_rows"]):
        y = top + row_h * index
        bar_h = 18
        populated_w = plot_w * row["populated"] / row["denominator"]
        empty_w = plot_w * row["empty"] / row["denominator"]
        parts.append(
            f'<text x="{left - 10}" y="{y + 14}" text-anchor="end" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="12" '
            f'fill="{TEXT_COLOR}">{escape(row["field"])}</text>')
        parts.append(
            f'<rect x="{left}" y="{y}" width="{populated_w:.1f}" '
            f'height="{bar_h}" fill="{BAR_COLOR}"/>')
        if row["empty"]:
            parts.append(
                f'<rect x="{left + populated_w:.1f}" y="{y}" '
                f'width="{empty_w:.1f}" height="{bar_h}" fill="{EMPTY_COLOR}"/>')
        parts.append(
            f'<text x="{left + plot_w + 8}" y="{y + 14}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
            f'fill="{TEXT_COLOR}">populated {row["populated"]}, empty '
            f'{row["empty"]} ({row["percentage"]}%)</text>')
    caption = (
        f"Denominator: {totals['protein_entity_count']} protein entities per field "
        "(populated + empty = denominator). Blue = populated, gray = empty. "
        "canonical_name and canonical_organism are representative values selected "
        "deterministically from available record values — NOT consensus and NOT "
        "source-confirmed truth. Empty values reflect source-dependent field "
        "supply, not source error, protein absence or negative evidence. "
        "canonical_gene and taxonomy_id are never populated by this builder and "
        "are deferred (not charted).")
    parts.append(
        f'<text x="{left - 280}" y="{height - 20}" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="10" '
        f'fill="{TEXT_COLOR}">{escape(caption)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render_readme(reproduction_command: str) -> str:
    return f"""# Q6 outputs: completeness of canonical protein fields

Catalog packaging completeness only. NOT evidence about proteins, NOT
source quality assessment, NOT MF/NMF truth. No statistical significance
claims.

## Unit, denominator and value handling

- Unit: protein entity. Denominator: the candidate manifest's
  `protein_entity_count` (2,322 for the pinned five-source candidate),
  reconciled against
  the derived row count and the unique `protein_id` count.
- A value is POPULATED iff it is not null and its stripped form is not
  empty; whitespace-only values count as empty.
- Every field row in `q6_canonical_completeness.csv` restates the
  denominator; the percentage column is meaningless without it.

## Field semantics

- `canonical_uniprot_accession`, `entity_status`: normalized/derived
  catalog values; populated for all entities in this candidate.
- `canonical_name`, `canonical_organism`: REPRESENTATIVE values selected
  deterministically by the catalog builder (lexicographically smallest of
  the verbatim raw values supplied by any claiming record). They are
  NOT consensus and NOT source-confirmed truth; a populated value does not
  mean any source "confirmed" it.

## Limits

- Entity-level field presence CANNOT be attributed to any one source: the
  packaged table carries no per-value provenance column. Per-source field
  supply is a known availability bias but is not computed here (it would
  require undeclared inputs beyond this analysis's scope).
- Empty `canonical_name`/`canonical_organism` reflects which sources claim
  the protein and which fields they supply — NOT source error, protein
  absence or negative MF evidence.
- `canonical_gene` and `taxonomy_id` are never populated by this builder
  (hard-coded empty) and are therefore DEFERRED; their absence is not
  charted as missing source metadata.
- No PlantMP records or any source records are altered by this analysis.

## Reproduce / verify

PACKAGE_VERIFY gate (runs first, offline):

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```

This analysis (gate included, deterministic, byte-stable):

```bash
{reproduction_command}
```

Outputs: `q6_canonical_completeness.csv`, `q6_canonical_completeness.svg`,
`analysis_manifest.json` (candidate contract, input and output SHA-256
hashes, rules, derived totals). Reruns are idempotent for identical bytes;
changed bytes require a new analysis version.
"""


def run(candidate_dir: Path, output_dir: Path,
        reproduction_command: str | None = None) -> int:
    """Verify, aggregate, render and publish Question 6 outputs."""
    try:
        manifest = load_manifest(candidate_dir)
        input_hash = verify_input(candidate_dir, manifest)
        totals = aggregate(candidate_dir, manifest)
        csv_bytes = render_csv(totals).encode("utf-8")
        svg_bytes = render_svg(
            totals,
            candidate_label=str(manifest.get("candidate_id") or "unknown-candidate")
        ).encode("utf-8")
        readme_bytes = render_readme(
            reproduction_command
            or "PYTHONPATH=src python scripts/analyze_question6.py").encode("utf-8")
        provenance = {
            "analysis_version": ANALYSIS_VERSION,
            "question": "Q6 completeness of canonical protein fields",
            "candidate": {
                "candidate_id": manifest.get("candidate_id"),
                "catalog_contract": manifest.get("catalog_contract"),
                "protein_id_scheme": manifest.get("protein_id_scheme"),
            },
            "inputs": {INPUT_TABLE: {"sha256": input_hash}},
            "rules": {
                "populated": "value not null and stripped form not empty; "
                             "whitespace-only counts as empty",
                "conservation": "populated + empty = denominator for every field; "
                                "denominator = manifest protein_entity_count, "
                                "reconciled with unique protein_id count",
                "measured_fields": list(MEASURED_FIELDS),
                "deferred_fields": "canonical_gene and taxonomy_id: never populated "
                                   "by this builder; not charted",
                "selection_semantics": "canonical_name/canonical_organism are "
                                       "representative values selected "
                                       "deterministically from available record "
                                       "values; not consensus, not source-confirmed "
                                       "truth; no per-source attribution possible",
            },
            "derived_totals": totals,
            "outputs": {
                "q6_canonical_completeness.csv": {
                    "sha256": hashlib.sha256(csv_bytes).hexdigest()},
                "q6_canonical_completeness.svg": {
                    "sha256": hashlib.sha256(svg_bytes).hexdigest()},
            },
            "interpretation": {
                "allowed": ["reporting packaged field completeness per entity"],
                "forbidden": [
                    "attributing entity-level field presence to any one source",
                    "interpreting emptiness as source error, protein absence or "
                    "negative evidence",
                    "charting canonical_gene/taxonomy_id zeroes as missing source "
                    "metadata",
                    "statistical significance claims"],
            },
        }
        provenance_bytes = (
            json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
        outputs = {
            "q6_canonical_completeness.csv": csv_bytes,
            "q6_canonical_completeness.svg": svg_bytes,
            "analysis_manifest.json": provenance_bytes,
            "README.md": readme_bytes,
        }
        if output_dir.exists():
            for name, content in outputs.items():
                path = output_dir / name
                if path.is_file():
                    if path.read_bytes() != content:
                        raise AnalysisError(
                            f"refusing to overwrite existing {path} with different "
                            "bytes; use a new analysis version")
                else:
                    raise AnalysisError(
                        f"existing output directory {output_dir} lacks {name}; "
                        "refusing partial overwrite")
        else:
            output_dir.mkdir(parents=True)
        for name, content in outputs.items():
            (output_dir / name).write_bytes(content)
        print(f"Q6 analysis published at {output_dir} "
              f"(entities={totals['protein_entity_count']}, "
              f"fields={len(totals['field_rows'])})")
        return 0
    except (AnalysisError, OSError, KeyError, ValueError) as exc:
        print(f"[analysis-q6] {exc}", file=sys.stderr)
        return 1
