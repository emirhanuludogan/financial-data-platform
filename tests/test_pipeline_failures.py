"""Regression checks for failure propagation, paths and the Windows launcher.

External EVDS/Spark dependencies are mocked; no live data is requested.
"""
import importlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import venv


class PipelineFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        external = {
            name: MagicMock(name=name)
            for name in (
                "dotenv", "evds", "pyspark", "pyspark.sql",
                "pyspark.sql.functions", "pyspark.sql.window",
            )
        }
        cls.dependencies = patch.dict(sys.modules, external)
        cls.dependencies.start()
        cls.addClassCleanup(cls.dependencies.stop)
        cls.ingestion = importlib.import_module("src.ingestion.ingestion")
        cls.processing = importlib.import_module("src.processing")
        cls.features = importlib.import_module("src.features")
        cls.orchestrator = importlib.import_module("src.pipelines.main")

    def setUp(self):
        self.ingestion.SparkSession.reset_mock()
        self.ingestion.evdsAPI.reset_mock()

    def test_missing_api_key_stops_before_network_or_spark(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "EVDS_API_KEY"):
                self.ingestion.run_ingestion()
        self.ingestion.evdsAPI.assert_not_called()
        self.ingestion.SparkSession.builder.appName.assert_not_called()

    def test_empty_api_response_stops_before_spark(self):
        for response in (None, []):
            with self.subTest(response=response):
                self.ingestion.evdsAPI.return_value.get_data.return_value = response
                with patch.dict(os.environ, {"EVDS_API_KEY": "test-placeholder"}):
                    with self.assertRaisesRegex(RuntimeError, "bos veri"):
                        self.ingestion.run_ingestion()
        self.ingestion.SparkSession.builder.appName.assert_not_called()

    def test_missing_raw_uses_renamed_repository_path(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "renamed-project"
            with patch.object(self.processing, "__file__", str(root / "src/processing.py")):
                with self.assertRaises(FileNotFoundError) as error:
                    self.processing.run_processing()
            self.assertIn(str(root / "data/raw/usd_kur_raw.parquet"), str(error.exception))
        self.processing.SparkSession.builder.appName.assert_not_called()

    def test_missing_silver_uses_renamed_repository_path(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "renamed-project"
            with patch.object(self.features, "__file__", str(root / "src/features.py")):
                with self.assertRaises(FileNotFoundError) as error:
                    self.features.run_features()
            self.assertIn(str(root / "data/silver/usd_kur_cleaned.parquet"), str(error.exception))
        self.features.SparkSession.builder.appName.assert_not_called()

    def test_processing_reads_raw_inside_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "renamed-project"
            raw = root / "data/raw/usd_kur_raw.parquet"
            raw.mkdir(parents=True)
            with patch.object(self.processing, "__file__", str(root / "src/processing.py")):
                self.processing.run_processing()
            spark = self.processing.SparkSession.builder.appName.return_value.getOrCreate.return_value
            spark.read.parquet.assert_called_once_with(str(raw))

    def test_features_reads_silver_inside_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "renamed-project"
            silver = root / "data/silver/usd_kur_cleaned.parquet"
            silver.mkdir(parents=True)
            with patch.object(self.features, "__file__", str(root / "src/features.py")):
                self.features.run_features()
            spark = self.features.SparkSession.builder.appName.return_value.getOrCreate.return_value
            spark.read.parquet.assert_called_once_with(str(silver))

    def test_orchestrator_stops_after_ingestion_failure(self):
        with patch.object(self.orchestrator, "run_ingestion", side_effect=RuntimeError("failed")), \
             patch.object(self.orchestrator, "run_processing") as processing, \
             patch.object(self.orchestrator, "run_features") as features:
            with self.assertRaises(SystemExit) as error:
                self.orchestrator.main()
        self.assertEqual(error.exception.code, 1)
        processing.assert_not_called()
        features.assert_not_called()


@unittest.skipUnless(os.name == "nt", "Windows batch launcher")
class WindowsLauncherTests(unittest.TestCase):
    def test_launcher_preserves_success_and_failure_exit_codes(self):
        launcher = Path(__file__).resolve().parents[1] / "run_pipeline.bat"
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "run_pipeline.bat").write_bytes(launcher.read_bytes())
            venv.EnvBuilder(with_pip=False).create(root / ".venv")
            package = root / "src/pipelines"
            package.mkdir(parents=True)
            (root / "src/__init__.py").touch()
            (package / "__init__.py").touch()
            for exit_code in (0, 7):
                with self.subTest(exit_code=exit_code):
                    (package / "main.py").write_text(
                        f"import sys\nsys.exit({exit_code})\n", encoding="utf-8"
                    )
                    result = subprocess.run(
                        ["cmd", "/d", "/c", "run_pipeline.bat"], cwd=root,
                        capture_output=True, timeout=30,
                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                    )
                    self.assertEqual(result.returncode, exit_code, result.stderr)
                    log = (root / "logs/automation.log").read_text()
                    if exit_code:
                        self.assertIn("basarisiz. Cikis kodu: 7", log)
                    else:
                        self.assertIn("Otomatik calistirma basarili.", log)


if __name__ == "__main__":
    unittest.main()
