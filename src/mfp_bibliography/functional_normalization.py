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

DEFAULT_MOONDB_EMF_PATH = Path("data/raw/moondb/all_EMF_annotation.tsv")
DEFAULT_MOONDB_MANUAL_PATH = Path("data/raw/moondb/all_manual_curated.tsv")

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


def load_obo_aspects(obo_path: str | Path | None = None) -> dict[str, str]:
    """Parse go-basic.obo to extract namespace aspect (BP, MF, CC) for primary and alt IDs."""
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

    obo_aspects: dict[str, str] = {}
    current_ids: list[str] = []
    with candidate_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                current_ids = []
            elif line.startswith("id: GO:"):
                current_ids.append(line[4:].strip())
            elif line.startswith("alt_id: GO:"):
                current_ids.append(line[8:].strip())
            elif line.startswith("namespace:") and current_ids:
                ns = line[10:].strip().lower()
                asp = None
                if ns == "biological_process":
                    asp = "BP"
                elif ns == "molecular_function":
                    asp = "MF"
                elif ns == "cellular_component":
                    asp = "CC"
                if asp:
                    for cid in current_ids:
                        obo_aspects[cid] = asp
    return obo_aspects


CELLULAR_LOCATION_KEYWORDS: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile(r"\b(nucle(us|ar|i))\b", re.IGNORECASE), "GO:0005634"),  # nucleus
    (re.compile(r"\b(plasma\s*membrane)\b", re.IGNORECASE), "GO:0005886"),  # plasma membrane
    (re.compile(r"\b(cytosol|cytosolic|cytoplasm)\b", re.IGNORECASE), "GO:0005737"),  # cytoplasm
    (re.compile(r"\b(mitochondri(on|al|a))\b", re.IGNORECASE), "GO:0005739"),  # mitochondrion
    (re.compile(r"\b(extracellular)\b", re.IGNORECASE), "GO:0005576"),  # extracellular region
    (re.compile(r"\b(endosom(e|al)|escrt)\b", re.IGNORECASE), "GO:0005768"),  # endosome
    (re.compile(r"\b(eye\s*lens|lens)\b", re.IGNORECASE), "GO:0005212"),  # structural constituent of eye lens
    (re.compile(r"\b(membrane)\b", re.IGNORECASE), "GO:0016020"),  # membrane
)


def extract_cellular_components_from_text(text: str | None) -> list[str]:
    """Detect cellular compartment keywords in text (e.g. from Condition: clauses) and map to GO-CC."""
    if not text:
        return []
    terms = set()
    for pattern, go_id in CELLULAR_LOCATION_KEYWORDS:
        if pattern.search(text):
            terms.add(go_id)
    return sorted(terms)


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
            elif "activity" in line_rest or "binding" in line_rest or "function" in line_rest:
                mf2_terms.append(gid)
            elif "component" in line_rest or "cellular" in line_rest:
                cc2_terms.append(gid)
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


def load_moondb_emf_data(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Load all_EMF_annotation.tsv into a dictionary grouped by UniprotKB_AC.
    Preserves raw terms_1 and terms_2 without imposing fixed categories.
    """
    file_path = Path(path) if path else DEFAULT_MOONDB_EMF_PATH
    if not file_path.exists():
        return {}

    emf_data: dict[str, dict[str, Any]] = {}
    with file_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            acc = normalize_uniprot_accession(row.get("UniprotKB_AC"))
            if not acc:
                continue
            if acc not in emf_data:
                emf_data[acc] = {
                    "terms_1": set(),
                    "terms_2": set(),
                    "names_1": set(),
                    "names_2": set(),
                }
            g1 = row.get("GO_ID_1", "").strip()
            g2 = row.get("GO_ID_2", "").strip()
            if g1:
                emf_data[acc]["terms_1"].add(g1)
            if g2:
                emf_data[acc]["terms_2"].add(g2)
            n1 = row.get("GO_Name_1", "").strip()
            n2 = row.get("GO_ID_Name", "").strip()
            if n1:
                emf_data[acc]["names_1"].add(n1)
            if n2:
                emf_data[acc]["names_2"].add(n2)
    return emf_data


def load_moondb_manual_data(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Load all_manual_curated.tsv into a dictionary keyed by UniprotAC."""
    file_path = Path(path) if path else DEFAULT_MOONDB_MANUAL_PATH
    if not file_path.exists():
        return {}

    manual_data: dict[str, dict[str, Any]] = {}
    with file_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            acc = normalize_uniprot_accession(row.get("UniprotAC"))
            if not acc:
                continue
            f1 = row.get("Function_1_text", "").strip()
            f2 = row.get("Function_2_text", "").strip()
            raw_pubs = row.get("Publications", "").strip()
            pubs = [p.strip() for p in raw_pubs.split(",") if p.strip() and p.strip().isdigit()]
            cc1_terms = extract_cellular_components_from_text(f1)
            cc2_terms = extract_cellular_components_from_text(f2)
            manual_data[acc] = {
                "f1": f1,
                "f2": f2,
                "pubs": pubs,
                "cc1_terms": cc1_terms,
                "cc2_terms": cc2_terms,
                "species": row.get("Species", "").strip(),
            }
    return manual_data


def normalize_moondb_record(
    accession: str,
    source_record_id: str,
    emf_data: dict[str, dict[str, Any]] | None = None,
    manual_data: dict[str, dict[str, Any]] | None = None,
    td_client: TargetDataClient | None = None,
    obo_aspects: dict[str, str] | None = None,
) -> ProteinFacetsRecord:
    """Normalize a MoonDB protein using rich EMF predictions or manual curation data.
    Dynamically routes each GO term according to its real ontology aspect (BP, MF, CC).
    """
    clean_acc = normalize_uniprot_accession(accession) or ""
    protein_id = make_protein_id_uniprot(clean_acc) if clean_acc else ""
    emf_data = emf_data or {}
    manual_data = manual_data or {}
    obo_aspects = obo_aspects or {}

    def get_aspect(go_id: str) -> str | None:
        if td_client:
            asp = td_client.get_go_aspect(go_id)
            if asp:
                return asp
        return obo_aspects.get(go_id)

    bp1_terms: list[str] = []
    mf1_terms: list[str] = []
    cc1_terms: list[str] = []
    pmid1 = ""
    func1_desc = ""

    bp2_terms: list[str] = []
    mf2_terms: list[str] = []
    cc2_terms: list[str] = []
    pmid2 = ""
    func2_desc = ""

    res_sources = []

    # Priority 1: Manual Curated
    if clean_acc in manual_data:
        m = manual_data[clean_acc]
        func1_desc = m["f1"]
        func2_desc = m["f2"]
        pmid2 = "; ".join(m["pubs"])
        cc1_terms.extend(m["cc1_terms"])
        cc2_terms.extend(m["cc2_terms"])
        res_sources.append("source_raw_moondb_curated")

        # Query TargetData with PMIDs to enrich GO terms
        if td_client and clean_acc and m["pubs"]:
            for p in m["pubs"]:
                annos = td_client.get_annotations_by_pmid(clean_acc, p)
                if annos:
                    res_sources.append("targetdata_matched_pmid")
                for a in annos:
                    if a["aspect"] == "BP":
                        bp2_terms.append(a["go_id"])
                    elif a["aspect"] == "MF":
                        mf2_terms.append(a["go_id"])
                    elif a["aspect"] == "CC" and a["go_id"] not in cc2_terms:
                        cc2_terms.append(a["go_id"])

    # Priority 2: Predicted EMF
    elif clean_acc in emf_data:
        emf = emf_data[clean_acc]
        func1_desc = "; ".join(sorted(emf["names_1"]))
        func2_desc = "; ".join(sorted(emf["names_2"]))
        res_sources.append("source_raw_moondb_emf")

        # Dynamically classify terms_1 by their true ontology aspect
        for g in sorted(emf["terms_1"]):
            asp = get_aspect(g)
            if asp == "BP":
                bp1_terms.append(g)
            elif asp == "MF":
                mf1_terms.append(g)
            elif asp == "CC":
                cc1_terms.append(g)
            else:
                bp1_terms.append(g)

        # Dynamically classify terms_2 by their true ontology aspect
        for g in sorted(emf["terms_2"]):
            asp = get_aspect(g)
            if asp == "BP":
                bp2_terms.append(g)
            elif asp == "MF":
                mf2_terms.append(g)
            elif asp == "CC":
                cc2_terms.append(g)
            else:
                bp2_terms.append(g)

        # Enrich with TargetData overall annotations if missing MF / CC
        if td_client and clean_acc and (not mf1_terms or not cc1_terms):
            all_td = td_client.get_annotations_for_accession(clean_acc)
            for a in all_td:
                if a["aspect"] == "MF" and not mf1_terms:
                    mf1_terms.append(a["go_id"])
                    res_sources.append("targetdata_enriched")
                elif a["aspect"] == "CC" and not cc1_terms:
                    cc1_terms.append(a["go_id"])
                    res_sources.append("targetdata_enriched")

    else:
        return resolve_mono_source_record("SRC_MOONDB", source_record_id, clean_acc, td_client)

    has_facet1 = bool(bp1_terms or mf1_terms or cc1_terms or func1_desc)
    has_facet2 = bool(bp2_terms or mf2_terms or cc2_terms or func2_desc or pmid2)
    status = "resolved" if (has_facet1 and has_facet2) else ("partial" if (has_facet1 or has_facet2) else "unresolved")

    return ProteinFacetsRecord(
        protein_id=protein_id,
        canonical_uniprot_accession=clean_acc,
        source_name="SRC_MOONDB",
        source_record_id=source_record_id,
        bp1=join_terms(bp1_terms),
        mf1=join_terms(mf1_terms),
        cc1=join_terms(cc1_terms),
        pmid1=pmid1,
        func1_desc=func1_desc,
        bp2=join_terms(bp2_terms),
        mf2=join_terms(mf2_terms),
        cc2=join_terms(cc2_terms),
        pmid2=pmid2,
        func2_desc=func2_desc,
        facet_status=status,
        resolution_sources="; ".join(sorted(set(res_sources))),
        notes="Normalized via MoonDB EMF predictions or manual curation.",
    )
