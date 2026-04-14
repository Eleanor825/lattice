# Lattice

Lattice is an open-source domain data compiler for turning heterogeneous scientific sources into training-ready dataset views.

The current implementation targets **Phase 1** of the research plan:

- ingest text, HTML, JSON, JSONL, and optional PDF sources
- normalize them into a minimal schema family
- attach provenance and dedup metadata
- filter low-value inputs
- export multiple dataset views for training and evaluation

It now also includes a **real-source demo fetcher** that can pull a small public sample from:

- OpenAlex
- arXiv
- PubChem

## Project Layout

- `src/lattice/`: Python package
- `examples/materials/raw/`: sample materials/science inputs
- `docs/`: lightweight project docs
- `tests/`: unit and end-to-end tests
- `01_*.md`, `02_*.md`, `03_*.md`: project notes and proposal drafts

## Minimal Schema Family

- `Document`
- `StructuredRecord`
- `KnowledgeRecord`
- `InstructionTrace`

Each record carries shared metadata:

- `source_id`
- `source_type`
- `url_or_ref`
- `timestamp`
- `license`
- `domain`
- `schema_type`
- `dedup_id`
- `provenance_chain`

## Quickstart

```bash
cd /Users/huanzhang/Desktop/lattice
PYTHONPATH=src python3 -m lattice compile \
  --input examples/materials/raw \
  --output outputs/materials \
  --domain materials \
  --dataset-name Lattice-Materials-v0.1
```

Inspect the generated manifest:

```bash
PYTHONPATH=src python3 -m lattice stats --path outputs/materials
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Or use the convenience targets:

```bash
make compile-example
make test
```

Run a real-source demo:

```bash
PYTHONPATH=src python3 -m lattice demo \
  --raw-output data/demo_raw/solid_state \
  --compiled-output data/demo_compiled/solid_state \
  --domain materials \
  --dataset-name Lattice-Materials-RealDemo \
  --query "solid state battery electrolyte" \
  --compound "lithium iron phosphate" \
  --compound "lithium cobalt oxide"
```

## Output Views

The compiler exports four dataset views:

- `pretrain_view.jsonl`
- `qa_view.jsonl`
- `instruction_view.jsonl`
- `knowledge_view.jsonl`

Each item keeps a reference back to the normalized source record and its provenance chain.

## Current Scope

This repository intentionally ships a compact, runnable Phase 1 baseline instead of a broad placeholder framework. The focus is on:

- a stable schema boundary
- reproducible compilation
- provenance tracking
- training-facing dataset views

Future work will add value modeling, proxy experiments, and data mixture optimization.

## Open-Source Status

Phase 1 currently includes:

- runnable compiler CLI
- example materials/science dataset
- dataset manifest, source coverage report, and dataset card generation
- end-to-end tests
- GitHub Actions CI
- contribution and release scaffolding

## Storage Recommendation

For serious use, keep real fetched data **outside the git-tracked repo**.

- use the repo for code, configs, manifests, and small fixtures
- use a separate local data root or object store for raw and compiled datasets

See [docs/storage_architecture.md](docs/storage_architecture.md) for the recommended layout.
