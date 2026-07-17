# Playbook: demo readiness

## Mục tiêu

Đảm bảo MVP chạy được, kể câu chuyện rõ và có fallback trước hạn nộp; mode dùng là `verify-demo`, không phải quyền riêng của một người/agent.

## Thực hiện

1. Cập nhật [`docs/ai/DEMO.md`](../../docs/ai/DEMO.md): ref/commit, seed data, thao tác demo, kết quả mong đợi, fallback và resource claim.
2. Tạo hoặc cập nhật Context Pack cho demo-impacting task; ghi URL/port/model/local DB dùng chung cùng owner và hạn release.
3. Chạy rehearsal từ môi trường gần trình diễn; ghi evidence và Task Record `priority:p0` nếu demo bị chặn.
4. Xác nhận không dùng key thật, dữ liệu nhạy cảm hoặc dependency không có fallback. Release runtime/resource claim sau rehearsal.
5. Sau scope freeze chỉ nhận sửa lỗi, demo polish và reliability có xác nhận peer theo `TEAM_PROTOCOL.md`.

## Đầu ra

Demo runbook và handoff có thể được bất kỳ peer nào thực hiện lại mà không cần agent hoặc owner ban đầu.
