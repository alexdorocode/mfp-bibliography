#!/usr/bin/env python3
"""Parse local MoonProt HTML fixtures offline (MFPB_0_11_MOONPROT_OFFLINE_PARSER).

Reads one or more local HTML fixture files and prints a deterministic JSON
result per fixture: the extracted record, or a typed parse error. This script
contains no network, HTTP client, scraper, retry, or acquisition code and
never contacts MoonProt or any external URL. It assigns no policy status and
creates no source claims.

Usage:
    python scripts/parse_moonprot_fixture.py data/fixtures/moonprot/mpid_1_valid.html
    python scripts/parse_moonprot_fixture.py --expected-mpid 2 data/fixtures/moonprot/mpid_2_reordered.html
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mfp_bibliography.moonprot_parser import (
    CONTRACT_ID,
    MoonProtParseError,
    parse_moonprot_fixture,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse local MoonProt HTML fixtures offline; no network access."
    )
    parser.add_argument(
        "fixtures",
        type=Path,
        nargs="+",
        help="One or more local MoonProt HTML fixture file paths.",
    )
    parser.add_argument(
        "--expected-mpid",
        type=str,
        default=None,
        help="Expected MoonProt ID; a conflict raises a typed parse error.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    all_ok = True
    for fixture in args.fixtures:
        try:
            record = parse_moonprot_fixture(fixture, expected_mpid=args.expected_mpid)
            result = {
                "contract_id": CONTRACT_ID,
                "fixture": fixture.name,
                "ok": True,
                "record": record.to_dict(),
            }
        except MoonProtParseError as exc:
            all_ok = False
            result = {
                "contract_id": CONTRACT_ID,
                "fixture": fixture.name,
                "ok": False,
                "error_type": type(exc).__name__,
                "message": str(exc),
            }
        print(json.dumps(result, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
