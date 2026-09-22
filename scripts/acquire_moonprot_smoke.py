#!/usr/bin/env python3
"""MoonProt smoke-acquisition CLI (MPIDs 1, 2, 3 only; dry-run by default).

Implements the contract in docs/acquisition-protocols/moonprot.md. Without the
mandatory --execute-smoke-test flag this CLI performs no transport call of
any kind and only prints the acquisition plan. With the flag it performs real
HTTP requests through UrllibTransport; the flag must never be used before the
source-policy/robots.txt approval gate has been passed by a human reviewer.

Usage:
    python scripts/acquire_moonprot_smoke.py --mpid 1 --mpid 2 --mpid 3 \
        --user-agent "mfp-bibliography/0.1 (contact: name@example.org)"
    python scripts/acquire_moonprot_smoke.py --mpid 1 --user-agent "..." --execute-smoke-test
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mfp_bibliography.moonprot_client import (
    ALLOWED_MPIDS,
    ROBOTS_URL,
    MoonProtSmokeClient,
    MoonProtSmokeConfig,
    UrllibTransport,
    protein_url,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "MoonProt smoke acquisition for MPIDs 1, 2, 3. Dry-run by default; "
            "real requests require --execute-smoke-test."
        )
    )
    parser.add_argument(
        "--mpid",
        action="append",
        type=int,
        required=True,
        help="Explicit MPID to acquire (repeatable; only 1, 2, 3 are allowed).",
    )
    parser.add_argument(
        "--user-agent",
        required=True,
        help=(
            "Honest User-Agent identifying this project and a contact, "
            "e.g. 'mfp-bibliography/0.1 (contact: name@example.org)'."
        ),
    )
    parser.add_argument(
        "--execute-smoke-test",
        action="store_true",
        help=(
            "Actually perform requests. Without this flag the CLI exits before "
            "any transport call (dry-run)."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root for artifact paths (default: this repository).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    mpids = tuple(args.mpid)

    out_of_scope = [mpid for mpid in mpids if mpid not in ALLOWED_MPIDS]
    if out_of_scope:
        print(f"ERROR: MPIDs outside the approved scope {{1, 2, 3}}: {out_of_scope}")
        return 2

    config = MoonProtSmokeConfig(user_agent=args.user_agent, root=args.root)

    if not args.execute_smoke_test:
        print("DRY-RUN: no requests will be made and no files will be written.")
        print(f"  Approved scope      : MPIDs {sorted(set(mpids))} (allowed: {list(ALLOWED_MPIDS)})")
        print(f"  robots gate         : {ROBOTS_URL} checked before every protein request")
        for mpid in mpids:
            print(f"  would request       : {protein_url(mpid)} -> {config.raw_path(mpid)}")
        print(f"  User-Agent          : {config.user_agent}")
        print(f"  timeout             : {config.timeout_seconds} s")
        print(f"  delay between reqs  : {config.delay_seconds} s (sequential only)")
        print(f"  retry policy        : max {config.max_retries} per MPID, {config.retry_backoff_seconds} s backoff")
        print("To perform real requests, re-run with --execute-smoke-test after the")
        print("source-policy and robots.txt/terms approval gate has been passed.")
        return 0

    client = MoonProtSmokeClient(config, UrllibTransport())
    report = client.run(mpids)
    print(json.dumps(report.to_dict(), indent=2))
    if report.stopped or len(report.acquired_mpids) != len(mpids):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
