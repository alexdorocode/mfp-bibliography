"""Question 4 analysis: MoonProt MPID snapshot coverage (statuses only).

Deterministic, stdlib-only aggregation over the packaged
`mfp_coverage.csv` of `mfp-catalog-candidate-v0.2.0` (see
docs/analysis/five-source-descriptive-study-plan.md, Q4).

The MPID universe is DECLARED, not inferred from filenames: the manifest's
`measured_counts.moonprot_coverage` (acquired/known_absent/unresolved) sums
to the snapshot universe size, and every MPID 1..N must appear exactly once.
Coverage statuses are acquisition bookkeeping only: known_absent and
unresolved MPIDs are NOT negative examples and NOT non-multifunctional
proteins; they never create protein entities (ADR-006). The figure
denominator is MPIDs, not protein entities or articles.
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
    read_csv_rows,
    sha256_file,
)

ANALYSIS_VERSION = "q4-moonprot-coverage-v1"
BAR_COLOR = "#0072B2"
TEXT_COLOR = "#333333"
COVERAGE_TABLE = "mfp_coverage.csv"
ALLOWED_STATUSES = ("acquired", "known_absent", "unresolved")
# Pinned candidate v0.2.0 expectations (derived first, then compared).
PINNED_KNOWN_ABSENT_MPIDS = (103,)
PINNED_UNRESOLVED_MPIDS = (542, 543, 626)


def verify_coverage_input(candidate_dir: Path, manifest: dict) -> str:
    """Enforce the packaged coverage-table hash before analysis."""
    path = candidate_dir / COVERAGE_TABLE
    if not path.is_file():
        raise AnalysisError(f"missing packaged input {COVERAGE_TABLE}")
    checksums_path = candidate_dir / "checksums.sha256"
    if not checksums_path.is_file():
        raise AnalysisError(f"missing {checksums_path}")
    listed = {}
    for line in checksums_path.read_text().splitlines():
        digest, name = line.split("  ", 1)
        listed[name] = digest
    actual = sha256_file(path)
    expected = manifest["packaged_outputs"].get(COVERAGE_TABLE, {}).get("sha256")
    if expected is None:
        raise AnalysisError(
            f"MANIFEST.json lacks packaged_outputs entry for {COVERAGE_TABLE}")
    if actual != expected:
        raise AnalysisError(
            f"input {COVERAGE_TABLE} hash mismatch: file is {actual}, "
            f"manifest says {expected}")
    if listed.get(COVERAGE_TABLE) != actual:
        raise AnalysisError(f"input {COVERAGE_TABLE} hash mismatch vs checksums.sha256")
    return actual


def aggregate(candidate_dir: Path, manifest: dict,
              expected_known_absent: tuple[int, ...] | None = None,
              expected_unresolved: tuple[int, ...] | None = None) -> dict:
    """Status counts over the declared MPID universe, with integrity checks."""
    counts = manifest["measured_counts"]
    if "moonprot_coverage" not in counts:
        raise AnalysisError("MANIFEST.json measured_counts lacks moonprot_coverage")
    declared = counts["moonprot_coverage"]
    universe_size = sum(declared.values())

    rows = read_csv_rows(candidate_dir / COVERAGE_TABLE)
    if len(rows) != universe_size:
        raise AnalysisError(
            f"packaged coverage rows {len(rows)} != declared universe size "
            f"{universe_size} (from manifest moonprot_coverage)")
    mpids: list[int] = []
    status_by_mpid: dict[int, str] = {}
    for row in rows:
        if row["status"] not in ALLOWED_STATUSES:
            raise AnalysisError(
                f"unexpected coverage status {row['status']!r} for MPID {row['mpid']}")
        try:
            mpid = int(row["mpid"])
        except ValueError as exc:
            raise AnalysisError(f"non-integer mpid {row['mpid']!r}") from exc
        if mpid in status_by_mpid:
            raise AnalysisError(f"duplicate MPID {mpid} in packaged coverage table")
        status_by_mpid[mpid] = row["status"]
        mpids.append(mpid)
    expected_universe = set(range(1, universe_size + 1))
    missing = sorted(expected_universe - set(mpids))
    if missing:
        raise AnalysisError(
            f"{len(missing)} MPIDs of the declared universe 1..{universe_size} are "
            f"missing from the coverage table (first: {missing[0]})")

    status_counts = {status: 0 for status in ALLOWED_STATUSES}
    for status in status_by_mpid.values():
        status_counts[status] += 1
    if status_counts != declared:
        raise AnalysisError(
            f"derived status counts {status_counts} != manifest "
            f"moonprot_coverage {declared}")

    if expected_known_absent is not None:
        for mpid in expected_known_absent:
            if status_by_mpid.get(mpid) != "known_absent":
                raise AnalysisError(
                    f"MPID {mpid} is {status_by_mpid.get(mpid)!r}, expected "
                    "known_absent")
    if expected_unresolved is not None:
        for mpid in expected_unresolved:
            if status_by_mpid.get(mpid) != "unresolved":
                raise AnalysisError(
                    f"MPID {mpid} is {status_by_mpid.get(mpid)!r}, expected "
                    "unresolved")
    return {
        "status_counts": status_counts,
        "universe_size": universe_size,
        "known_absent_mpids": sorted(
            m for m, s in status_by_mpid.items() if s == "known_absent"),
        "unresolved_mpids": sorted(
            m for m, s in status_by_mpid.items() if s == "unresolved"),
    }


def render_csv(totals: dict) -> str:
    lines = ["status,mpid_count"]
    lines += [
        f"{status},{totals['status_counts'][status]}"
        for status in sorted(totals["status_counts"])]
    return "\n".join(lines) + "\n"


def render_svg(totals: dict) -> str:
    """Deterministic labeled bar chart; denominator is MPIDs, not proteins."""
    width, height = 980, 430
    left, right, top, bottom = 90, 40, 96, 118
    plot_w = width - left - right
    plot_h = height - top - bottom
    statuses = sorted(totals["status_counts"])
    max_val = max(totals["status_counts"].values())
    group_w = plot_w / len(statuses)
    bar_w = min(90.0, group_w / 2)
    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Q4: MoonProt MPID snapshot coverage by status</title>',
        '<desc id="desc">Bar chart of MoonProt snapshot MPIDs per coverage status. '
        'The denominator is the declared MPID universe, not protein entities. '
        'Values are shown above each bar.</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="26" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="16" font-weight="bold" fill="{TEXT_COLOR}">Q4: MoonProt MPID '
        'snapshot coverage by status</text>',
        f'<text x="{left}" y="46" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">Candidate mfp-catalog-candidate-v0.2.0 — '
        'acquisition bookkeeping only, not evidence or protein counts</text>',
        f'<text x="{left}" y="66" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">unit: MPID; denominator '
        f'{totals["universe_size"]} (declared snapshot universe 1..'
        f'{totals["universe_size"]}, from the manifest)</text>',
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
    for index, status in enumerate(statuses):
        cx = left + group_w * (index + 0.5)
        value = totals["status_counts"][status]
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
            f'fill="{TEXT_COLOR}">{escape(status)}</text>')
    caption = (
        f"Denominator: {totals['universe_size']} MPIDs of the declared MoonProt "
        f"snapshot universe 1..{totals['universe_size']} — NOT protein entities and "
        "NOT articles. known_absent and unresolved MPIDs are coverage-only "
        "statuses (ADR-006): they are not negative examples and not "
        "non-multifunctional proteins, and they never create protein entities.")
    parts.append(
        f'<text x="{left}" y="{height - 26}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="10" fill="{TEXT_COLOR}">{escape(caption)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render_readme(reproduction_command: str) -> str:
    return f"""# Q4 outputs: MoonProt MPID snapshot coverage by status

Acquisition bookkeeping only. NOT protein counts, NOT article counts, NOT
evidence about absent proteins. No statistical significance claims.

## Definition

`mfp_coverage.csv` holds one row per MoonProt MPID of the DECLARED snapshot
universe (from the candidate manifest's `measured_counts.moonprot_coverage`;
702 acquired + 1 known_absent + 3 unresolved = 706, universe 1..706). The
universe is not inferred from filenames. Coverage statuses are
administrative: known_absent (MPID 103) and unresolved (MPIDs 542, 543,
626) MPIDs are NOT negative examples and NOT non-multifunctional proteins;
they never create protein entities (ADR-006).

## Reproduce / verify

PACKAGE_VERIFY gate (runs first, offline):

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```

This analysis (gate included, deterministic, byte-stable):

```bash
{reproduction_command}
```

Outputs: `q4_moonprot_coverage_status.csv` (status, mpid_count),
`q4_moonprot_coverage.svg` (denominator: 706 MPIDs),
`analysis_manifest.json` (candidate contract, input and output SHA-256
hashes, definitions, derived totals). Reruns are idempotent for identical
bytes; changed bytes require a new analysis version.
"""


def run(candidate_dir: Path, output_dir: Path,
        expected_known_absent: tuple[int, ...] | None = None,
        expected_unresolved: tuple[int, ...] | None = None,
        reproduction_command: str | None = None) -> int:
    """Verify, aggregate, render and publish Question 4 outputs."""
    try:
        manifest = load_manifest(candidate_dir)
        input_hash = verify_coverage_input(candidate_dir, manifest)
        totals = aggregate(
            candidate_dir, manifest,
            expected_known_absent=expected_known_absent,
            expected_unresolved=expected_unresolved)
        csv_bytes = render_csv(totals).encode("utf-8")
        svg_bytes = render_svg(totals).encode("utf-8")
        readme_bytes = render_readme(
            reproduction_command
            or "PYTHONPATH=src python scripts/analyze_question4.py").encode("utf-8")
        provenance = {
            "analysis_version": ANALYSIS_VERSION,
            "question": "Q4 MoonProt MPID snapshot coverage by status",
            "candidate": {
                "candidate_id": manifest.get("candidate_id"),
                "catalog_contract": manifest.get("catalog_contract"),
                "protein_id_scheme": manifest.get("protein_id_scheme"),
            },
            "inputs": {COVERAGE_TABLE: {"sha256": input_hash}},
            "definitions": {
                "universe": "declared by manifest moonprot_coverage (sum of "
                            "statuses); every MPID 1..N appears exactly once; not "
                            "inferred from filenames",
                "status_semantics": "coverage-only acquisition bookkeeping; "
                                    "known_absent/unresolved are not negative "
                                    "examples, not non-multifunctional proteins, "
                                    "and never protein entities (ADR-006)",
                "denominator": "MPIDs of the snapshot universe, NOT protein "
                               "entities or articles",
            },
            "derived_totals": totals,
            "outputs": {
                "q4_moonprot_coverage_status.csv": {
                    "sha256": hashlib.sha256(csv_bytes).hexdigest()},
                "q4_moonprot_coverage.svg": {
                    "sha256": hashlib.sha256(svg_bytes).hexdigest()},
            },
            "interpretation": {
                "allowed": ["describing acquisition coverage of the local MoonProt "
                            "snapshot"],
                "forbidden": [
                    "treating known_absent or unresolved MPIDs as negative examples "
                    "or non-multifunctional proteins",
                    "claiming complete MoonProt coverage or a complete bibliography",
                    "statistical significance claims"],
            },
        }
        provenance_bytes = (
            json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
        outputs = {
            "q4_moonprot_coverage_status.csv": csv_bytes,
            "q4_moonprot_coverage.svg": svg_bytes,
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
        print(f"Q4 analysis published at {output_dir} "
              f"(universe={totals['universe_size']}, "
              f"statuses={totals['status_counts']})")
        return 0
    except (AnalysisError, OSError, KeyError, ValueError) as exc:
        print(f"[analysis-q4] {exc}", file=sys.stderr)
        return 1
