"""Build a clean RAG pack from an explicitly reviewed source manifest."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.rag.approved import (  # noqa: E402
    APPROVED_SOURCE_COLUMNS,
    build_approved_pack,
    write_jsonl,
)


def _require_artifacts_path(path: Path, parser: argparse.ArgumentParser) -> Path:
    resolved = path.resolve()
    artifacts = (REPOSITORY_ROOT / "artifacts").resolve()
    if artifacts not in resolved.parents:
        parser.error("outputs must be below ignored artifacts/")
    return resolved


def _write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=APPROVED_SOURCE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _write_flat_chunks(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            for chunk in record["chunks"]:
                handle.write(
                    json.dumps(chunk, ensure_ascii=False, sort_keys=True) + "\n"
                )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument(
        "--approved-manifest",
        type=Path,
        help="Manifest da duoc reviewer dien provenance va gan approved ro rang.",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=REPOSITORY_ROOT
        / "artifacts"
        / "chatbot"
        / "clean-approved-sources.csv",
    )
    parser.add_argument(
        "--grouped-output",
        type=Path,
        default=REPOSITORY_ROOT / "artifacts" / "chatbot" / "clean-rag-pack.jsonl",
    )
    parser.add_argument(
        "--chunks-output",
        type=Path,
        default=REPOSITORY_ROOT / "artifacts" / "chatbot" / "clean-rag-chunks.jsonl",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=REPOSITORY_ROOT / "artifacts" / "chatbot" / "clean-rag-report.json",
    )
    parser.add_argument("--as-of", default="2026-07-18")
    arguments = parser.parse_args(argv)

    if arguments.approved_manifest is None:
        print(
            "Clean RAG pack build blocked: --approved-manifest is required; "
            "candidate annotations are not K1 approval.",
            file=sys.stderr,
        )
        return 2

    repository_root = arguments.repository_root.resolve()
    manifest_output = _require_artifacts_path(arguments.manifest_output, parser)
    grouped_output = _require_artifacts_path(arguments.grouped_output, parser)
    chunks_output = _require_artifacts_path(arguments.chunks_output, parser)
    report_output = _require_artifacts_path(arguments.report_output, parser)

    try:
        with arguments.approved_manifest.resolve().open(
            encoding="utf-8", newline=""
        ) as handle:
            approved_rows = list(csv.DictReader(handle))
        records, report = build_approved_pack(
            arguments.approved_manifest.resolve(), repository_root, arguments.as_of
        )
        _write_manifest(approved_rows, manifest_output)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Demo clean RAG pack build failed: {error}", file=sys.stderr)
        return 1

    write_jsonl(records, grouped_output)
    _write_flat_chunks(records, chunks_output)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "Demo clean RAG pack built: "
        f"sources={report['selected']} chunks={report['chunk_count']} "
        f"approved={report['approved']} max_tokens={report['token_percentiles']['p100']} "
        f"chunks={chunks_output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
