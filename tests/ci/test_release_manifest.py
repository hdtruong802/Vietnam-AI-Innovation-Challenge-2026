from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "release_manifest.py"
SPEC = importlib.util.spec_from_file_location("release_manifest", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load release manifest module.")
release_manifest = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = release_manifest
SPEC.loader.exec_module(release_manifest)


class ReleaseManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.git("init")
        self.git("config", "user.email", "release@example.test")
        self.git("config", "user.name", "Release Manifest Test")
        (self.root / "source.txt").write_text("source\n", encoding="utf-8")
        self.git("add", "source.txt")
        self.git("commit", "-m", "source")

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

    def test_manifest_verifies_only_for_matching_tree_and_artifacts(self) -> None:
        artifact_directory = self.root / "artifacts"
        artifact_directory.mkdir()
        frontend = artifact_directory / "frontend.tar.gz"
        backend = artifact_directory / "backend.tar.gz"
        frontend.write_bytes(b"frontend")
        backend.write_bytes(b"backend")
        manifest = release_manifest.build_manifest(self.root, frontend, backend, "123")
        manifest_path = artifact_directory / "release-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        self.assertEqual(
            [],
            release_manifest.verify_manifest(
                manifest_path, artifact_directory, self.git("rev-parse", "HEAD^{tree}")
            ),
        )

        frontend.write_bytes(b"tampered")
        errors = release_manifest.verify_manifest(
            manifest_path, artifact_directory, self.git("rev-parse", "HEAD^{tree}")
        )
        self.assertIn("Checksum mismatch for frontend artifact.", errors)


if __name__ == "__main__":
    unittest.main()
