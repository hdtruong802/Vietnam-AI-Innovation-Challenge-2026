# Playbook: claim task

## Mục tiêu

Claim một Task Record nhỏ, có ranh giới rõ và có thể bàn giao độc lập. GitHub Issue chỉ là bản publish của record khi team đã bật remote workflow.

## Thực hiện

1. Áp dụng **Prompt Intake Gate** trong `AGENTS.md`. Nếu thiếu Goal, Success Criteria hoặc Stopping Conditions, dừng và hỏi gộp; không tạo claim để bắt đầu task.
2. Đọc `docs/ai/TEAM_PROTOCOL.md`, Project Context và Decision Log liên quan.
3. Tạo/claim Task Record với ID `local-YYYYMMDD-slug`, owner tạm thời, mode `explore`, base ref, `risk`, Goal, Success Criteria, Constraints, Stopping Conditions, files/API/resources và blocker.
4. Với task code/API/data/config/demo hoặc `risk:shared`, tạo Context Pack bằng playbook `prepare-context` trước khi mode `implement`.
5. Kiểm tra `git status --short --branch`; tạo branch/worktree riêng từ `dev` bằng playbook `start-worktree`.
6. Nếu task đụng shared API, schema, dependency, deploy flow hoặc demo flow, tạo/đề xuất Decision Log và nhận peer confirmation trước khi sửa.

## Dừng và hỏi peer khi

- Hai Task Record cùng claim một file, endpoint, schema, component public hoặc runtime resource.
- Prompt Intake Gate chưa có đủ Goal, Success Criteria hoặc Stopping Conditions.
- Acceptance criteria không đo được, context chưa đủ, hoặc scope lớn hơn một thay đổi dễ review.
- Có nguy cơ lộ secret/dữ liệu nhạy cảm, vi phạm điều kiện cuộc thi hoặc thay đổi demo flow.

## Đầu ra

Task Record/Context Pack có scope, claims, mode và branch/worktree rõ ràng. Khi publish, sao chép record này vào Issue thay vì tạo ownership mới.
