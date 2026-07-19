#!/usr/bin/env python3
"""Validate only Git metadata for raw data payloads; never read their contents."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path
from typing import Iterable


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_DATA_PATTERNS = (
    # Small normalized/fixture payloads retained for backwards compatibility.
    re.compile(r"data/[^/]+\.txt\Z"),
    # Curated public-source text used as review input. The guard deliberately
    # validates only Git metadata, never source content.
    re.compile(r"data/Data_DVC/[^/]+\.txt\Z"),
    # Public official-form templates used by the procedure workspace.  Their
    # content remains opaque to CI; only an explicit path and blob-size cap
    # are accepted here.
    re.compile(r"data/form/[^/]+\.(?:doc|docx)\Z"),
    # Family registry is metadata consumed by release tooling, not a raw
    # document payload.
    re.compile(r"data/registry/procedure-family-registry\.csv\Z"),
)
MAX_BLOB_BYTES = 2 * 1024 * 1024


def run_git(root: Path, arguments: list[str]) -> bytes:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if completed.returncode:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {' '.join(arguments)} failed")
    return completed.stdout


def parse_range(value: str) -> tuple[str, str]:
    parts = value.split("...")
    if len(parts) != 2 or not all(parts):
        raise ValueError("--range must use <base...head>")
    return parts[0], parts[1]


def changed_data_paths(root: Path, git_range: str) -> tuple[list[str], str]:
    base, head = parse_range(git_range)
    output = run_git(
        root,
        ["diff", "--name-only", "-z", "--diff-filter=ACMRT", "-M", f"{base}...{head}", "--", "data"],
    )
    return [os.fsdecode(value) for value in output.split(b"\0") if value], head


def data_blob_sizes(root: Path, revision: str) -> dict[str, int]:
    """Read the entire data tree metadata once without opening any payload blob."""
    output = run_git(root, ["ls-tree", "-rl", revision, "--", "data"])
    sizes: dict[str, int] = {}
    for line in output.splitlines():
        try:
            metadata, raw_path = line.split(b"\t", maxsplit=1)
            mode, object_type, _object_id, raw_size = metadata.split()
            if mode and object_type == b"blob":
                sizes[os.fsdecode(raw_path)] = int(raw_size)
        except (ValueError, UnicodeDecodeError):
            continue
    return sizes


def validate(root: Path, git_range: str) -> list[str]:
    paths, head = changed_data_paths(root, git_range)
    errors: list[str] = []
    sizes = data_blob_sizes(root, head) if paths else {}
    for path in paths:
        if not any(pattern.fullmatch(path) for pattern in ALLOWED_DATA_PATTERNS):
            errors.append(f"Unexpected data path: {path}")
            continue
        size = sizes.get(path)
        if size is None:
            errors.append(f"Unable to read data metadata for {path}.")
            continue
        if size > MAX_BLOB_BYTES:
            errors.append(f"Data blob exceeds {MAX_BLOB_BYTES} bytes: {path}")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--range", dest="git_range", required=True, metavar="BASE...HEAD")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        errors = validate(args.root, args.git_range)
    except (RuntimeError, ValueError) as error:
        print(f"Data metadata guard error: {error}")
        return 1
    if errors:
        print("Data metadata guard failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Data metadata guard passed (payload content was not read).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
