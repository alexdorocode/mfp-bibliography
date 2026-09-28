"""Minimal normalization interfaces for future source adapters."""

from __future__ import annotations

import hashlib

from collections.abc import Iterable, Mapping
from typing import Any, Protocol


class SourceAdapter(Protocol):
    """Protocol for future per-source normalization adapters.

    Implementations should convert source-specific records into canonical
    dictionaries compatible with the JSON schema.
    """

    source_id: str

    def normalize(self, raw_records: Iterable[Mapping[str, Any]]) -> Iterable[dict[str, Any]]:
        """Normalize source records into canonical dictionaries."""


class AdapterNotAvailableError(RuntimeError):
    """Raised when a requested adapter is not available."""


def get_adapter(adapter_name: str) -> SourceAdapter:
    """Resolve a source adapter by name.

    The bootstrap release intentionally ships no source adapters.
    """
    raise AdapterNotAvailableError(
        f"No adapter is installed for '{adapter_name}'. "
        "Source-specific normalization remains future work."
    )


def normalize_records(adapter_name: str, raw_records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Normalize records with a resolved adapter.

    Raises AdapterNotAvailableError when no adapter is installed.
    """
    adapter = get_adapter(adapter_name)
    return list(adapter.normalize(raw_records))


# --- Canonical protein identity (scheme MFPB_PROTEIN_ID_V1) ---

PROTEIN_ID_SCHEME_VERSION = "MFPB_PROTEIN_ID_V1"
PROTEIN_ID_DIGEST_LENGTH = 16


def normalize_uniprot_accession(value: str | None) -> str | None:
    """Canonical UniProt accession: strip, first whitespace token, uppercase.

    None/empty input normalizes to None. This is the single normalization rule
    for all cross-source identity assignment.
    """
    if not value:
        return None
    token = value.strip().split(" ")[0].strip().upper()
    return token or None


def _protein_id_digest(namespace: str, payload: str) -> str:
    data = f"{PROTEIN_ID_SCHEME_VERSION}::{namespace}::{payload}"
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:PROTEIN_ID_DIGEST_LENGTH]


def make_protein_id_uniprot(accession: str) -> str:
    """Deterministic protein ID for a UniProt-resolved record.

    Format: ``MFP:U:<16 hex>`` (SHA-256, documented 16-hex length). Distinct
    canonical accessions must be checked for digest collisions by the caller.
    """
    canonical = normalize_uniprot_accession(accession)
    if not canonical:
        raise ValueError("make_protein_id_uniprot requires a non-empty accession")
    return f"MFP:U:{_protein_id_digest('uniprot', canonical)}"


def make_protein_id_fallback(source_name: str, local_key: str) -> str:
    """Deterministic, source-scoped protein ID for a record without UniProt.

    Format: ``MFP:F:<source_name>:<16 hex>``. Each source record keeps its own
    entity; records are never merged by display text, name, gene, or organism.
    """
    if not source_name or not local_key:
        raise ValueError("make_protein_id_fallback requires source_name and local_key")
    payload = f"{source_name}::{local_key}"
    return f"MFP:F:{source_name}:{_protein_id_digest('fallback', payload)}"
