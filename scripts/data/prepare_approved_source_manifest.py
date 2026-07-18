"""Create a candidate source manifest for explicit K1 review.

Parser-boundary annotations are not legal/content approval. The generated rows
therefore remain ``needs_review`` until a reviewer fills provenance and changes
the status in a separate reviewed manifest.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.rag.approved import APPROVED_SOURCE_COLUMNS  # noqa: E402
from backend.app.rag.normalization import decode_utf8, normalize_document  # noqa: E402

DEFAULT_PHASE1_MANIFEST = (
    REPOSITORY_ROOT / "tests" / "rag" / "fixtures" / "chunking_phase1_manifest.csv"
)


def _require_artifacts_path(
    path: Path, repository_root: Path, parser: argparse.ArgumentParser
) -> Path:
    resolved = path.resolve()
    artifacts = (repository_root / "artifacts").resolve()
    if artifacts not in resolved.parents:
        parser.error("--output must be below ignored artifacts/")
    return resolved


def build_template_rows(
    phase1_manifest: Path,
    repository_root: Path,
) -> list[dict[str, str]]:
    with phase1_manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    output: list[dict[str, str]] = []
    for row in rows:
        if row["annotation_status"] != "approved":
            continue
        raw_path = repository_root / row["raw_path"]
        payload = raw_path.read_bytes()
        document = normalize_document(decode_utf8(payload))
        output.append(
            {
                "source_id": row["raw_document_id"],
                "raw_document_id": row["raw_document_id"],
                "raw_path": row["raw_path"],
                "procedure_ids": row["procedure_id"],
                "title": "",
                "authority": "",
                "jurisdiction": "",
                "source_ref": "",
                "document_version": "",
                "document_type": "official_guidance",
                "effective_from": "",
                "effective_to": "",
                "last_verified_at": "",
                "permission_status": "",
                "review_status": "needs_review",
                "reviewed_by": "",
                "reviewed_at": "",
                "raw_sha256": hashlib.sha256(payload).hexdigest(),
                "normalized_sha256": hashlib.sha256(
                    document.text.encode("utf-8")
                ).hexdigest(),
                "expected_sections": row["expected_sections"],
            }
        )
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase1-manifest", type=Path, default=DEFAULT_PHASE1_MANIFEST)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)

    repository_root = arguments.repository_root.resolve()
    output_path = _require_artifacts_path(arguments.output, repository_root, parser)
    try:
        rows = build_template_rows(
            arguments.phase1_manifest.resolve(),
            repository_root,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Approved source template failed: {error}", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=APPROVED_SOURCE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"Approved source manifest template written: rows={len(rows)} path={output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
