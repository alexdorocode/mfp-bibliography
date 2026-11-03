"""Functional normalization pipeline for MFP proteins.

Normalizes the 8 functional attributes:
    BP1, MF1, CC1, PMID1 (Function 1 / Canonical)
    BP2, MF2, CC2, PMID2 (Function 2 / Moonlighting)
across all catalog datasets, leveraging TargetData annotations and ontology mappings.
"""

from __future__ import annotations

import csv
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from mfp_bibliography.moonprot_parser import MoonProtRecord
from mfp_bibliography.normalization import make_protein_id_uniprot, normalize_uniprot_accession
from mfp_bibliography.targetdata_client import TargetDataClient

DEFAULT_OBO_PATHS = (
    Path("/home/alexdoro/repositories/mfp-dataset-designer/go-basic.obo"),
    Path("/home/alexdoro/repositories/BioData/notebooks/data/go-basic.obo"),
    Path("/home/alexdoro/repositories/FANTASIA/go-basic.obo"),
)

RE_GO_ID = re.compile(r"GO:(\d{7})")
RE_NUM_ONLY = re.compile(r"\b(\d{7})\b")
RE_ARTICLE_NUM = re.compile(r"^\d+$")


def format_go_id(val: str) -> str | None:
    """Ensure a string is formatted as canonical GO:0000000."""
    clean = val.strip()
    if clean.startswith("GO:"):
        return clean
    if clean.isdigit() and len(clean) <= 7:
        return f"GO:{clean:0>7}"
    return None


def parse_go_list(text: str | None) -> list[str]:
    """Extract and canonicalize all GO terms found in a raw text string."""
    if not text:
        return []
    terms = set()
    for m in RE_GO_ID.findall(text):
        terms.add(f"GO:{m}")
    for m in RE_NUM_ONLY.findall(text):
        terms.add(f"GO:{m}")
    return sorted(terms)


def join_terms(terms: Iterable[str]) -> str:
    """Format an iterable of terms into a sorted semicolon-separated string."""
    clean = sorted(set(t.strip() for t in terms if t and t.strip()))
    return "; ".join(clean)


def load_ec2go_mappings(obo_path: str | Path | None = None) -> dict[str, str]:
    """Parse go-basic.obo to build a mapping from EC number to GO Molecular Function ID."""
    candidate_path = None
    if obo_path:
        p = Path(obo_path)
        if p.exists():
            candidate_path = p
    else:
        for p in DEFAULT_OBO_PATHS:
            if p.exists():
                candidate_path = p
                break

    if not candidate_path:
        return {}

    ec2go: dict[str, str] = {}
    current_go = None
    with candidate_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                current_go = None
            elif line.startswith("id: GO:"):
                current_go = line[4:].strip()
            elif line.startswith("xref: EC:") and current_go:
                ec = line[9:].strip().split()[0]
                if ec not in ec2go:
                    ec2go[ec] = current_go
    return ec2go


@dataclass
class ProteinFacetsRecord:
    """Standardized 8-attribute functional record for a protein."""

    protein_id: str
    canonical_uniprot_accession: str
    source_name: str
    source_record_id: str
    # Facet 1 (Canonical / Primary)
    bp1: str = ""
    mf1: str = ""
    cc1: str = ""
    pmid1: str = ""
    func1_desc: str = ""
    # Facet 2 (Moonlighting / Secondary)
    bp2: str = ""
    mf2: str = ""
    cc2: str = ""
    pmid2: str = ""
    func2_desc: str = ""
    # Status and Provenance
    facet_status: str = "resolved"  # "resolved", "partial", "unassigned_mono_source"
    resolution_sources: str = "source_raw"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_plantmp_record(
    row: dict[str, str],
    td_client: TargetDataClient | None = None,
) -> ProteinFacetsRecord:
    """Normalize a raw PlantMP CSV row into a standardized ProteinFacetsRecord."""
    order = row.get("order", "").strip()
    raw_acc = row.get("uniport_id", "").strip()
    accession = normalize_uniprot_accession(raw_acc) or ""
    protein_id = make_protein_id_uniprot(accession) if accession else ""

    bp1_terms = parse_go_list(row.get("go_canonical_bp"))
    mf1_terms = parse_go_list(row.get("go_canonical_mf"))
    bp2_terms = parse_go_list(row.get("go_moonlighting_bp"))
    mf2_terms = parse_go_list(row.get("go_moonlighting_mf"))

    # In PlantMP, pubmed_id is the paper characterizing the moonlighting event
    pmid2 = row.get("pubmed_id", "").strip()
    pmid1 = ""

    cc1_terms: list[str] = []
    cc2_terms: list[str] = []

    res_sources = ["source_raw"]

    if td_client and accession:
        # Check if TargetData has annotations matching the PMID
        if pmid2:
            annos_pmid = td_client.get_annotations_by_pmid(accession, pmid2)
            for a in annos_pmid:
                if a["aspect"] == "CC":
                    cc2_terms.append(a["go_id"])
                elif a["aspect"] == "BP":
                    bp2_terms.append(a["go_id"])
                elif a["aspect"] == "MF":
                    mf2_terms.append(a["go_id"])
            if annos_pmid:
                res_sources.append("targetdata_matched_pmid")

        # Check overall CC annotations in TargetData for canonical CC
        all_annos = td_client.get_annotations_for_accession(accession)
        for a in all_annos:
            if a["aspect"] == "CC" and a["go_id"] not in cc2_terms:
                cc1_terms.append(a["go_id"])

    has_facet1 = bool(bp1_terms or mf1_terms or cc1_terms)
    has_facet2 = bool(bp2_terms or mf2_terms or cc2_terms or pmid2)

    status = "resolved" if (has_facet1 and has_facet2) else ("partial" if (has_facet1 or has_facet2) else "unresolved")

    return ProteinFacetsRecord(
        protein_id=protein_id,
        canonical_uniprot_accession=accession,
        source_name="SRC_PLANTMP",
        source_record_id=f"plantmp_order_{order}",
        bp1=join_terms(bp1_terms),
        mf1=join_terms(mf1_terms),
        cc1=join_terms(cc1_terms),
        pmid1=pmid1,
        func1_desc=row.get("canonical_function_bp") or row.get("canonical_function_mf") or "",
        bp2=join_terms(bp2_terms),
        mf2=join_terms(mf2_terms),
        cc2=join_terms(cc2_terms),
        pmid2=pmid2,
        func2_desc=row.get("moonlighting_function_bp") or row.get("moonlighting_function_mf") or "",
        facet_status=status,
        resolution_sources="; ".join(res_sources),
    )


def normalize_multitaskprotdb_ii_record(
    row: dict[str, str],
    aspect_lookup: dict[str, str] | None = None,
    td_client: TargetDataClient | None = None,
) -> ProteinFacetsRecord:
    """Normalize a MultitaskProtDB-II interim record or raw row into ProteinFacetsRecord."""
    source_record_id = row.get("source_record_id") or f"multitaskprotdb_ii_row_{row.get('row_index', 'unknown')}"
    raw_acc = row.get("uniprot_normalized") or row.get("UniProt") or ""
    accession = normalize_uniprot_accession(raw_acc) or ""
    protein_id = make_protein_id_uniprot(accession) if accession else ""

    # Parse Canonical GO block: "GO:0005840; C:ribosome; IEA:UniProtKB-KW.\nGO:..."
    go_raw = row.get("go_raw") or row.get("GO") or ""
    bp1_terms: list[str] = []
    mf1_terms: list[str] = []
    cc1_terms: list[str] = []

    for line in go_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m_go = RE_GO_ID.search(line)
        if not m_go:
            continue
        gid = f"GO:{m_go.group(1)}"
        m_aspect = re.search(r";\s*([CFP]):", line)
        if m_aspect:
            code = m_aspect.group(1).upper()
            if code == "P":
                bp1_terms.append(gid)
            elif code == "F":
                mf1_terms.append(gid)
            elif code == "C":
                cc1_terms.append(gid)
        elif aspect_lookup and gid in aspect_lookup:
            asp = aspect_lookup[gid]
            if asp == "BP":
                bp1_terms.append(gid)
            elif asp == "MF":
                mf1_terms.append(gid)
            elif asp == "CC":
                cc1_terms.append(gid)

    # Parse Moonlighting GO block: "GO:0008150 biological_process\n..."
    go_moon_raw = row.get("go_moon_raw") or row.get("GO_Moon") or ""
    bp2_terms: list[str] = []
    mf2_terms: list[str] = []
    cc2_terms: list[str] = []

    for m in RE_GO_ID.finditer(go_moon_raw):
        gid = f"GO:{m.group(1)}"
        asp = aspect_lookup.get(gid) if aspect_lookup else None
        if not asp and td_client:
            asp = td_client.get_go_aspect(gid)
        if asp == "BP":
            bp2_terms.append(gid)
        elif asp == "MF":
            mf2_terms.append(gid)
        elif asp == "CC":
            cc2_terms.append(gid)
        else:
            # Fallback based on text next to the term
            end_pos = m.end()
            line_rest = go_moon_raw[end_pos:end_pos + 40].lower()
            if "process" in line_rest or "response" in line_rest:
                bp2_terms.append(gid)
            elif "activity" in line_rest or "binding" in line_rest:
                mf2_terms.append(gid)
            else:
                bp2_terms.append(gid)

    # Reference is the moonlighting reference
    ref_raw = (row.get("reference_raw") or row.get("Reference") or "").strip()
    pmid2 = ref_raw if RE_ARTICLE_NUM.match(ref_raw) else ""
    pmid1 = ""

    res_sources = ["source_raw"]

    if td_client and accession:
        # Check if TargetData has annotations matching pmid2
        if pmid2:
            matched_annos = td_client.get_annotations_by_pmid(accession, pmid2)
            if matched_annos:
                res_sources.append("targetdata_matched_pmid")
                for a in matched_annos:
                    if a["aspect"] == "CC" and a["go_id"] not in cc2_terms:
                        cc2_terms.append(a["go_id"])
                    elif a["aspect"] == "BP" and a["go_id"] not in bp2_terms:
                        bp2_terms.append(a["go_id"])
                    elif a["aspect"] == "MF" and a["go_id"] not in mf2_terms:
                        mf2_terms.append(a["go_id"])

    has_facet1 = bool(bp1_terms or mf1_terms or cc1_terms)
    has_facet2 = bool(bp2_terms or mf2_terms or cc2_terms or pmid2)
    status = "resolved" if (has_facet1 and has_facet2) else ("partial" if (has_facet1 or has_facet2) else "unresolved")

    return ProteinFacetsRecord(
        protein_id=protein_id,
        canonical_uniprot_accession=accession,
        source_name="SRC_MULTITASKPROTDB_II",
        source_record_id=source_record_id,
        bp1=join_terms(bp1_terms),
        mf1=join_terms(mf1_terms),
        cc1=join_terms(cc1_terms),
        pmid1=pmid1,
        func1_desc=row.get("canonical_function_raw") or row.get("Canonical_Function") or "",
        bp2=join_terms(bp2_terms),
        mf2=join_terms(mf2_terms),
        cc2=join_terms(cc2_terms),
        pmid2=pmid2,
        func2_desc=row.get("moonlighting_function_raw") or row.get("Moonlighting_function") or "",
        facet_status=status,
        resolution_sources="; ".join(res_sources),
    )


def normalize_moonprot_record(
    record: MoonProtRecord,
    ec2go: dict[str, str] | None = None,
    aspect_lookup: dict[str, str] | None = None,
    td_client: TargetDataClient | None = None,
) -> ProteinFacetsRecord:
    """Normalize a parsed MoonProtRecord into ProteinFacetsRecord."""
    accession = normalize_uniprot_accession(record.uniprot_id) or ""
    protein_id = make_protein_id_uniprot(accession) if accession else ""
    ec2go = ec2go or {}

    bp1_terms: list[str] = []
    mf1_terms: list[str] = []
    cc1_terms: list[str] = []
    pmid1_list: list[str] = []
    func1_desc = ""

    bp2_terms: list[str] = []
    mf2_terms: list[str] = []
    cc2_terms: list[str] = []
    pmid2_list: list[str] = []
    func2_desc = ""

    res_sources = ["source_raw"]

    # Process Function 1
    if len(record.functions) >= 1:
        f1 = record.functions[0]
        func1_desc = f1.description or ""
        pmid1_list = list(f1.pmids)
        if f1.ec_number and f1.ec_number in ec2go:
            mf1_terms.append(ec2go[f1.ec_number])
            res_sources.append("ec2go_mapped")

    # Process Function 2
    if len(record.functions) >= 2:
        f2 = record.functions[1]
        func2_desc = f2.description or ""
        pmid2_list = list(f2.pmids)
        if f2.ec_number and f2.ec_number in ec2go:
            mf2_terms.append(ec2go[f2.ec_number])
            res_sources.append("ec2go_mapped")

    # TargetData enrichment via PMIDs
    if td_client and accession:
        # Match Function 1 PMIDs
        for p in pmid1_list:
            annos = td_client.get_annotations_by_pmid(accession, p)
            if annos:
                res_sources.append("targetdata_matched_pmid")
            for a in annos:
                if a["aspect"] == "BP":
                    bp1_terms.append(a["go_id"])
                elif a["aspect"] == "MF":
                    mf1_terms.append(a["go_id"])
                elif a["aspect"] == "CC":
                    cc1_terms.append(a["go_id"])

        # Match Function 2 PMIDs
        for p in pmid2_list:
            annos = td_client.get_annotations_by_pmid(accession, p)
            if annos:
                res_sources.append("targetdata_matched_pmid")
            for a in annos:
                if a["aspect"] == "BP":
                    bp2_terms.append(a["go_id"])
                elif a["aspect"] == "MF":
                    mf2_terms.append(a["go_id"])
                elif a["aspect"] == "CC":
                    cc2_terms.append(a["go_id"])

        # If aspects are still empty, cross-check overall TargetData annotations against MoonProt raw GO terms
        if record.raw_go_terms and (not bp1_terms or not mf1_terms or not cc1_terms):
            raw_gos = parse_go_list(record.raw_go_terms)
            all_td = td_client.get_annotations_for_accession(accession)
            for a in all_td:
                if a["go_id"] in raw_gos:
                    if a["aspect"] == "BP" and not bp1_terms:
                        bp1_terms.append(a["go_id"])
                    elif a["aspect"] == "MF" and not mf1_terms:
                        mf1_terms.append(a["go_id"])
                    elif a["aspect"] == "CC" and not cc1_terms:
                        cc1_terms.append(a["go_id"])

    has_facet1 = bool(bp1_terms or mf1_terms or cc1_terms or pmid1_list or func1_desc)
    has_facet2 = bool(bp2_terms or mf2_terms or cc2_terms or pmid2_list or func2_desc)
    status = "resolved" if (has_facet1 and has_facet2) else ("partial" if (has_facet1 or has_facet2) else "unresolved")

    return ProteinFacetsRecord(
        protein_id=protein_id,
        canonical_uniprot_accession=accession,
        source_name="SRC_MOONPROT",
        source_record_id=f"moonprot_{record.moonprot_id}",
        bp1=join_terms(bp1_terms),
        mf1=join_terms(mf1_terms),
        cc1=join_terms(cc1_terms),
        pmid1="; ".join(pmid1_list),
        func1_desc=func1_desc,
        bp2=join_terms(bp2_terms),
        mf2=join_terms(mf2_terms),
        cc2=join_terms(cc2_terms),
        pmid2="; ".join(pmid2_list),
        func2_desc=func2_desc,
        facet_status=status,
        resolution_sources="; ".join(sorted(set(res_sources))),
    )


def resolve_mono_source_record(
    source_name: str,
    source_record_id: str,
    accession: str,
    td_client: TargetDataClient | None = None,
) -> ProteinFacetsRecord:
    """Create a standardized record for mono-source entries (e.g. exclusive MoonDB or MultifacetedProtDB)."""
    clean_acc = normalize_uniprot_accession(accession) or ""
    protein_id = make_protein_id_uniprot(clean_acc) if clean_acc else ""

    notes = "Mono-source entry without source-native facet separation; unassigned per repository policy."
    all_gos = []
    if td_client and clean_acc:
        annos = td_client.get_annotations_for_accession(clean_acc)
        all_gos = sorted(set(a["go_id"] for a in annos))
        if all_gos:
            notes += f" TargetData inventory: {len(all_gos)} GO annotations."

    return ProteinFacetsRecord(
        protein_id=protein_id,
        canonical_uniprot_accession=clean_acc,
        source_name=source_name,
        source_record_id=source_record_id,
        bp1="",
        mf1="",
        cc1="",
        pmid1="",
        func1_desc="",
        bp2="",
        mf2="",
        cc2="",
        pmid2="",
        func2_desc="",
        facet_status="unassigned_mono_source",
        resolution_sources="none",
        notes=notes,
    )
