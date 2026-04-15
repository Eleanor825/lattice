from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from typing import Any
import urllib.request

from lattice.sources.common import timestamp_now
from lattice.training.datasets import load_texts_for_workflow
from lattice.training import TrainingConfig, run_training_workflow
from lattice.utils import ensure_dir, write_json


@dataclass(slots=True)
class ModelBackendConfig:
    backend: str
    model_name: str
    provider: str = "local"
    model_family: str = "open"
    api_base: str = ""
    api_key_env: str = ""


def run_backend_workflow(
    *,
    workflow: str,
    dataset_dir: str,
    output_dir: str,
    run_name: str,
    checkpoint_dir: str,
    backend_config: ModelBackendConfig,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    max_length: int,
    hidden_size: int,
) -> dict[str, Any]:
    if backend_config.backend == "local_tiny":
        result = run_training_workflow(
            TrainingConfig(
                workflow=workflow,
                input_dir=dataset_dir,
                output_dir=output_dir,
                run_name=run_name,
                checkpoint_dir=checkpoint_dir,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate,
                max_length=max_length,
                hidden_size=hidden_size,
            )
        )
        return {
            "mode": "local_train",
            "backend": asdict(backend_config),
            "result": asdict(result),
        }

    if backend_config.backend == "hf_causal_lm":
        from lattice.training.hf_backend import run_hf_causal_lm_workflow

        texts = load_texts_for_workflow(workflow, dataset_dir)
        result = run_hf_causal_lm_workflow(
            workflow=workflow,
            texts=texts,
            output_dir=output_dir,
            run_name=run_name,
            model_name=backend_config.model_name,
            checkpoint_dir=checkpoint_dir,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            max_length=max_length,
            hidden_size=hidden_size,
        )
        return {
            "mode": "hf_train",
            "backend": asdict(backend_config),
            "result": asdict(result),
        }

    if backend_config.backend == "external_connector":
        api_key = os.environ.get(backend_config.api_key_env, "") if backend_config.api_key_env else ""
        if backend_config.api_base and api_key:
            ensure_dir(output_dir)
            payload = {
                "workflow": workflow,
                "run_name": run_name,
                "model": backend_config.model_name,
                "model_family": backend_config.model_family,
                "dataset_dir": str(Path(dataset_dir).resolve()),
                "checkpoint_dir": str(Path(checkpoint_dir).resolve()) if checkpoint_dir else "",
            }
            request = urllib.request.Request(
                backend_config.api_base.rstrip("/") + "/training/jobs",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                response_payload = json.load(response)
            write_json(Path(output_dir) / "provider_response.json", response_payload)
            return {
                "mode": "provider_job",
                "backend": asdict(backend_config),
                "response": response_payload,
            }

    ensure_dir(output_dir)
    connector_manifest = {
        "generated_at": timestamp_now(),
        "mode": "connector_request",
        "workflow": workflow,
        "run_name": run_name,
        "dataset_dir": str(Path(dataset_dir).resolve()),
        "checkpoint_dir": str(Path(checkpoint_dir).resolve()) if checkpoint_dir else "",
        "backend": asdict(backend_config),
        "status": "prepared",
        "note": (
            "This run is prepared for an external model provider. "
            "Closed models are supported through a unified connector manifest rather than local weight training."
        ),
    }
    write_json(Path(output_dir) / "connector_manifest.json", connector_manifest)
    return connector_manifest
