"""TargetData PostgreSQL database client for GO annotations and aspect lookups."""

from __future__ import annotations

import os
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def normalize_category_aspect(raw_category: str | None) -> str | None:
    """Normalize a GO category into standard two-letter aspect: BP, MF, or CC."""
    if not raw_category:
        return None
    cat = raw_category.strip().upper()
    if cat in ("P", "BIOLOGICAL_PROCESS", "BIOLOGICAL PROCESS"):
        return "BP"
    if cat in ("F", "MOLECULAR_FUNCTION", "MOLECULAR FUNCTION"):
        return "MF"
    if cat in ("C", "CELLULAR_COMPONENT", "CELLULAR COMPONENT"):
        return "CC"
    return cat


class TargetDataClient:
    """Read-only client for querying TargetData PostgreSQL database."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        dbname: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self.host = host or os.environ.get("TARGETDATA_HOST", "localhost")
        self.port = port or int(os.environ.get("TARGETDATA_PORT", "5432"))
        self.dbname = dbname or os.environ.get("TARGETDATA_DB", "TargetData")
        self.user = user or os.environ.get("TARGETDATA_USER", "usuario")
        self.password = password or os.environ.get("TARGETDATA_PASSWORD") or os.environ.get("PGPASSWORD", "clave")

        self._conn = None
        self._aspect_cache: dict[str, str] = {}
        self._cache_preloaded = False

    def connect(self) -> None:
        """Establish connection if psycopg2 is available and connection is not active."""
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2 is not installed; cannot connect to TargetData database.")
        if self._conn is None or self._conn.closed != 0:
            self._conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
            )

    def close(self) -> None:
        """Close database connection."""
        if self._conn is not None and self._conn.closed == 0:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> TargetDataClient:
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def preload_go_aspects(self) -> dict[str, str]:
        """Preload all GO ID -> aspect mappings into memory for instant lookup."""
        if self._cache_preloaded:
            return self._aspect_cache

        self.connect()
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT go_id, category FROM go_terms;")
            for row in cur.fetchall():
                aspect = normalize_category_aspect(row["category"])
                if aspect:
                    self._aspect_cache[row["go_id"]] = aspect

        self._cache_preloaded = True
        return self._aspect_cache

    def get_go_aspect(self, go_id: str) -> str | None:
        """Get the aspect ('BP', 'MF', 'CC') for a given GO identifier."""
        if not self._cache_preloaded:
            self.preload_go_aspects()
        return self._aspect_cache.get(go_id)

    def get_annotations_for_accession(self, accession: str) -> list[dict[str, Any]]:
        """Fetch all GO annotations for a canonical UniProt accession.

        Returns list of dicts with keys:
            go_id, aspect, go_desc, evidence_code, publication_id
        """
        self.connect()
        query = """
            SELECT 
                pga.go_id,
                gt.category as raw_category,
                gt.description as go_desc,
                pga.evidence_code,
                pga.publication_id
            FROM accession a
            JOIN protein p ON a.protein_id = p.id
            JOIN protein_go_term_annotation pga ON pga.protein_id = p.id
            JOIN go_terms gt ON gt.go_id = pga.go_id
            WHERE a.code = %s
            ORDER BY pga.go_id, pga.evidence_code;
        """
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (accession,))
            results = []
            for row in cur.fetchall():
                results.append({
                    "go_id": row["go_id"],
                    "aspect": normalize_category_aspect(row["raw_category"]),
                    "go_desc": row["go_desc"],
                    "evidence_code": row["evidence_code"],
                    "publication_id": row["publication_id"],
                })
            return results

    def get_annotations_by_pmid(self, accession: str, pmid: str) -> list[dict[str, Any]]:
        """Fetch GO annotations for a canonical UniProt accession linked to a specific PMID."""
        all_annos = self.get_annotations_for_accession(accession)
        clean_pmid = pmid.strip()
        return [a for a in all_annos if a.get("publication_id") == clean_pmid]
