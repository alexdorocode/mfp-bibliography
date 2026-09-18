#!/usr/bin/env python3
"""Read-only local profiling command for source artifacts.

This script profiles a source artifact without making network calls or
mutating data/raw/. It emits structured, reproducible JSON output and
fails explicitly for malformed input.

Usage:
    python scripts/profile_source.py data/raw/moondb/all_emf_and_curated.tsv
    python scripts/profile_source.py --source-id SRC_MOONDB data/raw/moondb/all_emf_and_curated.tsv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ColumnProfile:
    """Profile of a single column."""

    name: str
    position: int
    data_type: str
    nullable: bool
    unique: bool
    cardinality: int
    value_counts: dict[str, int] = field(default_factory=dict)
    sample_values: list[str] = field(default_factory=list)


@dataclass
class SourceProfile:
    """Complete profile of a source artifact."""

    source_id: str
    file_path: str
    filename: str
    file_size_bytes: int
    sha256: str
    encoding: str
    delimiter: str
    line_ending: str
    has_trailing_newline: bool
    total_lines: int
    header_line: int
    data_rows: int
    columns: list[ColumnProfile]
    identifier_candidates: list[str] = field(default_factory=list)
    parsing_anomalies: list[str] = field(default_factory=list)
    error: str | None = None


def detect_encoding(file_path: Path) -> str:
    """Detect file encoding. Returns 'ascii' or 'utf-8' based on content."""
    try:
        with file_path.open("rb") as f:
            chunk = f.read(1024)
        # Check for non-ASCII bytes
        chunk.decode("ascii")
        return "ascii"
    except UnicodeDecodeError:
        return "utf-8"


def detect_delimiter(file_path: Path) -> str:
    """Detect delimiter from file content."""
    with file_path.open("r", encoding="ascii") as f:
        first_line = f.readline()
    
    # Count tabs and commas in first line
    tab_count = first_line.count("\t")
    comma_count = first_line.count(",")
    semicolon_count = first_line.count(";")
    pipe_count = first_line.count("|")
    
    if tab_count > comma_count and tab_count > semicolon_count and tab_count > pipe_count:
        return "\\t"
    elif comma_count > tab_count and comma_count > semicolon_count and comma_count > pipe_count:
        return ","
    elif semicolon_count > tab_count and semicolon_count > comma_count and semicolon_count > pipe_count:
        return ";"
    elif pipe_count > tab_count and pipe_count > comma_count and pipe_count > semicolon_count:
        return "|"
    
    # Default to tab if we can't determine
    return "\\t"


def detect_line_ending(file_path: Path) -> str:
    """Detect line ending style."""
    with file_path.open("rb") as f:
        content = f.read()
    
    if b"\r\n" in content:
        return "CRLF"
    elif b"\n" in content:
        return "LF"
    else:
        return "unknown"


def check_trailing_newline(file_path: Path) -> bool:
    """Check if file ends with newline."""
    with file_path.open("rb") as f:
        content = f.read()
    return content.endswith(b"\n")


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 checksum of file."""
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def profile_file(file_path: Path, source_id: str = "unknown") -> SourceProfile:
    """Profile a source file and return structured results."""
    # Gather file-level facts
    file_path = file_path.resolve()
    
    if not file_path.exists():
        return SourceProfile(
            source_id=source_id,
            file_path=str(file_path),
            filename=file_path.name,
            file_size_bytes=0,
            sha256="",
            encoding="unknown",
            delimiter="unknown",
            line_ending="unknown",
            has_trailing_newline=False,
            total_lines=0,
            header_line=0,
            data_rows=0,
            columns=[],
            error=f"File not found: {file_path}",
        )
    
    file_size = file_path.stat().st_size
    
    # Compute checksum
    try:
        sha256 = compute_sha256(file_path)
    except Exception as e:
        return SourceProfile(
            source_id=source_id,
            file_path=str(file_path),
            filename=file_path.name,
            file_size_bytes=file_size,
            sha256="",
            encoding="unknown",
            delimiter="unknown",
            line_ending="unknown",
            has_trailing_newline=False,
            total_lines=0,
            header_line=0,
            data_rows=0,
            columns=[],
            error=f"Checksum computation failed: {e}",
        )
    
    # Detect encoding
    encoding = detect_encoding(file_path)
    
    # Detect delimiter
    delimiter = detect_delimiter(file_path)
    
    # Detect line ending
    line_ending = detect_line_ending(file_path)
    
    # Check trailing newline
    has_trailing_newline = check_trailing_newline(file_path)
    
    # Read all lines
    with file_path.open("r", encoding=encoding) as f:
        all_lines = f.readlines()
    
    total_lines = len(all_lines)
    
    # Detect actual delimiter from first line
    if delimiter == "\\t":
        actual_delimiter = "\t"
    else:
        actual_delimiter = delimiter
    
    # Parse header
    if all_lines:
        first_line = all_lines[0]
        header = first_line.rstrip("\r\n").split(actual_delimiter)
    else:
        header = []
    
    # Parse with CSV reader - skip header row
    try:
        reader = csv.DictReader(
            all_lines,
            delimiter=actual_delimiter,
        )
        rows = list(reader)
        data_rows = len(rows)
        
        # Profile each column
        columns = []
        for idx, col_name in enumerate(header):
            values = [row[col_name] for row in rows]
            
            # Check for nulls
            null_count = sum(1 for v in values if not v or v.strip() == "")
            nullable = null_count > 0
            
            # Check uniqueness
            unique = len(set(values)) == len(values)
            
            # Cardinality
            cardinality = len(set(values))
            
            # Value counts (limit to top 10)
            value_counts = {}
            for v in values:
                value_counts[v] = value_counts.get(v, 0) + 1
            
            # Sample values (first 5 unique)
            seen = set()
            sample_values = []
            for v in values:
                if v not in seen:
                    seen.add(v)
                    sample_values.append(v)
                    if len(sample_values) >= 5:
                        break
            
            # Determine data type
            if all(v.isdigit() for v in values if v):
                data_type = "integer"
            elif all(
                v.replace(".", "").replace("-", "").replace("+", "").isdigit()
                for v in values
                if v
            ):
                data_type = "numeric"
            else:
                data_type = "string"
            
            columns.append(
                ColumnProfile(
                    name=col_name,
                    position=idx + 1,
                    data_type=data_type,
                    nullable=nullable,
                    unique=unique,
                    cardinality=cardinality,
                    value_counts=value_counts,
                    sample_values=sample_values,
                )
            )
        
        # Identify identifier candidates
        # Columns that are unique, non-nullable, and have reasonable cardinality
        identifier_candidates = []
        for col in columns:
            if col.unique and not col.nullable and col.cardinality > 1:
                # Check if values look like identifiers (alphanumeric, underscores)
                if col.sample_values:
                    import re
                    id_pattern = re.compile(r"^[A-Za-z0-9_\-\.]+$")
                    if all(id_pattern.match(v) for v in col.sample_values if v):
                        identifier_candidates.append(col.name)
        
        # Detect parsing anomalies
        parsing_anomalies = []
        
        # Check for header anomalies (special characters in header)
        for col_name in header:
            if col_name.startswith("#"):
                parsing_anomalies.append(
                    f"Header '{col_name}' has '#' prefix which does not appear in data"
                )
        
        if not has_trailing_newline:
            parsing_anomalies.append("File does not end with newline character")
        
        return SourceProfile(
            source_id=source_id,
            file_path=str(file_path),
            filename=file_path.name,
            file_size_bytes=file_size,
            sha256=sha256,
            encoding=encoding,
            delimiter=actual_delimiter if actual_delimiter == "\t" else delimiter,
            line_ending=line_ending,
            has_trailing_newline=has_trailing_newline,
            total_lines=total_lines,
            header_line=1,
            data_rows=data_rows,
            columns=columns,
            identifier_candidates=identifier_candidates,
            parsing_anomalies=parsing_anomalies,
            error=None,
        )
        
    except Exception as e:
        return SourceProfile(
            source_id=source_id,
            file_path=str(file_path),
            filename=file_path.name,
            file_size_bytes=file_size,
            sha256=sha256,
            encoding=encoding,
            delimiter=delimiter,
            line_ending=line_ending,
            has_trailing_newline=has_trailing_newline,
            total_lines=total_lines,
            header_line=0,
            data_rows=0,
            columns=[],
            error=f"Parsing failed: {e}",
        )


def serialize_profile(profile: SourceProfile) -> dict[str, Any]:
    """Convert profile to JSON-serializable dict."""
    result = {
        "source_id": profile.source_id,
        "file_path": profile.file_path,
        "filename": profile.filename,
        "file_size_bytes": profile.file_size_bytes,
        "sha256": profile.sha256,
        "encoding": profile.encoding,
        "delimiter": profile.delimiter,
        "line_ending": profile.line_ending,
        "has_trailing_newline": profile.has_trailing_newline,
        "total_lines": profile.total_lines,
        "header_line": profile.header_line,
        "data_rows": profile.data_rows,
        "identifier_candidates": profile.identifier_candidates,
        "parsing_anomalies": profile.parsing_anomalies,
        "columns": [],
    }
    
    for col in profile.columns:
        col_dict = {
            "name": col.name,
            "position": col.position,
            "data_type": col.data_type,
            "nullable": col.nullable,
            "unique": col.unique,
            "cardinality": col.cardinality,
            "sample_values": col.sample_values,
        }
        # Only include value_counts if cardinality is small
        if col.cardinality <= 20:
            col_dict["value_counts"] = col.value_counts
        else:
            col_dict["value_counts"] = {"<omitted>": "cardinality > 20"}
        
        result["columns"].append(col_dict)
    
    if profile.error:
        result["error"] = profile.error
        result["ok"] = False
    else:
        result["ok"] = True
    
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile a source artifact without network calls or mutations."
    )
    parser.add_argument(
        "file_path",
        type=Path,
        help="Path to the source artifact file to profile.",
    )
    parser.add_argument(
        "--source-id",
        type=str,
        default="unknown",
        help="Source ID to include in profile (default: unknown).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path for JSON profile (default: stdout).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    # Validate that file is under data/raw/ if it exists
    file_path = args.file_path.resolve()
    try:
        rel_path = file_path.relative_to(Path(__file__).resolve().parents[1])
        if not str(rel_path).startswith("data/raw/"):
            print(
                f"Warning: File path {file_path} is not under data/raw/ - "
                "this script is intended for raw source artifacts.",
                file=sys.stderr,
            )
    except ValueError:
        pass  # File is outside repository
    
    profile = profile_file(file_path, args.source_id)
    
    if profile.error:
        print(json.dumps(serialize_profile(profile), indent=2), file=sys.stdout)
        return 1
    
    result = serialize_profile(profile)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Profile written to {output_path}")
    else:
        print(json.dumps(result, indent=2))
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
