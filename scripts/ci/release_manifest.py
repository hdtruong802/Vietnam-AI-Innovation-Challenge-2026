#!/usr/bin/env python3
"""Create and verify provider-neutral release artifact manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(root: Path, revision: str) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", revision],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        return None
    return completed.stdout.decode("ascii").strip()


def build_manifest(root: Path, frontend: Path, backend: Path, run_id: str) -> dict[str, object]:
    if not frontend.is_file() or not backend.is_file():
        raise ValueError("Both frontend and backend archives must exist.")
    commit = git_value(root, "HEAD")
    tree = git_value(root, "HEAD^{tree}")
    if not commit or not tree:
        raise ValueError("Unable to resolve the current Git commit and tree.")
    return {
        "schema_version": 1,
        "source_commit": commit,
        "source_tree": tree,
        "ci_run_id": str(run_id),
        "frontend": {"file": frontend.name, "sha256": sha256(frontend)},
        "backend": {"file": backend.name, "sha256": sha256(backend)},
        "data_tree": git_value(root, "HEAD:data"),
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def verify_manifest(manifest_path: Path, artifact_directory: Path, expected_tree: str) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [f"Invalid release manifest: {error}"]
    if manifest.get("schema_version") != 1:
        errors.append("Unsupported release manifest schema_version.")
    if manifest.get("source_tree") != expected_tree:
        errors.append("Release artifact source_tree does not match the selected main tree.")
    for artifact_name in ("frontend", "backend"):
        artifact = manifest.get(artifact_name)
        if not isinstance(artifact, dict):
            errors.append(f"Manifest is missing {artifact_name} artifact metadata.")
            continue
        name = artifact.get("file")
        checksum = artifact.get("sha256")
        if not isinstance(name, str) or Path(name).name != name:
            errors.append(f"Invalid {artifact_name} artifact filename.")
            continue
        if not isinstance(checksum, str) or len(checksum) != 64:
            errors.append(f"Invalid {artifact_name} artifact checksum.")
            continue
        artifact_path = artifact_directory / name
        if not artifact_path.is_file() or sha256(artifact_path) != checksum:
            errors.append(f"Checksum mismatch for {artifact_name} artifact.")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    create = subcommands.add_parser("create")
    create.add_argument("--root", type=Path, default=DEFAULT_ROOT, help=argparse.SUPPRESS)
    create.add_argument("--frontend", type=Path, required=True)
    create.add_argument("--backend", type=Path, required=True)
    create.add_argument("--run-id", required=True)
    create.add_argument("--output", type=Path, required=True)

    verify = subcommands.add_parser("verify")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--artifacts", type=Path, required=True)
    verify.add_argument("--expected-tree", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    if args.command == "create":
        try:
            manifest = build_manifest(args.root, args.frontend, args.backend, args.run_id)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except (OSError, ValueError) as error:
            print(f"Release manifest creation failed: {error}")
            return 1
        return 0

    errors = verify_manifest(args.manifest, args.artifacts, args.expected_tree)
    if errors:
        print("Release manifest verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Release manifest verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
