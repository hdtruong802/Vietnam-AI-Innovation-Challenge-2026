from __future__ import annotations

from app.models.procedure import ProcedureSummary, ReviewStatus

CANONICAL_PROCEDURES: tuple[ProcedureSummary, ...] = (
    ProcedureSummary(
        procedure_id="dang-ky-khai-sinh",
        name="Đăng ký khai sinh",
        review_status=ReviewStatus.UNAVAILABLE,
    ),
    ProcedureSummary(
        procedure_id="dang-ky-thuong-tru",
        name="Đăng ký thường trú",
        review_status=ReviewStatus.UNAVAILABLE,
    ),
    ProcedureSummary(
        procedure_id="dang-ky-ho-kinh-doanh",
        name="Đăng ký thành lập hộ kinh doanh",
        review_status=ReviewStatus.UNAVAILABLE,
    ),
)


def is_known_procedure(procedure_id: str) -> bool:
    return any(item.procedure_id == procedure_id for item in CANONICAL_PROCEDURES)
