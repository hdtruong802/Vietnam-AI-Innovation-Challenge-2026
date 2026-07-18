# Context Pack — local-20260717-change-third-mvp

> Product-scope change `risk:shared`; không chứa chi tiết nghiệp vụ chưa được nguồn chính thức xác minh.

## Identity

- Task ID: `local-20260717-change-third-mvp` | GitHub Issue: chưa publish
- Owner tạm thời: Codex
- Mode hiện tại: `verify-demo`
- Base ref / commit: `truong` / `75b8155`
- Branch / worktree: `truong` / working tree hiện tại theo yêu cầu

## Mục tiêu và ranh giới

- Mục tiêu: thay procedure pack thứ ba từ Phiếu lý lịch tư pháp cá nhân sang đăng ký thành lập hộ kinh doanh và đồng bộ source-of-truth/tài liệu team.
- Non-goals: không viết checklist, form fields, validation rules hoặc căn cứ pháp lý cho hộ kinh doanh khi chưa có procedure research/K1; không đổi runtime API, stack/deploy hoặc application code; không commit/push.
- Acceptance criteria: D-005 được giữ như lịch sử `Superseded`; D-007 trở thành product Decision hiện hành; Project Context/Product/Architecture/Demo/Data policy và `team_docs/` dùng cùng ba MVP mới; không còn reference cũ ngoài historical records có nhãn superseded.
- Constraints: policy repo là baseline; giữ nguyên hai MVP đầu; procedure pack mới phải dùng cùng schema/evaluation/trust contract; mọi fact chưa xác minh ghi `TBD` hoặc giao procedure research.
- Stop condition / blocker cần hỏi peer: cần tự suy diễn quy định, giấy tờ, biểu mẫu, cơ quan, phí/thời hạn hoặc validation rule; cần đổi public API/stack/deploy; cần sửa dữ liệu nguồn ngoài phạm vi docs.

## Scope đã claim

- Files/areas được phép chạm: `README.md`, `docs/PRODUCT.md`, `docs/ai/{PROJECT_CONTEXT,ARCHITECTURE,DECISIONS,DEMO,SECRETS_AND_DATA}.md`, `team_docs/{proposal,phancong,TEAM_BOOTSTRAP_OVERVIEW}.md`, Context Pack hiện tại và historical proposal pack bằng superseded note.
- API, schema hoặc contract liên quan: giữ nguyên procedure-pack schema, sáu public endpoint, ba trust states và evaluation contract.
- Không được chạm: `raw.md`, application source/dependencies, secrets, remote GitHub, hosting/database, nội dung nghiệp vụ chưa có nguồn.
- Risk: `shared`
- Decision Log liên quan: D-005, D-006, D-007.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Product scope | `docs/ai/PROJECT_CONTEXT.md`, D-005 | Xác định danh sách MVP hiện hành cần supersede. |
| Architecture/demo | `docs/ai/ARCHITECTURE.md`, `docs/ai/DEMO.md` | Giữ contract và evidence depth khi đổi pack. |
| Team documents | `team_docs/proposal.md`, `team_docs/phancong.md` | Đồng bộ proposal, timeline và task research/data. |

## Dependencies và resource claim

- Depends on / blocked by: user đã chọn repo-wide synchronization; chi tiết pack hộ kinh doanh vẫn blocked bởi source discovery và K1.
- Shared resource: product/demo scope và Decision Log.
- Claim owner + thời hạn: Codex giữ claim tài liệu trên đến hết turn này.
- Cách thông báo peer và điều kiện release: release sau khi repository guard, unit tests, Markdown links và stale-reference audit pass.

## Kiểm chứng và handoff

- Commands / manual checks: `rg` old/new MVP references; Markdown link checks; `python scripts/ci/validate_repo.py`; unit tests repository guard; `git diff --check`.
- Demo impact và rollback: demo pack thứ ba đổi; rollback bằng Decision mới hoặc khôi phục diff tài liệu, không có runtime/remote state.
- Evidence / kết quả: D-005 đã `Superseded by D-007`; D-007 `Accepted`; D-006 vẫn `Proposed`; không còn reference Phiếu lý lịch tư pháp hoặc framing “ba thủ tục cá nhân” trong active docs; Project Context, Demo, proposal và assignment đều có MVP mới; repository guard pass; 8 unit tests pass; local Markdown links và `git diff --check` pass; `raw.md` không đổi.
- Files, API và resources đã chạm: `README.md`, `docs/PRODUCT.md`, `docs/ai/{PROJECT_CONTEXT,ARCHITECTURE,DECISIONS,DEMO,SECRETS_AND_DATA}.md`, `team_docs/{proposal,phancong,TEAM_BOOTSTRAP_OVERVIEW}.md`, historical proposal Context Pack bằng superseded notice và Context Pack này. Không đổi API/schema/runtime.
- Claims đã release: claim product/docs/Decision Log đã release.
- Việc tiếp theo hoặc peer có thể tiếp nhận: Member 1/2 tạo source registry, curated acquisition, normalized pack và K1 cho đăng ký thành lập hộ kinh doanh trước khi Member 3/4/5 implement hoặc đánh dấu `verified_guidance`.
