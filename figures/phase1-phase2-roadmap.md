# Phase 1 / Phase 2 Roadmap

This diagram summarizes how Lattice moves from a data compiler in Phase 1 to a data intelligence layer in Phase 2.

```mermaid
flowchart LR
    G["Overall Goal<br/>Build a data-centric infrastructure for science and materials foundation models"]

    subgraph P1["Phase 1: Data Compiler"]
        S1["Source Registry<br/>OpenAlex / arXiv / OQMD / NOMAD / MP / PubChem / Patents"]
        S2["Ingestion<br/>API fetch / dumps / web / files"]
        S3["Normalization<br/>Document / StructuredRecord / KnowledgeRecord / InstructionTrace"]
        S4["Data Quality<br/>provenance / license / dedup / filtering"]
        S5["Compiled Views<br/>pretraining / QA / instruction / knowledge"]
        S6["Release Layer<br/>manifests / dataset cards / reproducible outputs"]
        S1 --> S2 --> S3 --> S4 --> S5 --> S6
    end

    subgraph P2["Phase 2: Data Intelligence"]
        T1["Value Modeling<br/>quality / novelty / affinity / coverage / utility"]
        T2["Proxy Experiments<br/>small-budget utility estimation"]
        T3["Mixture Selection<br/>which data to use"]
        T4["Feeding Strategy<br/>curriculum / schedule / allocation"]
        T5["Optimized Training Data<br/>task-conditioned data plan"]
        T1 --> T2 --> T3 --> T4 --> T5
    end

    G --> P1
    P1 --> P2
    S5 -. feeds .-> T1
    S6 -. release and evaluation signals .-> T2
```
