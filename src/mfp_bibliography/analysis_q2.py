"""Question 2 analysis: exact source-set overlap (exclusive combinations).

Deterministic, stdlib-only aggregation over the packaged candidate CSVs of
the packaged five-source candidate (see
docs/analysis/five-source-descriptive-study-plan.md, Q2). Reads only the
packaged tables; never writes inside the candidate; byte-stable outputs.

Definitions:
- For each protein_id, its source SET is the set of DISTINCT source_name
  values in mfp_source_records.csv; repeated observations within one source
  count once.
- EXCLUSIVE combinations: each protein belongs to exactly one combination,
  its exact source set; combination counts sum to the protein entity total.
  Zero-count combinations are NOT listed (only observed combinations).
- INCLUSIVE pairwise overlap (SECONDARY): for each source pair (a, b), the
  number of proteins whose source set contains BOTH; a protein in three
  sources contributes to each applicable pair but to exactly one exclusive
  combination. Pairwise counts must never be added together as a global
  unique protein count.

No fuzzy accession matching, evidence ranking, or article/GO claims.
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
    load_manifest,
    read_csv_rows,
    sha256_file,
    verify_inputs,
)

ANALYSIS_VERSION = "q2-source-overlap-v1"
BAR_COLOR = "#0072B2"
TEXT_COLOR = "#333333"
# Deterministic display rule: the five known source names are abbreviated
# in the SVG (legend maps them); unknown names render verbatim. Every
# observed combination appears in the SVG and in the CSV.
DISPLAY_LABELS = {
    "SRC_MOONDB": "MoonDB",
    "SRC_MOONPROT": "MoonProt",
    "SRC_MULTIFACETEDPROTDB": "Multifac",
    "SRC_MULTITASKPROTDB_II": "Multitask-II",
    "SRC_PLANTMP": "PlantMP",
}
# Pinned five-source candidate expectations (derived first, then compared).
PINNED_EXPECTED_BINS = {1: 1859, 2: 361, 3: 83, 4: 19, 5: 0}


def compute_source_sets(candidate_dir: Path) -> dict[str, frozenset[str]]:
    """protein_id -> set of distinct sources; enforces FK and full coverage."""
    records = read_csv_rows(candidate_dir / "mfp_source_records.csv")
    proteins = read_csv_rows(candidate_dir / "mfp_proteins.csv")
    protein_ids = [p["protein_id"] for p in proteins]
    if len(set(protein_ids)) != len(protein_ids):
        raise AnalysisError("mfp_proteins.csv has duplicate protein_id values")
    known = set(protein_ids)
    orphans = [r["source_record_id"] for r in records if r["protein_id"] not in known]
    if orphans:
        raise AnalysisError(
            f"{len(orphans)} source records reference missing proteins "
            f"(first: {orphans[0]})")
    source_sets: dict[str, set[str]] = {}
    for row in records:
        source_sets.setdefault(row["protein_id"], set()).add(row["source_name"])
    unsourced = sorted(set(protein_ids) - set(source_sets))
    if unsourced:
        raise AnalysisError(
            f"{len(unsourced)} packaged proteins have no source records "
            f"(first: {unsourced[0]})")
    return {pid: frozenset(sources) for pid, sources in source_sets.items()}


def aggregate(candidate_dir: Path, manifest: dict,
              expected_bins: dict[int, int] | None = None) -> dict:
    """Exclusive combinations, source-count bins and inclusive pairwise counts."""
    source_sets = compute_source_sets(candidate_dir)
    counts = manifest["measured_counts"]
    if len(source_sets) != counts["protein_entity_count"]:
        raise AnalysisError(
            f"derived protein entities {len(source_sets)} != manifest "
            f"{counts['protein_entity_count']}")

    combination_counts: dict[frozenset[str], int] = {}
    bins: dict[int, int] = {i: 0 for i in range(1, len(counts["source_record_counts"]) + 1)}
    for sources in source_sets.values():
        key = frozenset(sources)
        combination_counts[key] = combination_counts.get(key, 0) + 1
        bins[len(sources)] += 1
    if sum(bins.values()) != len(source_sets):
        raise AnalysisError("distinct-source-count bins do not sum to protein entities")

    shared = sum(count for n, count in bins.items() if n >= 2)
    if "exact_uniprot_merge_count" not in counts:
        raise AnalysisError("MANIFEST.json measured_counts lacks exact_uniprot_merge_count")
    if shared != counts["exact_uniprot_merge_count"]:
        raise AnalysisError(
            f"derived proteins in >=2 sources {shared} != manifest "
            f"exact_uniprot_merge_count {counts['exact_uniprot_merge_count']}")
    if expected_bins is not None and bins != expected_bins:
        raise AnalysisError(
            f"derived distinct-source-count bins {bins} != expected {expected_bins}")

    exclusive_rows = [
        {"source_set": "|".join(sorted(sources)), "protein_count": count}
        for sources, count in sorted(
            combination_counts.items(), key=lambda item: (-item[1], sorted(item[0])))
    ]
    sources_universe = sorted(counts["source_record_counts"])
    pairwise_rows = []
    for index, source_a in enumerate(sources_universe):
        for source_b in sources_universe[index + 1:]:
            inclusive = sum(
                1 for s in source_sets.values()
                if source_a in s and source_b in s)
            pairwise_rows.append({
                "source_a": source_a,
                "source_b": source_b,
                "inclusive_protein_count": inclusive,
            })
    return {
        "exclusive_rows": exclusive_rows,
        "pairwise_rows": pairwise_rows,
        "bins": bins,
        "protein_entity_count": len(source_sets),
        "proteins_in_two_or_more_sources": shared,
        "combination_count": len(exclusive_rows),
    }


def render_exclusive_csv(rows: list[dict]) -> str:
    lines = ["source_set,protein_count"]
    lines += [f'{row["source_set"]},{row["protein_count"]}' for row in rows]
    return "\n".join(lines) + "\n"


def render_pairwise_csv(rows: list[dict]) -> str:
    lines = ["source_a,source_b,inclusive_protein_count"]
    lines += [
        f'{row["source_a"]},{row["source_b"]},{row["inclusive_protein_count"]}'
        for row in rows]
    return "\n".join(lines) + "\n"


def _display_label(source_set: str) -> str:
    return "|".join(DISPLAY_LABELS.get(s, s) for s in source_set.split("|"))


def render_svg(rows: list[dict], totals: dict, candidate_label: str) -> str:
    """Deterministic horizontal-bar SVG; every observed combination is shown."""
    width = 980
    left, right = 300, 150
    top, bottom = 128, 92
    row_height = 26
    height = top + row_height * len(rows) + bottom
    max_count = max(row["protein_count"] for row in rows)
    plot_w = width - left - right

    legend = "  ".join(
        f"{short} = {full}" for full, short in sorted(DISPLAY_LABELS.items()))
    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Q2: Protein overlap by exact source set '
        '(exclusive combinations)</title>',
        '<desc id="desc">Horizontal bar chart of exclusive source-set '
        'combinations. Each protein belongs to exactly one combination; bar '
        'length is the number of protein entities; values are shown.</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left - 280}" y="26" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="16" font-weight="bold" fill="{TEXT_COLOR}">Q2: Protein overlap '
        'by exact source set (exclusive combinations)</text>',
        f'<text x="{left - 280}" y="46" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">{candidate_label} — '
        'catalog coverage description, not evidence quality or prevalence</text>',
        f'<text x="{left - 280}" y="66" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="10" fill="{TEXT_COLOR}">{escape(legend)}</text>',
        f'<text x="{left - 280}" y="84" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">unit: protein entity '
        f'(denominator {totals["protein_entity_count"]}); values = entities per exact '
        'source set</text>',
        f'<line x1="{left}" y1="{top - 6}" x2="{left}" y2="{height - bottom + 6}" '
        f'stroke="{TEXT_COLOR}" stroke-width="1"/>',
    ]
    for index, row in enumerate(rows):
        y = top + row_height * index
        bar_w = plot_w * row["protein_count"] / max_count
        parts.append(
            f'<text x="{left - 8}" y="{y + 14}" text-anchor="end" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
            f'fill="{TEXT_COLOR}">{escape(_display_label(row["source_set"]))}</text>')
        parts.append(
            f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="16" '
            f'fill="{BAR_COLOR}"/>')
        parts.append(
            f'<text x="{left + bar_w + 6:.1f}" y="{y + 13}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
            f'fill="{TEXT_COLOR}">{row["protein_count"]}</text>')
    caption = (
        f"Exclusive combinations sum to {totals['protein_entity_count']} protein "
        f"entities; {totals['proteins_in_two_or_more_sources']} entities are claimed by "
        f">=2 sources. Distinct-source-count bins (1..{max(totals['bins'])}): "
        + ", ".join(f"{n}={totals['bins'][n]}" for n in sorted(totals["bins"]))
        + ". Every observed combination is shown; zero-count combinations are omitted.")
    parts.append(
        f'<text x="{left - 280}" y="{height - 26}" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="10" '
        f'fill="{TEXT_COLOR}">{escape(caption)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render_readme(reproduction_command: str) -> str:
    return f"""# Q2 outputs: exact source-set overlap (exclusive combinations)

Catalog coverage/overlap description only. NOT evidence quality, validation,
article/GO support, or biological prevalence. No statistical significance
claims.

## Definitions

- Source set of a protein: DISTINCT `source_name` values claiming it in
  `mfp_source_records.csv`; repeated observations within one source count
  once.
- `q2_exclusive_combinations.csv` (PRIMARY): each protein belongs to exactly
  ONE combination — its exact source set. Counts sum to the protein entity
  total. Only observed (non-zero) combinations are listed; zero-count
  combinations are omitted.
- `q2_pairwise_overlap_secondary_inclusive.csv` (SECONDARY, inclusive): for
  each source pair, proteins whose source set contains BOTH sources; all
  pairs of the five sources are listed, including zero counts. A protein in
  three sources contributes to each applicable pair but to exactly one
  exclusive combination. NEVER sum pairwise counts as a global unique
  protein count.

## Display rule (SVG)

Horizontal bars, sorted by descending protein count then lexicographic source
set; every observed combination is shown (figure height grows with the
combination count). Source names are abbreviated with the legend mapping in
the figure; the CSV retains full source names. No fuzzy matching: sets are
exact `source_name` values.

## Reproduce / verify

PACKAGE_VERIFY gate (runs first, offline):

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```

This analysis (gate included, deterministic, byte-stable):

```bash
{reproduction_command}
```

Outputs: the two CSVs above, `q2_source_overlap.svg`, `analysis_manifest.json`
(candidate contract, input and output SHA-256 hashes, definitions, derived
totals). Reruns are idempotent for identical bytes; changed bytes require a
new analysis version.
"""


def run(candidate_dir: Path, output_dir: Path,
        expected_bins: dict[int, int] | None = None,
        reproduction_command: str | None = None) -> int:
    """Verify, aggregate, render and publish Question 2 outputs."""
    try:
        manifest = load_manifest(candidate_dir)
        input_hashes = verify_inputs(candidate_dir, manifest)
        totals = aggregate(candidate_dir, manifest, expected_bins=expected_bins)
        exclusive_bytes = render_exclusive_csv(totals["exclusive_rows"]).encode("utf-8")
        pairwise_bytes = render_pairwise_csv(totals["pairwise_rows"]).encode("utf-8")
        svg_bytes = render_svg(
            totals["exclusive_rows"], totals,
            candidate_label=str(manifest.get("candidate_id") or "unknown-candidate")
        ).encode("utf-8")
        readme_bytes = render_readme(
            reproduction_command
            or "PYTHONPATH=src python scripts/analyze_question2.py").encode("utf-8")
        provenance = {
            "analysis_version": ANALYSIS_VERSION,
            "question": "Q2 exact source-set overlap (exclusive combinations)",
            "candidate": {
                "candidate_id": manifest.get("candidate_id"),
                "catalog_contract": manifest.get("catalog_contract"),
                "protein_id_scheme": manifest.get("protein_id_scheme"),
            },
            "inputs": {name: {"sha256": input_hashes[name]}
                       for name in ("mfp_source_records.csv", "mfp_proteins.csv")},
            "definitions": {
                "source_set": "distinct source_name values per protein_id; repeated "
                              "observations within one source count once",
                "exclusive_combination": "each protein belongs to exactly one exact "
                                          "source set; counts sum to the entity total; "
                                          "zero-count combinations omitted",
                "pairwise_inclusive_secondary": "proteins in BOTH sources of a pair; "
                                                "all pairs listed including zeros; "
                                                "never summed as a global entity count",
                "svg_display_rule": "horizontal bars sorted by count desc then "
                                     "lexicographic set; every observed combination "
                                     "shown; abbreviated source names with legend",
            },
            "derived_totals": {
                "protein_entity_count": totals["protein_entity_count"],
                "combination_count": totals["combination_count"],
                "distinct_source_count_bins": totals["bins"],
                "proteins_in_two_or_more_sources":
                    totals["proteins_in_two_or_more_sources"],
            },
            "outputs": {
                "q2_exclusive_combinations.csv": {
                    "sha256": hashlib.sha256(exclusive_bytes).hexdigest()},
                "q2_pairwise_overlap_secondary_inclusive.csv": {
                    "sha256": hashlib.sha256(pairwise_bytes).hexdigest()},
                "q2_source_overlap.svg": {
                    "sha256": hashlib.sha256(svg_bytes).hexdigest()},
            },
            "interpretation": {
                "allowed": ["describing overlap and combination coverage of the "
                            "catalog"],
                "forbidden": [
                    "summing pairwise inclusive counts as a global unique protein count",
                    "interpreting overlap as confirmation or evidence quality",
                    "fuzzy accession matching, evidence ranking, article/GO claims",
                    "statistical significance claims"],
            },
        }
        provenance_bytes = (
            json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
        outputs = {
            "q2_exclusive_combinations.csv": exclusive_bytes,
            "q2_pairwise_overlap_secondary_inclusive.csv": pairwise_bytes,
            "q2_source_overlap.svg": svg_bytes,
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
        print(f"Q2 analysis published at {output_dir} "
              f"(proteins={totals['protein_entity_count']}, "
              f"combinations={totals['combination_count']}, "
              f">=2 sources={totals['proteins_in_two_or_more_sources']})")
        return 0
    except (AnalysisError, OSError, KeyError, ValueError) as exc:
        print(f"[analysis-q2] {exc}", file=sys.stderr)
        return 1
