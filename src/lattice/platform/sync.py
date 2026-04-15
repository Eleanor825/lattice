from __future__ import annotations

from pathlib import Path
from typing import Any

from lattice.platform.registry import PlatformRegistry
from lattice.utils import read_json, stable_hash


def sync_phase1_manifest(db_path: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    payload = read_json(manifest_path)
    registry = PlatformRegistry(db_path)
    try:
        for section in ("bronze", "gold"):
            section_payload = payload[section]
            dataset_id = stable_hash(f"{section}:{section_payload['dataset_name']}:{section_payload['output_dir']}")
            registry.register_dataset(
                dataset_id=dataset_id,
                phase="phase1",
                dataset_name=section_payload["dataset_name"],
                domain=section_payload["domain"],
                manifest_path=str(Path(section_payload["output_dir"]) / "reports" / "manifest.json"),
                output_dir=section_payload["output_dir"],
                generated_at=payload["generated_at"],
                payload=section_payload,
            )

        run_id = stable_hash(f"phase1:{payload['release_name']}:{payload['paths']['root']}")
        registry.register_run(
            run_id=run_id,
            phase="phase1",
            workflow="phase1-release",
            engine="multi",
            model_backend="none",
            model_family="none",
            status="completed",
            domain=payload["domain"],
            run_name=payload["release_name"],
            input_dir=payload["paths"]["raw"],
            output_dir=payload["paths"]["gold"],
            generated_at=payload["generated_at"],
            payload=payload,
        )
        return {"status": "ok", "run_id": run_id}
    finally:
        registry.close()


def sync_phase2_manifest(db_path: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    payload = read_json(manifest_path)
    backend = payload["backend_result"]["backend"]
    registry = PlatformRegistry(db_path)
    try:
        backend_id = stable_hash(f"{backend['backend']}:{backend['provider']}:{backend['model_name']}")
        registry.register_backend(backend_id=backend_id, payload=backend)
        run_id = stable_hash(f"phase2:{payload['run_name']}:{payload['workflow']}:{payload['output_dir']}")
        registry.register_run(
            run_id=run_id,
            phase="phase2",
            workflow=payload["workflow"],
            engine=payload["engine"],
            model_backend=backend["backend"],
            model_family=backend["model_family"],
            status="completed",
            domain=payload["config"]["domain"],
            run_name=payload["run_name"],
            input_dir=payload["input_dir"],
            output_dir=payload["output_dir"],
            generated_at=payload["generated_at"],
            payload=payload,
        )
        return {"status": "ok", "run_id": run_id, "backend_id": backend_id}
    finally:
        registry.close()
