# GO Annotation, Evidence-Code and Bibliography Contract

## Metadata

- **Status:** draft (version 0.1) for roadmap Phase D0.
- **Owner:** repository maintainers.
- **Normative external references:** [GO evidence-code guide](http://geneontology.org/docs/guide-go-evidence-codes/) and [GAF 2.2 specification](http://geneontology.org/docs/go-annotation-file-gaf-2.2-spec/). They define code and field semantics; their tables are not copied here.
- **Related:** [evidence taxonomy](evidence-taxonomy.md), [source claims contract](../source-claims-contract.md), [release policy](../release-policy.md).

## Scope

- In this repository, MF/MFP means multifunctional/moonlighting proteins. In GO, MF means the Molecular Function aspect.
- Catalog outputs contain source observations, not MF/NMF binary truth. A GO annotation is a sourced function statement, never a multifunctionality verdict.
- The knowledge model must preserve ALL retrieved GO annotation evidence codes, including codes excluded from any particular analysis.
- No GO annotation alone proves that a protein is multifunctional.

## Annotation grain

Distinct grains, each with its own identifier:

- **Protein entity** — catalog entity; automatic merging only by exact normalized UniProt accession.
- **Source record** — one entry from a specific source artifact.
- **GO annotation/assertion** — one protein–GO statement from one provider with one evidence code.
- **Evidence statement** — the evidence-bearing detail (code, qualifier, With/From) behind an annotation.
- **Reference/work** — a bibliographic work (PMID/DOI) or non-article reference (e.g. GO_REF).
- **Annotation–reference relation** — the claim that a reference supports a specific annotation.

Repeated protein–GO pairs are preserved whenever reference, evidence code, relation, qualifier, provider, annotation date, form/isoform, or context differs. Distinct annotation rows are distinct retrieved statements, not asserted to be distinct biological facts.

Stored fields: raw and normalized GO ID, evidence code, and reference identifiers; plus aspect, relation/NOT qualifier, With/From, annotation extension, Assigned By, source dataset/version, and provenance where available. Missing source values are stored as null, never invented.

### Stable IDs and deduplication keys

Each observation grain carries a stable ID, computed as a hash over a canonical serialization of its normalized tuple; rows differing in any tuple element are never merged. Provider/Assigned By, source dataset/version, and provenance appear in the tuples so that independent observations never collapse.

- **GO/functional annotation (`go_annotation_id`)** — grain: one protein–GO (or free-text function) statement from one provider. Tuple: (protein_id, raw GO ID/function text, normalized GO ID, evidence code, qualifier/relation incl. NOT, aspect, form/isoform, Assigned By, annotation date, source dataset/version, context).
- **Evidence statement (`evidence_statement_id`)** — grain: one evidence-bearing detail behind one annotation. Tuple: (go_annotation_id, raw code, code scheme, qualifier, With/From, annotation extension, provider, dataset/version).
- **Annotation–reference relation (`annotation_reference_id`)** — grain: one work supports one annotation. Tuple: (go_annotation_id, work_id, role, support scope, polarity, source, extraction/run version).
- **Bibliographic work (`work_id`)** — grain: one verified work (article or non-article reference). Tuple: (verified identifier-equivalence set, reference type, equivalence source, identity-rule version); raw identifier variants (PMID, DOI, GO_REF ID) live on a work-identifier table keyed to `work_id`.
- **Record-level reference relation (`record_reference_id`)** — grain: one source record cites one work. Tuple: (source_name, source_record_id, work_id, role, extraction/run version).

A stable ID identifies one retrieved observation. Derived grouping keys such as `(protein_id, go_id)` group observations for views and counts only; they are never primary keys and may legitimately cover multiple rows.

## Evidence vocabulary and policy

GO categories, per the normative guide: standard experimental (EXP, IDA, IPI, IMP, IGI, IEP); high-throughput experimental (HTP, HDA, HMP, HGI, HEP); phylogenetic; computational; author statement (TAS, NAS); curator statement (IC, ND); electronic (IEA).

- **Analysis cohort v0 (exact code set):** EXP, IDA, IPI, IMP, IGI, IEP, TAS, IC.
- **TAS and IC are NOT experimental codes.** TAS is an author statement; IC is a curator statement. Cohort v0 is an "experimentally or authoritatively asserted support" cohort, not an experimental one.
- **Strict-experimental view (separate, exact code set):** EXP, IDA, IPI, IMP, IGI, IEP.
- Inclusion of high-throughput experimental codes in a cohort is a documented policy decision — neither implicit omission nor automatic inclusion.
- The raw code, its code scheme, an optional ECO mapping, and the mapping version are stored separately. An evidence code is never inferred from a PMID or article alone.
- Filtering changes derived views only; the stored annotation inventory is never filtered.

## Reference semantics

- **Assertion-level support** (a reference supports a specific annotation) and **record-level citation** (a source record cites a work) are separate relation types.
- A record-level citation must never become support for every GO term in that record.
- Bibliographic works (PMID/DOI) are distinct from GO_REF and other non-article references.
- One work may carry multiple identifiers; one annotation may cite multiple references; one work may support multiple annotation relations.
- Role, support scope, polarity, source, extraction/run version, and review status are preserved when provided.
- "Cited" is never equated with "experimentally demonstrates".

## Work identity

- PMID and DOI are equivalent — the same verified work — only when an explicit source-provided cross-reference or a documented, versioned identity rule links them; the rule version is recorded.
- Otherwise the identifiers receive separate `work_id` values and cross-identifier identity is marked `unknown`; they are never silently merged or counted as one verified work.
- Counts must report unique verified works separately from works whose identifier equivalence is unresolved (labeled unknown-identity), per the Counting contract.

## Catalog linkage

- Annotation, evidence, and reference-relation records link to the existing catalog `protein_id` (from `mfp_proteins.csv`) through documented foreign keys; they retain source-record provenance (`source_name`, `source_record_id`) and retrieval provenance (dataset/version, retrieval run).
- The laboratory adapter never creates a competing protein identity; the exact-normalized-UniProt merge rule is unchanged.
- Input identifiers that match no catalog protein are quarantined for review — never assigned a new `protein_id`, never silently discarded.

## Entity–relationship sketch (Phase D0)

```
protein ──1:n── source_record
source_record ──0:n── go_annotation
go_annotation ──1:n── evidence_statement
go_annotation ──0:n── annotation_reference ──n:1── work
source_record ──0:n── record_reference ──n:1── work
```

- Mandatory: every source record belongs to exactly one protein; every annotation links to one source record and one protein; every annotation has at least one evidence statement.
- Optional: a source record may carry no GO annotation (free-text functions only); annotation–reference and record–reference relations may be absent.
- The two reference paths are independent: a work reachable via `record_reference` is not thereby in `annotation_reference` for any annotation. No link implies that a record-cited article supports every GO annotation of the protein.

## Counting contract

Aggregates are reported separately, each labeled with grain and cohort version:

1. Unique bibliographic works per protein, linked at annotation level.
2. Unique works per GO annotation (grain: annotation row; any protein-level sum is a union over annotations and must say so).
3. Record-level works per protein.
4. Annotation–reference relation count.
5. Annotations by evidence code and by evidence category.
6. Counts in the full inventory versus each versioned analysis cohort.

Counting rules: PMID and DOI for the same verified work count once (see [Work identity](#work-identity)); works of unresolved identifier equivalence count separately as unknown-identity works, and both figures are reported. Non-article references (e.g. GO_REF) are excluded from "article" counts and reported alongside. Contradictory and NOT annotations are retained in the inventory and reported explicitly in cohort views. No aggregate may silently mix protein-level citations with GO-level support.

## Governance

- The [roadmap](../roadmap/mfp-catalog-implementation-plan.md) is the milestone and status tracker; this contract is the source of truth for these semantics.
- Changes to the code set, counting grain, identity rules, or relation semantics require an ADR or a versioned policy change producing a new cohort version — never a silent edit.
- Fixtures must cover: same protein/GO pair with two articles; one article as PMID and DOI; TAS and IC in cohort v0 but not experimental; IEA retained but excluded from cohort v0; record-level-only citation; a NOT annotation; GO_REF versus PMID; an unknown evidence code.
- The future laboratory annotation-retrieval adapter must conform to this contract; its retrieval implementation is out of scope here.
- Current catalog outputs contain no GO annotations or article links; the criteria above are future obligations, not present claims.

## Unresolved policy decisions

- **Schema-freeze blocker:** ECO column shape and required mapping version must be decided before schemas are frozen; no default is assumed here.
- Versioned analysis choices (no schema impact): whether high-throughput experimental codes (HTP, HDA, HMP, HGI, HEP) enter a later cohort version, and at which grain; whether TAS/IC split from cohort v0 into a separate curator-statement view. The stored inventory retains all codes regardless.
