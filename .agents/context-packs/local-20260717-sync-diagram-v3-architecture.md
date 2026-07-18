# Context Pack — Đồng bộ kiến trúc từ `diagram_v3.mmd`

- **Task ID:** `local-20260717-sync-diagram-v3-architecture`
- **Owner:** current implementer
- **Mode:** `verify-demo`
- **Base ref:** `truong` @ `75b8155`
- **Risk:** `risk:shared`
- **Status:** handoff

## Prompt Intake Gate

- **Goal:** đọc `diagram_v3.mmd` và đồng bộ kiến trúc hiện hành trong source-of-truth, tài liệu kỹ thuật và proposal.
- **Success Criteria:** API Gateway, Orchestrator, PII Guard theo session, LLM Gateway, deterministic validation, redacted audit và approved knowledge được thể hiện nhất quán; ba MVP, public API, trust state và policy dữ liệu hiện hành không đổi.
- **Constraints:** chỉ sửa tài liệu; không sửa `diagram_v3.mmd`, không thêm code/dependency/provider, không commit/push; D-006 vẫn `Proposed` cho tới peer review.
- **Stopping Conditions:** dừng nếu cần đổi MVP, public API, retention, phạm vi PII, hoặc phải chọn framework/database/provider/hosting mới.

## Mục tiêu và non-goals

### Mục tiêu

- Dùng `diagram_v3.mmd` làm input thiết kế cho luồng guided intake, pre-submission checking và portal integration.
- Làm rõ trust boundary giữa raw form data nội bộ, PII Guard, external LLM và redacted audit.
- Giữ Rule Engine deterministic là nguồn duy nhất tạo finding field/cross-field; LLM chỉ hỏi làm rõ và giải thích finding đã có.

### Non-goals

- Không sao chép ví dụ giấy phép xây dựng hoặc giả định scrape từ sơ đồ vào phạm vi MVP.
- Không cho raw identifier hoặc free-text chưa giảm thiểu đi tới external LLM.
- Không triển khai long-term memory, KMS/Vault, crawler, application scaffold hoặc deploy.

## Acceptance Criteria

1. `docs/ai/ARCHITECTURE.md`, D-006, `team_docs/kientruc.md` và Section 5 của `team_docs/proposal.md` cùng mô tả một trust boundary.
2. PII token map chỉ tồn tại in-memory trong phiên, không log/DB/disk/vector/CaseSnapshot.
3. Guided intake và pre-check có fallback fail-closed; model failure không làm mất deterministic path.
4. Ba MVP theo D-007, sáu endpoint và ba trust state không đổi.
5. Markdown/Mermaid checks, repository guard và `git diff --check` pass.

## Scope claim

- `.agents/context-packs/local-20260717-sync-diagram-v3-architecture.md`
- `docs/ai/ARCHITECTURE.md`
- `docs/ai/DECISIONS.md` — chỉ refinement của D-006
- `team_docs/kientruc.md`
- `team_docs/proposal.md` — chỉ Section 5

## Context đã chọn

- `diagram_v3.mmd` — input trực quan, không phải source-of-truth.
- `docs/ai/DECISIONS.md` — D-006 và D-007.
- `docs/ai/ARCHITECTURE.md` — architecture source-of-truth.
- `docs/ai/SECRETS_AND_DATA.md` — policy PII/retention hiện hành.
- `team_docs/kientruc.md` — capability architecture và review gates.

## Shared-resource claim

- **Resource:** architecture/trust boundary docs.
- **Claim:** một writer trong task này; cần peer review trước khi D-006 được Accepted hoặc scaffold bắt đầu.
- **Release:** sau validation và handoff.

## Lệnh kiểm tra

```text
python scripts/ci/validate_repo.py
python -m unittest discover -s scripts/ci/tests -p "test_*.py"
git diff --check
```

## Handoff

- **Task Record / branch:** `local-20260717-sync-diagram-v3-architecture` / `truong`.
- **Kết quả:** logical architecture đã đồng bộ API Gateway, session-scoped PII Guard, provider-neutral LLM Gateway, deterministic Rule Engine, redacted audit và approved RAG; không đổi MVP/API/trust/retention.
- **Files chạm tới:** Context Pack này, `docs/ai/ARCHITECTURE.md`, refinement D-006 trong `docs/ai/DECISIONS.md`, `team_docs/kientruc.md` và Section 5 của `team_docs/proposal.md`.
- **Kiểm tra:** repository guard pass; 8 unit tests pass; Mermaid block balance pass cho cả hai team docs; `git diff --check` pass.
- **Risk / rollback:** D-006 vẫn `Proposed`; PII Guard/LLM Gateway chỉ là logical capability, chưa có code/provider. Rollback bằng cách bỏ refinement và khôi phục ba tài liệu từ diff của Task Record.
- **Resource claim:** released sau handoff; mọi scaffold vẫn cần một peer chấp thuận D-006.
- **Việc tiếp theo:** peer review D-006, đặc biệt raw-PII boundary, token-map lifecycle và deterministic fallback, trước khi tạo Task Record scaffold.
