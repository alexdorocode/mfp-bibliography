"""Tests for source profiling functionality."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from mfp_bibliography.validation import EXPECTED_MANIFEST_HEADER

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestProfileSource:
    """Tests for the profile_source.py script."""

    def test_profile_moondb_fixture(self, tmp_path) -> None:
        """Test profiling the MoonDB sample fixture."""
        # Copy fixture to temp
        fixture = REPO_ROOT / "data" / "fixtures" / "moondb" / "sample.tsv"
        assert fixture.exists()
        
        # Profile it
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/profile_source.py", "--source-id", "SRC_MOONDB", str(fixture)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        
        assert result.returncode == 0
        profile = json.loads(result.stdout)
        
        # Basic assertions
        assert profile["ok"] is True
        assert profile["source_id"] == "SRC_MOONDB"
        assert profile["filename"] == "sample.tsv"
        assert profile["data_rows"] == 3
        assert profile["delimiter"] == "\t"
        assert profile["encoding"] == "ascii"
        assert profile["line_ending"] == "LF"
        
        # Column assertions
        assert len(profile["columns"]) == 3
        
        # Check column names
        col_names = [c["name"] for c in profile["columns"]]
        assert "#UniProtKB_ac" in col_names
        assert "UniProtKB_ac" in col_names
        assert "type" in col_names
        
        # Check type column values
        type_col = next(c for c in profile["columns"] if c["name"] == "type")
        assert type_col["value_counts"]["Predicted"] == 2
        assert type_col["value_counts"]["Curated"] == 1
        
        # Check identifier candidates
        assert "UniProtKB_ac" in profile["identifier_candidates"]
        
        # Check parsing anomalies
        assert any("#" in anomaly for anomaly in profile["parsing_anomalies"])

    def test_profile_nonexistent_file(self, tmp_path) -> None:
        """Test profiling a non-existent file returns error."""
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/profile_source.py", str(tmp_path / "nonexistent.tsv")],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        
        profile = json.loads(result.stdout)
        assert profile["ok"] is False
        assert "error" in profile
        assert "not found" in profile["error"]

    def test_profile_malformed_file(self, tmp_path) -> None:
        """Test profiling a malformed file."""
        # Create a malformed file
        malformed = tmp_path / "malformed.tsv"
        malformed.write_text("bad\theader\n", encoding="utf-8")
        
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/profile_source.py", str(malformed)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        
        # Should still work with just one column
        profile = json.loads(result.stdout)
        assert profile["ok"] is True


class TestSourceManifest:
    """Tests for source manifest updates."""

    def test_manifest_header_unchanged(self) -> None:
        """Verify manifest header is still correct."""
        manifest = REPO_ROOT / "data" / "manifests" / "source_manifest.csv"
        content = manifest.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        assert lines[0] == EXPECTED_MANIFEST_HEADER

    def test_moondb_entry_present(self) -> None:
        """Verify MoonDB entry is in manifest."""
        manifest = REPO_ROOT / "data" / "manifests" / "source_manifest.csv"
        content = manifest.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        # Should have header + at least MoonDB entry
        assert len(lines) >= 2
        
        # Check MoonDB entry exists
        moondb_line = next((line for line in lines if "SRC_MOONDB" in line), None)
        assert moondb_line is not None
        
        # Parse the line
        parts = moondb_line.split(",")
        assert parts[0] == "SRC_MOONDB"
        assert parts[1] == "MoonDB"
        assert parts[2] == "imported"
        assert parts[6] == "data/raw/moondb/all_emf_and_curated.tsv"
        assert parts[8] == "c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55"
        assert parts[9] == "8331"
        assert parts[10] == "351"


class TestFileChecksums:
    """Tests for file checksums."""

    def test_moondb_checksum_present(self) -> None:
        """Verify MoonDB checksum is in checksums file."""
        checksums = REPO_ROOT / "data" / "manifests" / "file_checksums.sha256"
        content = checksums.read_text(encoding="utf-8")
        
        # Check for MoonDB checksum
        expected_checksum = "c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55"
        assert expected_checksum in content
        assert "data/raw/moondb/all_emf_and_curated.tsv" in content


class TestSourceProfileDocument:
    """Tests for source profile documentation."""

    def test_moondb_profile_exists(self) -> None:
        """Verify MoonDB profile document exists."""
        profile = REPO_ROOT / "docs" / "source-profiles" / "moondb.md"
        assert profile.exists()
        
        content = profile.read_text(encoding="utf-8")
        
        # Check for key facts
        assert "SRC_MOONDB" in content
        assert "all_emf_and_curated.tsv" in content
        assert "8331" in content
        assert "c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55" in content
        assert "351" in content
        assert "UniProtKB_ac" in content
        assert "Predicted" in content
        assert "Curated" in content


class TestRawArtifactImmutability:
    """Tests to verify raw artifact remains unchanged."""

    def test_moondb_artifact_checksum_matches(self) -> None:
        """Verify the MoonDB artifact checksum still matches."""
        import hashlib
        
        artifact = REPO_ROOT / "data" / "raw" / "moondb" / "all_emf_and_curated.tsv"
        
        sha256 = hashlib.sha256()
        with artifact.open("rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        expected = "c503101da091ba457f9480f094b67f939fe3b0ac9310b3f7e5d7868b21532d55"
        assert sha256.hexdigest() == expected

    def test_moondb_artifact_size_unchanged(self) -> None:
        """Verify the MoonDB artifact size is unchanged."""
        artifact = REPO_ROOT / "data" / "raw" / "moondb" / "all_emf_and_curated.tsv"
        
        assert artifact.stat().st_size == 8331

    def test_moondb_artifact_first_bytes_unchanged(self) -> None:
        """Verify the first bytes of MoonDB artifact are unchanged."""
        artifact = REPO_ROOT / "data" / "raw" / "moondb" / "all_emf_and_curated.tsv"
        
        with artifact.open("rb") as f:
            first_bytes = f.read(100)
        
        expected_start = b"#UniProtKB_ac\tUniProtKB_ac\ttype\nQ86VP1\tQ86VP1\tPredicted\n"
        assert first_bytes[:len(expected_start)] == expected_start

    def test_moondb_artifact_last_bytes_unchanged(self) -> None:
        """Verify the last bytes of MoonDB artifact are unchanged."""
        artifact = REPO_ROOT / "data" / "raw" / "moondb" / "all_emf_and_curated.tsv"
        
        with artifact.open("rb") as f:
            content = f.read()
        
        # File ends with "Predicted" without newline
        assert content.endswith(b"Predicted")
        assert not content.endswith(b"\n")
