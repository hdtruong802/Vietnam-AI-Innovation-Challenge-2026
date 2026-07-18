# Context Pack — local-20260717-integrate-origin-main

## Identity

- Task ID: `local-20260717-integrate-origin-main` | GitHub Issue: `chưa publish`
- Owner tạm thời: Codex trong phiên hiện tại
- Mode hiện tại: `implement`
- Base ref / commit: `truong@75b815531a9a9fab2f71ec9339b9b25bc8bc513a` + `origin/main@731076df87d999a080f8d7090ce3a6b650836727`
- Branch / worktree: `truong` / working tree hiện tại
- AI Log member / tool binding / readiness: `TBD — manual onboarding trước commit`

## Mục tiêu và ranh giới

- Mục tiêu: tích hợp `origin/main` vào `truong`, dùng D-005 mới cho scaffold FastAPI/Next.js, đồng bộ context/architecture/docs với application đã có và giữ D-006 chỉ cho capability chưa có evidence triển khai.
- Non-goals: không push, không thay GitHub settings, không xóa historical Context Pack, không thay MVP D-007/D-008, không tự khẳng định deploy/model/provider/remote enforcement đã hoạt động.
- Acceptance criteria: không còn conflict; một D-005 hiện hành duy nhất; D-006 được phân định rõ implementation hiện có và phần còn proposed; docs/README/team docs khớp code; tests/guard/check phù hợp pass.
- Constraints: bảo toàn local changes hiện có qua stash/merge có thể đảo ngược; chỉ dùng source/code dữ liệu đã có trong repo; không đưa secret/PII hoặc raw session vào Git; mọi commit có AI Log manual evidence, nhưng không tự push.
- Stop condition / blocker cần hỏi peer: dừng nếu phát hiện secret/PII, conflict mới không thể quyết định từ D-005/D-006, test fail không thuộc scope integration, hoặc phải thay MVP/shared contract không có Decision.

## Scope đã claim

- Files/areas được phép chạm: conflict files `.gitignore`, `docs/ai/ARCHITECTURE.md`, `docs/ai/DECISIONS.md`, `docs/ai/PROJECT_CONTEXT.md`; docs/protocol/team overview/deployment/demo cần đồng bộ; integration metadata của branch.
- API, schema hoặc contract liên quan: D-005 scaffold, D-006 architecture/API/deploy proposal, public `/v1` boundaries theo application hiện có.
- Không được chạm: raw `data/` nội dung, remote settings, secret, history Context Pack cũ và deployment credentials.
- Risk: `shared`
- Decision Log liên quan: D-005 mới, D-006, D-007, D-008, D-009.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Protocol | `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md` | Merge, AI Log, handoff và peer-equal constraints. |
| Product / architecture | `docs/ai/PROJECT_CONTEXT.md`, `docs/ai/ARCHITECTURE.md` | Đồng bộ code mới với product/trust boundaries. |
| Decision | `docs/ai/DECISIONS.md`, remote D-005 | Giải quyết collision D-005/D-006. |
| Remote code | `origin/main:backend/`, `origin/main:frontend/` | Chỉ xác minh facts đã scaffold. |

## Dependencies và resource claim

- Depends on / blocked by: user đã xác nhận dùng D-005 mới; code remote là source evidence cho scaffold.
- Shared resource: branch `truong`, shared docs và Decision Log.
- Claim owner + thời hạn: Codex trong phiên hiện tại; release khi integration handoff.
- Cách thông báo peer và điều kiện release: ghi rõ conflict resolution, refs, test evidence, rollback và khác biệt chưa verify.

## Kiểm chứng và handoff

- Commands / manual checks: AI Log doctor/record; merge status; bootstrap guard/tests; backend/frontend checks theo manifest; `git diff --check`; Markdown links; compare app interfaces với docs.
- Demo impact và rollback: rollback local bằng reset/revert commit integration sau khi team chấp thuận; chưa ảnh hưởng remote hoặc deploy.
- Evidence / kết quả: `TBD`.
- AI-Log ID + capture status: `TBD`.
- Files, API và resources đã chạm: `TBD`.
- Claims đã release: `TBD`.
- Việc tiếp theo hoặc peer có thể tiếp nhận: `TBD`.
