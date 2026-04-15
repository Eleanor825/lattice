from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
import unittest

from lattice.reports import build_phase1_quality_report
from lattice.utils import read_json, write_json


ROOT = Path(__file__).resolve().parents[1]


class Phase1QualityReportTest(unittest.TestCase):
    def test_build_phase1_quality_report_from_existing_release(self) -> None:
        source_root = ROOT / "phase1-data"
        source_manifest = source_root / "manifests" / "release=lattice-materials-demo" / "phase1_manifest.json"

        with tempfile.TemporaryDirectory(prefix="lattice-phase1-report-") as tmp:
            tmp_root = Path(tmp) / "phase1-data"
            shutil.copytree(source_root, tmp_root)

            manifest = read_json(source_manifest)
            manifest["data_root"] = str(tmp_root.resolve())
            manifest["paths"] = {
                "root": str(tmp_root.resolve()),
                "raw": str((tmp_root / "raw" / "api" / "date=2026-04-15" / "run=lattice-materials-demo").resolve()),
                "bronze": str((tmp_root / "bronze" / "release=lattice-materials-demo").resolve()),
                "silver": str((tmp_root / "silver" / "release=lattice-materials-demo").resolve()),
                "gold": str((tmp_root / "gold" / "release=lattice-materials-demo").resolve()),
                "manifests": str((tmp_root / "manifests" / "release=lattice-materials-demo").resolve()),
            }

            manifest_path = tmp_root / "manifests" / "release=lattice-materials-demo" / "phase1_manifest.json"
            write_json(manifest_path, manifest)

            payload = build_phase1_quality_report(manifest_path, ROOT / "configs" / "source_registry.json")
            report = payload["report"]

            self.assertEqual(report["release_name"], "lattice-materials-demo")
            self.assertEqual(report["scale"]["normalized_records"], 2)
            self.assertEqual(report["quality"]["schema_counts"]["StructuredRecord"], 2)
            self.assertEqual(report["source_inventory"]["selected_source_count"], 3)
            self.assertTrue(Path(payload["quality_report_path"]).exists())
            self.assertTrue(Path(payload["source_inventory_path"]).exists())
            self.assertTrue(Path(payload["quality_markdown_path"]).exists())


if __name__ == "__main__":
    unittest.main()
