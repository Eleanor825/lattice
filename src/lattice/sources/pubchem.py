from __future__ import annotations

from typing import Any

from lattice.sources.common import http_get_json, safe_query, timestamp_now
from lattice.utils import slugify


def fetch_pubchem_compounds(names: list[str], domain: str) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    property_fields = "MolecularFormula,CanonicalSMILES,InChIKey,IUPACName"
    for name in names:
        url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
            f"{safe_query(name)}/property/{property_fields}/JSON"
        )
        try:
            payload = http_get_json(url)
        except Exception as exc:  # pragma: no cover - network-dependent warning path
            warnings.append(f"PubChem lookup failed for '{name}': {exc}")
            continue
        properties = payload.get("PropertyTable", {}).get("Properties", [])
        if not properties:
            warnings.append(f"PubChem returned no properties for '{name}'")
            continue
        item = properties[0]
        source_id = f"pubchem-{slugify(name)}"
        rows.append(
            {
                "schema_type": "StructuredRecord",
                "source_type": "pubchem",
                "source_id": source_id,
                "url_or_ref": f"https://pubchem.ncbi.nlm.nih.gov/#query={safe_query(name)}",
                "timestamp": timestamp_now(),
                "license": "PubChem open data",
                "domain": domain,
                "provenance_chain": [source_id],
                "payload": {
                    "entity": name,
                    "entity_type": "compound",
                    "fields": {
                        "molecular_formula": item.get("MolecularFormula", ""),
                        "canonical_smiles": item.get("CanonicalSMILES", ""),
                        "inchikey": item.get("InChIKey", ""),
                        "iupac_name": item.get("IUPACName", ""),
                    },
                    "description": f"Compound metadata fetched from PubChem for {name}.",
                },
            }
        )
    return rows, warnings

