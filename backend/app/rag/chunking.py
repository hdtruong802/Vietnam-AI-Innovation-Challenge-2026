"""Deterministic evidence chunk builder with provider-neutral token accounting."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Protocol

from .normalization import NORMALIZER_VERSION
from .parsing import PARSER_VERSION, ParsedSection


CHUNKER_VERSION = "vaic-structure-chunker-v1"
DEFAULT_TOKENIZER_ID = "heuristic-wordpunct-v1"
DEFAULT_TARGET_TOKENS = 320
DEFAULT_HARD_MAXIMUM_TOKENS = 450
DEFAULT_MERGE_THRESHOLD_TOKENS = 80

_WORD_OR_PUNCTUATION = re.compile(r"\w+|[^\w\s]", re.UNICODE)
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?;:])\s+")


class TokenCounter(Protocol):
    tokenizer_id: str

    def count(self, text: str) -> int:
        """Return the number of tokens used by a chunk payload."""


@dataclass(frozen=True, slots=True)
class HeuristicTokenCounter:
    """Fixture-only token counter; runtime tokenizers need their own adapter."""

    tokenizer_id: str = DEFAULT_TOKENIZER_ID

    def count(self, text: str) -> int:
        return len(_WORD_OR_PUNCTUATION.findall(text))


@dataclass(frozen=True, slots=True)
class ChunkerConfig:
    target_tokens: int = DEFAULT_TARGET_TOKENS
    hard_maximum_tokens: int = DEFAULT_HARD_MAXIMUM_TOKENS
    merge_threshold_tokens: int = DEFAULT_MERGE_THRESHOLD_TOKENS

    def __post_init__(self) -> None:
        if self.merge_threshold_tokens < 1:
            raise ValueError("merge_threshold_tokens must be positive")
        if self.target_tokens < self.merge_threshold_tokens:
            raise ValueError("target_tokens must be >= merge_threshold_tokens")
        if self.hard_maximum_tokens < self.target_tokens:
            raise ValueError("hard_maximum_tokens must be >= target_tokens")


@dataclass(frozen=True, slots=True)
class ChunkSourceMetadata:
    source_id: str
    procedure_ids: tuple[str, ...]
    jurisdiction: str = "unknown"
    source_refs: tuple[str, ...] = ()
    effective_from: str | None = None
    effective_to: str | None = None
    review_status: str = "needs_review"

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id is required")
        if not self.procedure_ids:
            raise ValueError("at least one procedure_id is required")


@dataclass(frozen=True, slots=True)
class EvidenceChunk:
    chunk_id: str
    source_id: str
    section_ids: tuple[str, ...]
    procedure_ids: tuple[str, ...]
    chunk_type: str
    section_path: tuple[str, ...]
    context_prefix: str
    text: str
    token_count: int
    tokenizer_id: str
    jurisdiction: str
    effective_from: str | None
    effective_to: str | None
    source_refs: tuple[str, ...]
    legal_basis_refs: tuple[str, ...]
    review_status: str
    chunker_version: str
    content_checksum: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ChunkBuildReport:
    build_id: str
    started_at: str
    completed_at: str
    source_snapshot_id: str
    normalizer_version: str
    parser_version: str
    chunker_version: str
    tokenizer_id: str
    selected: int
    approved: int
    quarantined: int
    rejected: int
    chunk_count: int
    token_percentiles: dict[str, int]
    warning_counts: dict[str, int]
    input_manifest_checksum: str
    output_manifest_checksum: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class _ChunkUnit:
    source_id: str
    section_ids: tuple[str, ...]
    procedure_ids: tuple[str, ...]
    chunk_type: str
    section_path: tuple[str, ...]
    text: str
    legal_basis_refs: tuple[str, ...]
    parse_warnings: tuple[str, ...]


def _context_prefix(metadata: ChunkSourceMetadata, unit: _ChunkUnit) -> str:
    procedures = ",".join(metadata.procedure_ids)
    section = "/".join(unit.section_path)
    return f"source={metadata.source_id} | procedures={procedures} | section={section}"


def _payload(prefix: str, text: str) -> str:
    return f"{prefix}\n{text}" if prefix else text


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _split_words_to_budget(
    text: str,
    prefix: str,
    token_counter: TokenCounter,
    hard_maximum: int,
) -> list[str]:
    tokens = _WORD_OR_PUNCTUATION.findall(text)
    if not tokens:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    for token in tokens:
        candidate = " ".join([*current, token]).strip()
        if current and token_counter.count(_payload(prefix, candidate)) > hard_maximum:
            chunks.append(" ".join(current).strip())
            current = [token]
        else:
            current.append(token)
    if current:
        chunks.append(" ".join(current).strip())
    return chunks


def _split_text_to_budget(
    text: str,
    prefix: str,
    token_counter: TokenCounter,
    hard_maximum: int,
) -> list[str]:
    if token_counter.count(_payload(prefix, text)) <= hard_maximum:
        return [text]

    candidates: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        candidates.extend(
            part.strip() for part in _SENTENCE_BOUNDARY.split(stripped) if part.strip()
        )

    pieces: list[str] = []
    current = ""
    for candidate in candidates or [text]:
        if token_counter.count(_payload(prefix, candidate)) > hard_maximum:
            if current:
                pieces.append(current)
                current = ""
            pieces.extend(
                _split_words_to_budget(candidate, prefix, token_counter, hard_maximum)
            )
            continue
        merged = f"{current}\n{candidate}".strip() if current else candidate
        if current and token_counter.count(_payload(prefix, merged)) > hard_maximum:
            pieces.append(current)
            current = candidate
        else:
            current = merged
    if current:
        pieces.append(current)
    return pieces


def _units_from_section(
    section: ParsedSection,
    metadata: ChunkSourceMetadata,
    token_counter: TokenCounter,
    config: ChunkerConfig,
) -> list[_ChunkUnit]:
    base_unit = _ChunkUnit(
        source_id=metadata.source_id,
        section_ids=(section.section_id,),
        procedure_ids=metadata.procedure_ids,
        chunk_type=section.section_type,
        section_path=section.section_path,
        text=section.text,
        legal_basis_refs=section.legal_basis_refs,
        parse_warnings=section.parse_warnings,
    )
    prefix = _context_prefix(metadata, base_unit)
    parts = _split_text_to_budget(
        section.text, prefix, token_counter, config.hard_maximum_tokens
    )
    if len(parts) == 1:
        return [base_unit]
    units: list[_ChunkUnit] = []
    for index, part in enumerate(parts, start=1):
        section_path = (*base_unit.section_path, f"part-{index}")
        provisional = _ChunkUnit(
            source_id=base_unit.source_id,
            section_ids=base_unit.section_ids,
            procedure_ids=base_unit.procedure_ids,
            chunk_type=base_unit.chunk_type,
            section_path=section_path,
            text=part,
            legal_basis_refs=base_unit.legal_basis_refs,
            parse_warnings=base_unit.parse_warnings,
        )
        final_prefix = _context_prefix(metadata, provisional)
        final_parts = _split_text_to_budget(
            part, final_prefix, token_counter, config.hard_maximum_tokens
        )
        for final_part in final_parts:
            units.append(
                _ChunkUnit(
                    source_id=base_unit.source_id,
                    section_ids=base_unit.section_ids,
                    procedure_ids=base_unit.procedure_ids,
                    chunk_type=base_unit.chunk_type,
                    section_path=section_path,
                    text=final_part,
                    legal_basis_refs=base_unit.legal_basis_refs,
                    parse_warnings=base_unit.parse_warnings,
                )
            )
    return units


def _compatible(left: _ChunkUnit, right: _ChunkUnit) -> bool:
    return (
        left.source_id == right.source_id
        and left.procedure_ids == right.procedure_ids
        and left.chunk_type == right.chunk_type
        and left.legal_basis_refs == right.legal_basis_refs
        and not (set(left.section_ids) & set(right.section_ids))
    )


def _merge_units(left: _ChunkUnit, right: _ChunkUnit) -> _ChunkUnit:
    return _ChunkUnit(
        source_id=left.source_id,
        section_ids=(*left.section_ids, *right.section_ids),
        procedure_ids=left.procedure_ids,
        chunk_type=left.chunk_type,
        section_path=(left.chunk_type,),
        text=f"{left.text}\n{right.text}".strip(),
        legal_basis_refs=left.legal_basis_refs,
        parse_warnings=tuple(sorted({*left.parse_warnings, *right.parse_warnings})),
    )


def _should_merge(
    current: _ChunkUnit,
    candidate: _ChunkUnit,
    metadata: ChunkSourceMetadata,
    token_counter: TokenCounter,
    config: ChunkerConfig,
) -> bool:
    if not _compatible(current, candidate):
        return False
    merged = _merge_units(current, candidate)
    token_count = token_counter.count(_payload(_context_prefix(metadata, merged), merged.text))
    if token_count > config.hard_maximum_tokens:
        return False
    current_tokens = token_counter.count(
        _payload(_context_prefix(metadata, current), current.text)
    )
    return current_tokens < config.merge_threshold_tokens or token_count <= config.target_tokens


def _stable_chunk_id(
    unit: _ChunkUnit,
    ordinal: int,
    tokenizer_id: str,
    content_checksum: str,
) -> str:
    identity = "|".join(
        (
            CHUNKER_VERSION,
            unit.source_id,
            ",".join(unit.section_ids),
            str(ordinal),
            "/".join(unit.section_path),
            tokenizer_id,
            content_checksum,
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]


def build_evidence_chunks(
    sections: list[ParsedSection],
    metadata: ChunkSourceMetadata,
    token_counter: TokenCounter | None = None,
    config: ChunkerConfig | None = None,
) -> list[EvidenceChunk]:
    """Build ordered evidence chunks from parsed sections without indexing them."""

    if not sections:
        return []
    token_counter = token_counter or HeuristicTokenCounter()
    config = config or ChunkerConfig()

    units: list[_ChunkUnit] = []
    for section in sorted(sections, key=lambda item: item.ordinal):
        if section.source_id != metadata.source_id:
            raise ValueError("section source_id must match chunk metadata")
        units.extend(_units_from_section(section, metadata, token_counter, config))

    merged_units: list[_ChunkUnit] = []
    for unit in units:
        if merged_units and _should_merge(
            merged_units[-1], unit, metadata, token_counter, config
        ):
            merged_units[-1] = _merge_units(merged_units[-1], unit)
        else:
            merged_units.append(unit)

    chunks: list[EvidenceChunk] = []
    for ordinal, unit in enumerate(merged_units, start=1):
        prefix = _context_prefix(metadata, unit)
        checksum = _text_hash(_payload(prefix, unit.text))
        token_count = token_counter.count(_payload(prefix, unit.text))
        if token_count > config.hard_maximum_tokens:
            raise ValueError("chunk exceeds hard maximum token budget")
        chunks.append(
            EvidenceChunk(
                chunk_id=_stable_chunk_id(
                    unit, ordinal, token_counter.tokenizer_id, checksum
                ),
                source_id=metadata.source_id,
                section_ids=unit.section_ids,
                procedure_ids=metadata.procedure_ids,
                chunk_type=unit.chunk_type,
                section_path=unit.section_path,
                context_prefix=prefix,
                text=unit.text,
                token_count=token_count,
                tokenizer_id=token_counter.tokenizer_id,
                jurisdiction=metadata.jurisdiction,
                effective_from=metadata.effective_from,
                effective_to=metadata.effective_to,
                source_refs=metadata.source_refs,
                legal_basis_refs=unit.legal_basis_refs,
                review_status=metadata.review_status,
                chunker_version=CHUNKER_VERSION,
                content_checksum=checksum,
            )
        )
    return chunks


def token_percentiles(chunks: list[EvidenceChunk]) -> dict[str, int]:
    if not chunks:
        return {"p50": 0, "p90": 0, "p95": 0, "p100": 0}
    values = sorted(chunk.token_count for chunk in chunks)

    def percentile(percent: float) -> int:
        index = round((len(values) - 1) * percent)
        return values[index]

    return {
        "p50": percentile(0.50),
        "p90": percentile(0.90),
        "p95": percentile(0.95),
        "p100": values[-1],
    }


def build_report(
    chunks: list[EvidenceChunk],
    selected: int,
    input_manifest_checksum: str,
    source_snapshot_id: str,
    warning_counts: Counter[str] | None = None,
    timestamp: str = "1970-01-01T00:00:00Z",
) -> ChunkBuildReport:
    review_counts = Counter(chunk.review_status for chunk in chunks)
    output_manifest = "\n".join(
        f"{chunk.chunk_id}:{chunk.content_checksum}:{chunk.token_count}"
        for chunk in chunks
    )
    output_manifest_checksum = _text_hash(output_manifest)
    identity = "|".join(
        (
            source_snapshot_id,
            CHUNKER_VERSION,
            chunks[0].tokenizer_id if chunks else DEFAULT_TOKENIZER_ID,
            input_manifest_checksum,
            output_manifest_checksum,
        )
    )
    return ChunkBuildReport(
        build_id=hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24],
        started_at=timestamp,
        completed_at=timestamp,
        source_snapshot_id=source_snapshot_id,
        normalizer_version=NORMALIZER_VERSION,
        parser_version=PARSER_VERSION,
        chunker_version=CHUNKER_VERSION,
        tokenizer_id=chunks[0].tokenizer_id if chunks else DEFAULT_TOKENIZER_ID,
        selected=selected,
        approved=review_counts.get("approved", 0),
        quarantined=review_counts.get("needs_review", 0),
        rejected=review_counts.get("rejected", 0),
        chunk_count=len(chunks),
        token_percentiles=token_percentiles(chunks),
        warning_counts=dict(sorted((warning_counts or Counter()).items())),
        input_manifest_checksum=input_manifest_checksum,
        output_manifest_checksum=output_manifest_checksum,
    )
