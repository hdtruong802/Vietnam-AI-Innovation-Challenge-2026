from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "validate_data.py"
SPEC = importlib.util.spec_from_file_location("validate_data", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load data guard module.")
data_guard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = data_guard
SPEC.loader.exec_module(data_guard)


class DataMetadataGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.git("init")
        self.git("config", "user.email", "data@example.test")
        self.git("config", "user.name", "Data Guard Test")
        self.write("README.md", "base\n")
        self.git("add", ".")
        self.git("commit", "-m", "base")
        self.base = self.git("rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def git(self, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=self.root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return completed.stdout.strip()

    def write(self, relative_path: str, content: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit_change(self, relative_path: str, content: str) -> str:
        self.write(relative_path, content)
        self.git("add", relative_path)
        self.git("commit", "-m", "data change")
        return self.git("rev-parse", "HEAD")

    def test_accepts_numbered_text_payload_without_reading_it(self) -> None:
        head = self.commit_change("data/1.000005.txt", "payload that is intentionally not inspected\n")

        self.assertEqual([], data_guard.validate(self.root, f"{self.base}...{head}"))

    def test_rejects_unexpected_path_and_oversize_blob(self) -> None:
        invalid_head = self.commit_change("data/raw.json", "{}\n")
        errors = data_guard.validate(self.root, f"{self.base}...{invalid_head}")
        self.assertIn("Unexpected data path: data/raw.json", errors)

        self.git("reset", "--hard", self.base)
        large_head = self.commit_change("data/1.000006.txt", "x" * (data_guard.MAX_BLOB_BYTES + 1))
        errors = data_guard.validate(self.root, f"{self.base}...{large_head}")
        self.assertIn("Data blob exceeds", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
