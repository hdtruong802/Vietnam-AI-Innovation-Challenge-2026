"""Unit test cho table parser cua RAG source (xem docs/ai/DECISIONS.md).

Dung du lieu synthetic (khong phu thuoc data/Data_DVC thuc) de kiem tra
deterministic parser khong bi mat phi/thoi han/nhom dieu kien khi source
that thay doi format nhe.
"""

from app.services.rag.chunking import build_chunks
from app.services.rag.source_store import (
    DocumentRow,
    SourceRecord,
    parse_documents,
    parse_submission_methods,
)

_SUBMISSION_METHODS_RAW = """
  * Hình thức nộp: ONLINE
    Thời hạn giải quyết: 7 WORKING_DAY
    Phí, lệ phí: 10000 VNĐ (Nộp qua cổng dịch vụ công)
  * Hình thức nộp: DIRECT
    Thời hạn giải quyết: 7 WORKING_DAY
    Phí, lệ phí: 20000 VNĐ (Nộp trực tiếp)
    Mô tả: Nộp tại bộ phận một cửa
"""

_DOCUMENTS_RAW = """
  [ Trường hợp đăng ký vào chỗ ở thuộc quyền sở hữu của mình ]
    - Giấy chứng nhận quyền sử dụng đất
      Số lượng: Bản chính: 1, Bản sao: 0
  [ Trường hợp đăng ký vào chỗ ở do thuê, mượn, ở nhờ ]
    - Hợp đồng thuê nhà được công chứng
      Số lượng: Bản chính: 1, Bản sao: 1
    - Văn bản đồng ý của chủ nhà tiếp tục nội dung dài bị wrap xuống dòng
      Số lượng: Bản chính: 0, Bản sao: 1
"""


def test_parse_submission_methods_keeps_fee_and_processing_time_per_row():
    rows = parse_submission_methods(_SUBMISSION_METHODS_RAW)

    assert len(rows) == 2
    online, direct = rows
    assert online.method == "ONLINE"
    assert online.processing_time == "7 WORKING_DAY"
    assert online.fee == "10000 VNĐ (Nộp qua cổng dịch vụ công)"
    assert direct.method == "DIRECT"
    assert direct.fee == "20000 VNĐ (Nộp trực tiếp)"
    assert direct.description == "Nộp tại bộ phận một cửa"


def test_parse_submission_methods_empty_input_returns_empty_list():
    assert parse_submission_methods("") == []
    assert parse_submission_methods("Không có thông tin") == []


def test_parse_documents_keeps_group_and_quantity_as_separate_fields():
    rows = parse_documents(_DOCUMENTS_RAW)

    assert len(rows) == 3
    assert rows[0].group == "Trường hợp đăng ký vào chỗ ở thuộc quyền sở hữu của mình"
    assert rows[0].name == "Giấy chứng nhận quyền sử dụng đất"
    assert rows[0].original_copies == "1"
    assert rows[0].duplicate_copies == "0"

    assert rows[1].group == "Trường hợp đăng ký vào chỗ ở do thuê, mượn, ở nhờ"
    assert rows[1].original_copies == "1"
    assert rows[1].duplicate_copies == "1"

    # Dong wrap khong co tien to "-" phai duoc noi vao ten cua row truoc do,
    # khong bi tach thanh row moi hoac bi mat.
    assert "nội dung dài bị wrap xuống dòng" in rows[2].name


def _make_record(**overrides) -> SourceRecord:
    base = dict(
        file_name="test.txt",
        procedure_code="1.000000",
        decision_no="",
        name="Thủ tục kiểm thử",
        level="",
        field_area="",
        steps="",
        submission_methods="",
        documents="",
        beneficiaries="",
        implementing_org="",
        authority_org="",
        result="",
        legal_basis_raw="",
        requirements="",
        keywords="",
        description="",
    )
    base.update(overrides)
    return SourceRecord(**base)


def test_build_chunks_emits_row_level_chunk_per_submission_method_and_document():
    record = _make_record(
        implementing_org="Ủy ban nhân dân cấp xã",
        authority_org="Ủy ban nhân dân cấp xã",
        submission_method_rows=parse_submission_methods(_SUBMISSION_METHODS_RAW),
        document_rows=parse_documents(_DOCUMENTS_RAW),
    )

    chunks = build_chunks("test-procedure", [record])
    sections = {c.section: [c for c in chunks if c.section == c.section] for c in chunks}

    method_chunks = [c for c in chunks if c.section == "Cách thức thực hiện"]
    document_chunks = [c for c in chunks if c.section == "Thành phần hồ sơ"]
    org_chunks = [c for c in chunks if c.section in ("Cơ quan thực hiện", "Cơ quan có thẩm quyền")]

    assert len(method_chunks) == 2
    assert any("10000" in c.text for c in method_chunks)
    assert any("20000" in c.text for c in method_chunks)

    assert len(document_chunks) == 3
    assert any("Áp dụng khi" in c.text for c in document_chunks)
    assert any("Bản chính" in c.text for c in document_chunks)

    assert len(org_chunks) == 2
    assert all(c.chunk_id for c in chunks)
    assert len(sections) > 0


def test_build_chunks_skips_missing_org_and_empty_rows():
    record = _make_record(implementing_org="Không có thông tin")

    chunks = build_chunks("test-procedure", [record])

    assert not any(c.section in ("Cơ quan thực hiện", "Cơ quan có thẩm quyền") for c in chunks)
    assert not any(c.section == "Cách thức thực hiện" for c in chunks)
    assert not any(c.section == "Thành phần hồ sơ" for c in chunks)


def test_document_row_defaults_are_empty_strings():
    row = DocumentRow(name="Giấy tờ mẫu")

    assert row.group == ""
    assert row.original_copies == ""
    assert row.duplicate_copies == ""
