"""Helpers for deterministic identifiers and checksums."""

from __future__ import annotations

import hashlib
from pathlib import Path


def make_record_id(source_id: str, source_record_id: str) -> str:
    """Create a deterministic record identifier from source identity fields."""
    payload = f"{source_id.strip()}::{source_record_id.strip()}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{source_id.strip()}:{digest}"


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 checksum of a local file."""
    file_path = Path(path)
    hasher = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
