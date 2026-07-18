"""Build a demo-ready clean RAG pack from K1-approved fixture rows.

This script is intentionally for local chatbot/demo use. It does not invent
official citations; it marks source_refs as local K1 fixture references.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.rag.approved import (  # noqa: E402
    APPROVED_SOURCE_COLUMNS,
    build_approved_pack,
    write_jsonl,
)
from scripts.data.prepare_approved_source_manifest import (  # noqa: E402
    DEFAULT_PHASE1_MANIFEST,
    build_template_rows,
)


PROCEDURE_TITLES = {
    "birth_registration": "Dang ky khai sinh",
    "residence_registration": "Dang ky thuong tru",
    "household_business_registration": "Dang ky thanh lap ho kinh doanh",
}


def _require_artifacts_path(path: Path, parser: argparse.ArgumentParser) -> Path:
    resolved = path.resolve()
    artifacts = (REPOSITORY_ROOT / "artifacts").resolve()
    if artifacts not in resolved.parents:
        parser.error("outputs must be below ignored artifacts/")
    return resolved


def _fill_demo_provenance(
    rows: list[dict[str, str]],
    reviewed_at: str,
) -> list[dict[str, str]]:
    filled: list[dict[str, str]] = []
    for row in rows:
        procedure_id = row["procedure_ids"]
        title = PROCEDURE_TITLES.get(procedure_id, procedure_id)
        updated = dict(row)
        updated.update(
            {
                "title": f"{title} - K1 local fixture {row['raw_document_id']}",
                "authority": "K1-reviewed local VAIC demo fixture",
                "jurisdiction": "VN",
                "source_ref": f"local-k1-fixture://{row['raw_document_id']}",
                "document_version": f"k1-local-{reviewed_at}",
                "effective_from": "2024-01-01",
                "effective_to": "",
                "permission_status": "official_public",
                "review_status": "approved",
            }
        )
        filled.append(updated)
    return filled


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
                handle.write(json.dumps(chunk, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase1-manifest", type=Path, default=DEFAULT_PHASE1_MANIFEST)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=REPOSITORY_ROOT / "artifacts" / "chatbot" / "clean-approved-sources.csv",
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
    parser.add_argument("--reviewed-by", default="K1")
    parser.add_argument("--reviewed-at", default="2026-07-18")
    parser.add_argument("--as-of", default="2026-07-18")
    arguments = parser.parse_args(argv)

    repository_root = arguments.repository_root.resolve()
    manifest_output = _require_artifacts_path(arguments.manifest_output, parser)
    grouped_output = _require_artifacts_path(arguments.grouped_output, parser)
    chunks_output = _require_artifacts_path(arguments.chunks_output, parser)
    report_output = _require_artifacts_path(arguments.report_output, parser)

    try:
        rows = build_template_rows(
            arguments.phase1_manifest.resolve(),
            repository_root,
            arguments.reviewed_by,
            arguments.reviewed_at,
        )
        filled_rows = _fill_demo_provenance(rows, arguments.reviewed_at)
        _write_manifest(filled_rows, manifest_output)
        with tempfile.TemporaryDirectory() as directory:
            temp_manifest = Path(directory) / "approved.csv"
            _write_manifest(filled_rows, temp_manifest)
            records, report = build_approved_pack(temp_manifest, repository_root, arguments.as_of)
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
