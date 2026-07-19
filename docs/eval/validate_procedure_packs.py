#!/usr/bin/env python3
"""Validate the three MVP procedure-pack candidates or release artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "approved-source-registry.json"
PACK_DIR = ROOT / "procedure-packs"
EXPECTED = {
    "dang-ky-khai-sinh": ("1.001193", "dang-ky-khai-sinh.json"),
    "dang-ky-thuong-tru": ("1.004222", "dang-ky-thuong-tru.json"),
    "dang-ky-ho-kinh-doanh": ("1.001612", "dang-ky-ho-kinh-doanh.json"),
}
RULE_TYPES = {"required", "type", "string_pattern", "date_format", "date_not_future", "conditional_required", "field_compare"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
LOCAL_SOURCE_SCHEMES = ("local-k1-fixture://", "file://")


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.code}: {self.path}: {self.message}"


def load(path: Path, issues: list[Issue]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        issues.append(Issue("invalid_json", str(path), str(error)))
        return None
    if not isinstance(value, dict):
        issues.append(Issue("invalid_root", str(path), "JSON object required"))
        return None
    return value


def required(value: Any, path: str, issues: list[Issue], code: str = "required") -> None:
    if not isinstance(value, str) or not value.strip():
        issues.append(Issue(code, path, "non-empty string required"))


def iso_date(value: Any) -> bool:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return True


def parsed_date(value: Any) -> date | None:
    if not iso_date(value):
        return None
    return date.fromisoformat(value)


def official_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (host == "gov.vn" or host.endswith(".gov.vn"))


def normalize_for_checksum(payload: bytes) -> str:
    text = payload.decode("utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", text)


def validate_dates(value: dict[str, Any], path: str, as_of: date, issues: list[Issue]) -> None:
    effective_from = parsed_date(value.get("effective_from"))
    effective_to = parsed_date(value.get("effective_to")) if value.get("effective_to") else None
    verified = parsed_date(value.get("last_verified_at"))
    reviewed = parsed_date(value.get("reviewed_at")) if value.get("reviewed_at") else None
    if effective_from and effective_to and effective_to < effective_from:
        issues.append(Issue("release_blocked", f"{path}.effective_to", "must not precede effective_from"))
    if effective_from and effective_from > as_of:
        issues.append(Issue("release_blocked", f"{path}.effective_from", "future-effective source"))
    if effective_to and effective_to < as_of:
        issues.append(Issue("release_blocked", f"{path}.effective_to", "source is no longer effective"))
    if verified and verified > as_of:
        issues.append(Issue("release_blocked", f"{path}.last_verified_at", "future verification date"))
    if reviewed and reviewed > as_of:
        issues.append(Issue("release_blocked", f"{path}.reviewed_at", "future review date"))


def unique_ids(items: Any, key: str, path: str, issues: list[Issue]) -> None:
    if not isinstance(items, list):
        issues.append(Issue("list_required", path, "list required"))
        return
    seen: set[str] = set()
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            issues.append(Issue("object_required", item_path, "object required"))
            continue
        value = item.get(key)
        required(value, f"{item_path}.{key}", issues)
        if isinstance(value, str) and value in seen:
            issues.append(Issue("duplicate_id", f"{item_path}.{key}", value))
        if isinstance(value, str):
            seen.add(value)


def validate_registry(registry: dict[str, Any], release: bool, as_of: date, repository_root: Path, issues: list[Issue]) -> dict[str, dict[str, Any]]:
    if registry.get("schema_version") != "vaic-approved-source-registry-v1":
        issues.append(Issue("schema", "registry", "unsupported schema"))
    required(registry.get("snapshot_id"), "registry.snapshot_id", issues)
    if release and registry.get("review_status") != "approved":
        issues.append(Issue("release_blocked", "registry.review_status", "approved required"))
    if release and not iso_date(registry.get("freeze_date")):
        issues.append(Issue("release_blocked", "registry.freeze_date", "ISO date required"))
    if release and (registry.get("not_for_production") is True or registry.get("approval_mode") != "human_k1"):
        issues.append(Issue("release_blocked", "registry.approval_mode", "human_k1 production release required"))
    rows = registry.get("sources")
    if not isinstance(rows, list):
        issues.append(Issue("sources", "registry.sources", "list required"))
        return {}
    sources: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        path = f"registry.sources[{index}]"
        if not isinstance(row, dict):
            issues.append(Issue("source", path, "object required"))
            continue
        source_id = row.get("source_id")
        procedure_id = row.get("procedure_id")
        if not isinstance(source_id, str) or source_id in sources:
            issues.append(Issue("source_id", path, "unique source_id required"))
            continue
        sources[source_id] = row
        if procedure_id not in EXPECTED or EXPECTED[procedure_id][0] != source_id:
            issues.append(Issue("canonical_pair", path, "unexpected procedure/source pair"))
        if release:
            for field in ("authority", "jurisdiction", "document_version", "permission_status", "reviewed_by", "review_notes"):
                required(row.get(field), f"{path}.{field}", issues, "release_blocked")
            if row.get("review_status") != "approved":
                issues.append(Issue("release_blocked", f"{path}.review_status", "approved required"))
            if not official_url(row.get("source_url")):
                issues.append(Issue("release_blocked", f"{path}.source_url", "official HTTPS .gov.vn URL required"))
            for field in ("effective_from", "last_verified_at", "reviewed_at"):
                if not iso_date(row.get(field)):
                    issues.append(Issue("release_blocked", f"{path}.{field}", "ISO date required"))
            for field in ("raw_sha256", "normalized_sha256"):
                if not isinstance(row.get(field), str) or not SHA256.fullmatch(row[field]):
                    issues.append(Issue("release_blocked", f"{path}.{field}", "SHA-256 required"))
            validate_dates(row, path, as_of, issues)
            raw_path = row.get("raw_path")
            if not isinstance(raw_path, str) or not raw_path.strip():
                issues.append(Issue("release_blocked", f"{path}.raw_path", "reviewed raw source path required"))
            else:
                candidate = (repository_root / raw_path).resolve()
                if repository_root.resolve() not in candidate.parents or not candidate.is_file():
                    issues.append(Issue("release_blocked", f"{path}.raw_path", "source file must exist inside repository"))
                else:
                    payload = candidate.read_bytes()
                    raw_digest = hashlib.sha256(payload).hexdigest()
                    normalized_digest = hashlib.sha256(normalize_for_checksum(payload).encode("utf-8")).hexdigest()
                    if row.get("raw_sha256") != raw_digest:
                        issues.append(Issue("release_blocked", f"{path}.raw_sha256", "raw source checksum mismatch"))
                    if row.get("normalized_sha256") != normalized_digest:
                        issues.append(Issue("release_blocked", f"{path}.normalized_sha256", "normalized source checksum mismatch"))
    if set(sources) != {item[0] for item in EXPECTED.values()}:
        issues.append(Issue("source_set", "registry.sources", "exactly three canonical sources required"))
    return sources


def validate_pack(pack: dict[str, Any], procedure_id: str, source_id: str, snapshot_id: Any, sources: dict[str, dict[str, Any]], release: bool, as_of: date, issues: list[Issue]) -> None:
    root = procedure_id
    if pack.get("schema_version") != "vaic-procedure-pack-v1":
        issues.append(Issue("schema", root, "unsupported schema"))
    if pack.get("procedure_id") != procedure_id:
        issues.append(Issue("procedure_id", root, "unexpected procedure"))
    required(pack.get("name"), f"{root}.name", issues)
    required(pack.get("version"), f"{root}.version", issues)
    if pack.get("source_snapshot_id") != snapshot_id:
        issues.append(Issue("snapshot", f"{root}.source_snapshot_id", "registry mismatch"))
    if pack.get("source_refs") != [source_id] or source_id not in sources:
        issues.append(Issue("source_refs", f"{root}.source_refs", "canonical source required"))
    scope = pack.get("scope")
    if not isinstance(scope, dict) or not scope.get("included_cases") or not scope.get("excluded_cases"):
        issues.append(Issue("scope", f"{root}.scope", "included and excluded cases required"))
    if not isinstance(pack.get("aliases"), list) or not pack["aliases"]:
        issues.append(Issue("aliases", f"{root}.aliases", "non-empty list required"))
    for collection, key in (("intake_questions", "id"), ("checklist_items", "id"), ("steps", "id"), ("validation_rules", "rule_id")):
        unique_ids(pack.get(collection), key, f"{root}.{collection}", issues)
    for collection in ("intake_questions", "checklist_items", "steps", "validation_rules"):
        for index, item in enumerate(pack.get(collection, [])):
            if not isinstance(item, dict):
                continue
            citation = item.get("source")
            path = f"{root}.{collection}[{index}].source"
            if not isinstance(citation, dict) or citation.get("source_id") != source_id:
                issues.append(Issue("citation", path, "canonical source for this pack required"))
            elif release:
                required(citation.get("locator"), f"{path}.locator", issues, "release_blocked")
            if collection == "validation_rules" and item.get("type") not in RULE_TYPES:
                issues.append(Issue("rule_type", f"{root}.{collection}[{index}]", "unsupported deterministic rule"))
    if not isinstance(pack.get("form_schema"), dict) or pack["form_schema"].get("type") != "object":
        issues.append(Issue("form_schema", f"{root}.form_schema", "object JSON schema required"))
    for field_id, field in pack.get("form_schema", {}).get("properties", {}).items():
        citation = field.get("source") if isinstance(field, dict) else None
        if not isinstance(citation, dict) or citation.get("source_id") != source_id:
            issues.append(Issue("citation", f"{root}.form_schema.properties.{field_id}.source", "canonical source for this pack required"))
        elif release:
            required(citation.get("locator"), f"{root}.form_schema.properties.{field_id}.source.locator", issues, "release_blocked")
    if release:
        if pack.get("not_for_production") is True or pack.get("approval_mode") != "human_k1":
            issues.append(Issue("release_blocked", f"{root}.approval_mode", "human_k1 production release required"))
        if pack.get("review_status") != "approved":
            issues.append(Issue("release_blocked", f"{root}.review_status", "approved required"))
        for field in ("effective_from", "last_verified_at"):
            if not iso_date(pack.get(field)):
                issues.append(Issue("release_blocked", f"{root}.{field}", "ISO date required"))
        for field in ("authority", "processing_time", "fee"):
            required(pack.get(field), f"{root}.{field}", issues, "release_blocked")
        approval = pack.get("approval", {})
        for field in ("reviewed_by", "review_notes"):
            required(approval.get(field), f"{root}.approval.{field}", issues, "release_blocked")
        if not iso_date(approval.get("reviewed_at")):
            issues.append(Issue("release_blocked", f"{root}.approval.reviewed_at", "ISO date required"))
        for collection in ("intake_questions", "checklist_items", "steps", "validation_rules"):
            if not pack.get(collection):
                issues.append(Issue("release_blocked", f"{root}.{collection}", "reviewed content required"))
        validate_dates({**pack, "reviewed_at": approval.get("reviewed_at")}, root, as_of, issues)


def validate_synthetic_chunks(root: Path, issues: list[Issue]) -> None:
    path = root / "synthetic-candidate-rag-chunks.jsonl"
    if not path.exists():
        return
    allowed_procedures = set(EXPECTED)
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            chunk = json.loads(line)
        except json.JSONDecodeError as error:
            issues.append(Issue("invalid_json", f"{path}:{line_number}", str(error)))
            continue
        prefix = f"synthetic_chunks[{line_number}]"
        if chunk.get("review_status") != "needs_review" or chunk.get("approval_mode") != "synthetic_demo" or chunk.get("not_for_production") is not True:
            issues.append(Issue("synthetic_boundary", prefix, "synthetic chunk must remain needs_review and not_for_production"))
        if chunk.get("release_eligible") is not False or chunk.get("quarantine_reason") != "missing_human_k1_and_official_evidence":
            issues.append(Issue("synthetic_boundary", prefix, "synthetic chunk must remain quarantined before K1"))
        if not set(chunk.get("procedure_ids", ())).issubset(allowed_procedures):
            issues.append(Issue("procedure_id", f"{prefix}.procedure_ids", "canonical procedure slug required"))
        if any(str(ref).startswith(LOCAL_SOURCE_SCHEMES) for ref in chunk.get("source_refs", ())):
            pass  # Explicitly allowed only because this file is synthetic and fail-closed.
        chunk_id = chunk.get("chunk_id")
        if chunk_id in seen:
            issues.append(Issue("duplicate_id", f"{prefix}.chunk_id", str(chunk_id)))
        seen.add(chunk_id)
        if not isinstance(chunk.get("token_count"), int) or chunk["token_count"] > 450:
            issues.append(Issue("token_budget", f"{prefix}.token_count", "integer <= 450 required"))


def validate(release: bool = False, root: Path = ROOT, as_of: date | None = None, repository_root: Path | None = None) -> list[Issue]:
    issues: list[Issue] = []
    registry = load(root / "approved-source-registry.json", issues)
    if registry is None:
        return issues
    review_date = as_of or date.today()
    repo = repository_root or root.parents[1]
    sources = validate_registry(registry, release, review_date, repo, issues)
    for procedure_id, (source_id, filename) in EXPECTED.items():
        pack = load(root / "procedure-packs" / filename, issues)
        if pack:
            validate_pack(pack, procedure_id, source_id, registry.get("snapshot_id"), sources, release, review_date, issues)
    validate_synthetic_chunks(root, issues)
    return issues


def coverage(root: Path = ROOT) -> dict[str, Any]:
    report: dict[str, Any] = {"schema_version": "vaic-procedure-pack-coverage-v1", "packs": {}}
    for procedure_id, (_, filename) in EXPECTED.items():
        pack = json.loads((root / "procedure-packs" / filename).read_text(encoding="utf-8"))
        claims = 0
        cited = 0
        for collection in ("intake_questions", "checklist_items", "steps", "validation_rules"):
            for item in pack.get(collection, []):
                claims += 1
                cited += int(isinstance(item, dict) and isinstance(item.get("source"), dict) and bool(item["source"].get("locator")))
        for field in pack.get("form_schema", {}).get("properties", {}).values():
            claims += 1
            cited += int(isinstance(field, dict) and isinstance(field.get("source"), dict) and bool(field["source"].get("locator")))
        report["packs"][procedure_id] = {"claims": claims, "cited_claims": cited, "citation_coverage": 0.0 if claims == 0 else cited / claims}
    return report


def checksum(root: Path = ROOT) -> str:
    digest = hashlib.sha256()
    paths = [root / "approved-source-registry.json", *sorted((root / "procedure-packs").glob("*.json"))]
    for path in paths:
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--report-output", type=Path)
    arguments = parser.parse_args(argv)
    issues = validate(arguments.release, as_of=arguments.as_of)
    if arguments.report_output:
        arguments.report_output.parent.mkdir(parents=True, exist_ok=True)
        arguments.report_output.write_text(json.dumps(coverage(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        for issue in issues:
            print(issue.render(), file=sys.stderr)
        print(f"Procedure-pack validation failed: issues={len(issues)}", file=sys.stderr)
        return 1
    mode = "release" if arguments.release else "candidate"
    print(f"Procedure-pack validation passed: mode={mode} procedures=3 checksum={checksum()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
