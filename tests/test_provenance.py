from __future__ import annotations

import hashlib

from mfp_bibliography.provenance import make_record_id, sha256_file


def test_record_id_is_stable() -> None:
    first = make_record_id("SRC_MOONDB", "MDB_001")
    second = make_record_id("SRC_MOONDB", "MDB_001")
    assert first == second


def test_sha256_file_matches_expected(tmp_path) -> None:
    fixture = tmp_path / "sample.txt"
    fixture.write_text("hello", encoding="utf-8")
    expected = hashlib.sha256(b"hello").hexdigest()
    assert sha256_file(fixture) == expected
