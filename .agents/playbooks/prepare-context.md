# Playbook: prepare context

## Mục tiêu

Tạo Context Pack nhỏ, có thể review và đủ để một peer/agent khác bắt đầu task mà không phải suy đoán hoặc đọc toàn bộ repo.

## Thực hiện ở mode `explore`

1. Đọc `AGENTS.md`, `TEAM_PROTOCOL.md`, `PROJECT_CONTEXT.md` và Decision Log liên quan.
2. Xác nhận Prompt Intake Gate đã đủ Goal, Success Criteria, Constraints và Stopping Conditions. Nếu prompt tham chiếu record active, chỉ dùng các field được tham chiếu trực tiếp.
3. Tạo Task ID `local-YYYYMMDD-slug` khi chưa publish; tạo file từ [Context Pack template](../context-packs/TEMPLATE.md) với tên `<task-id>.md`.
4. Ghi objective, non-goals, acceptance criteria, Constraints, base ref, scope files/API, risk, dependency và stop condition.
5. Chỉ tìm/đọc các file cần thiết; ghi file, line/ref và lý do vào bảng context. Không đưa transcript dài, toàn repo, secret hoặc raw sensitive data vào pack.
6. Claim resource dùng chung nếu có, ghi thời hạn và báo peer trước khi chuyển mode.
7. Chỉ chuyển sang `implement` khi scope, checks và rollback đủ rõ; nếu không, giữ `explore` hoặc đặt `blocked`.

## Đầu ra

Context Pack có thể review, Task Record rõ ràng và đúng một implementer được quyền sửa source khi task bắt đầu.
