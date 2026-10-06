"""Question 1 analysis: source records vs unique protein entities by source.

Deterministic, stdlib-only aggregation over the packaged candidate CSVs of
the packaged five-source candidate (see
docs/analysis/five-source-descriptive-study-plan.md, Q1). Reads only the
packaged tables; never writes inside the candidate. Outputs are byte-stable
(no timestamps).

Aggregation rules:
- source_record_count: rows per `source_name` in `mfp_source_records.csv`;
- unique_protein_count: distinct `protein_id` within each source;
- per-source unique counts are NOT additive across sources (shared entities
  appear in more than one source); the global entity total is a separate,
  derived check against the candidate manifest.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ANALYSIS_VERSION = "q1-records-vs-entities-v1"
INPUT_TABLES = ("mfp_source_records.csv", "mfp_proteins.csv")
RECORD_COLOR = "#0072B2"
PROTEIN_COLOR = "#E69F00"
TEXT_COLOR = "#333333"


class AnalysisError(RuntimeError):
    """Question 1 analysis failed; nothing is published."""


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_manifest(candidate_dir: Path) -> dict:
    manifest_path = candidate_dir / "MANIFEST.json"
    if not manifest_path.is_file():
        raise AnalysisError(f"missing {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    counts = manifest.get("measured_counts", {})
    for key in ("source_record_count", "protein_entity_count", "source_record_counts"):
        if key not in counts:
            raise AnalysisError(f"MANIFEST.json measured_counts lacks {key}")
    if "packaged_outputs" not in manifest:
        raise AnalysisError("MANIFEST.json lacks packaged_outputs")
    return manifest


def verify_inputs(candidate_dir: Path, manifest: dict) -> dict[str, str]:
    """Enforce packaged-input hashes against MANIFEST.json and checksums.sha256."""
    checksums_path = candidate_dir / "checksums.sha256"
    if not checksums_path.is_file():
        raise AnalysisError(f"missing {checksums_path}")
    listed: dict[str, str] = {}
    for line in checksums_path.read_text().splitlines():
        digest, name = line.split("  ", 1)
        listed[name] = digest
    hashes: dict[str, str] = {}
    for name in INPUT_TABLES:
        path = candidate_dir / name
        if not path.is_file():
            raise AnalysisError(f"missing packaged input {name}")
        actual = sha256_file(path)
        expected = manifest["packaged_outputs"].get(name, {}).get("sha256")
        if expected is None:
            raise AnalysisError(f"MANIFEST.json lacks packaged_outputs entry for {name}")
        if actual != expected:
            raise AnalysisError(
                f"input {name} hash mismatch: file is {actual}, manifest says {expected}")
        if listed.get(name) != actual:
            raise AnalysisError(f"input {name} hash mismatch vs checksums.sha256")
        hashes[name] = actual
    return hashes


def read_csv_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def aggregate(candidate_dir: Path, manifest: dict) -> tuple[list[dict], dict]:
    """Compute per-source record and unique-protein counts; enforce invariants."""
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

    record_counts: dict[str, int] = {}
    per_source_proteins: dict[str, set[str]] = {}
    for row in records:
        source = row["source_name"]
        record_counts[source] = record_counts.get(source, 0) + 1
        per_source_proteins.setdefault(source, set()).add(row["protein_id"])

    counts = manifest["measured_counts"]
    if record_counts != counts["source_record_counts"]:
        raise AnalysisError(
            f"derived per-source record counts {dict(sorted(record_counts.items()))} != "
            f"manifest source_record_counts {counts['source_record_counts']}")
    if len(records) != counts["source_record_count"]:
        raise AnalysisError(
            f"derived total source records {len(records)} != manifest "
            f"{counts['source_record_count']}")
    if len(known) != counts["protein_entity_count"]:
        raise AnalysisError(
            f"derived global protein entities {len(known)} != manifest "
            f"{counts['protein_entity_count']}")

    rows = [
        {
            "source_name": source,
            "source_record_count": record_counts[source],
            "unique_protein_count": len(per_source_proteins[source]),
        }
        for source in sorted(record_counts)
    ]
    totals = {
        "source_record_count": len(records),
        "protein_entity_count": len(known),
        "per_source_records": dict(sorted(record_counts.items())),
        "per_source_unique_proteins": {
            s: len(per_source_proteins[s]) for s in sorted(per_source_proteins)},
    }
    return rows, totals


def _nice_ceiling(value: float) -> int:
    for exponent in range(0, 8):
        for mantissa in (1, 2, 5):
            candidate = mantissa * 10 ** exponent
            if candidate >= value:
                return candidate
    return 10 ** 8


def render_svg(rows: list[dict], totals: dict, candidate_label: str) -> str:
    """Deterministic, accessible grouped-bar SVG; all text is XML-escaped."""
    width, height = 980, 470
    left, right, top, bottom = 110, 30, 96, 104
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_val = _nice_ceiling(max(
        max(r["source_record_count"], r["unique_protein_count"]) for r in rows) * 1.05)
    group_w = plot_w / len(rows)
    bar_w = min(46.0, group_w / 3.4)

    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        'viewBox="0 0 %d %d" role="img" aria-labelledby="title desc">' % (width, height),
        '<title id="title">Q1: Source records vs unique protein entities by source</title>',
        '<desc id="desc">Grouped bar chart with two series per source: number of source '
        'records (rows) and number of unique protein entities (distinct protein_id within '
        'the source). Values are shown above each bar.</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="28" font-family="Helvetica,Arial,sans-serif" font-size="16" '
        f'font-weight="bold" fill="{TEXT_COLOR}">Q1: Source records vs unique protein '
        'entities by source</text>',
        f'<text x="{left}" y="48" font-family="Helvetica,Arial,sans-serif" font-size="11" '
        f'fill="{TEXT_COLOR}">{candidate_label} — catalog coverage '
        'description, not validated articles, GO support or prevalence</text>',
    ]
    # Legend
    legend_y = 68
    parts.append(
        f'<rect x="{left}" y="{legend_y}" width="12" height="12" fill="{RECORD_COLOR}"/>')
    parts.append(
        f'<text x="{left + 18}" y="{legend_y + 11}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="12" fill="{TEXT_COLOR}">Source records (rows per source; denominator '
        f'per source)</text>')
    parts.append(
        f'<rect x="{left + 340}" y="{legend_y}" width="12" height="12" '
        f'fill="{PROTEIN_COLOR}"/>')
    parts.append(
        f'<text x="{left + 358}" y="{legend_y + 11}" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="12" fill="{TEXT_COLOR}">'
        'Unique protein entities (distinct protein_id per source)</text>')

    # Y axis with 5 ticks
    ticks = [round(max_val * i / 5) for i in range(0, 6)]
    for tick in ticks:
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
    parts.append(
        f'<text x="18" y="{top + plot_h / 2:.0f}" text-anchor="middle" '
        'transform="rotate(-90 18 %d)" font-family="Helvetica,Arial,sans-serif" '
        'font-size="12" fill="%s">count (rows / distinct protein_id)</text>'
        % (top + plot_h / 2, TEXT_COLOR))

    # Bars
    for index, row in enumerate(rows):
        cx = left + group_w * (index + 0.5)
        series = (
            ("source_record_count", RECORD_COLOR, -1),
            ("unique_protein_count", PROTEIN_COLOR, 1),
        )
        for key, color, side in series:
            value = row[key]
            bar_h = plot_h * value / max_val
            x = cx + side * (bar_w / 2 + 3) - (bar_w if side > 0 else 0)
            y = top + plot_h - bar_h
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
                f'fill="{color}"/>')
            parts.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{y - 5:.1f}" text-anchor="middle" '
                f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
                f'fill="{TEXT_COLOR}">{value}</text>')
        parts.append(
            f'<text x="{cx:.1f}" y="{top + plot_h + 16:.1f}" text-anchor="middle" '
            'transform="rotate(-30 %.1f %.1f)" font-family="Helvetica,Arial,sans-serif" '
            'font-size="11" fill="%s">%s</text>'
            % (cx, top + plot_h + 16, TEXT_COLOR, escape(row["source_name"])))

    caption = (
        f"Denominators (derived from packaged CSVs): {totals['source_record_count']} source "
        f"records; {totals['protein_entity_count']} unique protein entities across five "
        "sources. Per-source unique protein counts do NOT sum to the global total: shared "
        "entities appear in more than one source.")
    parts.append(
        f'<text x="{left}" y="{height - 26}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="10" fill="{TEXT_COLOR}">{escape(caption)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render_csv(rows: list[dict]) -> str:
    lines = ["source_name,source_record_count,unique_protein_count"]
    lines += [
        f'{row["source_name"]},{row["source_record_count"]},{row["unique_protein_count"]}'
        for row in rows]
    return "\n".join(lines) + "\n"


def render_readme(reproduction_command: str) -> str:
    return f"""# Q1 outputs: source records vs unique protein entities by source

Analysis of catalog coverage only. NOT counts of validated articles,
GO-supported functions, or the biological prevalence of
multifunctionality. No statistical significance claims.

Interpretation allowed: describing per-source record counts and per-source
unique protein entities of the packaged candidate.
Interpretation forbidden: summing per-source unique protein counts into a
global total; reading record counts as evidence quality; treating absence
from a source as negative evidence.

## Reproduce / verify

PACKAGE_VERIFY gate (runs first, offline):

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```

This analysis (gate included, deterministic, byte-stable):

```bash
{reproduction_command}
```

Outputs: `q1_records_vs_entities.csv` (per-source aggregate),
`q1_records_vs_entities.svg` (figure), `analysis_manifest.json`
(provenance: candidate contract, input and output SHA-256 hashes,
aggregation rule, derived totals). Inputs are only the packaged
`mfp_source_records.csv` and `mfp_proteins.csv`. Reruns are idempotent for
identical bytes; changed bytes require a new analysis version.
"""


def run(candidate_dir: Path, output_dir: Path,
        reproduction_command: str | None = None) -> int:
    """Verify, aggregate, render and publish Question 1 outputs.

    Fails non-zero without writing if any verification, aggregation or
    conservation check fails. Never writes inside the candidate.
    """
    try:
        manifest = load_manifest(candidate_dir)
        input_hashes = verify_inputs(candidate_dir, manifest)
        rows, totals = aggregate(candidate_dir, manifest)
        svg_bytes = render_svg(
            rows, totals,
            candidate_label=str(manifest.get("candidate_id") or "unknown-candidate")
        ).encode("utf-8")
        csv_bytes = render_csv(rows).encode("utf-8")
        readme_bytes = render_readme(
            reproduction_command
            or "PYTHONPATH=src python scripts/analyze_question1.py").encode("utf-8")
        provenance = {
            "analysis_version": ANALYSIS_VERSION,
            "question": "Q1 source records vs unique protein entities by source",
            "candidate": {
                "candidate_id": manifest.get("candidate_id"),
                "catalog_contract": manifest.get("catalog_contract"),
                "protein_id_scheme": manifest.get("protein_id_scheme"),
            },
            "inputs": {
                name: {"sha256": input_hashes[name]} for name in INPUT_TABLES},
            "aggregation_rule": (
                "source_record_count = rows per source_name in mfp_source_records.csv; "
                "unique_protein_count = distinct protein_id within each source; per-source "
                "unique counts are not additive across sources"),
            "derived_totals": totals,
            "outputs": {
                "q1_records_vs_entities.csv": {
                    "sha256": hashlib.sha256(csv_bytes).hexdigest()},
                "q1_records_vs_entities.svg": {
                    "sha256": hashlib.sha256(svg_bytes).hexdigest()},
            },
            "interpretation": {
                "allowed": [
                    "describing per-source record and unique-protein counts of the candidate"],
                "forbidden": [
                    "summing per-source unique protein counts into a global total",
                    "reading counts as validated articles, GO support or prevalence",
                    "statistical significance claims"],
            },
        }
        provenance_bytes = (
            json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
        outputs = {
            "q1_records_vs_entities.csv": csv_bytes,
            "q1_records_vs_entities.svg": svg_bytes,
            "analysis_manifest.json": provenance_bytes,
            "README.md": readme_bytes,
        }
        if output_dir.exists():
            for name, content in outputs.items():
                path = output_dir / name
                if path.is_file():
                    if path.read_bytes() != content:
                        raise AnalysisError(
                            f"refusing to overwrite existing {path} with different bytes; "
                            "use a new analysis version")
                else:
                    raise AnalysisError(
                        f"existing output directory {output_dir} lacks {name}; "
                        "refusing partial overwrite")
        else:
            output_dir.mkdir(parents=True)
        for name, content in outputs.items():
            (output_dir / name).write_bytes(content)
        print(f"Q1 analysis published at {output_dir} "
              f"(records={totals['source_record_count']}, "
              f"proteins={totals['protein_entity_count']})")
        return 0
    except (AnalysisError, OSError, KeyError, ValueError) as exc:
        print(f"[analysis-q1] {exc}", file=sys.stderr)
        return 1
