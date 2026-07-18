"""Source-document approval gate for release-eligible RAG chunks."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any

from .chunking import ChunkSourceMetadata
from .normalization import NORMALIZER_VERSION
from .parsing import PARSER_VERSION

SOURCE_REGISTRY_VERSION = "vaic-source-registry-v1"
APPROVED_REVIEW_STATUS = "approved"
RELEASE_BLOCKED_REVIEW_STATUSES = {
    "staging",
    "parsed",
    "needs_review",
    "rejected",
    "stale",
}
VALID_PERMISSION_STATUSES = {"official_public", "permission_recorded"}


@dataclass(frozen=True, slots=True)
class SourceValidationIssue:
    field: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceDocument:
    source_id: str
    raw_document_id: str
    procedure_ids: tuple[str, ...]
    title: str
    authority: str
    jurisdiction: str
    source_ref: str
    document_version: str
    document_type: str
    effective_from: str | None
    effective_to: str | None
    last_verified_at: str
    permission_status: str
    review_status: str
    reviewed_by: str | None
    reviewed_at: str | None
    raw_checksum: str
    normalized_checksum: str
    normalizer_version: str = NORMALIZER_VERSION
    parser_version: str = PARSER_VERSION
    source_registry_version: str = SOURCE_REGISTRY_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def snapshot_fingerprint(self) -> str:
        payload = "|".join(
            (
                self.source_registry_version,
                self.source_id,
                self.raw_checksum,
                self.normalized_checksum,
                self.normalizer_version,
                self.parser_version,
                self.review_status,
                self.reviewed_at or "",
            )
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def validation_issues(self, as_of: str | None = None) -> tuple[SourceValidationIssue, ...]:
        issues: list[SourceValidationIssue] = []
        required = {
            "source_id": self.source_id,
            "raw_document_id": self.raw_document_id,
            "title": self.title,
            "authority": self.authority,
            "jurisdiction": self.jurisdiction,
            "source_ref": self.source_ref,
            "document_version": self.document_version,
            "document_type": self.document_type,
            "last_verified_at": self.last_verified_at,
            "raw_checksum": self.raw_checksum,
            "normalized_checksum": self.normalized_checksum,
        }
        for field, value in required.items():
            if not str(value).strip():
                issues.append(SourceValidationIssue(field, "required"))
        if not self.procedure_ids:
            issues.append(SourceValidationIssue("procedure_ids", "required"))
        if self.permission_status not in VALID_PERMISSION_STATUSES:
            issues.append(SourceValidationIssue("permission_status", "invalid"))

        if self.review_status != APPROVED_REVIEW_STATUS:
            issues.append(SourceValidationIssue("review_status", "not_approved"))
        if not (self.reviewed_by or "").strip():
            issues.append(SourceValidationIssue("reviewed_by", "required_for_approved"))
        if not (self.reviewed_at or "").strip():
            issues.append(SourceValidationIssue("reviewed_at", "required_for_approved"))

        if as_of is not None:
            if self.effective_from is not None and self.effective_from > as_of:
                issues.append(SourceValidationIssue("effective_from", "future_effective"))
            if self.effective_to is not None and self.effective_to < as_of:
                issues.append(SourceValidationIssue("effective_to", "stale"))
            if self.last_verified_at > as_of:
                issues.append(SourceValidationIssue("last_verified_at", "future_verified"))
        return tuple(issues)

    def is_release_eligible(self, as_of: str | None = None) -> bool:
        return not self.validation_issues(as_of=as_of)

    def chunk_metadata(self, as_of: str | None = None) -> ChunkSourceMetadata:
        issues = self.validation_issues(as_of=as_of)
        if issues:
            encoded = ", ".join(f"{issue.field}:{issue.reason}" for issue in issues)
            raise ValueError(f"source is not release eligible: {encoded}")
        return ChunkSourceMetadata(
            source_id=self.source_id,
            procedure_ids=self.procedure_ids,
            jurisdiction=self.jurisdiction,
            source_refs=(self.source_ref,),
            effective_from=self.effective_from,
            effective_to=self.effective_to,
            review_status=APPROVED_REVIEW_STATUS,
        )


class SourceDocumentRegistry:
    def __init__(self, sources: tuple[SourceDocument, ...]) -> None:
        self._sources = sources
        self._by_id = {source.source_id: source for source in sources}
        if len(self._by_id) != len(sources):
            raise ValueError("source_id values must be unique")

    @property
    def selected_count(self) -> int:
        return len(self._sources)

    def get(self, source_id: str) -> SourceDocument | None:
        return self._by_id.get(source_id)

    def approved_sources(self, as_of: str | None = None) -> tuple[SourceDocument, ...]:
        return tuple(source for source in self._sources if source.is_release_eligible(as_of=as_of))

    def release_issues(
        self, as_of: str | None = None
    ) -> dict[str, tuple[SourceValidationIssue, ...]]:
        return {
            source.source_id: source.validation_issues(as_of=as_of)
            for source in self._sources
            if source.validation_issues(as_of=as_of)
        }
