# Playbook: implement and handoff

## Trước khi sửa

1. Xác nhận Task Record ở mode `implement`, Context Pack còn đúng base ref, branch/worktree đúng và working tree không chứa thay đổi lạ.
2. Đọc Project Context/Architecture/Decision liên quan; xác nhận files/API/resources được phép chạm.
3. Chia thay đổi thành bước nhỏ, có thể đảo ngược. Không mở rộng scope âm thầm.

## Khi thực hiện

- Chỉ một implementer ghi source cho Task Record. Sub-agent song song chỉ được explore/review.
- Chỉ sửa files/API đã claim; cập nhật record/pack trước khi thêm scope hoặc resource mới.
- Với thay đổi shared, có peer confirmation và Decision Log trước khi implement.
- Không thêm secret, raw data, binary/model lớn hoặc dependency không cần cho MVP.
- Chạy test/lint/build phù hợp; khi stack chưa chốt, mô tả kiểm tra thủ công và giới hạn của nó.

## Bàn giao

Chuyển record sang `review` hoặc `verify-demo` và điền:

```text
Task Record / Issue / branch:
Context Pack + base ref:
Kết quả đạt được:
Files, API và resources đã chạm:
Kiểm tra đã chạy + kết quả:
Risk / rollback / phần chưa kiểm tra:
Resource claims đã release:
Việc tiếp theo hoặc handoff cho peer:
```

Khi team chọn publish, đưa cùng nội dung vào Issue/PR; `risk:isolated` không đổi shared contract, còn trường hợp không chắc chắn dùng `risk:shared`.
