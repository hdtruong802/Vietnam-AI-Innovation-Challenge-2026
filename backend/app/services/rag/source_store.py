"""Source registry + staging cho RAG (xem 'RAG lifecycle' trong docs/proposal.md).

Nap va parse cac ban ghi thu tuc hanh chinh tu data/Data_DVC (nguon
dichvucong.gov.vn theo Note trong docs/diagram_v3.mmd), loc theo allowlist
cua 3 procedure pack MVP, roi chia thanh cac EvidenceChunk theo section.

Day la structured procedure store toi gian: khong dung DB ben ngoai (Neon/
pgvector van dang `TBD`/`Proposed` theo D-005 va D-006), chi doc file .txt
mot lan khi khoi dong process va giu trong memory.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from app.config import get_settings

_TOP_LEVEL_FIELDS = [
    "Mã thủ tục",
    "Số quyết định",
    "Tên thủ tục",
    "Cấp thực hiện",
    "Loại thủ tục",
    "Lĩnh vực",
    "Trình tự thực hiện",
    "Cách thức thực hiện",
    "Thành phần hồ sơ",
    "Đối tượng thực hiện",
    "Cơ quan thực hiện",
    "Cơ quan có thẩm quyền",
    "Địa chỉ tiếp nhận HS",
    "Cơ quan được ủy quyền",
    "Cơ quan phối hợp",
    "Kết quả thực hiện",
    "Căn cứ pháp lý",
    "Yêu cầu, điều kiện thực hiện",
    "Từ khóa",
    "Mô tả",
]

_HEADER_RE = re.compile(r"^(" + "|".join(re.escape(f) for f in _TOP_LEVEL_FIELDS) + r"):\s*(.*)$")

# Candidate allowlist cua 3 procedure pack MVP. Ten va ma thu tuc deu phai
# khop chinh xac; allowlist khong co nghia la noi dung da qua K1.
# khop pham vi de bai (trong nuoc, cap xa/huyen), khong suy dien theo
# keyword long leo (rat nhieu ban ghi "thuong tru" trong dataset la ho chieu/
# tam tru cua nguoi nuoc ngoai/phong vien, khong thuoc pham vi MVP).
PROCEDURE_ALLOWLIST: Dict[str, List[str]] = {
    "dang-ky-khai-sinh": [
        "Thủ tục đăng ký khai sinh",
    ],
    "dang-ky-thuong-tru": [
        "Đăng ký thường trú",
    ],
    "dang-ky-ho-kinh-doanh": [
        "Đăng ký thành lập hộ kinh doanh",
    ],
}

PROCEDURE_SOURCE_CODES: Dict[str, set[str]] = {
    "dang-ky-khai-sinh": {"1.001193"},
    "dang-ky-thuong-tru": {"1.004222"},
    "dang-ky-ho-kinh-doanh": {"1.001612"},
}

PROCEDURE_DISPLAY_NAME: Dict[str, str] = {
    "dang-ky-khai-sinh": "Đăng ký khai sinh",
    "dang-ky-thuong-tru": "Đăng ký thường trú",
    "dang-ky-ho-kinh-doanh": "Đăng ký thành lập hộ kinh doanh",
}


def strip_diacritics(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    folded = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return folded.replace("đ", "d").replace("Đ", "D")


def normalize_name(name: str) -> str:
    return strip_diacritics(name).lower().strip()


@dataclass
class SubmissionMethodRow:
    """Mot dong 'bang' trong Cach thuc thuc hien: 1 hinh thuc nop = 1 record
    rieng (phi/thoi han giai quyet khac nhau theo hinh thuc), khong duoc
    flatten chung mot doan text (xem ly do trong docs/ai/DECISIONS.md)."""

    method: str
    processing_time: str = ""
    fee: str = ""
    description: str = ""


@dataclass
class DocumentRow:
    """Mot dong 'bang' trong Thanh phan ho so: giu rieng ten giay to, nhom
    dieu kien ap dung (`[ Truong hop ... ]` trong nguon) va so luong ban
    chinh/ban sao — khong glom chung vao 1 doan text nhu truoc."""

    name: str
    group: str = ""
    original_copies: str = ""
    duplicate_copies: str = ""


_SUBMISSION_METHOD_RE = re.compile(r"^\*\s*Hình thức nộp:\s*(.*)$")
_PROCESSING_TIME_RE = re.compile(r"^Thời hạn giải quyết:\s*(.*)$")
_FEE_RE = re.compile(r"^Phí,\s*lệ phí:\s*(.*)$")
_METHOD_DESCRIPTION_RE = re.compile(r"^Mô tả:\s*(.*)$")
_DOC_GROUP_RE = re.compile(r"^\[\s*(.*?)\s*\]$")
_DOC_ITEM_RE = re.compile(r"^-\s*(.*)$")
_DOC_QUANTITY_RE = re.compile(r"^Số lượng:\s*Bản chính:\s*(\d+),\s*Bản sao:\s*(\d+)$")


def parse_submission_methods(raw: str) -> List[SubmissionMethodRow]:
    """Parse 'Cách thức thực hiện' thanh danh sach row-level (method/thoi
    han/phi), khong con la 1 doan text tho nhu SourceRecord.submission_methods."""

    rows: List[SubmissionMethodRow] = []
    current: Optional[SubmissionMethodRow] = None
    current_field: Optional[str] = None

    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        method_match = _SUBMISSION_METHOD_RE.match(line)
        if method_match:
            if current is not None:
                rows.append(current)
            current = SubmissionMethodRow(method=method_match.group(1).strip())
            current_field = None
            continue
        if current is None:
            continue
        time_match = _PROCESSING_TIME_RE.match(line)
        if time_match:
            current.processing_time = time_match.group(1).strip()
            current_field = "processing_time"
            continue
        fee_match = _FEE_RE.match(line)
        if fee_match:
            current.fee = fee_match.group(1).strip()
            current_field = "fee"
            continue
        desc_match = _METHOD_DESCRIPTION_RE.match(line)
        if desc_match:
            current.description = desc_match.group(1).strip()
            current_field = "description"
            continue
        # Dong tiep tuc (van ban dai bi wrap khong co tien to field) noi vao
        # dung field dang parse, tranh lac mat thong tin phi/mo ta dai.
        if current_field == "fee":
            current.fee = f"{current.fee} {line}".strip()
        elif current_field == "description":
            current.description = f"{current.description} {line}".strip()

    if current is not None:
        rows.append(current)
    return rows


def parse_documents(raw: str) -> List[DocumentRow]:
    """Parse 'Thành phần hồ sơ' thanh danh sach row-level, giu nguyen nhom
    dieu kien `[ ... ]` va so luong ban chinh/ban sao thanh field rieng
    (thay vi glom chung vao description nhu truoc)."""

    rows: List[DocumentRow] = []
    current_group = ""
    current: Optional[DocumentRow] = None

    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        group_match = _DOC_GROUP_RE.match(line)
        if group_match:
            current_group = group_match.group(1).strip()
            continue
        item_match = _DOC_ITEM_RE.match(line)
        if item_match:
            if current is not None:
                rows.append(current)
            current = DocumentRow(name=item_match.group(1).strip(), group=current_group)
            continue
        if current is None:
            continue
        qty_match = _DOC_QUANTITY_RE.match(line)
        if qty_match:
            current.original_copies = qty_match.group(1)
            current.duplicate_copies = qty_match.group(2)
            continue
        # Dong tiep tuc (ten giay to dai bi wrap) noi vao ten hien tai.
        current.name = f"{current.name} {line}".strip()

    if current is not None:
        rows.append(current)
    return rows


@dataclass
class SourceRecord:
    """Ban ghi thu tuc da parse, truoc khi chia chunk."""

    file_name: str
    procedure_code: str
    decision_no: str
    name: str
    level: str
    field_area: str
    steps: str
    submission_methods: str
    documents: str
    beneficiaries: str
    implementing_org: str
    authority_org: str
    result: str
    legal_basis_raw: str
    requirements: str
    keywords: str
    description: str
    legal_basis: List[Dict[str, str]] = field(default_factory=list)
    submission_method_rows: List[SubmissionMethodRow] = field(default_factory=list)
    document_rows: List[DocumentRow] = field(default_factory=list)


def _parse_legal_basis(raw: str) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("*"):
            continue
        line = line.lstrip("*").strip()
        match = re.match(r"^(.*)\(([^()]+)\)\s*$", line)
        if match:
            title, ref_code = match.group(1).strip(), match.group(2).strip()
        else:
            title, ref_code = line, ""
        if title:
            entries.append({"title": title, "ref_code": ref_code or title})
    return entries


def parse_source_file(path: Path) -> Optional[SourceRecord]:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None

    sections: Dict[str, List[str]] = {f: [] for f in _TOP_LEVEL_FIELDS}
    current_field: Optional[str] = None

    for line in raw_text.splitlines():
        header_match = _HEADER_RE.match(line)
        if header_match:
            current_field = header_match.group(1)
            remainder = header_match.group(2)
            if remainder:
                sections[current_field].append(remainder)
            continue
        if current_field is not None:
            sections[current_field].append(line)

    name = "\n".join(sections["Tên thủ tục"]).strip()
    if not name:
        return None

    legal_basis_raw = "\n".join(sections["Căn cứ pháp lý"]).strip()
    submission_methods_raw = "\n".join(sections["Cách thức thực hiện"]).strip()
    documents_raw = "\n".join(sections["Thành phần hồ sơ"]).strip()

    return SourceRecord(
        file_name=path.name,
        procedure_code="\n".join(sections["Mã thủ tục"]).strip(),
        decision_no="\n".join(sections["Số quyết định"]).strip(),
        name=name,
        level="\n".join(sections["Cấp thực hiện"]).strip(),
        field_area="\n".join(sections["Lĩnh vực"]).strip(),
        steps="\n".join(sections["Trình tự thực hiện"]).strip(),
        submission_methods=submission_methods_raw,
        documents=documents_raw,
        beneficiaries="\n".join(sections["Đối tượng thực hiện"]).strip(),
        implementing_org="\n".join(sections["Cơ quan thực hiện"]).strip(),
        authority_org="\n".join(sections["Cơ quan có thẩm quyền"]).strip(),
        result="\n".join(sections["Kết quả thực hiện"]).strip(),
        legal_basis_raw=legal_basis_raw,
        requirements="\n".join(sections["Yêu cầu, điều kiện thực hiện"]).strip(),
        keywords="\n".join(sections["Từ khóa"]).strip(),
        description="\n".join(sections["Mô tả"]).strip(),
        legal_basis=_parse_legal_basis(legal_basis_raw),
        submission_method_rows=parse_submission_methods(submission_methods_raw),
        document_rows=parse_documents(documents_raw),
    )


@lru_cache(maxsize=1)
def load_candidate_records(
    source_dir: Optional[str] = None,
) -> Dict[str, List[SourceRecord]]:
    """Nap source candidate theo ten va ma canonical, chua gan trang thai K1."""

    base_dir = Path(source_dir) if source_dir else get_settings().rag_source_path
    name_to_procedure: Dict[str, str] = {}
    for procedure_id, names in PROCEDURE_ALLOWLIST.items():
        for allowed_name in names:
            name_to_procedure[normalize_name(allowed_name)] = procedure_id

    result: Dict[str, List[SourceRecord]] = {pid: [] for pid in PROCEDURE_ALLOWLIST}

    if not base_dir.exists():
        return result

    for path in base_dir.glob("*.txt"):
        record = parse_source_file(path)
        if record is None:
            continue
        procedure_id = name_to_procedure.get(normalize_name(record.name))
        if procedure_id is None:
            continue
        if record.procedure_code not in PROCEDURE_SOURCE_CODES[procedure_id]:
            continue
        result[procedure_id].append(record)

    return result


def get_source_freeze_date() -> str:
    return get_settings().rag_source_freeze_date
