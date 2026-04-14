# Lattice Overview

## Goal

Lattice is a data-centric platform for large-model training and optimization in science and materials.

It starts by building the data foundation layer, then expands toward full training and optimization workflows.

## Phase 1 Pipeline

1. Ingest heterogeneous sources from APIs, files, web resources, and databases.
2. Normalize them into a minimal schema family.
3. Track provenance, license status, and dedup information.
4. Score and filter low-value records.
5. Export reusable dataset views.
6. Write manifests for reproducibility and auditing.

## Phase 2 Platform Layer

Phase 2 will consume Phase 1 artifacts and expand Lattice into a model-training and optimization platform:

- pretraining
- continued pretraining
- fine-tuning
- post-training
- value vectors
- proxy experiments
- mixture selection
- feeding schedule optimization
- conversational and low-code workflow control
