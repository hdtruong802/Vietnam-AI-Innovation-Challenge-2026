# Context Pack — <task-id>

> Dùng cho task có code, API, data, config, demo hoặc `risk:shared`. Không ghi secret, dữ liệu nhạy cảm, transcript dài hay bản sao toàn bộ repository.

## Identity

- Task ID: `local-YYYYMMDD-slug` | GitHub Issue: `<optional after publish>`
- Owner tạm thời:
- Mode hiện tại: `explore` | `implement` | `review` | `verify-demo`
- Base ref / commit:
- Branch / worktree:
- AI Log member / tool binding / readiness: `chưa bật` | `<member-id> / <tool + binding-id|manual> / doctor pass|warning>`

## Mục tiêu và ranh giới

- Mục tiêu:
- Non-goals:
- Acceptance criteria:
- Constraints: policy repo là baseline; ghi ràng buộc riêng nếu có.
- Stop condition / blocker cần hỏi peer:

## Scope đã claim

- Files/areas được phép chạm:
- API, schema hoặc contract liên quan:
- Không được chạm:
- Risk: `isolated` | `shared`
- Decision Log liên quan:

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Project context |  |  |
| Architecture / decision |  |  |
| Source hoặc test liên quan |  |  |

Chỉ giữ nguồn đủ để implement/review; cập nhật ref khi context đã stale.

## Dependencies và resource claim

- Depends on / blocked by:
- Shared resource: `none` | port / local DB migration / model download / demo environment / khác
- Claim owner + thời hạn:
- Cách thông báo peer và điều kiện release:

## Kiểm chứng và handoff

- Commands / manual checks:
- Demo impact và rollback:
- Evidence / kết quả:
- AI-Log ID + capture status: `chưa có` | `<log-id> / complete|warning|no_new_prompt|manual|git_operation`
- Files, API và resources đã chạm:
- Claims đã release:
- Việc tiếp theo hoặc peer có thể tiếp nhận:
