"""Build the ignored synthetic-approved 25-source family release for local demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.data.demo_family_release import (  # noqa: E402
    build_demo_family_release,
    write_demo_family_release,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--data-dvc-dir", type=Path)
    parser.add_argument(
        "--dataset-raw-dir",
        type=Path,
        required=True,
        help="Path to ignored dataset_raw; files are read in place and never copied.",
    )
    parser.add_argument("--manifest-output", type=Path)
    parser.add_argument("--grouped-output", type=Path)
    parser.add_argument("--chunks-output", type=Path)
    parser.add_argument("--report-output", type=Path)
    arguments = parser.parse_args(argv)

    repository_root = arguments.repository_root.resolve()
    registry = arguments.registry or (
        repository_root / "data" / "registry" / "procedure-family-registry.csv"
    )
    data_dvc_dir = arguments.data_dvc_dir or repository_root / "data" / "Data_DVC"
    manifest_output = arguments.manifest_output or (
        repository_root
        / "artifacts"
        / "demo-family-release"
        / "reviewed-family-sources.csv"
    )
    grouped_output = arguments.grouped_output or (
        repository_root / "artifacts" / "chatbot" / "clean-rag-pack.jsonl"
    )
    chunks_output = arguments.chunks_output or (
        repository_root / "artifacts" / "chatbot" / "clean-rag-chunks.jsonl"
    )
    report_output = arguments.report_output or (
        repository_root / "artifacts" / "chatbot" / "clean-rag-report.json"
    )

    try:
        approved_rows, records, report = build_demo_family_release(
            registry,
            data_dvc_dir,
            arguments.dataset_raw_dir,
        )
        write_demo_family_release(
            approved_rows,
            records,
            report,
            manifest_output,
            grouped_output,
            chunks_output,
            report_output,
            repository_root,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Demo family release failed: {error}", file=sys.stderr)
        return 1

    print(
        "Synthetic-approved demo family release built: "
        f"sources={report['unique_source_count']} "
        f"relationships={report['relationship_count']} "
        f"chunks={report['chunk_count']} "
        f"approval_mode={report['approval_mode']} "
        f"output={chunks_output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
