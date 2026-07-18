import pytest

import app.config as config
from app.services.rag.retrieval import RetrievalService
from app.services.rag.schemas import RetrievalQuery
from app.services.rag.source_store import load_approved_records


def _has_source_data() -> bool:
    return config.RAG_SOURCE_DIR.exists() and any(config.RAG_SOURCE_DIR.glob("*.txt"))


requires_source_data = pytest.mark.skipif(
    not _has_source_data(), reason="data/Data_DVC khong ton tai trong moi truong nay"
)


@requires_source_data
def test_load_approved_records_only_contains_allowlisted_packs():
    records = load_approved_records()

    assert set(records.keys()) == {
        "dang-ky-khai-sinh",
        "dang-ky-thuong-tru",
        "dang-ky-ho-kinh-doanh",
    }
    assert len(records["dang-ky-khai-sinh"]) > 0
    assert len(records["dang-ky-thuong-tru"]) > 0
    assert len(records["dang-ky-ho-kinh-doanh"]) > 0


@requires_source_data
@pytest.mark.parametrize(
    "query_text,expected_procedure_id",
    [
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
def test_retrieve_returns_grounded_evidence_with_citations():
    evidence = RetrievalService.retrieve(
        RetrievalQuery(text="giấy chứng sinh thủ tục đăng ký khai sinh", procedure_id="dang-ky-khai-sinh")
    )

    assert evidence.procedure_id == "dang-ky-khai-sinh"
    assert evidence.is_grounded is True
    assert evidence.chunks
    assert evidence.citations
    assert all(c.get("ref_code") for c in evidence.citations)


@requires_source_data
def test_retrieve_unknown_procedure_is_not_grounded():
    evidence = RetrievalService.retrieve(RetrievalQuery(text="bất kỳ", procedure_id="khong-ton-tai"))

    assert evidence.is_grounded is False
    assert evidence.chunks == []


def test_retrieve_with_missing_source_dir_fails_closed(tmp_path):
    RetrievalService.clear_cache()
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    original_dir = config.RAG_SOURCE_DIR
    config.RAG_SOURCE_DIR = empty_dir
    try:
        evidence = RetrievalService.retrieve(
            RetrievalQuery(text="khai sinh", procedure_id="dang-ky-khai-sinh")
        )
        assert evidence.is_grounded is False
        assert evidence.chunks == []
    finally:
        config.RAG_SOURCE_DIR = original_dir
        RetrievalService.clear_cache()
