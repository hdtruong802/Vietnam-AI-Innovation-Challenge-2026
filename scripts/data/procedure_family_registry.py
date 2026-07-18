"""Versioned procedure-family registry and dual-source K1 candidate builder."""

from __future__ import annotations

import csv
import hashlib
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.normalization import decode_utf8, normalize_document  # noqa: E402
from app.services.rag.source_store import (  # noqa: E402
    SourceRecord,
    normalize_name,
    parse_source_file,
)
from scripts.data.k1_review_package import K1Issue, K1PackageError  # noqa: E402

REGISTRY_VERSION = "vaic-procedure-family-registry-v1"
FAMILY_MANIFEST_VERSION = "vaic-family-k1-review-v1"
REGISTRY_COLUMNS = (
    "registry_version",
    "family_id",
    "anchor_code",
    "procedure_code",
    "procedure_name",
    "relation_type",
    "release_tier",
    "source_collection",
)
FAMILY_MANIFEST_COLUMNS = (
    "manifest_version",
    "registry_version",
    "source_id",
    "source_collection",
    "raw_path",
    "procedure_name",
    "decision_no",
    "level",
    "field_area",
    "authority",
    "family_ids",
    "family_relations",
    "release_tiers",
    "raw_sha256",
    "normalized_sha256",
    "source_url",
    "document_version",
    "effective_from",
    "effective_to",
    "last_verified_at",
    "permission_status",
    "review_status",
    "reviewed_by",
    "reviewed_at",
    "review_notes",
)

EXPECTED_ANCHORS = {
    "dang-ky-khai-sinh": "1.001193",
    "dang-ky-thuong-tru": "1.004222",
    "dang-ky-ho-kinh-doanh": "1.001612",
}
EXPECTED_PROCEDURE_CODES = {
    "1.000110",
    "1.000689",
    "1.000893",
    "1.001020",
    "1.001193",
    "1.001612",
    "1.001695",
    "1.003197",
    "1.003583",
    "1.004222",
    "1.004772",
    "1.004884",
    "1.010040",
    "1.013314",
    "1.014034",
    "1.014035",
    "2.000522",
    "2.000528",
    "2.000547",
    "2.000575",
    "2.000635",
    "2.000712",
    "2.000720",
    "2.000986",
    "2.001023",
}
ALLOWED_RELATION_TYPES = {
    "anchor",
    "direct_variant",
    "bundled_workflow",
    "supporting_prerequisite",
    "post_registration",
    "lifecycle_operation",
    "adjacent_broad",
}
ALLOWED_RELEASE_TIERS = {"anchor", "tier_1", "tier_2", "deferred"}
ALLOWED_SOURCE_COLLECTIONS = {"Data_DVC", "dataset_raw"}


@dataclass(frozen=True)
class FamilyRelationship:
    family_id: str
    anchor_code: str
    relation_type: str
    release_tier: str


@dataclass(frozen=True)
class FamilySource:
    procedure_code: str
    procedure_name: str
    source_collection: str
    relationships: tuple[FamilyRelationship, ...]


def _issue(
    code: str,
    message: str,
    procedure_code: str | None = None,
    family_id: str | None = None,
) -> K1Issue:
    return K1Issue(
        code=code,
        message=message,
        procedure_id=family_id,
        source_id=procedure_code,
    )


def load_family_registry(path: Path) -> dict[str, FamilySource]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = tuple(reader.fieldnames or ())
    if columns != REGISTRY_COLUMNS:
        raise K1PackageError(
            [
                _issue(
                    "registry_columns_invalid", "Registry columns do not match schema."
                )
            ]
        )

    issues: list[K1Issue] = []
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_relationships: set[tuple[str, str]] = set()
    anchor_rows: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        procedure_code = row["procedure_code"].strip()
        family_id = row["family_id"].strip()
        if row["registry_version"] != REGISTRY_VERSION:
            issues.append(
                _issue(
                    "registry_version_invalid",
                    "Registry version is not supported.",
                    procedure_code,
                    family_id,
                )
            )
        if family_id not in EXPECTED_ANCHORS:
            issues.append(
                _issue(
                    "family_out_of_scope",
                    "Family is outside the current three-family scope.",
                    procedure_code,
                    family_id,
                )
            )
        elif row["anchor_code"] != EXPECTED_ANCHORS[family_id]:
            issues.append(
                _issue(
                    "anchor_code_mismatch",
                    "Family anchor differs from the accepted anchor registry.",
                    procedure_code,
                    family_id,
                )
            )
        if not procedure_code or not row["procedure_name"].strip():
            issues.append(
                _issue(
                    "procedure_identity_required",
                    "Procedure code and name are required.",
                    procedure_code or None,
                    family_id or None,
                )
            )
        if row["relation_type"] not in ALLOWED_RELATION_TYPES:
            issues.append(
                _issue(
                    "relation_type_invalid",
                    "Relation type is not supported.",
                    procedure_code,
                    family_id,
                )
            )
        if row["release_tier"] not in ALLOWED_RELEASE_TIERS:
            issues.append(
                _issue(
                    "release_tier_invalid",
                    "Release tier is not supported.",
                    procedure_code,
                    family_id,
                )
            )
        if row["source_collection"] not in ALLOWED_SOURCE_COLLECTIONS:
            issues.append(
                _issue(
                    "source_collection_invalid",
                    "Source collection is not supported.",
                    procedure_code,
                    family_id,
                )
            )
        relationship_key = (family_id, procedure_code)
        if relationship_key in seen_relationships:
            issues.append(
                _issue(
                    "family_relationship_duplicate",
                    "Family/source relationship appears more than once.",
                    procedure_code,
                    family_id,
                )
            )
        seen_relationships.add(relationship_key)
        grouped[procedure_code].append(row)
        if row["relation_type"] == "anchor":
            anchor_rows[family_id].append(row)

    actual_codes = set(grouped)
    if actual_codes != EXPECTED_PROCEDURE_CODES:
        missing = sorted(EXPECTED_PROCEDURE_CODES - actual_codes)
        extra = sorted(actual_codes - EXPECTED_PROCEDURE_CODES)
        issues.append(
            _issue(
                "registry_code_set_mismatch",
                f"Registry code set mismatch; missing={missing} extra={extra}.",
            )
        )

    for family_id, anchor_code in EXPECTED_ANCHORS.items():
        family_anchor_rows = anchor_rows.get(family_id, [])
        if len(family_anchor_rows) != 1:
            issues.append(
                _issue(
                    "family_anchor_count_invalid",
                    "Family must contain exactly one anchor relationship.",
                    anchor_code,
                    family_id,
                )
            )
        elif family_anchor_rows[0]["procedure_code"] != anchor_code:
            issues.append(
                _issue(
                    "family_anchor_procedure_mismatch",
                    "Anchor relationship must point to the accepted anchor code.",
                    family_anchor_rows[0]["procedure_code"],
                    family_id,
                )
            )

    sources: dict[str, FamilySource] = {}
    for procedure_code, source_rows in grouped.items():
        names = {row["procedure_name"] for row in source_rows}
        collections = {row["source_collection"] for row in source_rows}
        if len(names) != 1:
            issues.append(
                _issue(
                    "shared_source_name_conflict",
                    "Shared source has conflicting names across families.",
                    procedure_code,
                )
            )
        if len(collections) != 1:
            issues.append(
                _issue(
                    "shared_source_collection_conflict",
                    "Shared source has conflicting source collections.",
                    procedure_code,
                )
            )
        relationships = tuple(
            sorted(
                (
                    FamilyRelationship(
                        family_id=row["family_id"],
                        anchor_code=row["anchor_code"],
                        relation_type=row["relation_type"],
                        release_tier=row["release_tier"],
                    )
                    for row in source_rows
                ),
                key=lambda item: item.family_id,
            )
        )
        sources[procedure_code] = FamilySource(
            procedure_code=procedure_code,
            procedure_name=next(iter(names), ""),
            source_collection=next(iter(collections), ""),
            relationships=relationships,
        )

    if issues:
        raise K1PackageError(issues)
    return sources


def _checksums(path: Path) -> tuple[str, str]:
    payload = path.read_bytes()
    document = normalize_document(decode_utf8(payload))
    return (
        hashlib.sha256(payload).hexdigest(),
        hashlib.sha256(document.text.encode("utf-8")).hexdigest(),
    )


def _authority(record: SourceRecord) -> str:
    for value in (record.authority_org, record.implementing_org):
        if value and normalize_name(value) != "khong co thong tin":
            return value
    return ""


def build_family_candidate_rows(
    registry_path: Path,
    data_dvc_dir: Path,
    dataset_raw_dir: Path,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    sources = load_family_registry(registry_path)
    source_dirs = {
        "Data_DVC": data_dvc_dir.resolve(),
        "dataset_raw": dataset_raw_dir.resolve(),
    }
    issues: list[K1Issue] = []
    rows: list[dict[str, str]] = []
    report_sources: list[dict[str, object]] = []

    for procedure_code, source in sorted(sources.items()):
        source_dir = source_dirs[source.source_collection]
        path = source_dir / f"{procedure_code}.txt"
        if not path.is_file():
            issues.append(
                _issue(
                    "family_source_missing",
                    "Registry source file is missing from its configured collection.",
                    procedure_code,
                )
            )
            continue
        record = parse_source_file(path)
        if record is None:
            issues.append(
                _issue(
                    "family_source_unreadable",
                    "Source is not strict UTF-8 or cannot be parsed.",
                    procedure_code,
                )
            )
            continue
        if record.procedure_code != procedure_code:
            issues.append(
                _issue(
                    "family_source_code_mismatch",
                    "Parsed procedure code differs from registry.",
                    procedure_code,
                )
            )
        if normalize_name(record.name) != normalize_name(source.procedure_name):
            issues.append(
                _issue(
                    "family_source_name_mismatch",
                    "Parsed procedure name differs from registry.",
                    procedure_code,
                )
            )
        try:
            raw_sha256, normalized_sha256 = _checksums(path)
        except (OSError, UnicodeError, ValueError):
            issues.append(
                _issue(
                    "family_source_normalization_failed",
                    "Source failed strict normalization/checksum.",
                    procedure_code,
                )
            )
            continue

        family_ids = [item.family_id for item in source.relationships]
        family_relations = [
            f"{item.family_id}:{item.relation_type}" for item in source.relationships
        ]
        release_tiers = [
            f"{item.family_id}:{item.release_tier}" for item in source.relationships
        ]
        logical_raw_path = (
            f"data/Data_DVC/{procedure_code}.txt"
            if source.source_collection == "Data_DVC"
            else f"dataset_raw/{procedure_code}.txt"
        )
        row = {column: "" for column in FAMILY_MANIFEST_COLUMNS}
        row.update(
            {
                "manifest_version": FAMILY_MANIFEST_VERSION,
                "registry_version": REGISTRY_VERSION,
                "source_id": procedure_code,
                "source_collection": source.source_collection,
                "raw_path": logical_raw_path,
                "procedure_name": record.name,
                "decision_no": record.decision_no,
                "level": record.level,
                "field_area": record.field_area,
                "authority": _authority(record),
                "family_ids": "|".join(family_ids),
                "family_relations": "|".join(family_relations),
                "release_tiers": "|".join(release_tiers),
                "raw_sha256": raw_sha256,
                "normalized_sha256": normalized_sha256,
                "review_status": "needs_review",
            }
        )
        rows.append(row)
        report_sources.append(
            {
                "source_id": procedure_code,
                "source_collection": source.source_collection,
                "raw_path": logical_raw_path,
                "family_ids": family_ids,
                "family_relations": family_relations,
                "release_tiers": release_tiers,
                "raw_sha256": raw_sha256,
                "normalized_sha256": normalized_sha256,
                "review_status": "needs_review",
            }
        )

    if issues:
        raise K1PackageError(issues)

    family_summary: dict[str, dict[str, object]] = {}
    for family_id, anchor_code in EXPECTED_ANCHORS.items():
        family_sources = [
            source for source in report_sources if family_id in source["family_ids"]
        ]
        family_summary[family_id] = {
            "anchor_code": anchor_code,
            "relationship_count": len(family_sources),
            "source_ids": [source["source_id"] for source in family_sources],
        }

    snapshot_payload = "|".join(
        f"{row['source_id']}:{row['raw_sha256']}:{row['family_relations']}"
        for row in rows
    )
    report: dict[str, object] = {
        "manifest_version": FAMILY_MANIFEST_VERSION,
        "registry_version": REGISTRY_VERSION,
        "status": "review_ready",
        "unique_source_count": len(rows),
        "relationship_count": sum(
            len(source.relationships) for source in sources.values()
        ),
        "source_snapshot_id": hashlib.sha256(
            snapshot_payload.encode("utf-8")
        ).hexdigest(),
        "issues": [],
        "families": family_summary,
        "sources": report_sources,
    }
    return rows, report


def write_family_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=FAMILY_MANIFEST_COLUMNS, extrasaction="raise"
        )
        writer.writeheader()
        writer.writerows(rows)


def render_family_review_checklist(rows: list[dict[str, str]]) -> str:
    family_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        for family_id in row["family_ids"].split("|"):
            family_groups[family_id].append(row)

    sections: list[str] = []
    for family_id in sorted(family_groups):
        source_lines = "\n".join(
            f"- [ ] `{row['source_id']}` - {row['procedure_name']} "
            f"(`{row['family_relations']}`)"
            for row in family_groups[family_id]
        )
        sections.append(f"## {family_id}\n\n{source_lines}")

    return """# Procedure Family K1 Review Checklist

> Candidate metadata only. No row in this package is K1-approved.

Review every source independently. A shared bundled workflow such as
`2.000986` has one checksum/source row but relationships to multiple families.
Do not copy its checklist into either anchor procedure.

{sections}

## Required Review

- [ ] Confirm exact code, title, authority, jurisdiction and current effective version.
- [ ] Confirm the assigned relation type and release tier for every family.
- [ ] Review checklist, conditions, fees, timing, steps and legal bases per source.
- [ ] Record official HTTPS URL, permission status, reviewer, date and review notes.
- [ ] Keep conflicts, broad adjacent sources and unresolved variants at `needs_review`.

This package must not be connected to runtime guidance until a separate reviewed
manifest validator and approved release task are completed.
""".format(sections="\n\n".join(sections))
