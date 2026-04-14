# Source Catalog

## Source Registry Snapshot

This table summarizes the current open-source source coverage and how each source maps into Lattice.

| Source | Category | Access | Priority | Main Use | Schema Targets |
|---|---|---|---|---|---|
| OpenAlex | Scholarly metadata | REST API | P0 | work discovery, paper metadata, provenance | `Document` |
| Crossref | Scholarly metadata | REST API | P0 | DOI metadata, metadata enrichment, provenance | `Document` |
| arXiv | Preprints / papers | API + bulk | P0 | abstracts and paper text | `Document` |
| Materials Project | Structured materials DB | API | P0 | material properties and summaries | `StructuredRecord`, `KnowledgeRecord` |
| OQMD | Structured materials DB | API / download | P0 | crystal and DFT properties | `StructuredRecord` |
| NOMAD | Materials repository | API | P0 | materials entries and repository metadata | `StructuredRecord`, `Document` |
| JARVIS | Materials repository | OPTIMADE / tools | P0 | materials structure and property records | `StructuredRecord`, `Document` |
| PubChem | Chemistry database | PUG REST | P0 | compound properties and identifiers | `StructuredRecord`, `KnowledgeRecord` |
| Wikidata | Open knowledge graph | MediaWiki API | P0 | entity descriptions and linked knowledge | `KnowledgeRecord` |
| PatentsView | Patents | ODP migration | P0 optional | patent metadata and technical prior art | `Document`, `StructuredRecord` |
| COD | Crystal structure database | search / dumps | P1 | crystal structure coverage | `StructuredRecord` |

## Data Type Classification

Lattice separates source type from data type.

### Source-side categories

| Category | Meaning | Example Sources |
|---|---|---|
| Scholarly metadata | Paper-level metadata and discovery signals | OpenAlex, Crossref |
| Preprints / papers | Paper text and abstracts | arXiv |
| Structured materials DB | Structured scientific property tables | Materials Project, OQMD |
| Materials repository | Broader materials datasets and archives | NOMAD, JARVIS |
| Chemistry database | Compound-level chemistry information | PubChem |
| Open knowledge graph | Entity-level symbolic knowledge | Wikidata |
| Patents | Technical and industrial documents | PatentsView |
| Crystal structure DB | Structure-centric crystallographic records | COD |

### Lattice schema types

| Schema Type | Meaning | Typical Fields | Example Sources |
|---|---|---|---|
| `Document` | Long-form text for reading or training | title, text, sections | arXiv, OpenAlex, Crossref |
| `StructuredRecord` | Entity-centered structured properties | entity, fields, description | OQMD, NOMAD, JARVIS, PubChem |
| `KnowledgeRecord` | Subject-predicate-object knowledge units | subject, predicate, object, evidence | Wikidata, Materials Project, PubChem |
| `InstructionTrace` | Instruction-following or workflow examples | instruction, input, output, tool trace | future task recipes, generated workflows |

### Training-facing compiled views

| View | Purpose |
|---|---|
| `pretrain_view` | language-model pretraining text |
| `qa_view` | supervised QA or retrieval-style supervision |
| `instruction_view` | instruction tuning or task adaptation |
| `knowledge_view` | structured knowledge or symbolic supervision |
