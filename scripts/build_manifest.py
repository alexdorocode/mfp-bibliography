#!/usr/bin/env python3
"""Safe skeleton CLI for future source manifest generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from mfp_bibliography.validation import EXPECTED_MANIFEST_HEADER


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize or refresh source_manifest.csv header without scanning external data."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Optional local input directory hint for future manifest builders (unused in bootstrap mode).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/manifests/source_manifest.csv"),
        help="Manifest output path.",
    )
    parser.add_argument("--force", action="store_true", help="Allow overwrite of a non-empty manifest file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output

    if output.exists() and output.stat().st_size > 0 and not args.force:
        print(
            "Refusing to overwrite non-empty manifest. "
            "Use --force to rewrite with header-only bootstrap content."
        )
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(EXPECTED_MANIFEST_HEADER + "\n", encoding="utf-8")
    if args.input_dir is not None:
        print(f"Bootstrap mode: input directory acknowledged but not scanned: {args.input_dir}")
    print(f"Wrote manifest header to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
