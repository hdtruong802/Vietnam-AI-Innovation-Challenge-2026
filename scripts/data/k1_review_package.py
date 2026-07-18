"""Deterministic helpers for a human-reviewed K1 source package."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.normalization import decode_utf8, normalize_document  # noqa: E402
from app.services.rag.source_store import (  # noqa: E402
    PROCEDURE_ALLOWLIST,
    PROCEDURE_SOURCE_CODES,
    SourceRecord,
    normalize_name,
    parse_source_file,
)

MANIFEST_VERSION = "vaic-k1-review-v1"
K1_REVIEW_COLUMNS = (
    "manifest_version",
    "procedure_id",
    "source_id",
    "raw_path",
    "procedure_code",
    "procedure_name",
    "decision_no",
    "level",
    "field_area",
    "authority",
    "jurisdiction",
    "source_url",
    "document_version",
    "effective_from",
    "effective_to",
    "last_verified_at",
    "permission_status",
    "raw_sha256",
    "normalized_sha256",
    "review_status",
    "reviewed_by",
    "reviewed_at",
    "review_notes",
)
ALLOWED_PERMISSION_STATUSES = {"official_public", "permission_recorded"}


@dataclass(frozen=True)
class K1Issue:
    code: str
    message: str
    procedure_id: str | None = None
    source_id: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {"code": self.code, "message": self.message}
        if self.procedure_id:
            payload["procedure_id"] = self.procedure_id
        if self.source_id:
            payload["source_id"] = self.source_id
        return payload


class K1PackageError(ValueError):
    def __init__(self, issues: Iterable[K1Issue]):
        self.issues = tuple(issues)
        super().__init__("; ".join(issue.code for issue in self.issues))


def _single_expected_value(values: Iterable[str], label: str) -> str:
    unique = tuple(values)
    if len(unique) != 1:
        raise RuntimeError(f"canonical {label} must contain exactly one value")
    return unique[0]


def canonical_sources() -> dict[str, dict[str, str]]:
    return {
        procedure_id: {
            "procedure_code": _single_expected_value(
                PROCEDURE_SOURCE_CODES[procedure_id], "source code"
            ),
            "procedure_name": _single_expected_value(names, "procedure name"),
        }
        for procedure_id, names in PROCEDURE_ALLOWLIST.items()
    }


def require_within(path: Path, parent: Path, label: str) -> Path:
    resolved = path.resolve()
    parent_resolved = parent.resolve()
    if resolved != parent_resolved and parent_resolved not in resolved.parents:
        raise ValueError(f"{label} must stay under {parent_resolved}")
    return resolved


def require_artifacts_output(path: Path, repository_root: Path) -> Path:
    artifacts_root = (repository_root / "artifacts").resolve()
    resolved = path.resolve()
    if artifacts_root not in resolved.parents:
        raise ValueError("output must stay below ignored artifacts/")
    return resolved


def _record_authority(record: SourceRecord) -> str:
    for value in (record.authority_org, record.implementing_org):
        if value and normalize_name(value) != "khong co thong tin":
            return value
    return ""


def _checksums(path: Path) -> tuple[str, str]:
    payload = path.read_bytes()
    document = normalize_document(decode_utf8(payload))
    return (
        hashlib.sha256(payload).hexdigest(),
        hashlib.sha256(document.text.encode("utf-8")).hexdigest(),
    )


def discover_canonical_records(
    source_dir: Path,
) -> dict[str, tuple[Path, SourceRecord]]:
    source_dir = source_dir.resolve()
    expected = canonical_sources()
    code_to_procedure = {
        metadata["procedure_code"]: procedure_id
        for procedure_id, metadata in expected.items()
    }
    matches: dict[str, list[tuple[Path, SourceRecord]]] = {
        procedure_id: [] for procedure_id in expected
    }
    issues: list[K1Issue] = []

    if not source_dir.is_dir():
        raise K1PackageError(
            [K1Issue("source_dir_missing", "Source directory is missing.")]
        )

    for path in sorted(source_dir.glob("*.txt")):
        record = parse_source_file(path)
        if record is None:
            if path.stem in code_to_procedure:
                issues.append(
                    K1Issue(
                        "canonical_source_unreadable",
                        "Canonical source is not valid strict UTF-8 or cannot be parsed.",
                        code_to_procedure[path.stem],
                        path.stem,
                    )
                )
            continue
        procedure_id = code_to_procedure.get(record.procedure_code)
        if procedure_id is None:
            continue
        expected_name = expected[procedure_id]["procedure_name"]
        if normalize_name(record.name) != normalize_name(expected_name):
            issues.append(
                K1Issue(
                    "canonical_name_mismatch",
                    "Procedure name does not match the canonical registry.",
                    procedure_id,
                    record.procedure_code,
                )
            )
            continue
        matches[procedure_id].append((path, record))

    selected: dict[str, tuple[Path, SourceRecord]] = {}
    for procedure_id, procedure_matches in matches.items():
        if not procedure_matches:
            issues.append(
                K1Issue(
                    "canonical_source_missing",
                    "Exactly one canonical source is required.",
                    procedure_id,
                )
            )
        elif len(procedure_matches) > 1:
            issues.append(
                K1Issue(
                    "canonical_source_duplicate",
                    "More than one source has the canonical code and name.",
                    procedure_id,
                )
            )
        else:
            selected[procedure_id] = procedure_matches[0]

    if issues:
        raise K1PackageError(issues)
    return selected


def build_candidate_rows(
    repository_root: Path, source_dir: Path
) -> tuple[list[dict[str, str]], dict[str, object]]:
    repository_root = repository_root.resolve()
    source_dir = require_within(source_dir, repository_root, "source_dir")
    selected = discover_canonical_records(source_dir)
    rows: list[dict[str, str]] = []
    report_sources: list[dict[str, str]] = []

    for procedure_id in sorted(selected):
        path, record = selected[procedure_id]
        raw_sha256, normalized_sha256 = _checksums(path)
        raw_path = path.resolve().relative_to(repository_root).as_posix()
        row = {column: "" for column in K1_REVIEW_COLUMNS}
        row.update(
            {
                "manifest_version": MANIFEST_VERSION,
                "procedure_id": procedure_id,
                "source_id": record.procedure_code,
                "raw_path": raw_path,
                "procedure_code": record.procedure_code,
                "procedure_name": record.name,
                "decision_no": record.decision_no,
                "level": record.level,
                "field_area": record.field_area,
                "authority": _record_authority(record),
                "raw_sha256": raw_sha256,
                "normalized_sha256": normalized_sha256,
                "review_status": "needs_review",
            }
        )
        rows.append(row)
        report_sources.append(
            {
                "procedure_id": procedure_id,
                "source_id": record.procedure_code,
                "raw_path": raw_path,
                "decision_no": record.decision_no,
                "raw_sha256": raw_sha256,
                "normalized_sha256": normalized_sha256,
                "review_status": "needs_review",
            }
        )

    snapshot_payload = "|".join(
        f"{row['source_id']}:{row['raw_sha256']}:{row['normalized_sha256']}"
        for row in rows
    )
    report: dict[str, object] = {
        "manifest_version": MANIFEST_VERSION,
        "status": "review_ready",
        "candidate_count": len(rows),
        "source_snapshot_id": hashlib.sha256(
            snapshot_payload.encode("utf-8")
        ).hexdigest(),
        "issues": [],
        "sources": report_sources,
    }
    return rows, report


def write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=K1_REVIEW_COLUMNS, extrasaction="raise"
        )
        writer.writeheader()
        writer.writerows(rows)


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = tuple(reader.fieldnames or ())
    if columns != K1_REVIEW_COLUMNS:
        raise K1PackageError(
            [
                K1Issue(
                    "manifest_columns_invalid",
                    "Manifest columns do not match K1 schema.",
                )
            ]
        )
    return rows


def render_review_checklist(rows: list[dict[str, str]]) -> str:
    source_lines = "\n".join(
        f"- [ ] `{row['procedure_id']}` / `{row['source_id']}` / `{row['raw_path']}`"
        for row in rows
    )
    return f"""# K1 Human Review Checklist

> Candidate package only. This file is not evidence that K1 approval occurred.

## Sources

{source_lines}

## Review Each Source

- [ ] Confirm procedure code, name, scope and jurisdiction match the intended MVP procedure.
- [ ] Confirm authority, decision/version, effective dates and current validity using an official source.
- [ ] Confirm checklist, steps, conditions, fees, processing time and legal bases against that source.
- [ ] Record an exact HTTPS official URL and permission/reuse status.
- [ ] Record reviewer identity, review date and substantive review notes.
- [ ] Resolve conflicts or leave `review_status=needs_review`; never approve by inference.

## Manifest Fields To Complete

`authority`, `jurisdiction`, `source_url`, `document_version`, `effective_from`,
optional `effective_to`, `last_verified_at`, `permission_status`, `reviewed_by`,
`reviewed_at`, `review_notes`, then explicitly set `review_status=approved`.

## Validate After Human Review

```powershell
python scripts/data/validate_k1_review_package.py `
  --manifest artifacts/k1-review/reviewed-sources.csv `
  --report-output artifacts/k1-review/release-ready-report.json
```

Validation proves manifest integrity and completeness only. It does not replace
the human/legal review recorded in the manifest.
"""


def write_json(payload: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _parse_date(
    value: str, field: str, row: dict[str, str], issues: list[K1Issue]
) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        issues.append(
            K1Issue(
                f"{field}_invalid",
                f"{field} must use ISO YYYY-MM-DD.",
                row.get("procedure_id") or None,
                row.get("source_id") or None,
            )
        )
        return None


def _official_https_url(value: str) -> bool:
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (
        hostname.endswith(".gov.vn") or hostname == "dichvucong.gov.vn"
    )


def validate_reviewed_rows(
    rows: list[dict[str, str]], repository_root: Path, as_of: date
) -> dict[str, object]:
    repository_root = repository_root.resolve()
    source_root = (repository_root / "data" / "Data_DVC").resolve()
    expected = canonical_sources()
    issues: list[K1Issue] = []
    seen_procedures: set[str] = set()
    seen_sources: set[str] = set()
    release_sources: list[dict[str, str]] = []

    if len(rows) != len(expected):
        issues.append(
            K1Issue("source_count_invalid", "Manifest must contain exactly 3 rows.")
        )

    for row in rows:
        procedure_id = row.get("procedure_id", "")
        source_id = row.get("source_id", "")
        metadata = expected.get(procedure_id)
        if metadata is None:
            issues.append(
                K1Issue(
                    "procedure_out_of_scope",
                    "Procedure is outside the canonical MVP set.",
                    procedure_id or None,
                    source_id or None,
                )
            )
            continue
        if procedure_id in seen_procedures:
            issues.append(
                K1Issue(
                    "procedure_duplicate",
                    "Procedure appears more than once.",
                    procedure_id,
                    source_id or None,
                )
            )
        if source_id in seen_sources:
            issues.append(
                K1Issue(
                    "source_duplicate",
                    "Source ID appears more than once.",
                    procedure_id,
                    source_id or None,
                )
            )
        seen_procedures.add(procedure_id)
        seen_sources.add(source_id)

        if row.get("manifest_version") != MANIFEST_VERSION:
            issues.append(
                K1Issue(
                    "manifest_version_invalid",
                    "Manifest version is not supported.",
                    procedure_id,
                    source_id,
                )
            )
        if (
            row.get("procedure_code") != metadata["procedure_code"]
            or source_id != metadata["procedure_code"]
        ):
            issues.append(
                K1Issue(
                    "procedure_code_mismatch",
                    "Source/procedure code is not canonical.",
                    procedure_id,
                    source_id,
                )
            )
        if normalize_name(row.get("procedure_name", "")) != normalize_name(
            metadata["procedure_name"]
        ):
            issues.append(
                K1Issue(
                    "procedure_name_mismatch",
                    "Procedure name is not canonical.",
                    procedure_id,
                    source_id,
                )
            )

        raw_path_value = row.get("raw_path", "")
        try:
            raw_path = require_within(
                repository_root / raw_path_value, source_root, "raw_path"
            )
        except ValueError:
            issues.append(
                K1Issue(
                    "raw_path_outside_source_root",
                    "Raw path must stay under data/Data_DVC.",
                    procedure_id,
                    source_id,
                )
            )
            raw_path = None
        if raw_path is not None:
            if not raw_path.is_file():
                issues.append(
                    K1Issue(
                        "raw_file_missing",
                        "Raw source file is missing.",
                        procedure_id,
                        source_id,
                    )
                )
            else:
                try:
                    raw_sha256, normalized_sha256 = _checksums(raw_path)
                    parsed_record = parse_source_file(raw_path)
                except (OSError, UnicodeError, ValueError):
                    raw_sha256 = normalized_sha256 = ""
                    parsed_record = None
                    issues.append(
                        K1Issue(
                            "raw_file_invalid",
                            "Raw source is not valid strict UTF-8.",
                            procedure_id,
                            source_id,
                        )
                    )
                if raw_sha256 and raw_sha256 != row.get("raw_sha256"):
                    issues.append(
                        K1Issue(
                            "raw_checksum_mismatch",
                            "Raw checksum changed after package preparation.",
                            procedure_id,
                            source_id,
                        )
                    )
                if normalized_sha256 and normalized_sha256 != row.get(
                    "normalized_sha256"
                ):
                    issues.append(
                        K1Issue(
                            "normalized_checksum_mismatch",
                            "Normalized checksum changed after package preparation.",
                            procedure_id,
                            source_id,
                        )
                    )
                if (
                    parsed_record is None
                    or parsed_record.procedure_code != metadata["procedure_code"]
                    or normalize_name(parsed_record.name)
                    != normalize_name(metadata["procedure_name"])
                ):
                    issues.append(
                        K1Issue(
                            "raw_procedure_mismatch",
                            "Raw source no longer matches canonical procedure.",
                            procedure_id,
                            source_id,
                        )
                    )
                elif row.get("decision_no") != parsed_record.decision_no:
                    issues.append(
                        K1Issue(
                            "decision_no_mismatch",
                            "Manifest decision number differs from raw source.",
                            procedure_id,
                            source_id,
                        )
                    )

        required_fields = (
            "authority",
            "jurisdiction",
            "source_url",
            "document_version",
            "effective_from",
            "last_verified_at",
            "permission_status",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
        )
        for field in required_fields:
            if not row.get(field, "").strip():
                issues.append(
                    K1Issue(
                        f"{field}_required",
                        f"{field} is required for approval.",
                        procedure_id,
                        source_id,
                    )
                )
        if row.get("review_status") != "approved":
            issues.append(
                K1Issue(
                    "review_status_not_approved",
                    "Human reviewer must explicitly set approved.",
                    procedure_id,
                    source_id,
                )
            )
        if (
            row.get("permission_status")
            and row["permission_status"] not in ALLOWED_PERMISSION_STATUSES
        ):
            issues.append(
                K1Issue(
                    "permission_status_invalid",
                    "Permission status is not release eligible.",
                    procedure_id,
                    source_id,
                )
            )
        if row.get("source_url") and not _official_https_url(row["source_url"]):
            issues.append(
                K1Issue(
                    "source_url_invalid",
                    "Source URL must be HTTPS on an official .gov.vn domain.",
                    procedure_id,
                    source_id,
                )
            )
        if (
            row.get("review_notes", "").strip()
            and len(row["review_notes"].strip()) < 20
        ):
            issues.append(
                K1Issue(
                    "review_notes_too_short",
                    "Review notes must record substantive checks.",
                    procedure_id,
                    source_id,
                )
            )

        effective_from = (
            _parse_date(row["effective_from"], "effective_from", row, issues)
            if row.get("effective_from")
            else None
        )
        effective_to = (
            _parse_date(row["effective_to"], "effective_to", row, issues)
            if row.get("effective_to")
            else None
        )
        last_verified = (
            _parse_date(row["last_verified_at"], "last_verified_at", row, issues)
            if row.get("last_verified_at")
            else None
        )
        reviewed_at = (
            _parse_date(row["reviewed_at"], "reviewed_at", row, issues)
            if row.get("reviewed_at")
            else None
        )
        if effective_from and effective_from > as_of:
            issues.append(
                K1Issue(
                    "effective_from_future",
                    "Source is not effective as of validation date.",
                    procedure_id,
                    source_id,
                )
            )
        if effective_to and effective_to < as_of:
            issues.append(
                K1Issue(
                    "effective_to_stale",
                    "Source is stale as of validation date.",
                    procedure_id,
                    source_id,
                )
            )
        if last_verified and last_verified > as_of:
            issues.append(
                K1Issue(
                    "last_verified_future",
                    "Verification date cannot be in the future.",
                    procedure_id,
                    source_id,
                )
            )
        if reviewed_at and reviewed_at > as_of:
            issues.append(
                K1Issue(
                    "reviewed_at_future",
                    "Review date cannot be in the future.",
                    procedure_id,
                    source_id,
                )
            )

        release_sources.append(
            {
                "procedure_id": procedure_id,
                "source_id": source_id,
                "raw_sha256": row.get("raw_sha256", ""),
                "normalized_sha256": row.get("normalized_sha256", ""),
                "source_url": row.get("source_url", ""),
                "document_version": row.get("document_version", ""),
                "last_verified_at": row.get("last_verified_at", ""),
                "reviewed_by": row.get("reviewed_by", ""),
                "reviewed_at": row.get("reviewed_at", ""),
            }
        )

    for procedure_id in expected:
        if procedure_id not in seen_procedures:
            issues.append(
                K1Issue(
                    "canonical_procedure_missing",
                    "Canonical procedure is missing.",
                    procedure_id,
                )
            )

    if issues:
        raise K1PackageError(issues)

    snapshot_payload = "|".join(
        f"{source['source_id']}:{source['raw_sha256']}:{source['reviewed_at']}"
        for source in sorted(release_sources, key=lambda item: item["procedure_id"])
    )
    return {
        "manifest_version": MANIFEST_VERSION,
        "status": "release_ready",
        "validated_as_of": as_of.isoformat(),
        "source_count": len(release_sources),
        "source_snapshot_id": hashlib.sha256(
            snapshot_payload.encode("utf-8")
        ).hexdigest(),
        "issues": [],
        "sources": sorted(release_sources, key=lambda item: item["procedure_id"]),
    }
