from __future__ import annotations

import pytest

from mfp_bibliography.normalization import AdapterNotAvailableError, normalize_records


def test_normalization_fails_without_adapter() -> None:
    with pytest.raises(AdapterNotAvailableError):
        normalize_records("moondb", [])
