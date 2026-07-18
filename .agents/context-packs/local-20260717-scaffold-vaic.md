# Context Pack — local-20260717-scaffold-vaic

> Dùng cho task có code, API, data, config, demo hoặc `risk:shared`. Không ghi secret, dữ liệu nhạy cảm, transcript dài hay bản sao toàn bộ repository.

## Identity

- Task ID: `local-20260717-scaffold-vaic`
- Status: `done`
- Owner tạm thời: Antigravity
- Mode hiện tại: `verify-demo`
- Base ref / commit: a677c7c
- Branch / worktree: `cao`


## Mục tiêu và ranh giới

- Mục tiêu: Khởi tạo khung dự án (scaffold) gồm backend FastAPI và frontend Next.js, tạo checklist tasks.txt và cập nhật các tài liệu AI context.
- Non-goals: Cài đặt CSDL thật (pgvector/Postgres), deploy lên cloud, hoặc tích hợp API của LLM thật.
- Acceptance criteria:
  - Có thư mục `backend/` chạy được FastAPI với lệnh local.
  - Có thư mục `frontend/` chạy được Next.js với lệnh local.
  - Có file `tasks.txt` chứa danh sách việc cần làm.
  - Cập nhật `PROJECT_CONTEXT.md`, `ARCHITECTURE.md`, `DECISIONS.md`.
  - Check repo bằng `validate_repo.py` chạy thành công.
- Constraints: policy repo là baseline.
- Stop condition / blocker cần hỏi peer: Không có.

## Scope đã claim

- Files/areas được phép chạm:
  - Thư mục `backend/`
  - Thư mục `frontend/`
  - `docs/ai/PROJECT_CONTEXT.md`
  - `docs/ai/ARCHITECTURE.md`
  - `docs/ai/DECISIONS.md`
  - `tasks.txt`
- API, schema hoặc contract liên quan: REST API routes defined in proposal.md.
- Không được chạm: Các files/thư mục khác ngoài scope.
- Risk: `shared` (vì cập nhật cấu hình/kiến trúc dùng chung).
- Decision Log liên quan: `D-005`

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Project context | `docs/proposal.md` | Lấy danh sách REST API routes và cấu trúc đề xuất |
| Architecture / decision | `docs/ai/TEAM_PROTOCOL.md` | Quy chuẩn đặt tên, mode và quy trình check |

## Dependencies và resource claim

- Depends on / blocked by: None
- Shared resource: `none`
- Claim owner + thời hạn: Antigravity + trong task session này.
- Cách thông báo peer và điều kiện release: Hoàn thành task và chuyển trạng thái sang `done`.

## Kiểm chứng và handoff

- Commands / manual checks:
  - `python scripts/ci/validate_repo.py` -> Đạt (Repository guard passed)
  - `python -m uvicorn backend.main:app` -> Đạt (Uvicorn running on http://127.0.0.1:8000)
  - `npm run build` tại `frontend/` -> Đạt (Compiled successfully and generated static pages)
- Demo impact và rollback: Khởi tạo mới nên rủi ro thấp.
- Evidence / kết quả: Khung xương ứng dụng backend (FastAPI) và frontend (Next.js) đã chạy ổn định cục bộ.
- Files, API và resources đã chạm:
  - `backend/requirements.txt`
  - `backend/main.py`
  - Thư mục `frontend/`
  - `docs/ai/PROJECT_CONTEXT.md`
  - `docs/ai/ARCHITECTURE.md`
  - `docs/ai/DECISIONS.md`
  - `tasks.txt`
- Claims đã release: Đã release toàn bộ files/resources đã claim.
- Việc tiếp theo hoặc peer có thể tiếp nhận: Viết schema chi tiết cho 3 procedure packs và cấu hình sqlite/postgres vector database.
