from __future__ import annotations

from typing import Any

from lattice.sources.common import http_get_json, safe_query, timestamp_now


def fetch_oqmd_structures(elements: list[str], limit: int, domain: str) -> list[dict[str, Any]]:
    filter_expr = "elements HAS ALL " + ", ".join(f'"{element}"' for element in elements)
    url = f"https://oqmd.org/optimade/structures?filter={safe_query(filter_expr)}&page_limit={limit}"
    payload = http_get_json(url)
    rows: list[dict[str, Any]] = []
    for item in payload.get("data", []):
        attributes = item.get("attributes", {})
        source_id = f"oqmd-{item.get('id')}"
        rows.append(
            {
                "schema_type": "StructuredRecord",
                "source_type": "oqmd",
                "source_id": source_id,
                "url_or_ref": f"https://oqmd.org/materials/entry/{attributes.get('_oqmd_entry_id', item.get('id'))}",
                "timestamp": timestamp_now(),
                "license": "CC BY 4.0",
                "domain": domain,
                "provenance_chain": [source_id],
                "payload": {
                    "entity": attributes.get("chemical_formula_reduced") or str(item.get("id")),
                    "entity_type": "material",
                    "fields": {
                        "chemical_formula_reduced": attributes.get("chemical_formula_reduced"),
                        "elements": ",".join(attributes.get("elements", [])),
                        "band_gap": attributes.get("_oqmd_band_gap"),
                        "stability": attributes.get("_oqmd_stability"),
                        "volume": attributes.get("_oqmd_volume"),
                        "spacegroup": attributes.get("_oqmd_spacegroup"),
                        "prototype": attributes.get("_oqmd_prototype"),
                        "nsites": attributes.get("nsites"),
                    },
                    "description": f"OQMD structure entry {item.get('id')} for elements {', '.join(elements)}.",
                },
            }
        )
    return rows

