#!/usr/bin/env python3
"""Validate repository scaffold invariants."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mfp_bibliography.validation import validate_repository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate repository structure, manifest header, and JSON schema.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path (default: script parent repository).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_repository(args.root)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
