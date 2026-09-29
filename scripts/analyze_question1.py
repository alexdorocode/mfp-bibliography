#!/usr/bin/env python3
"""Question 1 analysis CLI: source records vs unique protein entities by source.

Runs the offline PACKAGE_VERIFY gate first (fails non-zero, no outputs, if
the candidate is not intact), then computes deterministic aggregates from the
packaged CSVs only and publishes CSV + SVG + provenance + README to the
output location prescribed by docs/analysis/five-source-descriptive-study-plan.md.
Never writes inside the candidate.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from mfp_bibliography.analysis_q1 import run

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_ID = "mfp-catalog-candidate-v0.2.0"
DEFAULT_CANDIDATE = REPO_ROOT / "releases" / CANDIDATE_ID
DEFAULT_OUTPUT = REPO_ROOT / "analysis" / "five-source-v0.2.0" / "q1_records_vs_entities"


def package_verify(releases_root: Path) -> int:
    script = REPO_ROOT / "scripts" / "package_catalog_candidate.py"
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src")}
    result = subprocess.run(
        [sys.executable, str(script), "--verify-package",
         "--releases-root", str(releases_root)],
        capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(result.stdout.strip())
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    candidate_dir = args.candidate_dir.resolve()
    if candidate_dir.name != CANDIDATE_ID:
        print(f"[analysis-q1] candidate directory must be {CANDIDATE_ID}",
              file=sys.stderr)
        return 1
    gate = package_verify(candidate_dir.parent)
    if gate != 0:
        print("[analysis-q1] PACKAGE_VERIFY gate failed; no outputs published.",
              file=sys.stderr)
        return gate
    return run(candidate_dir, args.output_dir.resolve(),
               reproduction_command="PYTHONPATH=src python scripts/analyze_question1.py")


if __name__ == "__main__":
    raise SystemExit(main())
