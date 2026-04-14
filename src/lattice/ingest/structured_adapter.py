from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lattice.models import Metadata, Record, build_metadata
from lattice.utils import stable_hash


def _scalar_fields(item: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for key, value in item.items():
        if isinstance(value, (str, int, float, bool)) and key not in {"entity", "name", "id"}:
            fields[key] = value
    return fields


def _build_structured_record(item: dict[str, Any], file_path: Path, domain: str, index: int) -> Record:
    entity = str(item.get("entity") or item.get("name") or item.get("id") or f"{file_path.stem}-{index}")
    metadata = build_metadata(
        source_path=file_path,
        source_type="structured",
        domain=domain,
        schema_type="StructuredRecord",
        source_suffix=f"-{index}",
    )
    record_id = f"struct-{stable_hash(metadata.source_id + entity)}"
    payload = {
        "entity": entity,
        "entity_type": item.get("entity_type", "material"),
        "fields": _scalar_fields(item),
        "description": item.get("description", ""),
    }
    return Record(
        record_id=record_id,
        schema_type="StructuredRecord",
        metadata=metadata,
        payload=payload,
    )


def _build_normalized_record(item: dict[str, Any], file_path: Path, domain: str, index: int) -> Record:
    schema_type = str(item["schema_type"])
    source_id = str(item.get("source_id") or f"{file_path.stem}-{index}")
    url_or_ref = str(item.get("url_or_ref") or file_path)
    source_type = str(item.get("source_type") or "external")
    timestamp = str(item.get("timestamp") or "")
    license_name = str(item.get("license") or "unknown")
    provenance_chain = list(item.get("provenance_chain") or [source_id])
    dedup_seed = f"{schema_type}:{source_id}:{url_or_ref}:{index}"
    metadata = Metadata(
        source_id=source_id,
        source_type=source_type,
        url_or_ref=url_or_ref,
        timestamp=timestamp,
        license=license_name,
        domain=str(item.get("domain") or domain),
        schema_type=schema_type,
        dedup_id=str(item.get("dedup_id") or stable_hash(dedup_seed)),
        provenance_chain=provenance_chain,
    )
    payload = dict(item.get("payload") or {})
    record_id = str(item.get("record_id") or f"{schema_type.lower()}-{stable_hash(metadata.source_id + metadata.dedup_id)}")
    quality = dict(item.get("quality") or {})
    return Record(
        record_id=record_id,
        schema_type=schema_type,
        metadata=metadata,
        payload=payload,
        quality=quality,
    )


def parse_structured_file(path: str | Path, domain: str) -> list[Record]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    items: list[dict[str, Any]] = []
    if suffix == ".jsonl":
        with file_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
    else:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = [payload]
    records: list[Record] = []
    for idx, item in enumerate(items, start=1):
        if "schema_type" in item and "payload" in item:
            records.append(_build_normalized_record(item, file_path, domain, idx))
        else:
            records.append(_build_structured_record(item, file_path, domain, idx))
    return records
