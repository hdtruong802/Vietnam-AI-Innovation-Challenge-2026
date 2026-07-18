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

# Allowlist cua 3 procedure pack MVP: chi lay dung ten thu tuc da xac minh
# khop pham vi de bai (trong nuoc, cap xa/huyen), khong suy dien theo
# keyword long leo (rat nhieu ban ghi "thuong tru" trong dataset la ho chieu/
# tam tru cua nguoi nuoc ngoai/phong vien, khong thuoc pham vi MVP).
PROCEDURE_ALLOWLIST: Dict[str, List[str]] = {
    "dang-ky-khai-sinh": [
        "Thủ tục đăng ký khai sinh",
        "Thủ tục đăng ký lại khai sinh",
        "Thủ tục đăng ký khai sinh lưu động",
        "Thủ tục đăng ký khai sinh kết hợp đăng ký nhận cha, mẹ, con",
    ],
    "dang-ky-thuong-tru": [
        "Đăng ký thường trú",
        "Khai báo thông tin về cư trú đối với người chưa đủ điều kiện đăng ký thường trú, đăng ký tạm trú",
        "Xác nhận về điều kiện diện tích bình quân nhà ở để đăng ký thường trú vào chỗ ở do thuê, mượn, ở nhờ; nhà ở, đất ở không có tranh chấp quyền sở hữu nhà ở, quyền sử dụng đất ở, không thuộc địa điểm không được đăng ký thường trú mới",
    ],
    "dang-ky-ho-kinh-doanh": [
        "Đăng ký thành lập hộ kinh doanh",
    ],
}

PROCEDURE_DISPLAY_NAME: Dict[str, str] = {
    "dang-ky-khai-sinh": "Đăng ký khai sinh",
    "dang-ky-thuong-tru": "Đăng ký thường trú",
    "dang-ky-ho-kinh-doanh": "Đăng ký thành lập hộ kinh doanh",
}


def strip_diacritics(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_name(name: str) -> str:
    return strip_diacritics(name).lower().strip()


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
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
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

    return SourceRecord(
        file_name=path.name,
        procedure_code="\n".join(sections["Mã thủ tục"]).strip(),
        decision_no="\n".join(sections["Số quyết định"]).strip(),
        name=name,
        level="\n".join(sections["Cấp thực hiện"]).strip(),
        field_area="\n".join(sections["Lĩnh vực"]).strip(),
        steps="\n".join(sections["Trình tự thực hiện"]).strip(),
        submission_methods="\n".join(sections["Cách thức thực hiện"]).strip(),
        documents="\n".join(sections["Thành phần hồ sơ"]).strip(),
        beneficiaries="\n".join(sections["Đối tượng thực hiện"]).strip(),
        implementing_org="\n".join(sections["Cơ quan thực hiện"]).strip(),
        authority_org="\n".join(sections["Cơ quan có thẩm quyền"]).strip(),
        result="\n".join(sections["Kết quả thực hiện"]).strip(),
        legal_basis_raw=legal_basis_raw,
        requirements="\n".join(sections["Yêu cầu, điều kiện thực hiện"]).strip(),
        keywords="\n".join(sections["Từ khóa"]).strip(),
        description="\n".join(sections["Mô tả"]).strip(),
        legal_basis=_parse_legal_basis(legal_basis_raw),
    )


@lru_cache(maxsize=1)
def load_approved_records(
    source_dir: Optional[str] = None,
) -> Dict[str, List[SourceRecord]]:
    """Nap va loc source theo allowlist. Ket qua duoc cache trong process
    (tuong duong 'Approved release' step trong RAG lifecycle) vi day la
    tap tin tinh, khong doi trong luc server chay.
    """

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
        result[procedure_id].append(record)

    return result


def get_source_freeze_date() -> str:
    return get_settings().rag_source_freeze_date
