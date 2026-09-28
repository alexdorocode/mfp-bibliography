"""Read-only pre-build verification of raw inputs consumed by the MVP catalog.

Checks existence and SHA-256 of consumed raw artifacts against the
authoritative local records:

- MoonDB / PlantMP whole-file artifacts against ``data/manifests/source_manifest.csv``
  (hash grain: entire source artifact, ``raw_file_sha256``).
- MoonProt per-record HTML against ``data/raw/moonprot/artifact_index.csv``
  (hash grain: one specific HTML file, ``raw_record_sha256``).

The verifier never writes, never regenerates manifests, and never fabricates
hashes. Duplicate or conflicting entries are reported as errors.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

SOURCE_MANIFEST = "data/manifests/source_manifest.csv"
MOONPROT_INDEX = "data/raw/moonprot/artifact_index.csv"
MOONPROT_RAW_DIR = "data/raw/moonprot"

_CONSUMED_SOURCES = ("SRC_MOONDB", "SRC_PLANTMP", "SRC_MULTIFACETEDPROTDB", "SRC_MULTITASKPROTDB_II")


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_source_manifest(root: str | Path) -> tuple[dict[str, dict], list[str]]:
    """Parse the source manifest into {source_id: row}, collecting duplicate errors."""
    manifest: dict[str, dict] = {}
    errors: list[str] = []
    path = Path(root) / SOURCE_MANIFEST
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            source_id = (row.get("source_id") or "").strip()
            if not source_id:
                errors.append(f"{SOURCE_MANIFEST}: row without source_id")
                continue
            if source_id in manifest:
                errors.append(f"{SOURCE_MANIFEST}: duplicate entry for source '{source_id}'")
                continue
            manifest[source_id] = row
    return manifest, errors


def parse_artifact_index(root: str | Path) -> tuple[dict[str, dict], list[str]]:
    """Parse the MoonProt artifact index into {mpid: row}, collecting duplicate errors."""
    index: dict[str, dict] = {}
    errors: list[str] = []
    path = Path(root) / MOONPROT_INDEX
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            mpid = (row.get("mpid") or "").strip()
            if not mpid:
                errors.append(f"{MOONPROT_INDEX}: row without mpid")
                continue
            if mpid in index:
                errors.append(f"{MOONPROT_INDEX}: duplicate entry for MPID {mpid}")
                continue
            index[mpid] = row
    return index, errors


def verify_catalog_inputs(root: str | Path) -> list[str]:
    """Verify consumed raw inputs; return a list of violations (empty = sound)."""
    root = Path(root)
    errors: list[str] = []

    manifest, manifest_errors = parse_source_manifest(root)
    errors.extend(manifest_errors)
    index, index_errors = parse_artifact_index(root)
    errors.extend(index_errors)

    # MoonDB / PlantMP: whole-file artifacts identified by the source manifest
    for source_id in _CONSUMED_SOURCES:
        row = manifest.get(source_id)
        if row is None:
            errors.append(f"missing {SOURCE_MANIFEST} entry for consumed source '{source_id}'")
            continue
        rel_path = (row.get("original_artifact_path") or "").strip()
        expected = (row.get("sha256") or "").strip()
        if not rel_path or not expected:
            errors.append(f"{SOURCE_MANIFEST} entry for '{source_id}' lacks path or sha256")
            continue
        artifact = root / rel_path
        if not artifact.is_file():
            errors.append(f"consumed raw artifact missing: {rel_path} (source '{source_id}')")
            continue
        actual = _sha256_file(artifact)
        if actual != expected:
            errors.append(
                f"raw artifact hash mismatch for '{source_id}' ({rel_path}): "
                f"manifest {expected}, actual {actual}"
            )

    # MoonProt: every consumed HTML must be indexed and byte-identical;
    # every index entry must have its file (no silently dropped records).
    raw_dir = root / MOONPROT_RAW_DIR
    consumed = {p.name[len("mpid_"):-len(".html")]: p
                for p in raw_dir.glob("mpid_*.html")}
    for mpid, path in sorted(consumed.items()):
        entry = index.get(mpid)
        if entry is None:
            errors.append(f"consumed MoonProt HTML mpid_{mpid}.html missing from {MOONPROT_INDEX}")
            continue
        expected = (entry.get("sha256") or "").strip()
        actual = _sha256_file(path)
        if expected and actual != expected:
            errors.append(
                f"MoonProt HTML hash mismatch for MPID {mpid}: "
                f"index {expected}, actual {actual}"
            )
    for mpid in sorted(index):
        if mpid not in consumed:
            errors.append(
                f"{MOONPROT_INDEX} entry MPID {mpid} has no raw file "
                f"(acquired record would be silently lost)"
            )

    return errors


def load_source_file_sha256(root: str | Path, source_id: str) -> str:
    """Return the manifest whole-file sha256 for a source (read-only)."""
    manifest, _ = parse_source_manifest(root)
    row = manifest.get(source_id)
    if row is None:
        raise ValueError(f"No {SOURCE_MANIFEST} entry for source '{source_id}'")
    return (row.get("sha256") or "").strip()
