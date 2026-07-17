# Kiến trúc tối thiểu

> Trạng thái: `TBD — xác nhận trong 90 phút đầu`
>
> Cập nhật gần nhất: `TBD`
> Decision liên quan: `TBD`

Tài liệu này mô tả kiến trúc đang được team chấp thuận, không phải nơi để đề xuất ngầm một stack mới. Khi chưa có quyết định, để `TBD` và tạo Task Record/Decision phù hợp; chỉ tạo Issue sau khi team chọn publish.

## Mục tiêu kiến trúc

- Phục vụ một demo MVP end-to-end đáng tin cậy trong 48 giờ.
- Tối ưu cho ranh giới rõ ràng, thay đổi độc lập và fallback dễ diễn tập.
- Tránh dependency, service và abstraction không trực tiếp phục vụ demo.

## Tổng quan hệ thống

```text
[User / Judge]
       |
       v
[TBD: UI / input] --> [TBD: application/API] --> [TBD: AI/model or rules]
                              |                         |
                              v                         v
                       [TBD: storage/data]       [TBD: output/result]
```

Thay sơ đồ này bằng các thành phần thực tế sau khi team chốt MVP. Mỗi mũi tên phải có contract rõ ràng hoặc link tới Decision Log.

## Thành phần và boundary

| Thành phần | Trách nhiệm | Input / output | Owner tạm thời / Task Record | Rủi ro |
| --- | --- | --- | --- | --- |
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

Owner chỉ điều phối boundary được ghi trong Task Record, không tạo quyền sở hữu cố định đối với thành phần.

## Contracts và tích hợp

| Boundary | Producer | Consumer | Contract/version | Validation | Fallback | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

Quy tắc cho shared contract:

- Contract phải chỉ rõ schema/input-output, lỗi có thể nhìn thấy và owner tạm thời của Task Record liên quan.
- Không sửa contract đã được consumer dùng mà không có Decision Log và peer confirmation.
- Ưu tiên compatibility adapter hoặc feature flag nhỏ khi demo đang phụ thuộc vào contract cũ.

## Data, AI và runtime

| Hạng mục | Lựa chọn | Giới hạn / giả định | Fallback | Quyết định |
| --- | --- | --- | --- | --- |
| Data source | `TBD` | `TBD` | `TBD` | `TBD` |
| Model/provider | `TBD` | `TBD` | `TBD` | `TBD` |
| Storage/cache | `TBD` | `TBD` | `TBD` | `TBD` |
| Hosting/runtime | `TBD` | `TBD` | `TBD` | `TBD` |

Không đưa secret, raw credentials hoặc dữ liệu nhạy cảm vào tài liệu này. Xem `SECRETS_AND_DATA.md`.

## Chạy, quan sát và khôi phục

| Việc | Lệnh hoặc bước đã kiểm chứng | Owner tạm thời / Task Record | Ghi chú |
| --- | --- | --- | --- |
| Cài dependencies | `TBD` | `TBD` | `TBD` |
| Chạy local | `TBD` | `TBD` | `TBD` |
| Chạy checks | `TBD` | `TBD` | `TBD` |
| Deploy/demo | `TBD` | `TBD` | `TBD` |
| Rollback/fallback | `TBD` | `TBD` | `TBD` |

Mọi thay đổi deploy hoặc runtime ảnh hưởng demo cần được ghi quyết định, diễn tập tối thiểu một lần và có rollback/fallback trước scope freeze.

## Thay đổi kiến trúc

1. Tạo Task Record/Context Pack với boundary, consumer bị ảnh hưởng, migration/compatibility và cách kiểm chứng; publish thành Issue nếu cần remote coordination.
2. Ghi Decision Log cho shared API, dependency, deploy hoặc demo flow.
3. Nhận peer confirmation trước khi implement hoặc merge thay đổi `risk:shared`.
4. Cập nhật bảng contracts, lệnh chạy, `DEMO.md` và handoff; cập nhật PR khi task đã được publish.
