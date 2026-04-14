# Phase 1 Release Workflow

Lattice Phase 1 is the data foundation layer.

The minimum complete Phase 1 workflow is:

1. fetch raw source snapshots
2. normalize them into Lattice schema records
3. keep provenance / license / dedup metadata
4. filter low-value records
5. compile reusable dataset views
6. write manifests for reproducibility
7. store the result under a structured data root

## Command

```bash
PYTHONPATH=src python3 -m lattice phase1-run \
  --data-root ~/lattice-data \
  --registry configs/source_registry.json \
  --domain materials \
  --release-name lattice-materials-demo \
  --source openalex \
  --source arxiv \
  --source pubchem \
  --query "solid state battery electrolyte" \
  --compound "lithium iron phosphate" \
  --compound "lithium cobalt oxide" \
  --limit 1
```

## Output Layout

```text
<data-root>/
  raw/
  bronze/
  gold/
  manifests/
```

## Current State

Lattice now has a runnable Phase 1 release pipeline.

What still remains outside a strict “complete” Phase 1 definition:

- wider source coverage
- stronger silver-layer linking
- fully working local Flink runtime

Those are important next steps, but the core Phase 1 data production chain is now executable.
