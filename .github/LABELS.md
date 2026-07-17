# Nhãn GitHub chuẩn

Tạo đúng tên, màu và mô tả dưới đây trong **Issues → Labels → New label**. Mỗi Issue đang mở cần một `type`, `priority`, `area`, `status` và `risk`. Các nhãn chỉ mô tả công việc, không gán cấp bậc cho người hay agent.

[`repository-settings.json`](repository-settings.json) là nguồn máy đọc được của cùng danh sách này; bảng dưới đây là bản tham chiếu cho team.

| Nhãn | Màu hex | Mô tả |
| --- | --- | --- |
| `type:feature` | `1D76DB` | Tính năng hoặc năng lực mới |
| `type:bug` | `D73A4A` | Hành vi sai hoặc hồi quy |
| `type:task` | `0E8A16` | Công việc kỹ thuật, nghiên cứu hoặc vận hành |
| `type:docs` | `0075CA` | Thay đổi tài liệu |
| `priority:p0` | `B60205` | Chặn nộp bài, demo hoặc an toàn dữ liệu; xử lý ngay |
| `priority:p1` | `D93F0B` | Ảnh hưởng lớn tới mục tiêu hackathon; xử lý sớm |
| `priority:p2` | `FBCA04` | Quan trọng nhưng chưa chặn mốc hiện tại |
| `area:ui` | `C5DEF5` | Giao diện và trải nghiệm người dùng |
| `area:api` | `BFDADC` | API, server và logic ứng dụng |
| `area:ai` | `D4C5F9` | Model, prompt, đánh giá hoặc inference |
| `area:data` | `F9D0C4` | Dữ liệu, schema, pipeline hoặc chất lượng dữ liệu |
| `area:infra` | `FEF2C0` | Deploy, cấu hình, bảo mật hoặc tooling |
| `area:docs` | `D4C5F9` | Context, runbook, quyết định hoặc tài liệu |
| `status:ready` | `0E8A16` | Đã đủ thông tin để bắt đầu |
| `status:in-progress` | `FBCA04` | Owner tạm thời đang thực hiện |
| `status:blocked` | `B60205` | Bị chặn bởi phụ thuộc hoặc quyết định bên ngoài |
| `risk:isolated` | `C2E0C6` | Không thay đổi shared contract; có thể self-merge sau checklist |
| `risk:shared` | `5319E7` | Ảnh hưởng shared API, dependency, deploy hoặc demo; cần peer xác nhận |

## Kiểm tra và fallback

Sau khi tạo, mở một Issue thử và xác nhận ba template xuất hiện; sau đó xóa Issue thử. Nếu chưa có quyền tạo label, ghi đúng tên nhãn ở phần đầu Issue/PR, ví dụ `Labels: type:bug, priority:p1, area:api, status:ready, risk:isolated`, cho tới khi quyền được cấp. Không tạo biến thể gần giống như `P1`, `backend` hoặc `shared-risk`.
