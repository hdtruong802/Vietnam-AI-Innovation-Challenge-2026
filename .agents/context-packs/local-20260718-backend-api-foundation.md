# Context Pack — local-20260718-backend-api-foundation

> Backend-only implementation for the AI Procedure Copilot. Do not record secrets, real citizen data, raw source payloads, or coding-agent transcripts.

## Identity

- Task ID: `local-20260718-backend-api-foundation`
- Status: `handoff-ready (local, uncommitted)`
- Owner tạm thời: `hdtruong802 / Codex`
- Mode hiện tại: `verify-demo`
- Base ref / commit: `f4827ae`
- Branch / worktree: `feature/local-20260718-backend-api-foundation`
- AI Log member / tool binding / readiness: `hdtruong802 / codex manual / doctor --strict PASS`; prompt candidate được hook ghi evidence khi có commit, không có commit trong task này.

## Mục tiêu và ranh giới

- Mục tiêu: Hoàn thiện backend FastAPI thành API integration-ready cho ba MVP, với contract typed, luồng deterministic, dev fixture an toàn và adapter seams để FE, data, RAG và AI tích hợp sau.
- Non-goals: Xây frontend/widget; thu thập hoặc đọc raw `data/**`; tạo Procedure Pack đã review; xây RAG/vector database; chọn/call model provider; account/long-term memory; provision/deploy/push.
- Acceptance criteria:
  - Có sáu endpoint mục tiêu, error/trust metadata ổn định và OpenAPI có thể bàn giao cho FE.
  - Backend không còn phát `verified_guidance` từ seed/fixture chưa approved.
  - Dev fixture chạy được recommend → intake → checklist → validate nhưng luôn fail closed về trust.
  - Data/RAG/LLM thay bằng adapter qua port mà không sửa router/public contract.
  - Unit, contract, security/fallback tests, formatting, lint và repository guard pass.
- Constraints: FastAPI/Pydantic hiện có là baseline; không thêm provider/vector/database dependency; form/chat chỉ transient; log redacted; canonical IDs giữ nguyên; policy repo áp dụng đầy đủ.
- Stop condition / blocker cần hỏi peer: Dừng nếu cần đổi six-endpoint contract sau khi freeze, bổ sung provider/vector/database/auth/long-term storage, dùng raw data, hoặc phát `verified_guidance` khi chưa có K1 approved release.

## Scope đã claim

- Files/areas được phép chạm: `backend/`, `.env.example`, `docs/api/` (mới), `docs/ai/` chỉ khi contract/handoff cần đồng bộ, `tests/` liên quan backend, Context Pack này; theo chấp thuận publish ngày 18/07/2026, `scripts/ai_log/ai_log.py` và `tests/ai_log/` chỉ để sửa hook commit đang chặn evidence.
- API, schema hoặc contract liên quan: sáu REST endpoint `/v1`, `TrustMetadata`, `SessionContext`, error envelope, ports `ProcedureRepository`, `RecommendationProvider`, `RetrievalProvider`, `LLMProvider`, `AuditSink`.
- Không được chạm: `frontend/`, raw `data/**`, cloud/deploy config, GitHub settings, provider credentials, existing completed Context Packs.
- Risk: `shared`
- Decision Log liên quan: D-005, D-006 (`Proposed`), D-007, D-008, D-009, D-010 (`Proposed`).

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Product scope | `docs/ai/PROJECT_CONTEXT.md` | Ba MVP, trust states, non-goals và public flow. |
| Architecture | `docs/ai/ARCHITECTURE.md` | Backend boundary, ports, PII/memory/fallback và endpoint target. |
| Decisions | `docs/ai/DECISIONS.md` D-005–D-010 | Phân biệt scaffold đã chấp thuận với capability chưa có evidence. |
| Backend baseline | `backend/app/`, `backend/tests/` | Router/model/service hiện có và regression scope. |
| Team ownership | `team_docs/phancong.md` Member 4, G0–G6 | Ranh giới với data, AI, FE và quality lanes. |
| Secrets/data | `docs/ai/SECRETS_AND_DATA.md` | Không dùng PII/raw data, data release và logging policy. |

## Dependencies và resource claim

- Depends on / blocked by: Approved Procedure Pack/release từ Member 1–2; RAG adapter từ Member 2; LLM adapter từ Member 3; FE consumer từ Member 5. Backend phải chạy an toàn trước các dependency này.
- Shared resource: public API/schema và backend source.
- Claim owner + thời hạn: `hdtruong802 / Codex` trong task này; release khi handoff review.
- Cách thông báo peer và điều kiện release: bàn giao OpenAPI, port contracts, test evidence và fallback behavior; peer review trước khi consumer phụ thuộc contract.

## Kiểm chứng và handoff

- Commands / manual checks: `pytest`, `black --check`, `flake8`, OpenAPI/contract tests, `python scripts/ci/validate_repo.py`, `git diff --check`.
- Demo impact và rollback: dev fixture only; rollback bằng revert branch/commit. Không có runtime hoặc remote state.
- Evidence / kết quả:
  - `backend/.venv/Scripts/python.exe -m pytest -q`: `11 passed` (một warning deprecation từ dependency TestClient, không làm fail).
  - `backend/.venv/Scripts/python.exe -m black --check .`: pass.
  - `backend/.venv/Scripts/python.exe -m flake8 .`: pass.
  - `python -m unittest discover -s tests/ci -p "test_*.py"`: `17 tests` pass.
  - `python scripts/ci/validate_repo.py`, `git diff --check`, `python scripts/ai_log/ai_log.py doctor --strict`: pass.
  - Phát hiện hook `prepare-commit-msg` restage evidence khi Git giữ index lock; sửa để hook chỉ tái dùng evidence đã stage từ `pre-commit`, có regression test riêng.
- AI-Log ID + capture status: manual Codex candidate đã được ghi; `AI-Log` ID/CommitEvidence chỉ phát sinh tại commit hook. Không commit/push trong task này.
- Files, API và resources đã chạm: `backend/app/**` (config, routers, typed models, ports, adapters, trust/rule/orchestration services, rate limit), `backend/tests/**`, `backend/requirements*`, `.env.example`, `docs/api/BACKEND_CONTRACT.md`, `docs/ai/PROJECT_CONTEXT.md`, `docs/ai/ARCHITECTURE.md`, `team_docs/TEAM_BOOTSTRAP_OVERVIEW.md` và Context Pack này.
- Claims đã release: backend implementation complete; public contract cần peer review trước khi FE/data/AI consumer phụ thuộc sâu.
- Việc tiếp theo hoặc peer có thể tiếp nhận:
  - Member 2 bàn giao approved Procedure Pack/repository adapter và retrieval adapter; fixture phải được thay thế qua port, không sửa router.
  - Member 3 bàn giao recommendation/LLM adapter, provider policy và evaluation; không cho LLM quyết định validation.
  - Member 5 tiêu thụ OpenAPI/contract sau peer review; chỉ dựa `verified_guidance` khi approved release tồn tại.
  - Member 6 chạy full CI/public smoke sau khi có deploy authority; không có public runtime trong handoff này.
