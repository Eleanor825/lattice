from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from lattice.sources.arxiv import fetch_arxiv_documents
from lattice.sources.common import ensure_dir, timestamp_now, write_source_jsonl, write_source_manifest
from lattice.sources.openalex import fetch_openalex_documents
from lattice.sources.pubchem import fetch_pubchem_compounds


@dataclass(slots=True)
class DemoFetchConfig:
    output_dir: str
    domain: str
    query: str = "solid state battery electrolyte"
    openalex_limit: int = 3
    arxiv_limit: int = 3
    compounds: list[str] = field(
        default_factory=lambda: ["lithium iron phosphate", "lithium cobalt oxide"]
    )


def run_demo_fetch(config: DemoFetchConfig) -> dict[str, Any]:
    output_dir = ensure_dir(config.output_dir)
    warnings: list[str] = []

    openalex_rows = fetch_openalex_documents(config.query, config.openalex_limit, config.domain)
    arxiv_rows = fetch_arxiv_documents(config.query, config.arxiv_limit, config.domain)
    pubchem_rows, pubchem_warnings = fetch_pubchem_compounds(config.compounds, config.domain)
    warnings.extend(pubchem_warnings)

    write_source_jsonl(output_dir, "openalex", openalex_rows)
    write_source_jsonl(output_dir, "arxiv", arxiv_rows)
    write_source_jsonl(output_dir, "pubchem", pubchem_rows)

    manifest = {
        "fetched_at": timestamp_now(),
        "domain": config.domain,
        "query": config.query,
        "compounds": config.compounds,
        "config": asdict(config),
        "output_dir": str(Path(output_dir).resolve()),
        "counts": {
            "openalex": len(openalex_rows),
            "arxiv": len(arxiv_rows),
            "pubchem": len(pubchem_rows),
        },
        "warnings": warnings,
    }
    write_source_manifest(output_dir, manifest)
    return manifest
