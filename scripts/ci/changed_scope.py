#!/usr/bin/env python3
"""Classify a Git diff so CI can run only the relevant jobs."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Iterable


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
ALL_SCOPES = ("frontend", "backend", "data", "design", "ai_log", "guard")


def run_git(root: Path, arguments: list[str]) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {' '.join(arguments)} failed")
    return completed.stdout


def parse_range(value: str) -> tuple[str, str]:
    parts = value.split("...")
    if len(parts) != 2 or not all(parts) or any(part.startswith("-") for part in parts):
        raise ValueError("--range must use <base...head>")
    return parts[0], parts[1]


def changed_paths(root: Path, git_range: str) -> list[str]:
    base, head = parse_range(git_range)
    output = run_git(
        root,
        ["diff", "--name-only", "-z", "--diff-filter=ACMRT", "-M", f"{base}...{head}"],
    )
    return [os.fsdecode(path) for path in output.split(b"\0") if path]


def classify_path(path: str) -> set[str]:
    scopes: set[str] = set()
    if path.startswith("frontend/") or path in {".env.example"}:
        scopes.add("frontend")
    if path.startswith("backend/") or path in {"requirements.txt", ".env.example"}:
        scopes.add("backend")
    if path.startswith("data/"):
        scopes.add("data")
    if path.startswith(("docs/design/", ".impeccable/", "scripts/design/", "tests/design/")):
        scopes.add("design")
    if path.startswith(("evidence/ai-log/", "scripts/ai_log/", ".githooks/")):
        scopes.add("ai_log")
    if path.startswith(("scripts/ci/", "tests/ci/", ".github/workflows/", ".github/repository-settings.json")):
        scopes.add("guard")
    return scopes


def classify(paths: Iterable[str]) -> dict[str, bool]:
    result = {scope: False for scope in ALL_SCOPES}
    for path in paths:
        for scope in classify_path(path):
            result[scope] = True
    return result


def write_github_output(path: Path, values: dict[str, bool]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as output:
        for name, value in values.items():
            output.write(f"{name}={'true' if value else 'false'}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--range", dest="git_range", required=True, metavar="BASE...HEAD")
    parser.add_argument("--github-output", type=Path, help="append booleans to a GitHub Actions output file")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        paths = changed_paths(args.root, args.git_range)
        result = classify(paths)
    except (RuntimeError, ValueError) as error:
        print(f"Changed-scope error: {error}")
        return 1

    if args.github_output:
        write_github_output(args.github_output, result)
    print(json.dumps({"changed_paths": len(paths), "scopes": result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
