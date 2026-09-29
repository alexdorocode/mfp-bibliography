"""Question 5 analysis (v2, corrected provenance): status-label inventory.

Deterministic, stdlib-only aggregation over the packaged
`mfp_source_records.csv` of `mfp-catalog-candidate-v0.2.0` (see
docs/analysis/five-source-descriptive-study-plan.md, Q5).

Corrected semantics (supersedes q5-status-labels-v1, which mislabeled
policy-mapped statuses as "verbatim"):
- SOURCE-PROVIDED labels are grouped by `raw_claim_value` (verbatim spelling
  and case preserved), after verifying `raw_claim_field` is the documented
  status field for that source (MoonDB and PlantMP: `type`, per
  configs/source_claim_policy_v0.1.yaml and the source profiles).
- The repository's policy-mapped `source_status` (e.g. PlantMP `likely` ->
  `excluded_likely`, MoonDB `Predicted` -> `predicted`) is reported
  SEPARATELY as `policy_mapped_status` and is never called verbatim. The
  two vocabularies are not a shared evidence scale and are not compared
  across sources.
- MoonProt's `source_status=valid` is a loader-generated technical status
  (scripts/build_mfp_catalog_mvp.py hard-codes it; MoonProt pages carry no
  claim field): it appears only in a separate technical-status category.
- MultifacetedProtDB and MultitaskProtDB-II provide no source status;
  their records are counted under `not_provided` (conservation includes
  them).
- `mfp_assertions.csv` is NOT used: its `original_value` copies the catalog
  field (`build_mfp_catalog_mvp.py` `original_value=record.source_status`)
  and is not independent proof of raw provenance.
- PlantMP's 12 raw `likely` records are retained in the bibliographic
  catalog; the policy excludes them only from a documented future
  derived effective status and from `primary_target_eligible`. Nothing is
  removed, and their source-exclusive protein entities are reported.
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

ANALYSIS_VERSION = "q5-status-labels-v2-corrected-provenance"
INPUT_TABLE = "mfp_source_records.csv"
TEXT_COLOR = "#333333"
KIND_COLORS = {
    "source_provided_label": "#0072B2",
    "loader_generated_technical_status": "#E69F00",
    "not_provided": "#999999",
}
KIND_LABELS = {
    "source_provided_label": "source-provided label (raw_claim_value, verbatim)",
    "loader_generated_technical_status": "loader-generated technical status",
    "not_provided": "no source status provided",
}
# Status-availability category and documented raw status field per source.
# Justification: configs/source_claim_policy_v0.1.yaml (MFPB_0_7) maps
# MoonDB `type` (Curated/Predicted) and PlantMP `type`
# (confirmed/likely/predicted); MoonProt pages carry no claim field
# (loader sets source_status="valid"); Multifaceted/Multitask have no
# observed status field.
SOURCE_SEMANTICS = {
    "SRC_MOONDB": ("source_provided_label", "type"),
    "SRC_PLANTMP": ("source_provided_label", "type"),
    "SRC_MOONPROT": ("loader_generated_technical_status", None),
    "SRC_MULTIFACETEDPROTDB": ("not_provided", None),
    "SRC_MULTITASKPROTDB_II": ("not_provided", None),
}
POLICY_MAPPED_SOURCES = ("SRC_MOONDB", "SRC_PLANTMP")


def verify_input(candidate_dir: Path, manifest: dict) -> str:
    """Enforce the packaged records-table hash before analysis."""
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


def aggregate(candidate_dir: Path, manifest: dict) -> dict:
    """Verbatim raw labels, policy-mapped statuses and availability counts."""
    records = read_csv_rows(candidate_dir / INPUT_TABLE)
    counts = manifest["measured_counts"]

    availability_counts: dict[tuple[str, str, str], int] = {}
    policy_counts: dict[tuple[str, str], int] = {}
    per_source_records: dict[str, int] = {}
    protein_sources: dict[str, set[str]] = {}
    plantmp_likely_rows: list[dict] = []

    for row in records:
        source = row["source_name"]
        if source not in SOURCE_SEMANTICS:
            raise AnalysisError(
                f"source {source!r} has no Q5 semantic classification; refusing to "
                "guess — extend SOURCE_SEMANTICS with documented justification")
        availability, status_field = SOURCE_SEMANTICS[source]
        raw_field = (row.get("raw_claim_field") or "").strip()
        raw_value = (row.get("raw_claim_value") or "").strip()
        mapped = (row.get("source_status") or "").strip()
        per_source_records[source] = per_source_records.get(source, 0) + 1
        protein_sources.setdefault(row["protein_id"], set()).add(source)

        if availability == "source_provided_label":
            if raw_field != status_field:
                raise AnalysisError(
                    f"record {row['source_record_id']} of {source}: raw_claim_field "
                    f"{raw_field!r} is not the documented status field "
                    f"{status_field!r}; refusing to group by an unrelated field")
            if not raw_value:
                raise AnalysisError(
                    f"record {row['source_record_id']} of {source}: empty "
                    "raw_claim_value; source-provided label cannot be verified")
            label = raw_value
            if not mapped:
                raise AnalysisError(
                    f"record {row['source_record_id']} of {source}: no "
                    "policy-mapped source_status alongside a raw claim value")
            policy_counts[(source, mapped)] = \
                policy_counts.get((source, mapped), 0) + 1
            if source == "SRC_PLANTMP" and raw_value == "likely":
                plantmp_likely_rows.append(row)
        elif availability == "loader_generated_technical_status":
            if raw_field or raw_value:
                raise AnalysisError(
                    f"record {row['source_record_id']} of {source}: unexpected raw "
                    f"claim ({raw_field!r}, {raw_value!r}); MoonProt records carry "
                    "no source-provided status")
            if not mapped:
                raise AnalysisError(
                    f"record {row['source_record_id']} of {source}: missing "
                    "loader-generated technical status")
            label = mapped
        else:  # not_provided
            if raw_field or raw_value:
                raise AnalysisError(
                    f"record {row['source_record_id']} of {source}: unexpected raw "
                    f"claim ({raw_field!r}, {raw_value!r}) for a status-less source")
            if mapped:
                raise AnalysisError(
                    f"record {row['source_record_id']} of {source}: source_status "
                    f"{mapped!r} present for a status-less source; refusing to "
                    "relabel an administrative value as a source label")
            label = "not_provided"
        availability_counts[(source, availability, label)] = \
            availability_counts.get((source, availability, label), 0) + 1

    availability_rows = [
        {"source_name": source, "status_availability": availability,
         "status_label": label, "record_count": count}
        for (source, availability, label), count in sorted(availability_counts.items())
    ]
    policy_rows = [
        {"source_name": source, "policy_mapped_status": status, "record_count": count}
        for (source, status), count in sorted(policy_counts.items())
    ]

    per_source: dict[str, int] = {}
    for row in availability_rows:
        per_source[row["source_name"]] = \
            per_source.get(row["source_name"], 0) + row["record_count"]
    if per_source != counts["source_record_counts"]:
        raise AnalysisError(
            f"derived per-source availability counts {per_source} != manifest "
            f"source_record_counts {counts['source_record_counts']}")
    if len(records) != counts["source_record_count"]:
        raise AnalysisError(
            f"derived total source records {len(records)} != manifest "
            f"{counts['source_record_count']}")
    policy_per_source: dict[str, int] = {}
    for row in policy_rows:
        policy_per_source[row["source_name"]] = \
            policy_per_source.get(row["source_name"], 0) + row["record_count"]
    for source in sorted(policy_per_source):
        if source not in POLICY_MAPPED_SOURCES:
            raise AnalysisError(
                f"policy-mapped statuses reported for {source!r}, which has no "
                "documented policy mapping")
        if policy_per_source[source] != counts["source_record_counts"].get(source):
            raise AnalysisError(
                f"policy-mapped counts for {source} do not sum to its record "
                "denominator")

    likely_exclusive = 0
    for row in plantmp_likely_rows:
        others = protein_sources.get(row["protein_id"], set()) - {"SRC_PLANTMP"}
        if not others:
            likely_exclusive += 1
    return {
        "availability_rows": availability_rows,
        "policy_rows": policy_rows,
        "source_record_count": len(records),
        "per_source_denominators": dict(sorted(per_source.items())),
        "plantmp_likely": {
            "records": len(plantmp_likely_rows),
            "source_exclusive_protein_ids": likely_exclusive,
            "retained_in_catalog": True,
            "excluded_only_from": "future derived effective-status precedence and "
                                  "primary_target_eligible (MFPB_0_7 policy); never "
                                  "removed from the bibliographic catalog",
        },
    }


def render_availability_csv(totals: dict) -> str:
    lines = ["source_name,status_availability,status_label,record_count"]
    lines += [
        f'{row["source_name"]},{row["status_availability"]},{row["status_label"]},'
        f'{row["record_count"]}'
        for row in totals["availability_rows"]]
    return "\n".join(lines) + "\n"


def render_policy_csv(totals: dict) -> str:
    lines = ["source_name,policy_mapped_status,record_count"]
    lines += [
        f'{row["source_name"]},{row["policy_mapped_status"]},{row["record_count"]}'
        for row in totals["policy_rows"]]
    return "\n".join(lines) + "\n"


def render_svg(totals: dict) -> str:
    """Source-faceted bars of SOURCE-PROVIDED labels (per-source scale)."""
    by_source: dict[str, list[dict]] = {}
    for row in totals["availability_rows"]:
        by_source.setdefault(row["source_name"], []).append(row)
    sources = sorted(by_source)
    panel_w, gap, top, bottom = 190, 24, 128, 106
    width = 60 + (panel_w + gap) * len(sources) + 20
    row_h = 26
    max_rows = max(len(rows) for rows in by_source.values())
    height = top + row_h * max_rows + bottom
    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Q5 v2: Source-provided status labels per source</title>',
        '<desc id="desc">Source-faceted bar chart. MoonDB and PlantMP show verbatim '
        'source-provided labels from raw_claim_value. MoonProt shows only a '
        'loader-generated technical status. MultifacetedProtDB and MultitaskProtDB-II '
        'provide no source status. Policy-mapped repository statuses are reported '
        'separately in the CSV, not here.</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="40" y="26" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="16" font-weight="bold" fill="{TEXT_COLOR}">Q5 v2: '
        'Source-provided status labels per source</text>',
        f'<text x="40" y="46" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">Candidate mfp-catalog-candidate-v0.2.0 '
        '— verbatim labels (raw_claim_value) only; NOT a shared evidence scale; '
        'not MF/NMF truth</text>',
        f'<text x="40" y="66" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" fill="{TEXT_COLOR}">unit: source record; per-source '
        'denominator in each panel; per-panel scales are independent; '
        'policy-mapped statuses are in a separate CSV</text>',
    ]
    for index, source in enumerate(sources):
        x0 = 40 + (panel_w + gap) * index
        rows = by_source[source]
        denominator = totals["per_source_denominators"][source]
        parts.append(
            f'<text x="{x0}" y="{top - 34}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="12" font-weight="bold" fill="{TEXT_COLOR}">'
            f'{escape(source)}</text>')
        parts.append(
            f'<text x="{x0}" y="{top - 20}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="10" fill="{TEXT_COLOR}">{denominator} source records</text>')
        max_val = max(row["record_count"] for row in rows)
        for row_index, row in enumerate(rows):
            y = top + row_h * row_index
            bar_w = (panel_w - 80) * row["record_count"] / max_val
            color = KIND_COLORS[row["status_availability"]]
            parts.append(
                f'<rect x="{x0}" y="{y}" width="{bar_w:.1f}" height="16" '
                f'fill="{color}"/>')
            parts.append(
                f'<text x="{x0 + bar_w + 4:.1f}" y="{y + 13}" '
                f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
                f'fill="{TEXT_COLOR}">{row["record_count"]}</text>')
            parts.append(
                f'<text x="{x0}" y="{y - 4}" font-family="Helvetica,Arial,sans-serif" '
                f'font-size="10" fill="{TEXT_COLOR}">'
                f'{escape(row["status_label"])}</text>')
            parts.append(
                f'<text x="{x0}" y="{y + 30}" font-family="Helvetica,Arial,sans-serif" '
                f'font-size="8" fill="{TEXT_COLOR}">'
                f'{escape(KIND_LABELS[row["status_availability"]])}</text>')
    caption = (
        f"Availability counts per source sum to the record denominators; total "
        f"{totals['source_record_count']} source records. Blue = source-provided "
        "verbatim label; orange = loader-generated technical status (MoonProt "
        "'valid', not an experimental evidence tier); gray = no source status "
        "provided. PlantMP 'likely' records are retained in the catalog.")
    parts.append(
        f'<text x="40" y="{height - 20}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="10" fill="{TEXT_COLOR}">{escape(caption)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render_readme(reproduction_command: str) -> str:
    return f"""# Q5 v2 outputs: source-provided status labels (corrected provenance)

Supersedes the earlier Q5 output at `../q5_status_labels/` (v1), which
incorrectly called policy-mapped repository statuses "verbatim". This v2
groups source-provided labels by `raw_claim_value` (verbatim spelling/case)
after verifying `raw_claim_field`. The v1 output is left byte-unchanged and
superseded.

An inventory only. NOT a harmonization of evidence, NOT a comparison of
label strength across sources, NOT MF/NMF truth. No statistical significance
claims.

## Semantics (per source)

- `SRC_MOONDB`, `SRC_PLANTMP`: SOURCE-PROVIDED labels from `raw_claim_value`
  (verbatim: MoonDB `Predicted`/`Curated`; PlantMP
  `confirmed`/`likely`/`predicted`), field `type` verified per record.
- Policy-mapped repository `source_status` (MoonDB `predicted`/`curated`;
  PlantMP `curated`/`excluded_likely`/`predicted`, mapped per
  `configs/source_claim_policy_v0.1.yaml`, MFPB_0_7) is reported SEPARATELY
  in `q5_policy_mapped_status_v2.csv`; it is never called verbatim and the
  two vocabularies are not a shared evidence scale.
- `SRC_MOONPROT`: `source_status=valid` is a LOADER-GENERATED technical
  status (hard-coded in `scripts/build_mfp_catalog_mvp.py`; MoonProt pages
  carry no claim field). It appears only as a technical status here, not
  among source-provided labels and not as an experimental evidence tier.
- `SRC_MULTIFACETEDPROTDB`, `SRC_MULTITASKPROTDB_II`: no source status
  provided (`not_provided`); administrative `operational_status` values are
  never shown as labels.
- `mfp_assertions.csv` is NOT used: its `original_value` copies the catalog
  field and is not independent proof of raw provenance.

## PlantMP `likely` records

All 12 raw `likely` records are RETAINED in the bibliographic catalog. The
documented policy excludes them only from a future derived effective status
(precedence below curated/predicted) and from `primary_target_eligible`
(MFPB_0_7). Nothing is removed; their source-exclusive protein entities are
reported in the provenance manifest. "likely" does not mean "not MF".

## Reproduce / verify

PACKAGE_VERIFY gate (runs first, offline):

```bash
PYTHONPATH=src python scripts/package_catalog_candidate.py --verify-package
```

This analysis (gate included, deterministic, byte-stable):

```bash
{reproduction_command}
```

Outputs: `q5_status_availability_v2.csv` (mutually exclusive availability
categories; sums to per-source denominators and 2,962 total),
`q5_policy_mapped_status_v2.csv` (secondary, mapped statuses, MoonDB and
PlantMP only), `q5_status_labels_v2.svg`,
`analysis_manifest.json`. Reruns are idempotent for identical bytes;
changed bytes require a new analysis version.
"""


def run(candidate_dir: Path, output_dir: Path,
        reproduction_command: str | None = None) -> int:
    """Verify, aggregate, render and publish Question 5 v2 outputs."""
    try:
        manifest = load_manifest(candidate_dir)
        input_hash = verify_input(candidate_dir, manifest)
        totals = aggregate(candidate_dir, manifest)
        availability_bytes = render_availability_csv(totals).encode("utf-8")
        policy_bytes = render_policy_csv(totals).encode("utf-8")
        svg_bytes = render_svg(totals).encode("utf-8")
        readme_bytes = render_readme(
            reproduction_command
            or "PYTHONPATH=src python scripts/analyze_question5.py").encode("utf-8")
        provenance = {
            "analysis_version": ANALYSIS_VERSION,
            "supersedes": "q5-status-labels-v1 (../q5_status_labels/); v1 "
                          "mislabeled policy-mapped statuses as verbatim and is "
                          "left byte-unchanged",
            "question": "Q5 source-provided status-label inventory (corrected "
                        "provenance)",
            "candidate": {
                "candidate_id": manifest.get("candidate_id"),
                "catalog_contract": manifest.get("catalog_contract"),
                "protein_id_scheme": manifest.get("protein_id_scheme"),
            },
            "inputs": {INPUT_TABLE: {"sha256": input_hash}},
            "definitions": {
                "source_provided_label": "raw_claim_value, verbatim spelling/case; "
                                         "raw_claim_field verified as the documented "
                                         "status field per source",
                "policy_mapped_status": "repository source_status mapped by "
                                        "MFPB_0_7; reported separately; never called "
                                        "verbatim; not a shared evidence scale",
                "loader_generated_technical_status": "MoonProt source_status='valid', "
                                                     "hard-coded by the catalog "
                                                     "loader; pages carry no claim "
                                                     "field; not an experimental "
                                                     "evidence tier",
                "not_provided": "source provides no status; administrative "
                                "operational_status never used as a label",
                "assertions_not_used": "mfp_assertions.original_value copies the "
                                       "catalog field; not independent proof of raw "
                                       "provenance",
            },
            "derived_totals": totals,
            "outputs": {
                "q5_status_availability_v2.csv": {
                    "sha256": hashlib.sha256(availability_bytes).hexdigest()},
                "q5_policy_mapped_status_v2.csv": {
                    "sha256": hashlib.sha256(policy_bytes).hexdigest()},
                "q5_status_labels_v2.svg": {
                    "sha256": hashlib.sha256(svg_bytes).hexdigest()},
            },
            "interpretation": {
                "allowed": ["inventory of which labels each source provides, in "
                            "original wording"],
                "forbidden": [
                    "harmonizing or comparing evidence across sources",
                    "calling policy-mapped statuses verbatim source labels",
                    "treating MoonProt 'valid' or operational_status as evidence",
                    "removing or down-weighting PlantMP 'likely' records",
                    "inferring MF/NMF truth from presence or absence of labels",
                    "statistical significance claims"],
            },
        }
        provenance_bytes = (
            json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
        outputs = {
            "q5_status_availability_v2.csv": availability_bytes,
            "q5_policy_mapped_status_v2.csv": policy_bytes,
            "q5_status_labels_v2.svg": svg_bytes,
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
        print(f"Q5 v2 analysis published at {output_dir} "
              f"(records={totals['source_record_count']}, "
              f"availability_rows={len(totals['availability_rows'])}, "
              f"policy_rows={len(totals['policy_rows'])})")
        return 0
    except (AnalysisError, OSError, KeyError, ValueError) as exc:
        print(f"[analysis-q5v2] {exc}", file=sys.stderr)
        return 1
