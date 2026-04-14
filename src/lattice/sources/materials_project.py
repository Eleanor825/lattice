from __future__ import annotations

import os
from typing import Any

from lattice.sources.common import http_get_json, timestamp_now


def resolve_materials_project_api_key() -> str | None:
    for env_name in ("MP_API_KEY", "MATERIALS_PROJECT_API_KEY"):
        value = os.environ.get(env_name)
        if value:
            return value
    return None


def fetch_materials_project_materials(
    elements: list[str], limit: int, domain: str
) -> tuple[list[dict[str, Any]], list[str]]:
    api_key = resolve_materials_project_api_key()
    if not api_key:
        return [], ["Materials Project skipped: MP_API_KEY is not set."]

    query_fields = "material_id,formula_pretty,band_gap,energy_above_hull,is_stable,elements,nsites"
    url = (
        "https://api.materialsproject.org/materials/summary/"
        f"?elements={','.join(elements)}&_limit={limit}&_fields={query_fields}"
    )
    payload = http_get_json(url, headers={"X-API-KEY": api_key})
    rows: list[dict[str, Any]] = []
    for item in payload.get("data", []):
        material_id = item.get("material_id")
        formula = item.get("formula_pretty") or material_id
        source_id = f"materials-project-{material_id}"
        rows.append(
            {
                "schema_type": "StructuredRecord",
                "source_type": "materials_project",
                "source_id": source_id,
                "url_or_ref": f"https://materialsproject.org/materials/{material_id}",
                "timestamp": timestamp_now(),
                "license": "Materials Project API terms",
                "domain": domain,
                "provenance_chain": [source_id],
                "payload": {
                    "entity": formula,
                    "entity_type": "material",
                    "fields": {
                        "material_id": material_id,
                        "formula_pretty": formula,
                        "elements": ",".join(item.get("elements", [])),
                        "band_gap": item.get("band_gap"),
                        "energy_above_hull": item.get("energy_above_hull"),
                        "is_stable": item.get("is_stable"),
                        "nsites": item.get("nsites"),
                    },
                    "description": f"Materials Project summary entry for elements {', '.join(elements)}.",
                },
            }
        )
    return rows, []
