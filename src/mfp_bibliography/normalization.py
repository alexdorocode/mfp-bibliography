"""Minimal normalization interfaces for future source adapters."""

from __future__ import annotations

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
