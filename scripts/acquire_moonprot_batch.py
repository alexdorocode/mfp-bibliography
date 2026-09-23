#!/usr/bin/env python3
"""MoonProt controlled batch-acquisition CLI (explicit IDs/ranges only, max 100).

Implements the contract in docs/reconciliation-baseline-contract.md for batch mode:

- Accepts explicit MPID lists and inclusive ranges only (e.g., 1 2 3 or "1..5");
- Hard maximum per invocation: 100 MPIDs;
- Rejects IDs outside 1..706;
- Rejects any request for an ID already present in data/raw/moonprot/;
- Default batch is forbidden; user must explicitly pass IDs/range;
- Sequential-only behavior, one request at a time;
- Preserves all contract values: robots check, honest User-Agent, timeout 15s,
  delay >=10s, max one retry, retry backoff >=30s;
- Stop-on-error by default; optional --continue-on-error mode.

Without the mandatory --execute flag this CLI performs no transport call of any
kind and only prints the acquisition plan. With the flag it performs real HTTP
requests through UrllibTransport; the flag must never be used before the
source-policy/robots.txt approval gate has been passed by a human reviewer.

Usage:
    python scripts/acquire_moonprot_batch.py --mpid 1 --mpid 2 --mpid 3 \
        --user-agent "mfp-bibliography/0.1 (contact: name@example.org)"
    python scripts/acquire_moonprot_batch.py --mpid "1..5" --user-agent "..." --execute
    python scripts/acquire_moonprot_batch.py --mpid "1..20" --continue-on-error --user-agent "..." --execute
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mfp_bibliography.moonprot_client import (
    BATCH_ALLOWED_MPID_RANGE,
    BATCH_CONTRACT_ID,
    MAX_BATCH_SIZE,
    MoonProtBatchClient,
    MoonProtBatchConfig,
    UrllibTransport,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "MoonProt controlled batch acquisition for explicit MPID lists/ranges. "
            "Dry-run by default; real requests require --execute."
        )
    )
    parser.add_argument(
        "--mpid",
        action="append",
        type=str,
        required=True,
        help=(
            "Explicit MPID or range to acquire (repeatable; e.g., --mpid 1 --mpid 2..5). "
            f"MPIDs must be in range {BATCH_ALLOWED_MPID_RANGE[0]}..{BATCH_ALLOWED_MPID_RANGE[1]}. "
            f"Maximum {MAX_BATCH_SIZE} MPIDs per invocation."
        ),
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
        "--execute",
        action="store_true",
        help=(
            "Actually perform requests. Without this flag the CLI exits before "
            "any transport call (dry-run)."
        ),
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help=(
            "Continue acquiring remaining MPIDs even if one fails. "
            "By default, stops on first error."
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

    config = MoonProtBatchConfig(
        user_agent=args.user_agent,
        root=args.root,
        continue_on_error=args.continue_on_error,
    )

    if not args.execute:
        print("DRY-RUN: no requests will be made and no files will be written.")
        print(f"  Contract ID           : {BATCH_CONTRACT_ID}")
        print(f"  Allowed MPID range    : {BATCH_ALLOWED_MPID_RANGE[0]}..{BATCH_ALLOWED_MPID_RANGE[1]}")
        print(f"  Maximum batch size    : {MAX_BATCH_SIZE}")
        print(f"  User-Agent            : {config.user_agent}")
        print(f"  timeout               : {config.timeout_seconds} s")
        print(f"  delay between reqs    : {config.delay_seconds} s (sequential only)")
        print(f"  retry policy          : max {config.max_retries} per MPID, {config.retry_backoff_seconds} s backoff")
        print(f"  continue-on-error     : {config.continue_on_error}")
        print("\n  Resolved MPIDs:")
        
        # Resolve ranges for display
        resolved = []
        for item in mpids:
            if ".." in item:
                parts = item.split("..")
                if len(parts) == 2:
                    try:
                        start = int(parts[0].strip())
                        end = int(parts[1].strip())
                        resolved.extend(range(start, end + 1))
                    except ValueError:
                        resolved.append(item)
                else:
                    resolved.append(item)
            else:
                try:
                    resolved.append(int(item))
                except ValueError:
                    resolved.append(item)
        
        for mpid in resolved:
            print(f"    - {mpid}")
        print(f"\n  Total: {len(resolved)} MPID(s)")
        
        if len(resolved) > MAX_BATCH_SIZE:
            print(f"\n  WARNING: Batch size {len(resolved)} exceeds maximum of {MAX_BATCH_SIZE}!")
            print("  This would be rejected on execution.")
        
        print("\nTo perform real requests, re-run with --execute after the")
        print("source-policy and robots.txt/terms approval gate has been passed.")
        return 0

    client = MoonProtBatchClient(config, UrllibTransport())
    report = client.run(mpids)
    print(json.dumps(report.to_dict(), indent=2))
    if report.stopped or len(report.acquired_mpids) != len(report.requested):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
