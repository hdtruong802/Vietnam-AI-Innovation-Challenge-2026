import pytest

from app.config import get_settings
from app.services.rag.embedding import (
    build_embedding_index,
    clear_embedding_cache,
    cosine_similarity_dense,
    embed_query,
)
from app.services.rag.retrieval import RetrievalService
from app.services.rag.schemas import RetrievalQuery
from app.services.rag.source_store import (
    PROCEDURE_SOURCE_CODES,
    load_candidate_records,
    strip_diacritics,
)


def _has_source_data() -> bool:
    source_path = get_settings().rag_source_path
    return source_path.exists() and any(source_path.glob("*.txt"))


requires_source_data = pytest.mark.skipif(
    not _has_source_data(), reason="data/Data_DVC khong ton tai trong moi truong nay"
)

# ---------------------------------------------------------------------------
# Embedding unit tests (khong can source data, khong can API/model)
# ---------------------------------------------------------------------------


class TestCosineSimilarityDense:
    def test_identical_vectors_return_one(self):
        v = (1.0, 0.5, 0.3)
        assert cosine_similarity_dense(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors_return_zero(self):
        a = (1.0, 0.0)
        b = (0.0, 1.0)
        assert cosine_similarity_dense(a, b) == pytest.approx(0.0)

    def test_empty_vector_returns_zero(self):
        assert cosine_similarity_dense((), (1.0, 2.0)) == 0.0
        assert cosine_similarity_dense((1.0, 2.0), ()) == 0.0

    def test_mismatched_lengths_return_zero(self):
        assert cosine_similarity_dense((1.0, 2.0), (1.0,)) == 0.0

    def test_partial_overlap(self):
        a = (1.0, 1.0, 0.0)
        b = (1.0, 0.0, 0.0)
        score = cosine_similarity_dense(a, b)
        # dot=1, |a|=sqrt(2), |b|=1 → 1/sqrt(2) ≈ 0.707
        assert 0.7 < score < 0.8


class TestBuildEmbeddingIndex:
    def test_keyword_mode_returns_none(self, monkeypatch):
        """RAG_RETRIEVAL_MODE=keyword phai bo qua toan bo embedding."""
        clear_embedding_cache()
        from app.config import get_settings as _gs

        original = _gs()
        monkeypatch.setattr(
            "app.services.rag.embedding.get_settings",
            lambda: original.model_copy(update={"rag_retrieval_mode": "keyword"}),
        )
        try:
            result = build_embedding_index(
                chunk_ids=("c1", "c2"),
                chunk_texts=("text one", "text two"),
            )
            assert result is None
        finally:
            clear_embedding_cache()

    def test_empty_texts_returns_none(self, monkeypatch):
        clear_embedding_cache()
        from app.config import get_settings as _gs

        original = _gs()
        monkeypatch.setattr(
            "app.services.rag.embedding.get_settings",
            lambda: original.model_copy(update={"rag_retrieval_mode": "hybrid"}),
        )
        try:
            result = build_embedding_index(chunk_ids=(), chunk_texts=())
            assert result is None
        finally:
            clear_embedding_cache()

    def test_no_local_model_and_no_api_key_returns_none(self, monkeypatch):
        """Khi ca sentence-transformers lan API key deu vang: fallback keyword."""
        clear_embedding_cache()
        from app.config import get_settings as _gs

        original = _gs()
        no_key_settings = original.model_copy(
            update={
                "rag_retrieval_mode": "hybrid",
                "rag_embedding_provider": "openai",
                "ai_api_key": "",
                "openai_api_key": "",
            }
        )
        monkeypatch.setattr(
            "app.services.rag.embedding.get_settings",
            lambda: no_key_settings,
        )
        monkeypatch.setattr(
            "app.services.rag.embedding._embed_local",
            lambda *a, **kw: None,
        )
        try:
            result = build_embedding_index(
                chunk_ids=("c1",),
                chunk_texts=("khai sinh",),
            )
            assert result is None
        finally:
            clear_embedding_cache()


class TestEmbedQuery:
    def test_keyword_mode_returns_none(self, monkeypatch):
        from app.config import get_settings as _gs

        original = _gs()
        monkeypatch.setattr(
            "app.services.rag.embedding.get_settings",
            lambda: original.model_copy(update={"rag_retrieval_mode": "keyword"}),
        )
        assert embed_query("xin chào") is None


# ---------------------------------------------------------------------------
# Retrieval integration tests (phu thuoc source data)
# ---------------------------------------------------------------------------


def test_strip_diacritics_folds_vietnamese_d_stroke():
    assert strip_diacritics("Đăng ký thường trú") == "Dang ky thuong tru"


@requires_source_data
def test_load_candidate_records_only_contains_canonical_sources():
    records = load_candidate_records()

    assert set(records.keys()) == {
        "dang-ky-khai-sinh",
        "dang-ky-thuong-tru",
        "dang-ky-ho-kinh-doanh",
    }
    assert len(records["dang-ky-khai-sinh"]) > 0
    assert len(records["dang-ky-thuong-tru"]) > 0
    assert len(records["dang-ky-ho-kinh-doanh"]) > 0
    for procedure_id, procedure_records in records.items():
        assert {record.procedure_code for record in procedure_records} == (
            PROCEDURE_SOURCE_CODES[procedure_id]
        )


@requires_source_data
@pytest.mark.parametrize(
    "query_text,expected_procedure_id",
    [
        # colloquial phrasing that keyword search struggles with
        ("tôi muốn làm khai sinh cho con", "dang-ky-khai-sinh"),
        ("tôi muốn đăng ký thường trú tại nơi ở mới", "dang-ky-thuong-tru"),
        ("tôi muốn đăng ký thành lập hộ kinh doanh", "dang-ky-ho-kinh-doanh"),
    ],
)
def test_recommend_procedure_top1(query_text, expected_procedure_id):
    candidates = RetrievalService.recommend_procedure(query_text, top_k=1)

    assert candidates
    assert candidates[0].procedure_id == expected_procedure_id
    assert candidates[0].score > 0


@requires_source_data
@pytest.mark.parametrize(
    "query_text,expected_procedure_id",
    [
        # paraphrase queries — mai diem cua semantic search so voi keyword
        ("làm giấy khai sinh cho trẻ mới sinh", "dang-ky-khai-sinh"),
        ("chuyển khẩu về địa chỉ mới", "dang-ky-thuong-tru"),
        ("mở cửa hàng kinh doanh nhỏ lẻ", "dang-ky-ho-kinh-doanh"),
    ],
)
def test_recommend_procedure_paraphrase_queries(query_text, expected_procedure_id):
    """Semantic/hybrid mode phai xu ly paraphrase tot hon keyword-only."""
    candidates = RetrievalService.recommend_procedure(query_text, top_k=1)

    assert candidates, f"Khong tim thay candidate nao cho: '{query_text}'"
    assert candidates[0].procedure_id == expected_procedure_id, (
        f"Query '{query_text}' → expected {expected_procedure_id}, "
        f"got {candidates[0].procedure_id} (score={candidates[0].score})"
    )


@requires_source_data
def test_retrieve_returns_grounded_evidence_with_citations():
    evidence = RetrievalService.retrieve(
        RetrievalQuery(
            text="giấy chứng sinh thủ tục đăng ký khai sinh",
            procedure_id="dang-ky-khai-sinh",
        )
    )

    assert evidence.procedure_id == "dang-ky-khai-sinh"
    assert evidence.is_grounded is True
    assert evidence.chunks
    assert evidence.citations
    assert all(c.get("ref_code") for c in evidence.citations)


@requires_source_data
def test_retrieve_unknown_procedure_is_not_grounded():
    evidence = RetrievalService.retrieve(
        RetrievalQuery(text="bất kỳ", procedure_id="khong-ton-tai")
    )

    assert evidence.is_grounded is False
    assert evidence.chunks == []


def test_retrieve_with_missing_source_dir_fails_closed(tmp_path, monkeypatch):
    RetrievalService.clear_cache()
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    monkeypatch.setattr(
        "app.services.rag.source_store.get_settings",
        lambda: get_settings().model_copy(update={"rag_source_dir": str(empty_dir)}),
    )
    try:
        evidence = RetrievalService.retrieve(
            RetrievalQuery(text="khai sinh", procedure_id="dang-ky-khai-sinh")
        )
        assert evidence.is_grounded is False
        assert evidence.chunks == []
    finally:
        RetrievalService.clear_cache()


@requires_source_data
def test_keyword_mode_still_works(monkeypatch):
    """Tat dense embedding: keyword-only phai van tra ket qua dung."""
    RetrievalService.clear_cache()
    original = get_settings()
    monkeypatch.setattr(
        "app.services.rag.retrieval.get_settings",
        lambda: original.model_copy(update={"rag_retrieval_mode": "keyword"}),
    )
    monkeypatch.setattr(
        "app.services.rag.embedding.get_settings",
        lambda: original.model_copy(update={"rag_retrieval_mode": "keyword"}),
    )
    try:
        candidates = RetrievalService.recommend_procedure("đăng ký khai sinh", top_k=1)
        assert candidates
        assert candidates[0].procedure_id == "dang-ky-khai-sinh"
    finally:
        RetrievalService.clear_cache()
