# Demo runbook

> Trạng thái: `TBD`
>
> Demo owner tạm thời / Task Record: `TBD`
>
> Bản demo/commit đã kiểm chứng: `TBD`
> Lần diễn tập gần nhất: `TBD`

Runbook này biến MVP thành một demo lặp lại được. “Demo owner” chỉ là người điều phối phiên diễn tập hiện tại; bất kỳ peer nào có thể cập nhật hoặc tiếp nhận Task Record demo. Khi publish, Task Record được sao chép sang Issue/PR.

## Mục tiêu và thông điệp

- **Vấn đề mở đầu:** `TBD`
- **Người dùng mục tiêu:** `TBD`
- **Thông điệp một câu:** `TBD`
- **Điểm AI/đổi mới cần chứng minh:** `TBD`
- **Kết quả mà giám khảo phải nhìn thấy:** `TBD`

## Kịch bản demo

| Thời điểm | Người nói/làm | Hành động trong sản phẩm | Kết quả mong đợi | Fallback |
| --- | --- | --- | --- | --- |
| 00:00 | `TBD` | `TBD` | `TBD` | `TBD` |
| 00:30 | `TBD` | `TBD` | `TBD` | `TBD` |
| 01:30 | `TBD` | `TBD` | `TBD` | `TBD` |
| 02:30 | `TBD` | `TBD` | `TBD` | `TBD` |

Điều chỉnh mốc thời gian theo giới hạn chính thức của cuộc thi. Dùng demo data cố định và lưu nguồn/giấy phép trong `SECRETS_AND_DATA.md` hoặc Task Record liên quan.

## Preflight trước mỗi lần diễn tập

- [ ] Đang chạy đúng branch/commit đã ghi ở đầu tài liệu.
- [ ] Secrets nạp qua môi trường local; không hiển thị token trên terminal, browser, slide hoặc ghi hình.
- [ ] Lệnh run/build/check bên dưới đã chạy thành công trên ít nhất một máy khác hoặc worktree sạch.
- [ ] Demo data, tài khoản test và network fallback sẵn sàng.
- [ ] UI ở đúng viewport; tab, URL, terminal và notification không liên quan đã đóng/ẩn.
- [ ] Có ảnh/video/screenshot hoặc kết quả seed làm fallback cho mỗi bước phụ thuộc service bên ngoài.
- [ ] Người trình bày và một peer biết cách chuyển sang fallback.

## Lệnh và các bước đã kiểm chứng

Chỉ thay `TBD` bằng lệnh đã chạy được:

```bash
# Start application
TBD

# Verify happy path
TBD

# Build/package (if required)
TBD
```

| Kiểm tra | Kết quả mong đợi | Bằng chứng / ngày | Người thực hiện |
| --- | --- | --- | --- |
| Happy path | `TBD` | `TBD` | `TBD` |
| AI/provider response | `TBD` | `TBD` | `TBD` |
| Failure/fallback | `TBD` | `TBD` | `TBD` |
| Fresh startup | `TBD` | `TBD` | `TBD` |

## Fallback matrix

| Điểm lỗi | Dấu hiệu | Fallback đã chuẩn bị | Cách quay lại |
| --- | --- | --- | --- |
| Network/provider | `TBD` | `TBD` | `TBD` |
| Model latency/error | `TBD` | `TBD` | `TBD` |
| Deploy/runtime | `TBD` | `TBD` | `TBD` |
| Demo data | `TBD` | `TBD` | `TBD` |

## Scope freeze và sign-off

- Sáu giờ cuối, chỉ chấp nhận thay đổi trực tiếp làm demo đáng tin cậy hơn hoặc sửa P0.
- Mọi thay đổi mới cần hai peer xác nhận, evidence test và rollback/fallback rõ ràng trong Task Record/Decision Log; cập nhật PR khi task đã publish.
- Mỗi lần diễn tập phải cập nhật commit, lỗi phát hiện, owner tạm thời và Task Record follow-up; không chỉ ghi “đã test”.
