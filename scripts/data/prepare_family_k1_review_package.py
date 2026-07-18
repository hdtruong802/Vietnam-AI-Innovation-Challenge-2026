"""Prepare a K1 candidate package from Data_DVC plus external dataset_raw."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.data.k1_review_package import (  # noqa: E402
    K1PackageError,
    require_artifacts_output,
    write_json,
)
from scripts.data.procedure_family_registry import (  # noqa: E402
    build_family_candidate_rows,
    render_family_review_checklist,
    write_family_manifest,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--data-dvc-dir", type=Path, default=None)
    parser.add_argument(
        "--dataset-raw-dir",
        type=Path,
        default=None,
        help="Ignored dataset_raw path; may be outside this task worktree.",
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    arguments = parser.parse_args(argv)

    repository_root = arguments.repository_root.resolve()
    registry_path = (
        arguments.registry
        or repository_root / "data" / "registry" / "procedure-family-registry.csv"
    )
    data_dvc_dir = arguments.data_dvc_dir or repository_root / "data" / "Data_DVC"
    dataset_raw_dir = arguments.dataset_raw_dir or repository_root / "dataset_raw"
    output_dir_value = (
        arguments.output_dir or repository_root / "artifacts" / "family-k1-review"
    )

    try:
        output_dir = require_artifacts_output(output_dir_value, repository_root)
        rows, report = build_family_candidate_rows(
            registry_path.resolve(),
            data_dvc_dir.resolve(),
            dataset_raw_dir.resolve(),
        )
    except (K1PackageError, OSError, UnicodeError, ValueError) as error:
        if isinstance(error, K1PackageError):
            for issue in error.issues:
                location = "/".join(
                    value for value in (issue.procedure_id, issue.source_id) if value
                )
                print(
                    f"{issue.code}{f' [{location}]' if location else ''}: "
                    f"{issue.message}",
                    file=sys.stderr,
                )
        else:
            print(f"family_k1_prepare_failed: {error}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "candidate-family-sources.csv"
    report_path = output_dir / "family-provenance-report.json"
    checklist_path = output_dir / "family-review-checklist.md"
    write_family_manifest(rows, manifest_path)
    write_json(report, report_path)
    checklist_path.write_text(render_family_review_checklist(rows), encoding="utf-8")
    print(
        "Procedure-family K1 candidate package prepared: "
        f"sources={report['unique_source_count']} "
        f"relationships={report['relationship_count']} manifest={manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
