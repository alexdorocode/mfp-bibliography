#!/usr/bin/env python3
"""Placeholder CLI for future source-specific normalization adapters."""

from __future__ import annotations

import argparse

from mfp_bibliography.normalization import AdapterNotAvailableError, normalize_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize source records using a source adapter. "
            "Bootstrap release does not include source adapters."
        )
    )
    parser.add_argument("--adapter", required=True, help="Adapter name (future source-specific plugin).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        normalize_records(args.adapter, [])
    except AdapterNotAvailableError as exc:
        print(str(exc))
        return 2
    print("Normalization complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
