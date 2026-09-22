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

    def test_profile_flat_list_format(self, tmp_path) -> None:
        """Test profiling a single-line CSV flat list of identifiers."""
        # Create a flat-list fixture without trailing newline
        flat_file = tmp_path / "flat_list.txt"
        # Use open/write to avoid adding trailing newline
        with flat_file.open("w", encoding="utf-8") as f:
            f.write("P36873,P43320,P05109,P80297,P62851,Q12884")
        
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/profile_source.py", "--source-id", "TEST", str(flat_file)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        
        assert result.returncode == 0
        profile = json.loads(result.stdout)
        
        # Flat-list specific assertions
        assert profile["ok"] is True
        assert profile["data_rows"] == 1
        assert profile["has_trailing_newline"] is False
        assert profile["delimiter"] == ","
        
        # Single column for flat list
        assert len(profile["columns"]) == 1
        assert profile["columns"][0]["name"] == "value"
        assert profile["columns"][0]["cardinality"] == 6
        assert profile["columns"][0]["unique"] is True
        assert profile["columns"][0]["data_type"] == "string"
        
        # Check identifier candidates
        assert "value" in profile["identifier_candidates"]
        
        # Check parsing anomalies
        assert any("Flat-list format" in anomaly for anomaly in profile["parsing_anomalies"])

    def test_profile_flat_list_with_duplicates(self, tmp_path) -> None:
        """Test profiling a flat list with duplicate values."""
        flat_file = tmp_path / "flat_list_dups.txt"
        with flat_file.open("w", encoding="utf-8") as f:
            f.write("P36873,P43320,P36873,P05109")
        
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/profile_source.py", "--source-id", "TEST", str(flat_file)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        
        profile = json.loads(result.stdout)
        assert profile["ok"] is True
        assert profile["columns"][0]["unique"] is False
        assert profile["columns"][0]["cardinality"] == 3  # 3 unique values
        assert any("Duplicate values detected" in anomaly for anomaly in profile["parsing_anomalies"])

    def test_profile_flat_list_with_blanks(self, tmp_path) -> None:
        """Test profiling a flat list with blank values."""
        flat_file = tmp_path / "flat_list_blanks.txt"
        with flat_file.open("w", encoding="utf-8") as f:
            f.write("P36873,,P05109,")
        
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/profile_source.py", "--source-id", "TEST", str(flat_file)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        
        profile = json.loads(result.stdout)
        assert profile["ok"] is True
        assert profile["columns"][0]["nullable"] is True
        assert any("Blank/empty values detected" in anomaly for anomaly in profile["parsing_anomalies"])

    def test_profile_multitaskprotdb_ii_fixture(self, tmp_path) -> None:
        """Test profiling the MultitaskProtDB-II sample fixture."""
        fixture = REPO_ROOT / "data" / "fixtures" / "multitaskprotdb-ii" / "sample.csv"
        assert fixture.exists()
        
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/profile_source.py", "--source-id", "SRC_MULTITASKPROTDB_II", str(fixture)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        
        assert result.returncode == 0
        profile = json.loads(result.stdout)
        
        # Basic assertions
        assert profile["ok"] is True
        assert profile["source_id"] == "SRC_MULTITASKPROTDB_II"
        assert profile["filename"] == "sample.csv"
        assert profile["data_rows"] == 2
        assert profile["delimiter"] == ","
        assert profile["encoding"] in ("ascii", "utf-8", "utf-8-sig")
        
        # Column assertions
        assert len(profile["columns"]) == 15
        
        # Check column names
        col_names = [c["name"] for c in profile["columns"]]
        assert "UniProt" in col_names
        assert "Protein_Name" in col_names
        assert "Models" in col_names
        
        # Check Models column values
        models_col = next(c for c in profile["columns"] if c["name"] == "Models")
        assert models_col["value_counts"]["Phyre"] == 1
        assert models_col["value_counts"]["ITasser"] == 1
        assert models_col["cardinality"] == 2

    def test_profile_plantmp_fixture(self, tmp_path) -> None:
        """Test profiling the PlantMP sample fixture."""
        fixture = REPO_ROOT / "data" / "fixtures" / "plantmp" / "sample.csv"
        assert fixture.exists()
        
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/profile_source.py", "--source-id", "SRC_PLANTMP", str(fixture)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        
        assert result.returncode == 0
        profile = json.loads(result.stdout)
        
        # Basic assertions
        assert profile["ok"] is True
        assert profile["source_id"] == "SRC_PLANTMP"
        assert profile["filename"] == "sample.csv"
        assert profile["data_rows"] == 3
        assert profile["delimiter"] == ","
        assert profile["encoding"] in ("ascii", "utf-8")
        assert profile["line_ending"] == "LF"
        
        # Column assertions
        assert len(profile["columns"]) == 14
        
        # Check column names
        col_names = [c["name"] for c in profile["columns"]]
        assert "order" in col_names
        assert "protein name, gene" in col_names
        assert "uniport_id" in col_names
        assert "type" in col_names
        
        # Check type column values
        type_col = next(c for c in profile["columns"] if c["name"] == "type")
        assert type_col["value_counts"]["confirmed"] == 1
        assert type_col["value_counts"]["likely"] == 1
        assert type_col["value_counts"]["predicted"] == 1
        assert type_col["cardinality"] == 3

    def test_profile_utf8_csv_with_quotes(self, tmp_path) -> None:
        """Test profiling a UTF-8 CSV file with quoted fields containing commas."""
        csv_file = tmp_path / "quoted_csv.txt"
        with csv_file.open("w", encoding="utf-8") as f:
            f.write('order,"protein name, gene",uniport_id,type\n')
            f.write('1,"Protein A, GENE1",P12345,confirmed\n')
            f.write('2,"Protein B, GENE2",Q67890,likely\n')
        
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/profile_source.py", "--source-id", "TEST", str(csv_file)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        
        profile = json.loads(result.stdout)
        assert profile["ok"] is True
        assert profile["encoding"] in ("ascii", "utf-8")
        assert profile["delimiter"] == ","
        assert profile["data_rows"] == 2
        
        # Check that quoted field was parsed correctly
        col_names = [c["name"] for c in profile["columns"]]
        assert "protein name, gene" in col_names
        
        # Check sample values
        protein_col = next(c for c in profile["columns"] if c["name"] == "protein name, gene")
        assert "Protein A, GENE1" in protein_col["sample_values"]
        assert "Protein B, GENE2" in protein_col["sample_values"]


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

    def test_multifacetedprotdb_entry_present(self) -> None:
        """Verify MultifacetedProtDB entry is in manifest."""
        manifest = REPO_ROOT / "data" / "manifests" / "source_manifest.csv"
        content = manifest.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        # Check MultifacetedProtDB entry exists
        mfp_line = next((line for line in lines if "SRC_MULTIFACETEDPROTDB" in line), None)
        assert mfp_line is not None

    def test_multitaskprotdb_ii_entry_present(self) -> None:
        """Verify MultitaskProtDB-II entry is in manifest."""
        manifest = REPO_ROOT / "data" / "manifests" / "source_manifest.csv"
        content = manifest.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        # Check MultitaskProtDB-II entry exists
        mtp_line = next((line for line in lines if "SRC_MULTITASKPROTDB_II" in line), None)
        assert mtp_line is not None
        
        # Parse the line
        parts = mtp_line.split(",")
        assert parts[0] == "SRC_MULTITASKPROTDB_II"
        assert parts[1] == "MultitaskProtDB-II"
        assert parts[2] == "imported"
        assert parts[6] == "data/raw/multitaskprotdb-ii/proteins.csv"
        assert parts[8] == "84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482"
        assert parts[9] == "1324061"
        assert parts[10] == "694"

    def test_plantmp_entry_present(self) -> None:
        """Verify PlantMP entry is in manifest."""
        manifest = REPO_ROOT / "data" / "manifests" / "source_manifest.csv"
        content = manifest.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        # Check PlantMP entry exists
        plantmp_line = next((line for line in lines if "SRC_PLANTMP" in line), None)
        assert plantmp_line is not None
        
        # Parse the line
        parts = plantmp_line.split(",")
        assert parts[0] == "SRC_PLANTMP"
        assert parts[1] == "PlantMP"
        assert parts[2] == "imported"
        assert parts[6] == "data/raw/plantmp/PlantMP_all.csv"
        assert parts[8] == "97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9"
        assert parts[9] == "53366"
        assert parts[10] == "112"


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

    def test_multifacetedprotdb_checksum_present(self) -> None:
        """Verify MultifacetedProtDB checksum is in checksums file."""
        checksums = REPO_ROOT / "data" / "manifests" / "file_checksums.sha256"
        content = checksums.read_text(encoding="utf-8")
        
        # Check for MultifacetedProtDB checksum
        expected_checksum = "23a68fe6e5d6e8fa25af67786cdd64836e3b28d83316174e1b9f70e638ffabb4"
        assert expected_checksum in content
        assert "data/raw/multifacetedprotdb/MultifacetedProtDB_data.txt" in content

    def test_plantmp_checksum_present(self) -> None:
        """Verify PlantMP checksum is in checksums file."""
        checksums = REPO_ROOT / "data" / "manifests" / "file_checksums.sha256"
        content = checksums.read_text(encoding="utf-8")
        
        # Check for PlantMP checksum
        expected_checksum = "97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9"
        assert expected_checksum in content
        assert "data/raw/plantmp/PlantMP_all.csv" in content

    def test_multitaskprotdb_ii_checksum_present(self) -> None:
        """Verify MultitaskProtDB-II checksum is in checksums file."""
        checksums = REPO_ROOT / "data" / "manifests" / "file_checksums.sha256"
        content = checksums.read_text(encoding="utf-8")
        
        # Check for MultitaskProtDB-II checksum
        expected_checksum = "84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482"
        assert expected_checksum in content
        assert "data/raw/multitaskprotdb-ii/proteins.csv" in content


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

    def test_multifacetedprotdb_profile_exists(self) -> None:
        """Verify MultifacetedProtDB profile document exists."""
        profile = REPO_ROOT / "docs" / "source-profiles" / "multifacetedprotdb.md"
        assert profile.exists()
        
        content = profile.read_text(encoding="utf-8")
        
        # Check for key facts
        assert "SRC_MULTIFACETEDPROTDB" in content
        assert "MultifacetedProtDB_data.txt" in content
        assert "7724" in content
        assert "23a68fe6e5d6e8fa25af67786cdd64836e3b28d83316174e1b9f70e638ffabb4" in content
        assert "1103" in content
        assert "UniProtKB accession" in content
        assert "Single-line" in content

    def test_multitaskprotdb_ii_profile_exists(self) -> None:
        """Verify MultitaskProtDB-II profile document exists."""
        profile = REPO_ROOT / "docs" / "source-profiles" / "multitaskprotdb-ii.md"
        assert profile.exists()
        
        content = profile.read_text(encoding="utf-8")
        
        # Check for key facts
        assert "SRC_MULTITASKPROTDB_II" in content
        assert "proteins.csv" in content
        assert "1324061" in content
        assert "84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482" in content
        assert "694" in content
        assert "UniProt" in content
        assert "Phyre" in content
        assert "ITasser" in content

    def test_plantmp_profile_exists(self) -> None:
        """Verify PlantMP profile document exists."""
        profile = REPO_ROOT / "docs" / "source-profiles" / "plantmp.md"
        assert profile.exists()
        
        content = profile.read_text(encoding="utf-8")
        
        # Check for key facts
        assert "SRC_PLANTMP" in content
        assert "PlantMP_all.csv" in content
        assert "53366" in content
        assert "97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9" in content
        assert "112" in content
        assert "confirmed" in content
        assert "likely" in content
        assert "predicted" in content
        assert "Source-native category" in content


class TestRawArtifactImmutability:
    """Tests to verify raw artifact remains unchanged."""

    def test_multifacetedprotdb_artifact_checksum_matches(self) -> None:
        """Verify the MultifacetedProtDB artifact checksum still matches."""
        import hashlib
        
        artifact = REPO_ROOT / "data" / "raw" / "multifacetedprotdb" / "MultifacetedProtDB_data.txt"
        
        sha256 = hashlib.sha256()
        with artifact.open("rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        expected = "23a68fe6e5d6e8fa25af67786cdd64836e3b28d83316174e1b9f70e638ffabb4"
        assert sha256.hexdigest() == expected

    def test_multifacetedprotdb_artifact_size_unchanged(self) -> None:
        """Verify the MultifacetedProtDB artifact size is unchanged."""
        artifact = REPO_ROOT / "data" / "raw" / "multifacetedprotdb" / "MultifacetedProtDB_data.txt"
        
        assert artifact.stat().st_size == 7724

    def test_multifacetedprotdb_artifact_content_unchanged(self) -> None:
        """Verify the MultifacetedProtDB artifact content is unchanged."""
        artifact = REPO_ROOT / "data" / "raw" / "multifacetedprotdb" / "MultifacetedProtDB_data.txt"
        
        with artifact.open("rb") as f:
            content = f.read()
        
        # File is a single line with comma-separated UniProt accessions
        assert b"P36873,P43320,P05109,P80297,P62851" in content
        assert not content.endswith(b"\n")
        # Verify it starts with the first accession
        assert content.startswith(b"P36873,")

    def test_plantmp_artifact_checksum_matches(self) -> None:
        """Verify the PlantMP artifact checksum still matches."""
        import hashlib
        
        artifact = REPO_ROOT / "data" / "raw" / "plantmp" / "PlantMP_all.csv"
        
        sha256 = hashlib.sha256()
        with artifact.open("rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        expected = "97ae53eccbbd3a9c2a1e9b3247db8bcc0b66de929bf4471b37187de5e3a494a9"
        assert sha256.hexdigest() == expected

    def test_plantmp_artifact_size_unchanged(self) -> None:
        """Verify the PlantMP artifact size is unchanged."""
        artifact = REPO_ROOT / "data" / "raw" / "plantmp" / "PlantMP_all.csv"
        
        assert artifact.stat().st_size == 53366

    def test_plantmp_artifact_content_unchanged(self) -> None:
        """Verify the PlantMP artifact content is unchanged."""
        artifact = REPO_ROOT / "data" / "raw" / "plantmp" / "PlantMP_all.csv"
        
        with artifact.open("rb") as f:
            content = f.read()
        
        # Verify header and first data row
        assert b'order,"protein name, gene",uniport_id' in content
        assert b'confirmed' in content
        assert b'likely' in content
        assert b'predicted' in content
        assert content.endswith(b"\n")

    def test_multitaskprotdb_ii_artifact_checksum_matches(self) -> None:
        """Verify the MultitaskProtDB-II artifact checksum still matches."""
        import hashlib
        
        artifact = REPO_ROOT / "data" / "raw" / "multitaskprotdb-ii" / "proteins.csv"
        
        sha256 = hashlib.sha256()
        with artifact.open("rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        expected = "84871fd9ae5c5785adc14047d8a318b8b09aeadbfb12d9a7dd5d66a062cf6482"
        assert sha256.hexdigest() == expected

    def test_multitaskprotdb_ii_artifact_size_unchanged(self) -> None:
        """Verify the MultitaskProtDB-II artifact size is unchanged."""
        artifact = REPO_ROOT / "data" / "raw" / "multitaskprotdb-ii" / "proteins.csv"
        
        assert artifact.stat().st_size == 1324061

    def test_multitaskprotdb_ii_artifact_content_unchanged(self) -> None:
        """Verify the MultitaskProtDB-II artifact content is unchanged."""
        artifact = REPO_ROOT / "data" / "raw" / "multitaskprotdb-ii" / "proteins.csv"
        
        with artifact.open("rb") as f:
            content = f.read()
        
        # Verify header
        assert b'"UniProt","Protein_Name"' in content
        assert b'"Models","Reference"' in content
        assert b'Phyre' in content
        assert b'ITasser' in content

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
