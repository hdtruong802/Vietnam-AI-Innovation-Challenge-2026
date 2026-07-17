# Playbook: review and merge

## Phân loại

- `risk:isolated`: thay đổi nhỏ, cô lập, không đổi API/schema/dependency/deploy/demo flow.
- `risk:shared`: mọi thay đổi còn lại hoặc khi chưa chắc chắn; ưu tiên an toàn hơn tốc độ.

## Review ở mode `review`

1. Đối chiếu diff với Task Record/Context Pack: base ref, scope files/API, non-goals, claims và acceptance criteria.
2. Kiểm tra evidence, rollback, resource release và các thay đổi cần đưa vào demo/architecture/Decision Log.
3. Không có secret, dữ liệu nhạy cảm, binary/model lớn, local config hoặc thay đổi không được claim.
4. Với `risk:shared`, có peer acknowledgement và Decision Log trước khi chuyển sang verify/merge.
5. Reviewer không sửa hộ implementer; nếu cần thay đổi mới, tạo Task Record hoặc chuyển ownership rõ ràng.

## Verify, publish và merge

- Mode `verify-demo` chạy command/manual demo theo Context Pack, gồm `repository-guard` khi phù hợp.
- Trước publish, sao chép Task Record/handoff vào Issue/PR; kiểm tra base branch là `dev` và giải quyết conflict trên branch của owner.
- Mọi peer có cùng quyền merge khi điều kiện risk đã đủ. Dùng squash merge vào `dev` sau khi remote workflow được bật.
- Không merge `risk:shared` thiếu peer confirmation; sáu giờ cuối chỉ nhận sửa lỗi/demo-critical với hai peer xác nhận.
