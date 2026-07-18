# Context Pack — local-20260717-refactor-backend

> Dùng cho task có code, API, data, config, demo hoặc `risk:shared`. Không ghi secret, dữ liệu nhạy cảm, transcript dài hay bản sao toàn bộ repository.

## Identity

- Task ID: `local-20260717-refactor-backend`
- Status: `done`
- Owner tạm thời: Antigravity
- Mode hiện tại: `verify-demo`
- Base ref / commit: a677c7c
- Branch / worktree: `cao`


## Mục tiêu và ranh giới

- Mục tiêu: Tái cấu trúc thư mục `backend/` thành các mô-đun riêng biệt (models, routers, services, config) và giữ root `backend/main.py` làm entrypoint để đảm bảo tính tương thích.
- Non-goals: Viết thêm tính năng nghiệp vụ mới hoặc đổi cổng chạy local.
- Acceptance criteria:
  - Cấu trúc thư mục `backend/app/` hoàn chỉnh.
  - Chạy `python scripts/ci/validate_repo.py` không gặp lỗi trailing whitespaces hay link hỏng.
  - Chạy server `uvicorn main:app` tại `backend/` thành công và tất cả API Endpoint hoạt động bình thường.
- Constraints: chính sách repo là baseline.
- Stop condition / blocker cần hỏi peer: Không có.

## Scope đã claim

- Files/areas được phép chạm:
  - Thư mục `backend/` và các file bên trong.
- API, schema hoặc contract liên quan: REST API routes v1.
- Không được chạm: Thư mục `frontend/`.
- Risk: `isolated` (do chỉ tái cấu trúc mã nguồn nội bộ backend, không đổi API contract).
- Decision Log liên quan: D-005

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Root main.py | `backend/main.py` | Lấy toàn bộ code cũ để phân bổ vào các tệp mới |

## Dependencies và resource claim

- Depends on / blocked by: None
- Shared resource: none
- Claim owner + thời hạn: Antigravity + trong task session này.
- Cách thông báo peer và điều kiện release: Hoàn thành task và chuyển trạng thái sang `done`.

## Kiểm chứng và handoff

- Commands / manual checks:
  - `python scripts/ci/validate_repo.py` -> ĐẠT (Repository guard passed)
  - `python -m uvicorn main:app --port 8000` -> ĐẠT (Uvicorn starts successfully and serves routes properly)
- Demo impact và rollback: Reset git commit.
- Evidence / kết quả: Backend đã được tách biệt thành công thành các modules: app/config, app/models, app/routers, app/services.
- Files, API và resources đã chạm:
  - Thư mục `backend/` và các thư mục/file con bên trong.
- Claims đã release: Đã giải phóng toàn bộ files/resources đã claim.
- Việc tiếp theo hoặc peer có thể tiếp nhận: Phát triển logic validation hoàn chỉnh cho 3 thủ tục.
