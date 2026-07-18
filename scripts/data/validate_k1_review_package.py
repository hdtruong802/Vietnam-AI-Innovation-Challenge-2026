"""Validate a human-completed K1 manifest without changing source status."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.data.k1_review_package import (  # noqa: E402
    K1PackageError,
    load_manifest,
    require_artifacts_output,
    validate_reviewed_rows,
    write_json,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument(
        "--report-output",
        type=Path,
        default=None,
    )
    arguments = parser.parse_args(argv)

    repository_root = arguments.repository_root.resolve()
    report_output_value = (
        arguments.report_output
        or repository_root / "artifacts" / "k1-review" / "release-ready-report.json"
    )
    try:
        report_output = require_artifacts_output(report_output_value, repository_root)
        rows = load_manifest(arguments.manifest.resolve())
        report = validate_reviewed_rows(rows, repository_root, arguments.as_of)
    except (K1PackageError, OSError, UnicodeError, ValueError) as error:
        if isinstance(error, K1PackageError):
            for issue in error.issues:
                location = "/".join(
                    value for value in (issue.procedure_id, issue.source_id) if value
                )
                print(
                    f"{issue.code}{f' [{location}]' if location else ''}: {issue.message}",
                    file=sys.stderr,
                )
        else:
            print(f"k1_validation_failed: {error}", file=sys.stderr)
        return 1

    write_json(report, report_output)
    print(
        "K1 manifest is release-ready: "
        f"sources={report['source_count']} report={report_output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
