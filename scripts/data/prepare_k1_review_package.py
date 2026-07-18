"""Prepare a fail-closed K1 candidate package for the three canonical sources."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.data.k1_review_package import (  # noqa: E402
    K1PackageError,
    build_candidate_rows,
    render_review_checklist,
    require_artifacts_output,
    write_json,
    write_manifest,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
    )
    arguments = parser.parse_args(argv)

    repository_root = arguments.repository_root.resolve()
    source_dir = arguments.source_dir or repository_root / "data" / "Data_DVC"
    output_dir_value = (
        arguments.output_dir or repository_root / "artifacts" / "k1-review"
    )
    try:
        output_dir = require_artifacts_output(output_dir_value, repository_root)
        rows, report = build_candidate_rows(repository_root, source_dir)
    except (K1PackageError, OSError, UnicodeError, ValueError) as error:
        if isinstance(error, K1PackageError):
            for issue in error.issues:
                print(f"{issue.code}: {issue.message}", file=sys.stderr)
        else:
            print(f"k1_prepare_failed: {error}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "candidate-sources.csv"
    report_path = output_dir / "provenance-report.json"
    checklist_path = output_dir / "review-checklist.md"
    write_manifest(rows, manifest_path)
    write_json(report, report_path)
    checklist_path.write_text(render_review_checklist(rows), encoding="utf-8")
    print(
        "K1 candidate package prepared: "
        f"sources={len(rows)} manifest={manifest_path} report={report_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
