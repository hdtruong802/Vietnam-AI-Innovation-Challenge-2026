# Context Pack — Web-first và portal integration scope

- **Task ID:** `local-20260717-web-first-portal-scope`
- **Owner:** current implementer
- **Mode:** `verify-demo`
- **Base ref:** `truong` @ `75b8155`
- **Risk:** `risk:shared`
- **Status:** handoff

## Prompt Intake Gate

- **Goal:** bỏ mobile khỏi phạm vi sản phẩm/delivery hiện hành và tập trung vào web app có thể tích hợp Cổng Dịch vụ công Quốc gia trong tương lai.
- **Success Criteria:** source-of-truth, proposal, architecture, demo, design context và phân công cùng mô tả standalone web app + embeddable widget/iframe + headless API; không còn task/evidence mobile.
- **Constraints:** giữ nguyên ba MVP, sáu public API, trust states, PII/retention và deploy contract; không scaffold, chọn provider, provision, commit hoặc push.
- **Stopping Conditions:** dừng nếu cần thay MVP/API/PII/retention/deploy contract hoặc cam kết tích hợp thật với Cổng DVCQG khi chưa có sandbox/authorization.

## Mục tiêu và non-goals

### Mục tiêu

- Chốt delivery surface web-first cho demo và pilot pathway.
- Làm rõ integration target: standalone public web app, Web Component/iframe adapter và headless REST API.
- Thay mobile-specific acceptance bằng browser, portal-container, accessibility, CSP/CORS và embed compatibility.

### Non-goals

- Không xây native mobile app, PWA install flow hoặc app-store artifact.
- Không tuyên bố đã tích hợp với Cổng DVCQG.
- Không thay đổi wire contract, stack proposal hoặc hosting topology trong D-006.

## Acceptance Criteria

1. Không còn mobile-specific implementation task/evidence; từ `mobile` chỉ được xuất hiện để ghi non-goal, stopping condition hoặc Decision history.
2. Project Context, Product, Design, Architecture, Deployment và Demo nêu rõ web-first và portal integration pathway.
3. Proposal và phân công có evidence/task cho standalone web app, widget/iframe, headless API, browser/container compatibility và accessibility.
4. D-008 ghi nhận quyết định, compatibility và rollback; D-006 vẫn `Proposed`.
5. Repository guard, unit tests và `git diff --check` pass.

## Scope claim

- `.agents/context-packs/local-20260717-web-first-portal-scope.md`
- `README.md`
- `docs/PRODUCT.md`
- `docs/DESIGN.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/ai/ARCHITECTURE.md`
- `docs/ai/DECISIONS.md`
- `docs/ai/DEMO.md`
- `docs/ai/DEPLOYMENT.md`
- `team_docs/proposal.md`
- `team_docs/kientruc.md`
- `team_docs/phancong.md`
- `team_docs/TEAM_BOOTSTRAP_OVERVIEW.md`

## Context đã chọn

- `docs/ai/PROJECT_CONTEXT.md` — MVP, integration capability và UX priority.
- `docs/ai/ARCHITECTURE.md` — FE/widget/API boundary.
- `docs/ai/DECISIONS.md` — D-006/D-007 và decision process.
- `docs/ai/DEMO.md`, `docs/ai/DEPLOYMENT.md` — public web evidence và integration gate.
- `docs/PRODUCT.md`, `docs/DESIGN.md` — design/audit context.
- `team_docs/proposal.md`, `team_docs/phancong.md`, `team_docs/kientruc.md` — presentation và execution plan.

## Shared-resource claim

- **Resource:** product delivery surface, web integration narrative và frontend acceptance.
- **Claim:** một writer trong task này; user đã chọn đồng bộ repo-wide.
- **Release:** sau validation/handoff.

## Lệnh kiểm tra

```text
python scripts/ci/validate_repo.py
python -m unittest discover -s tests/ci -p "test_*.py"
git diff --check
```

## Handoff

- **Task Record / branch:** `local-20260717-web-first-portal-scope` / `truong`.
- **Kết quả:** D-008 đã khóa web-first delivery; source-of-truth, proposal, architecture, demo, deployment, design context và phân công cùng dùng standalone web app + widget/iframe + headless API.
- **Files chạm tới:** Context Pack, README, Product/Design, Project Context, Architecture, Decision Log, Demo, Deployment và bốn team docs trong scope.
- **Kiểm tra:** repository guard pass; 8 unit tests pass; không còn positive mobile/task pattern; `git diff --check` pass.
- **Risk / rollback:** D-006 vẫn `Proposed`; chưa có portal sandbox/authorization hoặc application code. Rollback bằng cách supersede D-008 và khôi phục wording/task từ diff, không tự thêm mobile scope.
- **Resource claim:** released sau handoff.
- **Việc tiếp theo:** peer review D-006 trước scaffold; khi triển khai, tạo Task Record riêng cho web app/widget và xác nhận browser matrix, CSP/CORS/origin allowlist cùng portal sandbox assumptions.
