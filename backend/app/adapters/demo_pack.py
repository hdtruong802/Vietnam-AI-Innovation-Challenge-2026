"""Demo-approved procedure packs for the local MVP flow.

Cac pack JSON trong app/data/demo_packs duoc author offline tu nguon cong khai
data/Data_DVC (ma 1.001193 / 1.004222 / 1.001612) va mang
review_status=demo_approved voi demo_pack=true. Day la du lieu ky thuat cho
demo, KHONG phai K1/human legal approval. TrustPolicy gan demo_mode vao moi
response de UI luon hien thi watermark demo.
"""

from __future__ import annotations

import json
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

from app.models.common import SessionContext
from app.models.procedure import (
    ProcedureCandidate,
    ProcedurePack,
    ProcedureSummary,
    ReviewStatus,
)
from app.services.intent_router import normalize_intent_text

DEMO_PACK_DIR = Path(__file__).resolve().parents[1] / "data" / "demo_packs"
FUZZY_ALIAS_THRESHOLD = 0.82
FUZZY_SCORE_MARGIN = 0.08


def _alias_score(query: str, alias: str) -> float:
    normalized_alias = normalize_intent_text(alias)
    if f" {normalized_alias} " in f" {query} ":
        return 1.0
    alias_words = normalized_alias.split()
    if len(alias_words) < 2:
        return 0.0
    query_words = query.split()
    if len(query_words) < len(alias_words):
        return SequenceMatcher(None, normalized_alias, query).ratio()
    return max(
        SequenceMatcher(
            None,
            normalized_alias,
            " ".join(query_words[index : index + len(alias_words)]),
        ).ratio()
        for index in range(len(query_words) - len(alias_words) + 1)
    )


@lru_cache(maxsize=1)
def load_demo_packs() -> dict[str, ProcedurePack]:
    packs: dict[str, ProcedurePack] = {}
    for path in sorted(DEMO_PACK_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        pack = ProcedurePack.model_validate(raw)
        if not pack.demo_pack:
            raise ValueError(
                f"Demo pack {path.name} thiếu demo_pack=true; "
                "chỉ pack watermark demo được nạp qua adapter này."
            )
        if pack.review_status != ReviewStatus.DEMO_APPROVED:
            raise ValueError(f"Demo pack {path.name} phải dùng review_status=demo_approved.")
        packs[pack.procedure_id] = pack
    if not packs:
        raise FileNotFoundError(f"Không tìm thấy demo pack JSON nào trong {DEMO_PACK_DIR}")
    return packs


class DemoPackProcedureRepository:
    async def list_procedures(self) -> list[ProcedureSummary]:
        return [
            ProcedureSummary(
                procedure_id=pack.procedure_id,
                name=pack.name,
                version=pack.version,
                review_status=pack.review_status,
                demo_mode=True,
            )
            for pack in load_demo_packs().values()
        ]

    async def get_procedure(self, procedure_id: str) -> ProcedurePack | None:
        return load_demo_packs().get(procedure_id)


class DemoPackRecommendationProvider:
    async def recommend(
        self, need_text: str, session_context: SessionContext
    ) -> list[ProcedureCandidate]:
        normalized_need = normalize_intent_text(need_text)
        ranked: list[tuple[float, ProcedurePack, str]] = []
        for pack in load_demo_packs().values():
            scored_aliases = [
                (_alias_score(normalized_need, alias), alias) for alias in pack.aliases
            ]
            score, alias = max(scored_aliases, key=lambda item: item[0])
            ranked.append((score, pack, alias))
        ranked.sort(key=lambda item: item[0], reverse=True)
        top_score, top_pack, top_alias = ranked[0]
        second_score = ranked[1][0]
        if top_score < FUZZY_ALIAS_THRESHOLD or top_score - second_score < FUZZY_SCORE_MARGIN:
            return []
        match_kind = "chính xác" if top_score == 1.0 else "gần đúng bảo thủ"
        return [
            ProcedureCandidate(
                procedure_id=top_pack.procedure_id,
                name=top_pack.name,
                reason=(f'Khớp {match_kind} với cụm "{top_alias}" (điểm {top_score:.2f}).'),
            )
        ]
