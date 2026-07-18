"""Dense embedding index cho hybrid RAG retrieval.

Provider priority (cau hinh qua RAG_EMBEDDING_PROVIDER):
  "local"  — sentence-transformers + HuggingFace model (offline, khong ton API).
  "openai" — OpenAI-compatible embedding API (can AI_API_KEY).
  "auto"   — thu local truoc, roi fallback openai, roi fallback keyword (default).

Model mac dinh: bkai-foundation-models/vietnamese-bi-encoder
  — duoc train tren du lieu retrieval tieng Viet, phu hop nhat voi tap thu tuc
    hanh chinh. Tai tu HuggingFace ~400 MB lan dau, sau do dung cache local.
  — Override: RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
    (nhe hon, 117 MB, van ho tro tieng Viet).

Thiet ke fail-open cho retrieval:
  - Neu ca local lan openai deu that bai: tra ve None, caller tu dong fallback
    ve keyword-only (khong co phan guidance nao bi mat hoac sai).
  - Khong luu vector ra disk/DB: chi in-memory, mat khi restart (acceptable MVP).
  - Index duoc build mot lan luc khoi dong qua @lru_cache.
"""

from __future__ import annotations

import logging
import math
from functools import lru_cache
from typing import Dict, List, Optional

from app.config import get_settings  # module-level import de monkeypatch hoat dong trong test

logger = logging.getLogger("vngov.embedding")

Vector = tuple[float, ...]
EmbeddingMap = Dict[str, Vector]  # chunk_id -> dense vector


# ---------------------------------------------------------------------------
# Pure-Python cosine similarity (khong can numpy; sentence-transformers da
# tinh toan vector, chung ta chi can dot-product de score luc retrieve).
# ---------------------------------------------------------------------------


def cosine_similarity_dense(a: Vector, b: Vector) -> float:
    """Cosine similarity giua hai dense float vector (pure Python, no numpy)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    if dot == 0.0:
        return 0.0
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------


def _embed_local(
    texts: List[str],
    model_name: str,
    batch_size: int,
) -> Optional[List[Vector]]:
    """Embed bang sentence-transformers (local HuggingFace model, offline)."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import]
    except ImportError:
        logger.warning(
            "sentence-transformers chua duoc cai dat. " "Chay: pip install sentence-transformers"
        )
        return None

    try:
        logger.info("Dang tai model local: %s", model_name)
        model = SentenceTransformer(model_name)
        # encode() tra ve numpy ndarray; chuyen sang list[tuple[float]] de
        # trang bi thi voi cosine_similarity_dense va de lru_cache hash duoc.
        all_vectors: List[Vector] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            vecs = model.encode(batch, show_progress_bar=False, convert_to_numpy=True)
            for vec in vecs:
                all_vectors.append(tuple(float(v) for v in vec))
        return all_vectors
    except Exception as exc:
        logger.warning("Local embedding loi (%s); thu fallback openai. %s", model_name, exc)
        return None


def _embed_openai(
    texts: List[str],
    model_name: str,
    api_key: str,
    base_url: Optional[str],
    timeout: float,
    batch_size: int,
) -> Optional[List[Vector]]:
    """Embed bang OpenAI-compatible embedding API."""
    try:
        from openai import OpenAI  # type: ignore[import]
    except ImportError:
        logger.warning("openai SDK chua duoc cai dat; bo qua openai embedding.")
        return None

    client_kwargs: dict = {"api_key": api_key, "timeout": timeout}
    if base_url:
        client_kwargs["base_url"] = base_url

    try:
        client = OpenAI(**client_kwargs)
        all_vectors: List[Vector] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = client.embeddings.create(
                model=model_name,
                input=batch,
                encoding_format="float",
            )
            for item in response.data:
                all_vectors.append(tuple(item.embedding))
        return all_vectors
    except Exception as exc:
        logger.warning("OpenAI embedding API loi; fallback keyword-only. %s", exc)
        return None


def _embed_texts(texts: List[str]) -> Optional[List[Vector]]:
    """Dispatch toi provider dua tren RAG_EMBEDDING_PROVIDER setting."""
    s = get_settings()
    provider = s.rag_embedding_provider
    model = s.rag_embedding_model
    batch = s.rag_embedding_batch_size

    if provider in ("local", "auto"):
        result = _embed_local(texts, model, batch)
        if result is not None:
            return result
        if provider == "local":
            return None  # "local" mode: khong fallback sang openai

    # "openai" mode hoac "auto" sau khi local that bai
    api_key = s.effective_ai_api_key
    if not api_key:
        logger.info(
            "RAG_EMBEDDING_PROVIDER=%s nhung AI_API_KEY trong; " "fallback keyword-only.",
            provider,
        )
        return None

    openai_model = model if provider == "openai" else "text-embedding-3-small"
    return _embed_openai(
        texts,
        openai_model,
        api_key,
        s.effective_ai_base_url,
        s.effective_ai_timeout_seconds,
        batch,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def build_embedding_index(
    chunk_ids: tuple[str, ...],
    chunk_texts: tuple[str, ...],
) -> Optional[EmbeddingMap]:
    """Xay dung in-memory dense embedding index cho toan bo corpus.

    Parameters
    ----------
    chunk_ids : tuple[str, ...]
        ID cua tung chunk (hashable de lru_cache hoat dong).
    chunk_texts : tuple[str, ...]
        Van ban tuong ung, cung thu tu voi chunk_ids.

    Returns
    -------
    EmbeddingMap (chunk_id -> Vector) hoac None neu embedding khong kha dung.
    """
    if get_settings().rag_retrieval_mode == "keyword":
        return None  # keyword-only mode: khong can build index

    if not chunk_texts:
        return None

    logger.info(
        "Building dense embedding index: %d chunks, model=%s, provider=%s",
        len(chunk_texts),
        get_settings().rag_embedding_model,
        get_settings().rag_embedding_provider,
    )

    vectors = _embed_texts(list(chunk_texts))
    if vectors is None or len(vectors) != len(chunk_ids):
        logger.warning(
            "Dense embedding that bai hoac so luong vector khong khop; "
            "retrieval se dung keyword-only."
        )
        return None

    index: EmbeddingMap = dict(zip(chunk_ids, vectors))
    logger.info("Dense embedding index san sang: %d entries.", len(index))
    return index


def embed_query(query_text: str) -> Optional[Vector]:
    """Embed mot query don le cho luc retrieve.

    Khong cache (query thay doi theo request). Tra ve None neu provider
    khong kha dung — caller fallback ve keyword score.
    """
    if get_settings().rag_retrieval_mode == "keyword":
        return None

    vectors = _embed_texts([query_text])
    if vectors and len(vectors) == 1:
        return vectors[0]
    return None


def clear_embedding_cache() -> None:
    """Chi dung trong test: reset lru_cache khi thay doi settings."""
    build_embedding_index.cache_clear()
