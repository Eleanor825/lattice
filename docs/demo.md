# Lattice Demo

## Demo A: Real-source Compilation

Lattice can already fetch a small real-source batch and compile it into training-ready views.

Current demo source mix:

- OpenAlex
- arXiv
- PubChem

Current result:

- raw records: `4`
- kept records: `4`
- source counts:
  - `arxiv: 1`
  - `openalex: 1`
  - `pubchem: 2`
- generated views:
  - `pretrain_view: 4`
  - `qa_view: 10`
  - `instruction_view: 4`
  - `knowledge_view: 10`

Reference:

- [Manifest](../data/demo_compiled/solid_state/reports/manifest.json)

## Demo B: Local and Spark Runtime

Lattice can also execute the same normalized input through different engines.

Currently verified:

- local engine
- Spark local engine

Current runtime fixture result:

- raw records: `4`
- kept records: `3`
- dropped records:
  - `boilerplate: 1`
- schema counts:
  - `Document: 1`
  - `StructuredRecord: 1`
  - `KnowledgeRecord: 1`

References:

- [Local manifest](../outputs/runtime-local/reports/manifest.json)
- [Spark manifest](../outputs/runtime-spark/reports/manifest.json)

## Flink

The Flink-compatible code path is implemented, but the current local environment still has a PyFlink installation blocker.

Reference:

- [Engine notes](engines.md)
