# Context Pack — local-20260718-rag-llm-guardrail

> Dùng cho task có code, API, data, config, demo hoặc `risk:shared`. Không ghi secret, dữ liệu nhạy cảm, transcript dài hay bản sao toàn bộ repository.

## Identity

- Task ID: `local-20260718-rag-llm-guardrail`
- Status: `done` (implement + verify-demo local hoàn tất; chưa publish)
- Owner tạm thời: Cursor (thực hiện theo yêu cầu người dùng hiện tại)
- Mode hiện tại: `verify-demo`
- Base ref / commit: `main` (nội dung backend tương đương `origin/dev`)
- Branch / worktree: `feature/rag-llm-guardrail-local-20260718` (branch cục bộ, không tạo worktree riêng vì chỉ một implementer đang chạm scope này)

## Mục tiêu và ranh giới

- Mục tiêu: Implement ba năng lực **RAG (Retrieval)**, **LLM Gateway** và **Guardrail (PII Guard + Trust Policy)** trong `backend/` theo `docs/proposal.md` mục 5 và `docs/diagram_v3.mmd`, thay phần mock heuristic hiện tại bằng pipeline có retrieval + grounding + citation + fail-closed.
- Non-goals: Không đổi Rule Engine deterministic (`validation_service.py` field/cross-field logic hiện có do lane Backend/rules sở hữu), không build Neon/pgvector thật (vẫn `TBD`/`Proposed` theo D-005/PROJECT_CONTEXT), không đổi Frontend, không đổi public REST contract (giữ nguyên request/response schema hiện có), không tự thêm long-term `CaseSnapshot`/S1 (out of scope theo proposal mục 6).
- Acceptance criteria:
  - RAG: có source store + retrieval hybrid (keyword + lexical scoring) chạy in-process trên `data/Data_DVC`, filter theo 3 procedure MVP, trả về evidence + citation + freshness + confidence; không đưa PII/chat memory vào index.
  - LLM: provider-neutral gateway (OpenAI-compatible qua `AI_PROVIDER/AI_MODEL/AI_API_KEY/AI_BASE_URL`), structured output (JSON), có fallback an toàn (không hallucinate) khi thiếu API key.
  - Guardrail: PII Guard tokenize/detokenize direct identifiers in-memory theo session (không log/lưu raw), Trust Policy quyết định `verified_guidance` / `need_more_information` / `official_review_required` và enforce citation bắt buộc (fail closed khi thiếu evidence).
  - Wiring: `intake.py`, `procedures.py` (checklist) dùng RAG+LLM+Guardrail thay mock; `validation_service.py` có thể dùng LLM để diễn giải finding (không đổi verdict) qua Guardrail, response schema giữ nguyên field.
  - `python scripts/ci/validate_repo.py` pass; các unit test mới cho PII Guard, Retrieval, Trust Policy chạy được bằng `pytest`.
- Constraints: chính sách repo (`AGENTS.md`, `TEAM_PROTOCOL.md`, D-001..D-005) là baseline. Không thêm dependency native nặng (theo rủi ro P0 trong `PROJECT_CONTEXT.md`); ưu tiên pure-Python cho retrieval để chạy độc lập không cần build toolchain.
- Stop condition / blocker cần hỏi peer: Nếu cần đổi public REST schema (`docs/ai/ARCHITECTURE.md`), cần thêm dependency nặng/service ngoài (Neon/pgvector thật), hoặc cần API key thật cho provider — dừng và hỏi trước khi tiếp tục.

## Scope đã claim

- Files/areas được phép chạm:
  - `backend/app/services/rag/**` (mới)
  - `backend/app/services/llm/**` (mới)
  - `backend/app/services/guardrail/**` (mới)
  - `backend/app/services/procedure_service.py`, `backend/app/services/validation_service.py` (wiring, không đổi schema public)
  - `backend/app/routers/intake.py`, `backend/app/routers/procedures.py`, `backend/app/routers/validation.py` (wiring)
  - `backend/app/config.py`, `backend/requirements.txt`
  - `backend/tests/**` (mới)
  - `docs/ai/DECISIONS.md`, `docs/ai/PROJECT_CONTEXT.md` (append/update nếu có quyết định kỹ thuật liên lane)
- API, schema hoặc contract liên quan: `/v1/intake/turn`, `/v1/procedures/{id}/checklist`, `/v1/applications/validate` — giữ nguyên request/response Pydantic schema, chỉ đổi nội dung/logic bên trong.
- Không được chạm: `frontend/**`, `data/Data_DVC/**` (chỉ đọc, không sửa/ghi), `docs/proposal.md`, các Task Record/Context Pack khác.
- Risk: `shared` (đổi behavior của API dùng chung + thêm dependency cấu hình AI provider).
- Decision Log liên quan: D-005 (đã accepted); đề xuất thêm D-006 cho lựa chọn kỹ thuật RAG/LLM/Guardrail (xem `DECISIONS.md`).

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Kiến trúc đề xuất | `docs/proposal.md` mục 5, 6 | Contract của RAG lifecycle, LLM Gateway, PII Guard, Trust Policy, memory boundary |
| Sequence diagram | `docs/diagram_v3.mmd` | Thứ tự gọi PII Guard tokenize -> LLM -> detokenize; log chỉ lưu bản redacted |
| Kiến trúc tối thiểu | `docs/ai/ARCHITECTURE.md` | API routes hiện có, contract phải giữ nguyên |
| Project context | `docs/ai/PROJECT_CONTEXT.md` | MVP, non-goals, rủi ro P0 (không dependency native nặng), lệnh chạy/test |
| Decision Log | `docs/ai/DECISIONS.md` D-005 | Stack FastAPI/Next.js đã accepted; AI/provider vẫn Proposed |
| Data nguồn thật | `data/Data_DVC/*.txt` (4288 files, format `Tên thủ tục:`/`Trình tự thực hiện:`/`Thành phần hồ sơ:`/`Căn cứ pháp lý:`) | Nguồn RAG cho 3 MVP pack (khớp chính xác "Thủ tục đăng ký khai sinh", "Đăng ký thường trú", "Đăng ký thành lập hộ kinh doanh") |
| Backend hiện có | `backend/app/models/*.py`, `backend/app/routers/*.py`, `backend/app/services/*.py` | Contract/schema hiện tại cần giữ tương thích |

## Dependencies và resource claim

- Depends on / blocked by: Không có (dùng lại D-005 scaffold).
- Shared resource: `none` (không dùng port/DB/account mới; không cần API key thật để demo chạy — có fallback offline).
- Claim owner + thời hạn: Cursor, trong phạm vi session task này.
- Cách thông báo peer và điều kiện release: Cập nhật Task Record sang `handoff`/`done` khi xong; release claim ngay khi hoàn tất.

## Kiểm chứng và handoff

- Commands / manual checks:
  - `pytest` (chạy tại `backend/`, dùng `backend/pytest.ini`) → 30 passed.
  - `python scripts/ci/validate_repo.py --staged` (sau khi `git add` scope của task) → `Repository guard passed`. (Chạy mặc định không `--staged` fail do lỗi trailing-whitespace có sẵn trong `data/Data_DVC/*.txt`, nằm ngoài scope claim của task này, không do task này gây ra.)
  - `uvicorn main:app --port 8010` (từ `backend/`) + `curl` smoke cho `/health`, `/v1/intake/turn`, `/v1/procedures/{id}/checklist`, `/v1/applications/validate` → tất cả trả 200, có citation thật từ `data/Data_DVC`, verdict rule engine giữ nguyên.
- Demo impact và rollback: Nếu lỗi, rollback bằng `git checkout main -- backend/app/services/rag backend/app/services/llm backend/app/services/guardrail backend/app/services/intake_service.py backend/app/services/procedure_service.py backend/app/services/validation_service.py backend/app/routers/intake.py backend/app/config.py`. Router vẫn có fallback deterministic nếu RAG/LLM lỗi hoặc thiếu `AI_API_KEY` (fail closed, không hallucinate).
- Evidence / kết quả:
  - RAG: `RetrievalService` nạp 3 pack MVP thật từ `data/Data_DVC` (allowlist theo tên thủ tục chính xác), hybrid lexical retrieval pure-Python, top-1 procedure identification đúng cho cả 3 pack trong test + smoke.
  - LLM: `LLMGateway` provider-neutral qua `openai` SDK, có fallback deterministic khi thiếu `AI_API_KEY` (mặc định môi trường demo).
  - Guardrail: `PIIGuard` tokenize/detokenize field-level theo session (token có salt theo session, TTL cấu hình), `TrustPolicy` fail-closed (thiếu evidence/citation -> `official_review_required`), `RedactedAudit` chỉ log bản đã redact.
  - `/v1/intake/turn`, `/v1/procedures/{id}/checklist`, `/v1/applications/validate` giữ nguyên public schema, chỉ đổi logic bên trong; `validation_service.py` giữ nguyên verdict rule engine, LLM chỉ diễn giải khi online.
- Files, API và resources đã chạm:
  - Mới: `backend/app/services/rag/**`, `backend/app/services/llm/**`, `backend/app/services/guardrail/**`, `backend/app/services/intake_service.py`, `backend/tests/**`, `backend/pytest.ini`.
  - Sửa: `backend/app/config.py`, `backend/app/routers/intake.py`, `backend/app/services/procedure_service.py`, `backend/app/services/validation_service.py`, `docs/ai/DECISIONS.md` (thêm D-006, `Proposed`).
  - Không đổi: public request/response schema trong `backend/app/models/*.py`, `frontend/**`, `data/Data_DVC/**` (chỉ đọc).
- Claims đã release: Toàn bộ files/areas đã claim được release; task chuyển `done`. D-006 vẫn `Proposed` — cần một peer khác xác nhận để chuyển `Accepted` khi có người online (roster hiện `TBD`).
- Việc tiếp theo hoặc peer có thể tiếp nhận:
  - Rule Engine mở rộng field/cross-field rules cho `dang-ky-thuong-tru` và `dang-ky-ho-kinh-doanh` (hiện chỉ có rule tối thiểu như cũ).
  - K1 review nội dung checklist tự sinh từ RAG cho 2 pack đó trước khi coi là `approved` chính thức (hiện là deterministic parser trên nguồn thật, chưa qua human review nghiệp vụ).
  - Xác nhận D-006 với một peer, hoặc mở lại nếu team quyết định dùng Neon/pgvector thật.
  - Cấu hình `AI_PROVIDER/AI_MODEL/AI_API_KEY/AI_BASE_URL` thật khi có quyết định provider (không cần đổi code).
