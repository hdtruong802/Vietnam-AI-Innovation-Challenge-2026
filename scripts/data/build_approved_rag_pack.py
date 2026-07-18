"""Build approved RAG chunks from a K1-reviewed source manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.rag.approved import build_approved_pack, write_jsonl  # noqa: E402


def _require_artifacts_path(path: Path, parser: argparse.ArgumentParser) -> Path:
    resolved = path.resolve()
    artifacts = (REPOSITORY_ROOT / "artifacts").resolve()
    if artifacts not in resolved.parents:
        parser.error("--output and --report-output must be below ignored artifacts/")
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-manifest", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    parser.add_argument("--as-of", default="2026-07-18")
    arguments = parser.parse_args(argv)

    output = _require_artifacts_path(arguments.output, parser)
    report_output = _require_artifacts_path(arguments.report_output, parser)
    try:
        records, report = build_approved_pack(
            arguments.approved_manifest.resolve(),
            arguments.repository_root.resolve(),
            arguments.as_of,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Approved RAG pack build failed: {error}", file=sys.stderr)
        return 1

    write_jsonl(records, output)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "Approved RAG pack build valid: "
        f"sources={report['selected']} chunks={report['chunk_count']} "
        f"approved={report['approved']} max_tokens={report['token_percentiles']['p100']} "
        f"output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
