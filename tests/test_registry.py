from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RegistryTest(unittest.TestCase):
    def _env(self) -> dict[str, str]:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        java_home = Path("/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home")
        if java_home.exists():
            env["JAVA_HOME"] = str(java_home)
            env["PATH"] = f"{java_home / 'bin'}:{env.get('PATH', '')}"
        return env

    def test_phase1_and_phase2_registry_sync(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lattice-registry-") as tmp:
            db_path = Path(tmp) / "registry.db"
            phase1_root = Path(tmp) / "phase1"
            phase2_root = Path(tmp) / "phase2"
            data_dir = ROOT / "examples" / "training" / "demo_dataset"

            phase1_cmd = [
                sys.executable, "-m", "lattice", "phase1-run",
                "--data-root", str(phase1_root),
                "--registry", str(ROOT / "configs" / "source_registry.json"),
                "--domain", "materials",
                "--release-name", "registry-phase1",
                "--source", "openalex",
                "--source", "pubchem",
                "--query", "solid state battery electrolyte",
                "--compound", "lithium iron phosphate",
                "--limit", "1",
                "--registry-db", str(db_path),
            ]
            subprocess.run(phase1_cmd, check=True, capture_output=True, text=True, env=self._env())

            phase2_cmd = [
                sys.executable, "-m", "lattice", "phase2-run",
                "--workflow", "finetune",
                "--engine", "pandas",
                "--input", str(data_dir),
                "--output", str(phase2_root),
                "--run-name", "registry-phase2",
                "--model-backend", "local_tiny",
                "--model-name", "tiny-local",
                "--compiled-input",
                "--registry-db", str(db_path),
            ]
            subprocess.run(phase2_cmd, check=True, capture_output=True, text=True, env=self._env())

            conn = sqlite3.connect(db_path)
            try:
                runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
                datasets = conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
                backends = conn.execute("SELECT COUNT(*) FROM backends").fetchone()[0]
                self.assertGreaterEqual(runs, 2)
                self.assertGreaterEqual(datasets, 2)
                self.assertGreaterEqual(backends, 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
