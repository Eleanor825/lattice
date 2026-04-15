from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from lattice.sources.registry import registry_source_map
from lattice.utils import read_json, write_json


EMPTY_LIKE_VALUES = {"", "unknown", "n/a", "na", "none", "null", "-"}
OPEN_LICENSE_TOKENS = ("cc", "open", "public domain", "cc0", "cc by")


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _license_is_known(value: str) -> bool:
    return value.strip().lower() not in {"", "unknown"}


def _license_is_open_like(value: str) -> bool:
    text = value.strip().lower()
    return any(token in text for token in OPEN_LICENSE_TOKENS)


def _mean_or_zero(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(float(mean(values)), 4)


def _record_applications(schema_type: str) -> list[str]:
    if schema_type == "Document":
        return ["pretrain", "qa", "instruction", "knowledge"]
    if schema_type in {"StructuredRecord", "KnowledgeRecord"}:
        return ["qa", "instruction", "knowledge"]
    if schema_type == "InstructionTrace":
        return ["instruction", "posttrain"]
    return []


def _fetch_status(count: int, warnings: list[str], payload: dict[str, Any]) -> str:
    if count > 0:
        return "fetched"
    if warnings:
        warning_blob = " ".join(warnings).lower()
        if "auth" in warning_blob or "api key" in warning_blob:
            return "auth_required"
        return "warning"
    if payload.get("auth_env"):
        return "auth_required"
    return "empty"


def _quality_summary(records: list[dict[str, Any]], registry: dict[str, dict[str, Any]]) -> dict[str, Any]:
    word_counts: list[float] = []
    unique_ratios: list[float] = []
    alpha_ratios: list[float] = []
    license_counts: Counter[str] = Counter()
    source_type_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    access_mode_counts: Counter[str] = Counter()
    schema_counts: Counter[str] = Counter()
    application_counts: Counter[str] = Counter()

    provenance_complete = 0
    known_license = 0
    open_like_license = 0

    structured_field_total = 0
    structured_field_missing = 0

    for row in records:
        schema_type = str(row.get("schema_type", ""))
        schema_counts[schema_type] += 1
        metadata = dict(row.get("metadata", {}))
        quality = dict(row.get("quality", {}))
        payload = dict(row.get("payload", {}))

        source_type = str(metadata.get("source_type", "unknown"))
        source_type_counts[source_type] += 1
        registry_payload = registry.get(source_type, {})
        category_counts[str(registry_payload.get("category", "unclassified"))] += 1
        access_mode_counts[str(registry_payload.get("access_mode", "unknown"))] += 1

        license_name = str(metadata.get("license", "unknown"))
        license_counts[license_name] += 1
        if _license_is_known(license_name):
            known_license += 1
        if _license_is_open_like(license_name):
            open_like_license += 1

        if metadata.get("provenance_chain") and metadata.get("url_or_ref"):
            provenance_complete += 1

        if "word_count" in quality:
            word_counts.append(float(quality["word_count"]))
        if "unique_ratio" in quality:
            unique_ratios.append(float(quality["unique_ratio"]))
        if "alpha_ratio" in quality:
            alpha_ratios.append(float(quality["alpha_ratio"]))

        for application in _record_applications(schema_type):
            application_counts[application] += 1

        if schema_type == "StructuredRecord":
            fields = dict(payload.get("fields", {}))
            for value in fields.values():
                structured_field_total += 1
                if str(value).strip().lower() in EMPTY_LIKE_VALUES:
                    structured_field_missing += 1

    total_records = len(records)
    return {
        "record_count": total_records,
        "schema_counts": dict(schema_counts),
        "source_type_counts": dict(source_type_counts),
        "source_category_counts": dict(category_counts),
        "source_access_mode_counts": dict(access_mode_counts),
        "license_counts": dict(license_counts),
        "application_support_counts": dict(application_counts),
        "avg_word_count": _mean_or_zero(word_counts),
        "avg_unique_ratio": _mean_or_zero(unique_ratios),
        "avg_alpha_ratio": _mean_or_zero(alpha_ratios),
        "total_word_count": int(sum(word_counts)),
        "provenance_completeness_ratio": round(provenance_complete / max(total_records, 1), 4),
        "known_license_ratio": round(known_license / max(total_records, 1), 4),
        "open_license_like_ratio": round(open_like_license / max(total_records, 1), 4),
        "structured_field_total": structured_field_total,
        "structured_field_missing": structured_field_missing,
        "structured_field_missing_ratio": round(structured_field_missing / max(structured_field_total, 1), 4),
    }


def _quality_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 1 Quality Report",
        "",
        f"- Release: {report['release_name']}",
        f"- Domain: {report['domain']}",
        f"- Selected sources: {report['source_inventory']['selected_source_count']}",
        f"- Successful sources: {report['source_inventory']['successful_source_count']}",
        f"- Raw fetched records: {report['scale']['raw_fetched_records']}",
        f"- Normalized kept records: {report['scale']['normalized_records']}",
        "",
        "## Data Types",
    ]
    for key, value in report["quality"]["schema_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Quality Metrics",
            f"- Avg word count: {report['quality']['avg_word_count']}",
            f"- Avg unique ratio: {report['quality']['avg_unique_ratio']}",
            f"- Avg alpha ratio: {report['quality']['avg_alpha_ratio']}",
            f"- Known license ratio: {report['quality']['known_license_ratio']}",
            f"- Open-license-like ratio: {report['quality']['open_license_like_ratio']}",
            f"- Provenance completeness ratio: {report['quality']['provenance_completeness_ratio']}",
            f"- Structured field missing ratio: {report['quality']['structured_field_missing_ratio']}",
            "",
            "## Application Views",
        ]
    )
    for key, value in report["scale"]["view_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Source Coverage"])
    for item in report["source_inventory"]["sources"]:
        lines.append(
            f"- {item['name']}: status={item['status']}, fetched={item['fetched_count']}, "
            f"kept={item['kept_record_count']}, category={item['category']}"
        )
    return "\n".join(lines) + "\n"


def build_phase1_quality_report(phase1_manifest_path: str | Path, registry_path: str | Path) -> dict[str, Any]:
    manifest_path = Path(phase1_manifest_path)
    manifest = read_json(manifest_path)
    registry = registry_source_map(registry_path)

    bronze_manifest = read_json(Path(manifest["paths"]["bronze"]) / "reports" / "manifest.json")
    gold_manifest = read_json(Path(manifest["paths"]["gold"]) / "reports" / "manifest.json")
    silver_manifest = read_json(Path(manifest["paths"]["silver"]) / "manifest.json")
    records = _read_jsonl(Path(manifest["paths"]["gold"]) / "normalized" / "records.jsonl")

    warnings_by_source: dict[str, list[str]] = defaultdict(list)
    for warning in manifest["fetch"]["warnings"]:
        prefix = str(warning).split(" ", 1)[0].strip(":")
        warnings_by_source[prefix].append(str(warning))

    source_inventory_rows: list[dict[str, Any]] = []
    successful_source_count = 0
    for source_name in manifest["sources"]:
        registry_payload = registry.get(source_name, {})
        fetched_count = int(manifest["fetch"]["counts"].get(source_name, 0))
        kept_record_count = int(gold_manifest["source_counts"].get(source_name, 0))
        source_warnings = warnings_by_source.get(source_name, [])
        status = _fetch_status(fetched_count, source_warnings, registry_payload)
        if fetched_count > 0:
            successful_source_count += 1
        source_inventory_rows.append(
            {
                "name": source_name,
                "status": status,
                "fetched_count": fetched_count,
                "kept_record_count": kept_record_count,
                "category": str(registry_payload.get("category", "unknown")),
                "priority": str(registry_payload.get("priority", "")),
                "access_mode": str(registry_payload.get("access_mode", "")),
                "schema_targets": list(registry_payload.get("schema_targets", [])),
                "license_status": str(registry_payload.get("license_status", "unknown")),
                "recommended_storage_tier": str(registry_payload.get("recommended_storage_tier", "")),
                "warnings": source_warnings,
            }
        )

    report = {
        "release_name": manifest["release_name"],
        "domain": manifest["domain"],
        "phase1_manifest_path": str(manifest_path.resolve()),
        "source_inventory": {
            "selected_source_count": len(manifest["sources"]),
            "successful_source_count": successful_source_count,
            "source_status_counts": dict(Counter(item["status"] for item in source_inventory_rows)),
            "source_category_counts": dict(Counter(item["category"] for item in source_inventory_rows)),
            "sources": source_inventory_rows,
        },
        "scale": {
            "raw_fetched_records": int(sum(manifest["fetch"]["counts"].values())),
            "normalized_records": int(gold_manifest["kept_record_count"]),
            "document_link_clusters": int(silver_manifest.get("document_clusters", 0)),
            "entity_link_clusters": int(silver_manifest.get("entity_clusters", 0)),
            "view_counts": dict(gold_manifest["view_counts"]),
        },
        "quality": _quality_summary(records, registry),
        "drops": dict(bronze_manifest["dropped_records"]),
        "warnings": list(manifest["fetch"]["warnings"]),
    }

    reports_dir = manifest_path.parent
    quality_report_path = reports_dir / "quality_report.json"
    source_inventory_path = reports_dir / "source_inventory.json"
    quality_markdown_path = reports_dir / "quality_report.md"

    write_json(quality_report_path, report)
    write_json(source_inventory_path, report["source_inventory"])
    quality_markdown_path.write_text(_quality_markdown(report), encoding="utf-8")

    return {
        "report": report,
        "quality_report_path": str(quality_report_path.resolve()),
        "source_inventory_path": str(source_inventory_path.resolve()),
        "quality_markdown_path": str(quality_markdown_path.resolve()),
    }
