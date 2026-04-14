from __future__ import annotations

import json
import urllib.request
from typing import Any

from lattice.sources.common import DEFAULT_USER_AGENT, _ssl_context, timestamp_now


def fetch_nomad_materials(elements: list[str], limit: int, domain: str) -> list[dict[str, Any]]:
    url = "https://nomad-lab.eu/prod/v1/api/v1/entries/query"
    payload = {
        "owner": "public",
        "query": {"results.material.elements": {"all": elements}},
        "pagination": {"page_size": limit},
        "required": {
            "include": [
                "entry_id",
                "upload_id",
                "entry_name",
                "results.material.chemical_formula_reduced",
                "results.material.elements",
            ]
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": DEFAULT_USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=30, context=_ssl_context()) as response:
        response_payload = json.load(response)

    rows: list[dict[str, Any]] = []
    for item in response_payload.get("data", []):
        material = item.get("results", {}).get("material", {})
        formula = material.get("chemical_formula_reduced") or item.get("entry_name") or item.get("entry_id")
        source_id = f"nomad-{item.get('entry_id')}"
        rows.append(
            {
                "schema_type": "StructuredRecord",
                "source_type": "nomad",
                "source_id": source_id,
                "url_or_ref": f"https://nomad-lab.eu/prod/v1/gui/search/entries/entry/id/{item.get('entry_id')}",
                "timestamp": timestamp_now(),
                "license": "CC BY 4.0",
                "domain": domain,
                "provenance_chain": [source_id],
                "payload": {
                    "entity": formula,
                    "entity_type": "material",
                    "fields": {
                        "entry_id": item.get("entry_id"),
                        "upload_id": item.get("upload_id"),
                        "chemical_formula_reduced": formula,
                        "elements": ",".join(material.get("elements", [])),
                    },
                    "description": f"NOMAD public entry for elements {', '.join(elements)}.",
                },
            }
        )
    return rows

