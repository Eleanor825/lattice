# Lattice Storage Architecture

## Short Answer

If this grows beyond a toy repository, **do not store real fetched data inside the git repo**.

Use this split:

- Git repo:
  - code
  - source registry
  - schemas
  - manifests
  - small fixtures only
- Data root or object storage:
  - raw source snapshots
  - normalized records
  - curated training views
  - indexes and manifests

## Recommended Layout

### Local Development

For a single machine or small prototype:

```text
~/lattice-data/
  raw/
    api/
      openalex/
      arxiv/
      pubchem/
      materials_project/
    web/
    dumps/
  bronze/
    normalized_records/
  silver/
    entities/
    linked_records/
  gold/
    pretrain/
    qa/
    instruction/
    knowledge/
  manifests/
  cache/
```

### Larger Project

For a serious project, use object storage:

```text
s3://lattice-data/
  raw/
  bronze/
  silver/
  gold/
  manifests/
```

Equivalent backends are fine:

- S3
- GCS
- Azure Blob
- MinIO
- Cloudflare R2

## What Goes Where

### `raw/`

Immutable snapshots from the original source.

Store by:

- source name
- acquisition date
- run id

Example:

```text
raw/api/openalex/date=2026-04-14/run=demo-001/openalex.jsonl
raw/api/arxiv/date=2026-04-14/run=demo-001/arxiv.xml
raw/api/pubchem/date=2026-04-14/run=demo-001/pubchem.jsonl
```

### `bronze/`

Normalized but source-faithful records.

This is where all sources are converted into the Lattice schema family with provenance preserved.

### `silver/`

Cross-source linked records.

Examples:

- DOI/arXiv/OpenAlex link tables
- material entity resolution
- property alignment
- duplicate clusters

### `gold/`

Training-facing outputs.

Examples:

- `pretrain_view`
- `qa_view`
- `instruction_view`
- `knowledge_view`

These should be versioned releases, not ad hoc scratch outputs.

## Metadata and Catalog

Use a catalog database in parallel with object storage.

### Small setup

- `DuckDB` or `SQLite` for manifests and indexes

### Larger setup

- `Postgres` for source registry, run logs, manifests, lineage, and release metadata

Track at minimum:

- source name
- source URL
- fetch time
- license status
- file checksum
- schema counts
- record counts
- release version

## File Formats

Recommended defaults:

- raw API snapshots: `jsonl`, `json`, `xml`
- normalized records: `jsonl` now, `parquet` later
- large training views: `jsonl` for simplicity, `parquet` for scale
- manifests: `json`

## Practical Recommendation

If you want this to become a serious project:

1. Keep the repo small and code-focused.
2. Store all real fetched data under a separate `data root` or bucket.
3. Treat `raw` as immutable.
4. Version `gold` datasets like releases.
5. Keep provenance and license metadata at every layer.

This is the main difference between a demo pipeline and a real data platform.

