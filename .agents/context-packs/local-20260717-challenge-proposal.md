# Context Pack — local-20260717-challenge-proposal

> Task tài liệu `risk:shared`; không chứa dữ liệu cá nhân, secret hoặc nội dung pháp lý chưa được xác minh.
>
> **Historical scope notice:** D-005 và procedure pack thứ ba của task này đã được D-007 supersede. Không dùng Context Pack này làm product scope hiện hành; xem `local-20260717-change-third-mvp` và Project Context.

## Identity

- Task ID: `local-20260717-challenge-proposal` | GitHub Issue: chưa publish
- Owner tạm thời: Codex
- Mode hiện tại: `verify-demo`
- Status: `handoff`
- Base ref / commit: `truong` / `75b8155`
- Branch / worktree: `truong` / working tree hiện tại theo yêu cầu local-only

## Mục tiêu và ranh giới

- Mục tiêu: chốt context đề bài và ba MVP, viết proposal tiếng Việt dựa trên `raw.md` cùng nguồn chính thức, đồng bộ source-of-truth của repo và quy mô team sáu người.
- Non-goals: không viết application code, không thêm dependency, không provision hosting/database, không xác nhận model/provider, không commit/push hoặc thay đổi remote.
- Acceptance criteria: proposal có one-page summary, SWOT, giải pháp, kiến trúc đề xuất, KPI, rubric, kế hoạch 48 giờ và pilot 90 ngày; ba MVP giữ nguyên; tài liệu nguồn sự thật không tuyên bố hạ tầng hay KPI đã tồn tại; các kiểm tra local pass.
- Constraints: policy repo là baseline; `raw.md` chỉ là phân tích nội bộ, phải giữ nguyên và untracked; fact quy phạm dùng nguồn chính thức với mốc khóa 2026-07-17; kiến trúc/API/deploy chỉ ở trạng thái `Proposed` cho đến khi có peer xác nhận.
- Stop condition / blocker cần hỏi peer: gặp mâu thuẫn về ba MVP đã chốt, cần khẳng định quy định pháp lý chưa có nguồn chính thức, cần thay shared contract ngoài D-006, hoặc cần scaffold/provision/publish.

## Scope đã claim

- Files/areas được phép chạm: `README.md`, Context Pack này, `docs/PRODUCT.md`, `docs/ai/{PROJECT_CONTEXT,ARCHITECTURE,TEAM_PROTOCOL,TEAM,DECISIONS,DEMO,DEPLOYMENT,SECRETS_AND_DATA}.md`, `.temp_docs/{proposal,TEAM_BOOTSTRAP_OVERVIEW}.md`.
- API, schema hoặc contract liên quan: procedure-pack schema, public REST surface, trust statuses và deploy topology chỉ ở mức đề xuất trong D-006.
- Không được chạm: `raw.md`, application source/dependency, `.env`, secret, remote GitHub, hosting/database thực.
- Risk: `shared`
- Decision Log liên quan: D-001, D-004, D-005 và D-006.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Project context | `docs/ai/PROJECT_CONTEXT.md` tại `75b8155` | Source-of-truth cần được điền khi đã nhận đề. |
| Protocol và kiến trúc | `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md`, `docs/ai/ARCHITECTURE.md` | Giữ Prompt Intake Gate, peer-equal workflow và ranh giới decision. |
| Phân tích nội bộ | `raw.md` tại working tree, không track | Gợi ý SWOT, định vị Procedure Copilot, data/trust/evaluation; không dùng làm nguồn pháp lý. |
| Nguồn chính thức | Cổng DVCQG, Cổng TTĐT Chính phủ và website cuộc thi, truy cập 2026-07-17 | Căn cứ factual và source freeze cho proposal. |

## Dependencies và resource claim

- Depends on / blocked by: D-006 cần một peer xác nhận trước khi scaffold application; chi tiết từng procedure pack cần cán bộ/người review nghiệp vụ xác minh.
- Shared resource: `none`
- Claim owner + thời hạn: Codex giữ scope tài liệu trong task này đến khi handoff.
- Cách thông báo peer và điều kiện release: handoff ghi rõ files, checks, phần Proposed/TBD; release ngay sau kiểm chứng.

## Kiểm chứng và handoff

- Commands / manual checks: `git check-ignore .temp_docs/proposal.md`; `python scripts/ci/validate_repo.py`; unit tests repository guard; `git diff --check`; rà link Markdown/Mermaid; tìm tham chiếu team năm người; kiểm tra `raw.md` không đổi và không stage.
- Demo impact và rollback: chỉ cập nhật tài liệu định hướng demo; rollback bằng cách bỏ các diff tài liệu của Task Record, không có runtime/remote state.
- Evidence / kết quả: `git check-ignore` xác nhận proposal bị ignore; repository guard pass; 8 unit tests pass; `git diff --check` pass; local links trong hai temp docs pass; không còn tham chiếu team năm người; các URL chính thức chính được rà ngày 2026-07-17.
- Files, API và resources đã chạm: `README.md`, Context Pack này, `docs/PRODUCT.md`, các tài liệu `docs/ai/` đã claim và hai file `.temp_docs/`; chỉ mô tả procedure-pack schema và `/v1` API ở trạng thái `Proposed`.
- Claims đã release: toàn bộ claim tài liệu đã release; không có port, database, model, deploy environment hoặc remote resource được claim.
- Việc tiếp theo hoặc peer có thể tiếp nhận: một peer review D-006; nếu chấp thuận, tạo Task Record scaffold riêng và cập nhật D-006 trước khi thêm code/dependency/provisioning.
