#!/usr/bin/env python3
"""Stage PIL-04.1B: QuickGO Pilot Concordance Recomparison & Transition Analysis CLI Runner.

Orchestrates verified offline input loading, cryptographic digest checks, isolated
staging directory execution, recomputed concordance generation, transition matrix
evaluation, schema and programmatic invariant validation, runtime manifest creation,
and atomic publication.

100% offline, zero network access, bitwise deterministic.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
import importlib.metadata
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mfp_bibliography.quickgo_concordance import (
    CONCORDANCE_COLUMNS,
    TRANSITION_COLUMNS,
    VERIFIED_COHORT_PAIRS,
    ConcordanceValidationError,
    build_concordance_matrix,
    build_concordance_transition_matrix,
    load_candidate_proteins,
    parse_concordance_csv_row,
    parse_csv_value,
    parse_transition_csv_row,
    validate_recomputed_concordance_matrix,
    validate_transition_matrix,
)

FROZEN_PILOT_ROW_COUNT = 353
FROZEN_PILOT_UNIVERSE_COUNT = 72

FROZEN_PILOT_EXPECTED_DIGESTS: Dict[str, str] = {
    "baseline_concordance": "12ce77f2421ee07f2230466c5b0788a95908ac950dd6125ab37a8b88f64ef8a7",
    "normalized_annotations": "2a6255c5059545d8b1bab06a6d73872d2a064add1c0dd7b25097bd95e47012de",
    "raw_coverage": "981c592f12bceb02e2c7a6404126dc7ad55053b2bd6383919658a5423241b9be",
    "source_annotations": "949e5050f6cb3e899f70ee32668694fa99a173b6ee30297aba090ebbbb105dda",
    "derived_aspects": "e4500d3cf93f2e8861ab7ea5a91a5f9ef55617dd3c6413f4b3abd2c7cf6b204e",
    "functional_coverage": "c29d28712c613211c6183f49ef304a63d94dd64a40de2ff682641037e2573e8d",
    "catalog_proteins": "a2e6cde1eebcb620cc94e77f2d86923bbedc8d25f62f0acd888d3714930e5bfc",
}

FROZEN_UPSTREAM_MANIFEST_DIGESTS: Dict[str, str] = {
    "pil041a_manifest_sha256": "5fe29c5fdefbbe0d14b755844dcecf9b6ca29afc460eb4aec7b3479b596b077f",
    "stage_p3_manifest_sha256": "01c6b54ac54ea34f7f1ab9ce49c074da347b62f1b13e437cb485fb34aa7515a7",
}


@dataclass(frozen=True)
class PilotInputContract:
    """Enforces cryptographic digests, cardinalities, universes, and lineage verification."""
    expected_digests: Optional[Dict[str, str]] = None
    expected_upstream_manifest_digests: Optional[Dict[str, str]] = None
    expected_source_cardinality: Optional[int] = FROZEN_PILOT_ROW_COUNT
    expected_derived_cardinality: Optional[int] = FROZEN_PILOT_ROW_COUNT
    expected_universe_count: Optional[int] = FROZEN_PILOT_UNIVERSE_COUNT
    expected_canonical_pairs: Optional[List[Tuple[str, str]]] = None
    p3_manifest_path: Optional[Path] = None
    pil041a_manifest_path: Optional[Path] = None
    enforce_upstream_manifest_verification: bool = True


PILOT_PRODUCTION_CONTRACT = PilotInputContract(
    expected_digests=FROZEN_PILOT_EXPECTED_DIGESTS,
    expected_upstream_manifest_digests=FROZEN_UPSTREAM_MANIFEST_DIGESTS,
    expected_source_cardinality=FROZEN_PILOT_ROW_COUNT,
    expected_derived_cardinality=FROZEN_PILOT_ROW_COUNT,
    expected_universe_count=FROZEN_PILOT_UNIVERSE_COUNT,
    expected_canonical_pairs=VERIFIED_COHORT_PAIRS,
    enforce_upstream_manifest_verification=True,
)


def compute_file_sha256(path: Path) -> str:
    """Compute the SHA-256 digest of a local file."""
    if not path.is_file():
        raise FileNotFoundError(f"File not found for hash calculation: {path}")
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_csv_rows(path: Path) -> List[Dict[str, str]]:
    """Load a CSV file as a list of string dictionaries."""
    if not path.is_file():
        raise FileNotFoundError(f"CSV input file not found: {path}")
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_git_head_commit(repo_root: Path) -> str:
    """Query git HEAD commit hash read-only."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "unknown"


def get_git_status(repo_root: Path) -> str:
    """Query git working tree status read-only."""
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return "dirty" if res.stdout.strip() else "clean"
    except Exception:
        return "unknown"


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage PIL-04.1B QuickGO Concordance Recomparison & Transition Analysis Runner."
    )
    parser.add_argument(
        "--baseline-concordance",
        type=Path,
        default=Path("data/interim/pilot/quickgo_slice/quickgo_concordance_pilot.csv"),
        help="Path to frozen baseline concordance CSV.",
    )
    parser.add_argument(
        "--normalized-annotations",
        type=Path,
        default=Path("data/interim/pilot/quickgo_slice/quickgo_annotations_pilot.csv"),
        help="Path to normalized QuickGO annotations CSV.",
    )
    parser.add_argument(
        "--raw-coverage",
        type=Path,
        default=Path("data/interim/pilot/quickgo_slice/quickgo_coverage_pilot.csv"),
        help="Path to raw QuickGO coverage CSV.",
    )
    parser.add_argument(
        "--source-annotations",
        type=Path,
        default=Path("data/interim/pilot/source_go_annotations_pilot.csv"),
        help="Path to source GO annotations CSV.",
    )
    parser.add_argument(
        "--derived-aspects",
        type=Path,
        default=Path("data/interim/pilot/quickgo_slice_enriched/derived_source_go_aspects_pilot.csv"),
        help="Path to PIL-04.1A derived source GO aspects CSV.",
    )
    parser.add_argument(
        "--functional-coverage",
        type=Path,
        default=Path("data/interim/pilot/functional_coverage_pilot.csv"),
        help="Path to functional coverage CSV.",
    )
    parser.add_argument(
        "--catalog-proteins",
        type=Path,
        default=Path("releases/mfp-catalog-candidate-v0.3.0/mfp_proteins.csv"),
        help="Path to candidate catalog mfp_proteins.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/interim/pilot/quickgo_slice_recomparison"),
        help="Destination directory for recomputed concordance and transition artifacts.",
    )
    parser.add_argument(
        "--concordance-schema",
        type=Path,
        default=Path("data/curated/quickgo_concordance.schema.json"),
        help="Path to concordance schema.",
    )
    parser.add_argument(
        "--transition-schema",
        type=Path,
        default=Path("data/curated/quickgo_concordance_transition.schema.json"),
        help="Path to transition schema.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    return parser.parse_args(argv)


def run_recomparison_pipeline(
    baseline_concordance_path: Path,
    normalized_annotations_path: Path,
    raw_coverage_path: Path,
    source_annotations_path: Path,
    derived_aspects_path: Path,
    functional_coverage_path: Path,
    catalog_proteins_path: Path,
    output_dir: Path,
    concordance_schema_path: Path,
    transition_schema_path: Path,
    contract: Optional[PilotInputContract] = None,
    cli_arguments: Optional[List[str]] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Execute the offline concordance recomparison pipeline."""
    start_time = datetime.now(timezone.utc)
    repo_root = Path(__file__).resolve().parents[1]

    effective_contract = contract if contract is not None else PILOT_PRODUCTION_CONTRACT

    # 1. Resolve and validate paths
    output_dir_res = output_dir.resolve()
    base_conc_res = baseline_concordance_path.resolve()
    norm_ann_res = normalized_annotations_path.resolve()
    raw_cov_res = raw_coverage_path.resolve()
    source_ann_res = source_annotations_path.resolve()
    derived_asp_res = derived_aspects_path.resolve()
    func_cov_res = functional_coverage_path.resolve()
    catalog_prot_res = catalog_proteins_path.resolve()
    conc_schema_res = concordance_schema_path.resolve()
    trans_schema_res = transition_schema_path.resolve()

    p3_manifest_res = (
        effective_contract.p3_manifest_path.resolve()
        if effective_contract.p3_manifest_path is not None
        else (base_conc_res.parent / "manifest.json").resolve()
    )
    pil041a_manifest_res = (
        effective_contract.pil041a_manifest_path.resolve()
        if effective_contract.pil041a_manifest_path is not None
        else (derived_asp_res.parent / "manifest.json").resolve()
    )

    # Comprehensive path collision and protection checks
    protected_files = [
        base_conc_res, norm_ann_res, raw_cov_res, source_ann_res,
        derived_asp_res, func_cov_res, catalog_prot_res,
        conc_schema_res, trans_schema_res,
        p3_manifest_res, pil041a_manifest_res,
    ]
    for p in protected_files:
        if p == output_dir_res or output_dir_res in p.parents or p in output_dir_res.parents:
            raise ValueError(f"Output directory '{output_dir_res}' collides with protected path '{p}'")

    protected_ancestor_dirs = [
        (repo_root / "data/interim/pilot/quickgo_slice").resolve(),
        (repo_root / "data/interim/pilot/quickgo_slice_enriched").resolve(),
        (repo_root / "data/raw").resolve(),
        (repo_root / "releases").resolve(),
        (repo_root / "docs").resolve(),
        (repo_root / "specs").resolve(),
        (repo_root / "src").resolve(),
    ]
    for ad in protected_ancestor_dirs:
        if ad.exists() and (output_dir_res == ad or output_dir_res in ad.parents or ad in output_dir_res.parents):
            raise ValueError(f"Output directory '{output_dir_res}' collides with protected repository directory '{ad}'")

    # Initial destination refusal
    if output_dir_res.exists():
        raise FileExistsError(
            f"Target directory '{output_dir_res}' already exists. "
            "Refusing to execute: initial pilot execution requires a non-existent destination "
            "to prevent accidental clobbering. Automated deletion or overwrite is disabled in this increment."
        )

    # 2. Setup run-unique isolated staging directory
    staging_timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    staging_dir = output_dir_res.parent / f".staging_recomparison_{staging_timestamp}_{os.getpid()}"
    staging_dir.mkdir(parents=True, exist_ok=False)

    try:
        if verbose:
            print("[1/7] Loading inputs and verifying cryptographic hashes...")

        # 3. Hash computation and contract verification
        input_file_map = [
            ("baseline_concordance", base_conc_res),
            ("normalized_annotations", norm_ann_res),
            ("raw_coverage", raw_cov_res),
            ("source_annotations", source_ann_res),
            ("derived_aspects", derived_asp_res),
            ("functional_coverage", func_cov_res),
            ("catalog_proteins", catalog_prot_res),
        ]
        input_hashes: Dict[str, str] = {}
        for name, p in input_file_map:
            digest = compute_file_sha256(p)
            input_hashes[name] = digest
            if effective_contract.expected_digests is not None:
                if name in effective_contract.expected_digests:
                    expected_h = effective_contract.expected_digests[name]
                    if digest != expected_h:
                        raise ConcordanceValidationError(
                            f"Cryptographic hash mismatch for frozen input '{name}' ({p}): "
                            f"actual {digest} != expected {expected_h}"
                        )

        # Load CSV rows
        base_conc_rows = load_csv_rows(base_conc_res)
        norm_ann_rows = load_csv_rows(norm_ann_res)
        raw_cov_rows = load_csv_rows(raw_cov_res)
        source_ann_rows = load_csv_rows(source_ann_res)
        derived_asp_rows = load_csv_rows(derived_asp_res)
        func_cov_rows = load_csv_rows(func_cov_res)
        catalog_map = load_candidate_proteins(catalog_prot_res)

        # Unconditional cardinality checks
        if effective_contract.expected_source_cardinality is not None:
            if len(source_ann_rows) != effective_contract.expected_source_cardinality:
                raise ConcordanceValidationError(
                    f"Source annotations row count {len(source_ann_rows)} != "
                    f"expected {effective_contract.expected_source_cardinality}"
                )

        if effective_contract.expected_derived_cardinality is not None:
            if len(derived_asp_rows) != effective_contract.expected_derived_cardinality:
                raise ConcordanceValidationError(
                    f"Derived aspects row count {len(derived_asp_rows)} != "
                    f"expected {effective_contract.expected_derived_cardinality}"
                )

        if effective_contract.expected_universe_count is not None:
            if len(base_conc_rows) != effective_contract.expected_universe_count:
                raise ConcordanceValidationError(
                    f"Baseline concordance universe count {len(base_conc_rows)} != "
                    f"expected {effective_contract.expected_universe_count}"
                )

        # Check comparison universe pairs (no silent fallback)
        target_pairs = sorted(list({(r["accession"], r["source_id"]) for r in base_conc_rows}))
        if not target_pairs:
            raise ConcordanceValidationError(
                "Baseline concordance matrix contains no valid (accession, source_id) comparison pairs"
            )

        if effective_contract.expected_canonical_pairs is not None:
            expected_sorted_pairs = sorted(effective_contract.expected_canonical_pairs)
            if target_pairs != expected_sorted_pairs:
                raise ConcordanceValidationError(
                    f"Comparison universe pairs do not match canonical contract: "
                    f"found {len(target_pairs)} pairs, expected {len(expected_sorted_pairs)} pairs"
                )

        if verbose:
            print("[2/7] Reconstructing baseline source term sets and verifying semantic baseline identity...")

        # 4. Reconstruct baseline source term sets in legacy mode
        base_source_sets: Dict[str, Optional[Set[str]]] = {}
        generated_legacy_rows = build_concordance_matrix(
            normalized_annotations=norm_ann_rows,
            raw_coverage=raw_cov_rows,
            source_go_annotations=source_ann_rows,
            functional_coverage=func_cov_rows,
            catalog_map=catalog_map,
            pairs=target_pairs,
            derived_aspects_rows=None,
            source_term_sets_out=base_source_sets,
        )

        # Semantic check of generated legacy matrix against frozen baseline
        if len(generated_legacy_rows) != len(base_conc_rows):
            raise ConcordanceValidationError(
                f"Generated legacy matrix row count ({len(generated_legacy_rows)}) != "
                f"frozen baseline row count ({len(base_conc_rows)})"
            )
        base_parsed_map = {r["concordance_id"]: parse_concordance_csv_row(r) for r in base_conc_rows}
        for leg_r in generated_legacy_rows:
            cid = leg_r["concordance_id"]
            if cid not in base_parsed_map:
                raise ConcordanceValidationError(
                    f"Generated legacy row '{cid}' not present in frozen baseline"
                )
            b_r = base_parsed_map[cid]
            for check_fld in [
                "concordance_status",
                "primary_non_evaluable_reason",
                "source_inventory_status",
                "quickgo_inventory_status",
                "source_terms_count",
                "quickgo_terms_count",
                "exact_overlap_count",
                "union_terms_count",
                "source_only_count",
                "quickgo_only_count",
                "jaccard_similarity",
            ]:
                leg_val = leg_r.get(check_fld)
                base_val = b_r.get(check_fld)
                if leg_val != base_val:
                    raise ConcordanceValidationError(
                        f"Semantic discrepancy in reconstructed legacy baseline row '{cid}' for '{check_fld}': "
                        f"generated {leg_val!r} != frozen baseline {base_val!r}"
                    )

        if verbose:
            print("[3/7] Computing enriched concordance matrix...")

        # 5. Compute recomputed concordance matrix with derived aspects
        recomp_source_sets: Dict[str, Optional[Set[str]]] = {}
        recomp_rows = build_concordance_matrix(
            normalized_annotations=norm_ann_rows,
            raw_coverage=raw_cov_rows,
            source_go_annotations=source_ann_rows,
            functional_coverage=func_cov_rows,
            catalog_map=catalog_map,
            pairs=target_pairs,
            derived_aspects_rows=derived_asp_rows,
            source_term_sets_out=recomp_source_sets,
        )

        if effective_contract.expected_universe_count is not None:
            if len(recomp_rows) != effective_contract.expected_universe_count:
                raise ConcordanceValidationError(
                    f"Recomparison row count {len(recomp_rows)} != "
                    f"expected universe count {effective_contract.expected_universe_count}"
                )

        if verbose:
            print("[4/7] Generating transition matrix...")

        # 6. Generate transition matrix with explicit source set maps
        transition_rows = build_concordance_transition_matrix(
            baseline_concordance_rows=base_conc_rows,
            recomparison_concordance_rows=recomp_rows,
            baseline_source_sets=base_source_sets,
            recomparison_source_sets=recomp_source_sets,
        )

        if effective_contract.expected_universe_count is not None:
            if len(transition_rows) != effective_contract.expected_universe_count:
                raise ConcordanceValidationError(
                    f"Transition row count {len(transition_rows)} != "
                    f"expected universe count {effective_contract.expected_universe_count}"
                )

        if verbose:
            print("[5/7] Staging CSV outputs, reloading bytes, and verifying contracts...")

        # 7. Write staged CSVs
        staged_recomp_csv = staging_dir / "quickgo_concordance_pilot_recomputed.csv"
        with open(staged_recomp_csv, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=CONCORDANCE_COLUMNS,
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )
            writer.writeheader()
            for r in recomp_rows:
                row_clean = {}
                for k in CONCORDANCE_COLUMNS:
                    val = r.get(k)
                    if val is None:
                        row_clean[k] = ""
                    elif isinstance(val, float):
                        row_clean[k] = f"{val:.4f}"
                    else:
                        row_clean[k] = str(val)
                writer.writerow(row_clean)

        staged_trans_csv = staging_dir / "quickgo_concordance_transition_pilot.csv"
        with open(staged_trans_csv, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=TRANSITION_COLUMNS,
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )
            writer.writeheader()
            for r in transition_rows:
                row_clean = {}
                for k in TRANSITION_COLUMNS:
                    val = r.get(k)
                    if val is None:
                        row_clean[k] = ""
                    elif isinstance(val, bool):
                        row_clean[k] = "true" if val else "false"
                    elif isinstance(val, float):
                        row_clean[k] = f"{val:.4f}"
                    else:
                        row_clean[k] = str(val)
                writer.writerow(row_clean)

        # 8. Reload staged CSVs from disk and validate published bytes
        reloaded_recomp_rows = load_csv_rows(staged_recomp_csv)
        reloaded_trans_rows = load_csv_rows(staged_trans_csv)

        validate_recomputed_concordance_matrix(
            rows=reloaded_recomp_rows,
            schema_path=conc_schema_res,
        )

        validate_transition_matrix(
            rows=reloaded_trans_rows,
            baseline_rows=base_conc_rows,
            recomparison_rows=reloaded_recomp_rows,
            schema_path=trans_schema_res,
        )

        if effective_contract.expected_universe_count is not None:
            if len(reloaded_recomp_rows) != effective_contract.expected_universe_count:
                raise ConcordanceValidationError(
                    f"Reloaded recomp row count {len(reloaded_recomp_rows)} != {effective_contract.expected_universe_count}"
                )
            if len(reloaded_trans_rows) != effective_contract.expected_universe_count:
                raise ConcordanceValidationError(
                    f"Reloaded transition row count {len(reloaded_trans_rows)} != {effective_contract.expected_universe_count}"
                )

        if verbose:
            print("[6/7] Authoring execution manifest with prospective provenance...")

        # 9. Compute hashes of reloaded staged outputs
        recomp_hash = compute_file_sha256(staged_recomp_csv)
        trans_hash = compute_file_sha256(staged_trans_csv)

        # Code & schema digests
        runner_hash = compute_file_sha256(Path(__file__).resolve())
        module_hash = compute_file_sha256(
            (repo_root / "src/mfp_bibliography/quickgo_concordance.py").resolve()
        )
        conc_schema_hash = compute_file_sha256(conc_schema_res)
        trans_schema_hash = compute_file_sha256(trans_schema_res)

        end_time = datetime.now(timezone.utc)
        duration_sec = round((end_time - start_time).total_seconds(), 4)

        # Upstream lineage verification
        upstream_lineage: Dict[str, Any] = {}
        if effective_contract.enforce_upstream_manifest_verification:
            if not p3_manifest_res.is_file():
                raise FileNotFoundError(f"Required Stage P3 manifest not found at '{p3_manifest_res}'")
            if not pil041a_manifest_res.is_file():
                raise FileNotFoundError(f"Required PIL-04.1A manifest not found at '{pil041a_manifest_res}'")

            p3_digest = compute_file_sha256(p3_manifest_res)
            pil041a_digest = compute_file_sha256(pil041a_manifest_res)

            # Explicit expected-versus-actual manifest digest checks
            if effective_contract.expected_upstream_manifest_digests is not None:
                exp_p3 = effective_contract.expected_upstream_manifest_digests.get("stage_p3_manifest_sha256")
                if exp_p3 and p3_digest != exp_p3:
                    raise ConcordanceValidationError(
                        f"Stage P3 upstream manifest cryptographic hash mismatch ({p3_manifest_res}): "
                        f"actual {p3_digest} != expected {exp_p3}"
                    )
                exp_pil = effective_contract.expected_upstream_manifest_digests.get("pil041a_manifest_sha256")
                if exp_pil and pil041a_digest != exp_pil:
                    raise ConcordanceValidationError(
                        f"PIL-04.1A upstream manifest cryptographic hash mismatch ({pil041a_manifest_res}): "
                        f"actual {pil041a_digest} != expected {exp_pil}"
                    )

            p3_manifest_json = json.loads(p3_manifest_res.read_text(encoding="utf-8"))
            pil041a_manifest_json = json.loads(pil041a_manifest_res.read_text(encoding="utf-8"))

            # Verify P3 manifest structure and consumed baseline concordance relationship
            p3_out_inv = p3_manifest_json.get("output_inventory")
            if not isinstance(p3_out_inv, dict):
                raise ConcordanceValidationError("Stage P3 manifest missing required 'output_inventory' section")

            p3_out_conc_entry = p3_out_inv.get("quickgo_concordance_pilot.csv")
            if not isinstance(p3_out_conc_entry, dict) or "sha256" not in p3_out_conc_entry:
                raise ConcordanceValidationError(
                    "Stage P3 manifest missing required output entry 'quickgo_concordance_pilot.csv' with 'sha256'"
                )
            p3_out_conc = p3_out_conc_entry["sha256"]
            if p3_out_conc != input_hashes["baseline_concordance"]:
                raise ConcordanceValidationError(
                    f"P3 manifest output digest mismatch for baseline concordance: "
                    f"{p3_out_conc} != consumed input {input_hashes['baseline_concordance']}"
                )

            # Verify PIL-04.1A manifest structure and consumed derived aspects relationship
            pil041a_outputs = pil041a_manifest_json.get("outputs")
            if not isinstance(pil041a_outputs, dict):
                raise ConcordanceValidationError("PIL-04.1A manifest missing required 'outputs' section")

            derived_aspects_entry = None
            for out_key, out_val in pil041a_outputs.items():
                if out_key.endswith("derived_source_go_aspects_pilot.csv") or out_key == "derived_aspects":
                    derived_aspects_entry = out_val
                    break

            if not isinstance(derived_aspects_entry, dict) or "sha256" not in derived_aspects_entry:
                raise ConcordanceValidationError(
                    "PIL-04.1A manifest missing required output entry for derived aspects with 'sha256'"
                )
            pil041a_derived_sha = derived_aspects_entry["sha256"]
            if pil041a_derived_sha != input_hashes["derived_aspects"]:
                raise ConcordanceValidationError(
                    f"PIL-04.1A manifest output digest mismatch for derived aspects: "
                    f"{pil041a_derived_sha} != consumed input {input_hashes['derived_aspects']}"
                )

            # Verify PIL-04.1A source annotations input relationship if present
            pil041a_inputs = pil041a_manifest_json.get("inputs")
            if isinstance(pil041a_inputs, dict):
                for in_key, in_val in pil041a_inputs.items():
                    if in_key.endswith("source_go_annotations_pilot.csv") and isinstance(in_val, dict) and "sha256" in in_val:
                        if in_val["sha256"] != input_hashes["source_annotations"]:
                            raise ConcordanceValidationError(
                                f"PIL-04.1A manifest input digest mismatch for source annotations: "
                                f"{in_val['sha256']} != consumed input {input_hashes['source_annotations']}"
                            )

            # Require ontology metadata directly from PIL-04.1A summary section
            pil041a_summary = pil041a_manifest_json.get("summary")
            if not isinstance(pil041a_summary, dict):
                raise ConcordanceValidationError("PIL-04.1A manifest missing required 'summary' section")

            ont_version = pil041a_summary.get("ontology_version")
            ont_sha = pil041a_summary.get("ontology_sha256")
            if not ont_version or not str(ont_version).strip():
                raise ConcordanceValidationError(
                    "Missing or empty required lineage field 'ontology_version' in PIL-04.1A manifest summary"
                )
            if not ont_sha or not str(ont_sha).strip():
                raise ConcordanceValidationError(
                    "Missing or empty required lineage field 'ontology_sha256' in PIL-04.1A manifest summary"
                )

            upstream_lineage = {
                "pil041a_manifest_sha256": pil041a_digest,
                "stage_p3_manifest_sha256": p3_digest,
                "pinned_ontology_data_version": str(ont_version).strip(),
                "pinned_ontology_sha256": str(ont_sha).strip(),
            }
        else:
            upstream_lineage = {
                "pil041a_manifest_sha256": compute_file_sha256(pil041a_manifest_res) if pil041a_manifest_res.is_file() else "synthetic_lineage",
                "stage_p3_manifest_sha256": compute_file_sha256(p3_manifest_res) if p3_manifest_res.is_file() else "synthetic_lineage",
                "pinned_ontology_data_version": "releases/2026-01-23",
                "pinned_ontology_sha256": "eee63704b5fe1c4680440341e07e759e92a472f3d30272e4f47497aa97943391",
            }

        effective_config = {
            "baseline_concordance_path": str(base_conc_res),
            "normalized_annotations_path": str(norm_ann_res),
            "raw_coverage_path": str(raw_cov_res),
            "source_annotations_path": str(source_ann_res),
            "derived_aspects_path": str(derived_asp_res),
            "functional_coverage_path": str(func_cov_res),
            "catalog_proteins_path": str(catalog_prot_res),
            "output_dir": str(output_dir_res),
            "concordance_schema_path": str(conc_schema_res),
            "transition_schema_path": str(trans_schema_res),
            "verbose": verbose,
        }

        manifest = {
            "task_id": "PIL-04.1B",
            "task_title": "QuickGO Pilot Concordance Recomparison & Transition Analysis",
            "execution_timestamp_utc": start_time.isoformat(),
            "execution_duration_seconds": duration_sec,
            "git_commit": get_git_head_commit(repo_root),
            "git_status": get_git_status(repo_root),
            "cli_arguments": cli_arguments or [],
            "effective_configuration": effective_config,
            "platform_environment": {
                "python_version": sys.version.split()[0],
                "system": platform.system(),
                "machine": platform.machine(),
            },
            "dependency_versions": {
                "python": platform.python_version(),
                "jsonschema": importlib.metadata.version("jsonschema"),
            },
            "upstream_lineage_manifests": upstream_lineage,
            "code_and_schema_digests": {
                "runner_script_sha256": runner_hash,
                "concordance_module_sha256": module_hash,
                "concordance_schema_sha256": conc_schema_hash,
                "transition_schema_sha256": trans_schema_hash,
            },
            "input_dataset_digests": input_hashes,
            "output_dataset_digests": {
                "quickgo_concordance_pilot_recomputed.csv": recomp_hash,
                "quickgo_concordance_transition_pilot.csv": trans_hash,
            },
            "cardinality_summary": {
                "baseline_concordance_rows": len(base_conc_rows),
                "recomparison_concordance_rows": len(recomp_rows),
                "transition_matrix_rows": len(transition_rows),
            },
        }

        staged_manifest_path = staging_dir / "manifest.json"
        staged_manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        if verbose:
            print(f"[7/7] Publishing staging directory to '{output_dir_res}'...")

        # 10. Check destination again before publication to prevent race overwrite
        if output_dir_res.exists():
            raise FileExistsError(
                f"Destination directory '{output_dir_res}' appeared or was created concurrently before publication."
            )

        # 11. Atomic move of staging directory to output_dir
        staging_dir.rename(output_dir_res)

        return manifest

    finally:
        # Crash cleanup: ensure only this run's staging directory is removed if it still exists
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint."""
    raw_args = sys.argv[1:] if argv is None else argv
    args = parse_args(raw_args)
    try:
        run_recomparison_pipeline(
            baseline_concordance_path=args.baseline_concordance,
            normalized_annotations_path=args.normalized_annotations,
            raw_coverage_path=args.raw_coverage,
            source_annotations_path=args.source_annotations,
            derived_aspects_path=args.derived_aspects,
            functional_coverage_path=args.functional_coverage,
            catalog_proteins_path=args.catalog_proteins,
            output_dir=args.output_dir,
            concordance_schema_path=args.concordance_schema,
            transition_schema_path=args.transition_schema,
            cli_arguments=raw_args,
            verbose=args.verbose,
        )
        print("Recomparison pipeline completed successfully.")
        return 0
    except Exception as exc:
        print(f"Error executing recomparison pipeline: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
