from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import threading
import unittest


ROOT = Path(__file__).resolve().parents[1]


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        payload = json.loads(body)
        response = {
            "job_id": "mock-job-001",
            "status": "submitted",
            "workflow": payload.get("workflow"),
            "model": payload.get("model"),
        }
        data = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):  # noqa: A003
        return


class Phase2ProviderTest(unittest.TestCase):
    def _parse_last_json(self, text: str) -> dict:
        start = text.rfind("\n{")
        if start == -1:
            start = text.find("{")
        if start == -1:
            raise ValueError("No JSON payload found in stdout")
        return json.loads(text[start:].strip())

    def _env(self) -> dict[str, str]:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        return env

    def test_phase2_hf_backend(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lattice-phase2-hf-") as tmp:
            cmd = [
                sys.executable, "-m", "lattice", "phase2-run",
                "--workflow", "finetune",
                "--engine", "pandas",
                "--input", str(ROOT / "examples" / "training" / "demo_dataset"),
                "--output", str(Path(tmp) / "run"),
                "--run-name", "hf-demo",
                "--model-backend", "hf_causal_lm",
                "--model-name", "hf-gpt2-tiny-local",
                "--compiled-input",
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=self._env())
            payload = self._parse_last_json(result.stdout)
            self.assertEqual(payload["backend_result"]["mode"], "hf_train")

    def test_phase2_provider_job_backend(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lattice-phase2-provider-") as tmp:
            server = HTTPServer(("127.0.0.1", 0), _Handler)
            host, port = server.server_address
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                env = self._env()
                env["LATTICE_TEST_API_KEY"] = "test-key"
                cmd = [
                    sys.executable, "-m", "lattice", "phase2-run",
                    "--workflow", "posttrain",
                    "--engine", "pandas",
                    "--input", str(ROOT / "examples" / "training" / "demo_dataset"),
                    "--output", str(Path(tmp) / "run"),
                    "--run-name", "provider-demo",
                    "--model-backend", "external_connector",
                    "--model-name", "closed-provider-model",
                    "--provider", "openai_compatible",
                    "--model-family", "closed",
                    "--api-base", f"http://{host}:{port}",
                    "--api-key-env", "LATTICE_TEST_API_KEY",
                    "--compiled-input",
                ]
                result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
                payload = self._parse_last_json(result.stdout)
                self.assertEqual(payload["backend_result"]["mode"], "provider_job")
                self.assertEqual(payload["backend_result"]["response"]["status"], "submitted")
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
