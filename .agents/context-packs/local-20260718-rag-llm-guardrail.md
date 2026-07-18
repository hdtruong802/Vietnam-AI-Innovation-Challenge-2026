# Context Pack — local-20260718-rag-llm-guardrail

> Dùng cho task có code, API, data, config, demo hoặc `risk:shared`. Không ghi secret, dữ liệu nhạy cảm, transcript dài hay bản sao toàn bộ repository.

## Identity

- Task ID: `local-20260718-rag-llm-guardrail`
- Status: `done` (implement + merge + verify-demo local hoàn tất; chưa publish; Decision D-011 vẫn `Proposed`, cần peer confirmation)
- Owner tạm thời: Cursor (thực hiện theo yêu cầu người dùng hiện tại)
- Mode hiện tại: `verify-demo`
- Base ref / commit: khởi tạo từ `main` @ `7066948`; đã merge `origin/main` @ `0cf872a` (PR #12, backend hexagonal refactor `truong`/`dev`) vào cùng branch
- Branch / worktree: `nguyetplt` (không tạo worktree riêng vì chỉ một implementer đang chạm scope này)

## Mục tiêu và ranh giới

- Mục tiêu: Implement ba năng lực **RAG (Retrieval)**, **LLM Gateway** và **Guardrail (PII Guard)** trong `backend/` theo `docs/proposal.md` mục 5 và `docs/diagram_v3.mmd`, và tích hợp vào kiến trúc hexagonal (`app/ports.py` + `AppContainer` + `CopilotService`) mà `origin/main` đã refactor song song trong lúc task này đang chạy.
- Non-goals: Không đổi `RuleEngine`/`TrustPolicy` gốc của backend refactor (D-006), không build Neon/pgvector thật (vẫn `TBD`/`Proposed`), không đổi Frontend, không đổi public REST schema (`app/models/*.py`) ngoại trừ một field additive (`ValidationResponse.explanations`), không tự thêm long-term `CaseSnapshot`/S1.
- Acceptance criteria:
  - RAG: source store + retrieval lexical (pure-Python, không numpy/sklearn) chạy in-process trên `data/Data_DVC`, filter theo 3 procedure MVP, trả evidence + citation + freshness + confidence; không đưa PII/chat memory vào index.
  - LLM: provider-neutral gateway (OpenAI-compatible qua `AI_PROVIDER/AI_MODEL/AI_API_KEY/AI_BASE_URL`), structured output (JSON), fallback deterministic khi thiếu API key hoặc lỗi provider.
  - Guardrail: PII Guard tokenize/detokenize direct identifiers in-memory theo session (salt theo session, TTL, không log/lưu raw).
  - Tích hợp: `app/adapters/rag_llm.py` implement đủ `ProcedureRepository`/`RecommendationProvider`/`RetrievalProvider`/`LLMProvider` của `app/ports.py`; `app/dependencies.py::build_container` chọn adapter RAG/LLM khi `procedure_data_mode=rag`, `rag_mode=rag`, `llm_mode=gateway`; mặc định (`fixture`/`disabled`) không đổi hành vi cũ.
  - Toàn bộ test hiện có của `origin/main` (`test_api_contract.py`, `test_rule_engine.py`) vẫn pass sau merge + tích hợp; `python scripts/ci/validate_repo.py --staged` pass.
- Constraints: chính sách repo (`AGENTS.md`, `TEAM_PROTOCOL.md`, D-001..D-010) là baseline. Không thêm dependency native nặng; ưu tiên pure-Python cho retrieval.
- Stop condition / blocker cần hỏi peer: Nếu cần đổi public REST schema ngoài field additive đã khai báo, cần thêm dependency nặng/service ngoài (Neon/pgvector thật), hoặc cần API key thật cho provider — dừng và hỏi trước khi tiếp tục.

## Scope đã claim

- Files/areas được phép chạm:
  - `backend/app/services/rag/**`, `backend/app/services/llm/**`, `backend/app/services/guardrail/**`
  - `backend/app/adapters/rag_llm.py` (mới), `backend/app/adapters/dev_fixture.py` (audit sink redaction), `backend/app/dependencies.py`, `backend/app/ports.py`, `backend/app/services/copilot_service.py`, `backend/app/models/validation.py` (field additive), `backend/app/config.py`
  - `backend/requirements.txt`, `backend/tests/**`
  - `docs/ai/DECISIONS.md`, `docs/ai/PROJECT_CONTEXT.md` (append/update quyết định kỹ thuật liên lane)
- API, schema hoặc contract liên quan: `/v1/procedures`, `/v1/procedures/recommend`, `/v1/intake/turn`, `/v1/procedures/{id}/checklist`, `/v1/applications/validate` — giữ nguyên contract của backend refactor (D-006), chỉ thêm field optional `explanations` vào `ValidationResponse` và cắm adapter thật thay `Disabled*`/fixture khi bật `rag`/`gateway` mode.
- Không được chạm: `frontend/**`, `data/Data_DVC/**` (chỉ đọc, không sửa/ghi), `docs/proposal.md`, các Task Record/Context Pack khác (`local-20260717-challenge-proposal`, `local-20260718-backend-api-foundation`...).
- Risk: `shared` (đổi behavior/wiring của API dùng chung + thêm dependency cấu hình AI provider + merge với refactor song song của peer khác).
- Decision Log liên quan: D-006 (Trust/RAG architecture, `Proposed`, do peer khác đề xuất — đã đọc và tuân theo contract của D-006 khi implement); D-011 (RAG/LLM/Guardrail concrete implementation, `Proposed`, do task này đề xuất, renumber từ D-006 cũ để tránh trùng ID với D-006 của peer).

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Kiến trúc đề xuất | `docs/proposal.md` mục 5, 6 | Contract của RAG lifecycle, LLM Gateway, PII Guard, memory boundary |
| Sequence diagram | `docs/diagram_v3.mmd` | Thứ tự gọi PII Guard tokenize -> LLM -> detokenize; log chỉ lưu bản redacted |
| Kiến trúc hexagonal mới | `backend/app/ports.py`, `backend/app/dependencies.py`, `backend/app/adapters/dev_fixture.py`, `backend/app/services/copilot_service.py` | Contract Protocol (`ProcedureRepository`/`RecommendationProvider`/`RetrievalProvider`/`LLMProvider`/`AuditSink`) mà adapter RAG/LLM phải implement đúng |
| Decision Log | `docs/ai/DECISIONS.md` D-006, D-011 | D-006 là kiến trúc port/fallback do peer khác propose; D-011 là phần concrete implementation của task này |
| Data nguồn thật | `data/Data_DVC/*.txt` (format `Tên thủ tục:`/`Trình tự thực hiện:`/`Thành phần hồ sơ:`/`Căn cứ pháp lý:`) | Nguồn RAG cho 3 MVP pack |
| Backend contract test | `backend/tests/test_api_contract.py`, `backend/tests/test_rule_engine.py` | Contract fixture mode phải giữ nguyên sau khi thêm adapter RAG |

## Dependencies và resource claim

- Depends on / blocked by: `origin/main` backend hexagonal refactor (PR #12, không phải Task Record local của mình) — đã merge vào `nguyetplt`, resolve conflict `config.py`/`routers/intake.py`, xóa `procedure_service.py`/`validation_service.py` cũ (bị refactor xóa, thay bằng `copilot_service.py`+`rule_engine.py`+`trust_policy.py`).
- Shared resource: `none` (không dùng port/DB/account mới; không cần API key thật để demo chạy — có fallback offline).
- Claim owner + thời hạn: Cursor, trong phạm vi session task này.
- Cách thông báo peer và điều kiện release: Cập nhật Task Record sang `handoff`/`done` khi xong; release claim ngay khi hoàn tất.

## Kiểm chứng và handoff

- Commands / manual checks (chạy tại `backend/`, Python 3.13 qua `/opt/homebrew/Caskroom/miniforge/base/bin/python3 -m venv .venv`):
  - `python -m pytest -q` → 36 passed (bao gồm `test_api_contract.py`, `test_rule_engine.py` của refactor gốc + `test_pii_guard.py`, `test_llm_gateway.py`, `test_retrieval.py`, `test_rag_adapter.py` của task này).
  - `python -m black . && python -m flake8 .` → sạch, không lỗi.
  - `python scripts/ci/validate_repo.py --staged` (chạy tại repo root, Python 3.9 hệ thống) → `Repository guard passed`.
- Demo impact và rollback: Mặc định `Settings()` vẫn `procedure_data_mode=fixture`, `rag_mode=disabled`, `llm_mode=disabled` — hành vi cũ của backend refactor không đổi. Set `procedure_data_mode=rag`, `rag_mode=rag`, `llm_mode=gateway` (biến môi trường hoặc `Settings(...)`) để bật RAG/LLM thật. Nếu lỗi, đặt lại 3 biến này về giá trị cũ để `AppContainer` quay lại adapter fixture/disabled, không cần đổi code.
- Evidence / kết quả:
  - RAG: `RagProcedureRepository`/`RagRecommendationProvider`/`RagRetrievalProvider` (`backend/app/adapters/rag_llm.py`) build `ProcedurePack` thật (checksum, source_refs, last_verified_at) từ `data/Data_DVC` cho cả 3 pack MVP; `test_rag_adapter.py` xác nhận review_status=APPROVED, trust_state đúng theo `TrustPolicy` gốc của D-006.
  - LLM: `GatewayLLMProvider` implement `LLMProvider.explain_findings` (mở rộng thêm vào `app/ports.py`), tokenize form_data qua PII Guard trước khi gọi `LLMGateway`, không đổi finding/verdict gốc; offline mặc định trả `{}` (fail-closed).
  - Guardrail: `PIIGuard` tokenize/detokenize field-level theo session (salt theo session, TTL cấu hình qua `Settings.pii_token_ttl_seconds`); `InMemoryAuditSink` được nâng cấp dùng `PIIGuard.redact_free_text`/`RedactedAudit` cho defense-in-depth.
  - Retiring: xoá `backend/app/services/guardrail/trust_policy.py` (duplicate logic với `backend/app/services/trust_policy.py` của D-006) và `backend/app/services/intake_service.py` (thay bằng `CopilotService.intake` có sẵn từ refactor).
- Files, API và resources đã chạm (sau merge + tích hợp):
  - Mới: `backend/app/adapters/rag_llm.py`, `backend/app/services/rag/**`, `backend/app/services/llm/**`, `backend/app/services/guardrail/{__init__.py,audit.py,pii_guard.py}`, `backend/tests/{test_pii_guard,test_llm_gateway,test_retrieval,test_rag_adapter}.py`.
  - Sửa: `backend/app/config.py` (Settings + field AI/RAG/PII, thêm literal `rag`/`gateway`), `backend/app/ports.py` (`LLMProvider.explain_findings`), `backend/app/dependencies.py` (build_container chọn adapter theo mode), `backend/app/adapters/dev_fixture.py` (`DisabledLLMProvider.explain_findings`, `InMemoryAuditSink` redaction), `backend/app/services/copilot_service.py` (nhận `llm_provider`, gọi explain trong `validate()`), `backend/app/models/validation.py` (field `explanations`), `backend/requirements.txt` (thêm `openai` optional), `docs/ai/DECISIONS.md` (D-011), `docs/ai/PROJECT_CONTEXT.md`.
  - Xoá: `backend/app/services/procedure_service.py`, `backend/app/services/validation_service.py`, `backend/app/services/intake_service.py`, `backend/app/services/guardrail/trust_policy.py`, `backend/tests/test_api_smoke.py`, `backend/tests/test_trust_policy.py` (đều bị refactor D-006 thay thế hoặc trùng logic).
  - Không đổi: public request/response schema khác trong `backend/app/models/*.py`, `frontend/**`, `data/Data_DVC/**` (chỉ đọc).
- Claims đã release: Toàn bộ files/areas đã claim được release; task chuyển `done`. D-011 vẫn `Proposed` — cần một peer khác xác nhận để chuyển `Accepted`.
- Việc tiếp theo hoặc peer có thể tiếp nhận:
  - K1 review nội dung checklist tự sinh từ RAG cho `dang-ky-thuong-tru`/`dang-ky-ho-kinh-doanh` trước khi coi là `approved` chính thức về nghiệp vụ (hiện là deterministic parser trên nguồn thật, đã review kỹ thuật nhưng chưa qua human review pháp lý).
  - Xác nhận D-011 với một peer.
  - Cấu hình `AI_PROVIDER/AI_MODEL/AI_API_KEY/AI_BASE_URL` thật khi có quyết định provider (không cần đổi code, chỉ set env + `llm_mode=gateway`).
  - Đồng bộ `procedure_data_mode`/`rag_mode`/`llm_mode` mặc định (`fixture`/`disabled`) sang `rag`/`gateway` cho môi trường demo chính thức khi team xác nhận.
