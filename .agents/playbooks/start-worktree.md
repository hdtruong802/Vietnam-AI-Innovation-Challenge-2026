# Playbook: start worktree

## Mục tiêu

Tách working tree của mỗi task/agent bằng Git native, không tạo daemon hay sao chép config nhạy cảm.

## Trước khi tạo

1. Đọc Task Record/Context Pack và xác nhận base ref là `dev` hoặc ref đã được peer thống nhất.
2. Chạy `git status --short --branch` tại worktree hiện có. Không dùng worktree của peer có thay đổi chưa commit.
3. Chọn tên branch theo `feature/<task>-<slug>`, `fix/<task>-<slug>`, `chore/<task>-<slug>` hoặc `spike/<task>-<slug>`.

## Lệnh Git portable

Từ root repository, thay các placeholder trước khi chạy:

```text
git worktree add <sibling-path> -b <branch-name> <base-ref>
git -C <sibling-path> status --short --branch
```

- `<sibling-path>` phải là thư mục mới bên ngoài working tree hiện tại, ví dụ `../project-<task>`.
- Không chạy lệnh tạo worktree nếu branch đã thuộc worktree khác; chọn Task Record/scope khác hoặc trao đổi với owner.
- Không copy `.env`, ignored config, token, model cache hay dữ liệu local. Dựng lại local setup từ `.env.example` và dùng kênh secrets đã được team chấp thuận.

## Handoff

Ghi branch/worktree vào Context Pack. Khi task chuyển `handoff`, dừng runtime/resource đã claim; chỉ gỡ worktree khi không còn thay đổi cần giữ và sau khi peer đã nhận bàn giao.
