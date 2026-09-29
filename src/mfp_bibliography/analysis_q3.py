"""Question 3 analysis: number of distinct sources per protein entity.

Deterministic, stdlib-only aggregation over the packaged candidate CSVs of
`mfp-catalog-candidate-v0.2.0` (see
docs/analysis/five-source-descriptive-study-plan.md, Q3).

Definition: for each protein_id, the number of DISTINCT `source_name`
values claiming it in mfp_source_records.csv (repeated observations within
one source count once). Bins 1..number_of_sources, zero-count bins included;
bins sum to the protein entity total (2,322 for this candidate).

This distribution is NOT the inclusive pairwise-overlap count of Q2: a
protein in three sources contributes 1 to bin 3 here, but 1 to EACH of its
three source pairs in the Q2 secondary table. Absence from a source is
never negative evidence; more sources is not more evidence.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from mfp_bibliography.analysis_q1 import (
    AnalysisError,
    load_manifest,
    verify_inputs,
)
from mfp_bibliography.analysis_q2 import compute_source_sets

ANALYSIS_VERSION = "q3-sources-per-protein-v1"
BAR_COLOR = "#0072B2"
TEXT_COLOR = "#333333"
# Pinned candidate v0.2.0 expectations (derived first, then compared).
PINNED_EXPECTED_BINS = {1: 1859, 2: 361, 3: 83, 4: 19, 5: 0}


def aggregate(candidate_dir: Path, manifest: dict,
              expected_bins: dict[int, int] | None = None) -> dict:
    """Distinct-source-count bins 1..N for every packaged protein entity."""
    source_sets = compute_source_sets(candidate_dir)
    counts = manifest["measured_counts"]
    if len(source_sets) != counts["protein_entity_count"]:
        raise AnalysisError(
            f"derived protein entities {len(source_sets)} != manifest "
            f"{counts['protein_entity_count']}")
    source_count = len(counts["source_record_counts"])
    bins = {n: 0 for n in range(1, source_count + 1)}
    for sources in source_sets.values():
        if not 1 <= len(sources) <= source_count:
            raise AnalysisError(
                f"protein claimed by {len(sources)} distinct sources, outside "
                f"the declared {source_count}-source universe")
        bins[len(sources)] += 1
    if sum(bins.values()) != len(source_sets):
        raise AnalysisError("bins do not sum to the protein entity total")
    shared = sum(count for n, count in bins.items() if n >= 2)
    if shared != counts["exact_uniprot_merge_count"]:
        raise AnalysisError(
            f"derived proteins in >=2 sources {shared} != manifest "
            f"exact_uniprot_merge_count {counts['exact_uniprot_merge_count']}")
    if expected_bins is not None and bins != expected_bins:
        raise AnalysisError(
            f"derived distinct-source-count bins {bins} != expected {expected_bins}")
    return {
        "bins": bins,
        "protein_entity_count": len(source_sets),
        "proteins_in_two_or_more_sources": shared,
    }


def render_csv(totals: dict) -> str:
    lines = ["distinct_source_count,protein_count"]
    lines += [
        f"{n},{totals['bins'][n]}" for n in sorted(totals["bins"])]
    return "\n".join(lines) + "\n"


def render_svg(totals: dict) -> str:
    """Deterministic labeled bar chart of bins 1..N (zero bins shown)."""
    width, height = 980, 430
    left, right, top, bottom = 90, 40, 96, 108
    plot_w = width - left - right
    plot_h = height - top - bottom
    bins = totals["bins"]
    max_val = max(max(bins.values()), 1)
    group_w = plot_w / len(bins)
    bar_w = min(70.0, group_w / 2)
    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Q3: Number of distinct sources per protein entity</title>',
        '<desc id="desc">Bar chart of protein entities by number of distinct '
        'claiming sources. Zero-count bins are shown. Values are displayed '
        'above each bar.</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="26" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="16" font-weight="bold" fill="{TEXT_COLOR}">Q3: Number of '
        'distinct sources per protein entity</text>',
        f'<text x="{left}" y="46" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">Candidate mfp-catalog-candidate-v0.2.0 — '
        'catalog coverage description, not evidence quality or prevalence</text>',
        f'<text x="{left}" y="66" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">unit: protein entity '
        f'(denominator {totals["protein_entity_count"]}); repeated observations '
        'within one source count once</text>',
    ]
    for tick in range(0, max_val + 1, max(1, max_val // 5)):
        y = top + plot_h * (1 - tick / max_val)
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" '
            f'stroke="#dddddd" stroke-width="1"/>')
        parts.append(
            f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
            f'fill="{TEXT_COLOR}">{tick}</text>')
    parts.append(
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" '
        f'stroke="{TEXT_COLOR}" stroke-width="1"/>')
    parts.append(
        f'<line x1="{left}" y1="{top + plot_h}" x2="{width - right}" '
        f'y2="{top + plot_h}" stroke="{TEXT_COLOR}" stroke-width="1"/>')
    for index, n in enumerate(sorted(bins)):
        cx = left + group_w * (index + 0.5)
        value = bins[n]
        bar_h = plot_h * value / max_val
        parts.append(
            f'<rect x="{cx - bar_w / 2:.1f}" y="{top + plot_h - bar_h:.1f}" '
            f'width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{BAR_COLOR}"/>')
        parts.append(
            f'<text x="{cx:.1f}" y="{top + plot_h - bar_h - 6:.1f}" '
            f'text-anchor="middle" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="11" fill="{TEXT_COLOR}">{value}</text>')
        parts.append(
            f'<text x="{cx:.1f}" y="{top + plot_h + 18:.1f}" text-anchor="middle" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="12" '
            f'fill="{TEXT_COLOR}">{n} source{"s" if n > 1 else ""}</text>')
    caption = (
        f"Bins sum to {totals['protein_entity_count']} protein entities; "
        f"{totals['proteins_in_two_or_more_sources']} entities are claimed by >=2 "
        "sources. Zero-count bins are shown. This is NOT the inclusive pairwise "
        "overlap of Q2 (a 3-source protein counts once in bin 3, but once per "
        "source pair there). Absence from a source is never negative evidence.")
    parts.append(
        f'<text x="{left}" y="{height - 26}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="10" fill="{TEXT_COLOR}">{escape(caption)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render_readme(reproduction_command: str) -> str:
    return f"""# Q3 outputs: number of distinct sources per protein entity

Catalog coverage description only. NOT evidence quality, article/GO support,
or biological prevalence. No statistical significance claims.

## Definition

For each protein_id: the number of DISTINCT `source_name` values claiming it
in `mfp_source_records.csv`; repeated observations within one source count
once. Bins 1..5 (number of sources), zero-count bins included; bins sum to
the protein entity total. This distribution is distinct from the Q2
inclusive pairwise overlap: a protein in three sources contributes 1 to bin 3
here, but 1 to EACH of its three source pairs in the Q2 secondary table.
"More sources" is not "more evidence"; absence from a source is never
negative evidence.

## Reproduce / verify

PACKAGE_VERIFY gate (runs first, offline):

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```

This analysis (gate included, deterministic, byte-stable):

```bash
{reproduction_command}
```

Outputs: `q3_sources_per_protein.csv` (bins 1..5, zeros included),
`q3_sources_per_protein.svg`, `analysis_manifest.json` (candidate contract,
input and output SHA-256 hashes, definitions, derived totals). Reruns are
idempotent for identical bytes; changed bytes require a new analysis version.
"""


def run(candidate_dir: Path, output_dir: Path,
        expected_bins: dict[int, int] | None = None,
        reproduction_command: str | None = None) -> int:
    """Verify, aggregate, render and publish Question 3 outputs."""
    try:
        manifest = load_manifest(candidate_dir)
        input_hashes = verify_inputs(candidate_dir, manifest)
        totals = aggregate(candidate_dir, manifest, expected_bins=expected_bins)
        csv_bytes = render_csv(totals).encode("utf-8")
        svg_bytes = render_svg(totals).encode("utf-8")
        readme_bytes = render_readme(
            reproduction_command
            or "PYTHONPATH=src python scripts/analyze_question3.py").encode("utf-8")
        provenance = {
            "analysis_version": ANALYSIS_VERSION,
            "question": "Q3 number of distinct sources per protein entity",
            "candidate": {
                "candidate_id": manifest.get("candidate_id"),
                "catalog_contract": manifest.get("catalog_contract"),
                "protein_id_scheme": manifest.get("protein_id_scheme"),
            },
            "inputs": {name: {"sha256": input_hashes[name]}
                       for name in ("mfp_source_records.csv", "mfp_proteins.csv")},
            "definitions": {
                "distinct_source_count": "number of DISTINCT source_name values "
                                         "per protein_id; repeated rows within one "
                                         "source count once",
                "bins": "1..number_of_sources, zero-count bins included; sum to "
                        "the protein entity total",
                "relation_to_q2": "distinct from inclusive pairwise overlap; bins "
                                  "count each protein once, Q2 pairs count a protein "
                                  "once per source pair",
            },
            "derived_totals": totals,
            "outputs": {
                "q3_sources_per_protein.csv": {
                    "sha256": hashlib.sha256(csv_bytes).hexdigest()},
                "q3_sources_per_protein.svg": {
                    "sha256": hashlib.sha256(svg_bytes).hexdigest()},
            },
            "interpretation": {
                "allowed": ["describing the multi-source membership distribution "
                            "of the catalog"],
                "forbidden": [
                    "reading more sources as stronger evidence of "
                    "multifunctionality",
                    "treating absence from a source as negative evidence",
                    "statistical significance claims"],
            },
        }
        provenance_bytes = (
            json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
        outputs = {
            "q3_sources_per_protein.csv": csv_bytes,
            "q3_sources_per_protein.svg": svg_bytes,
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
        print(f"Q3 analysis published at {output_dir} "
              f"(proteins={totals['protein_entity_count']}, bins={totals['bins']})")
        return 0
    except (AnalysisError, OSError, KeyError, ValueError) as exc:
        print(f"[analysis-q3] {exc}", file=sys.stderr)
        return 1
