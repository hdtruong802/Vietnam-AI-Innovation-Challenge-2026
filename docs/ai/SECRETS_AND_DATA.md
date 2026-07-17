# Chính sách secrets và dữ liệu

Mục tiêu là bảo vệ token, tài khoản, dữ liệu nhạy cảm và quyền sử dụng dữ liệu trong khi vẫn cho team phát triển nhanh. Chính sách này áp dụng như nhau cho mọi người và mọi agent.

## Không được đưa vào Git, Task Record, Issue, PR hay prompt agent

- API keys, access tokens, passwords, private keys, service-account JSON, cookie/session, webhook URL có secret.
- Dữ liệu nhận diện cá nhân, dữ liệu khách hàng, dữ liệu chưa được phép chia sẻ hoặc raw production export.
- File model lớn, dataset lớn, artifact build/cache không cần để tái lập demo.
- Ảnh chụp terminal/browser/slide chứa secret hoặc thông tin nhạy cảm.

Không dán secret vào chat với Codex, Claude, Cursor hoặc Antigravity. Nếu agent cần biết cấu trúc biến môi trường, chỉ cung cấp tên biến và giá trị giả/an toàn.

## Cách quản lý biến môi trường

- Dùng file local như `.env` hoặc secret manager của môi trường deploy; những file này phải bị ignore.
- Chỉ commit `.env.example` với **tên biến**, mô tả ngắn và giá trị placeholder vô hại, ví dụ `MODEL_API_KEY=replace_me`.
- Mỗi người tự nhận secret qua kênh được team chấp thuận; không copy file `.env` sang repo, PR hay công cụ ghi log chung.
- Khi thêm biến mới, cập nhật `.env.example`, hướng dẫn chạy và kiểm tra rằng biến thật không xuất hiện trong diff.
- Nếu dùng GitHub Actions/deploy, lưu giá trị thật trong GitHub Secrets hoặc secret store của nền tảng, không trong workflow hay source code.

## Dữ liệu và giấy phép

| Dataset / nguồn | Mục đích | Quyền sử dụng / license | Có dữ liệu nhạy cảm? | Nơi truy cập | Owner tạm thời / Task Record |
| --- | --- | --- | --- | --- | --- |
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

- Chỉ dùng dữ liệu được phép cho mục đích hackathon/demo; ghi nguồn, license, hạn chế attribution và cách truy cập.
- Ưu tiên dữ liệu công khai, tổng hợp, ẩn danh hoặc seed demo. Không thu thập thêm dữ liệu cá nhân chỉ để kịp demo.
- Trước khi gửi data cho provider/model bên thứ ba, xác nhận điều khoản sử dụng, khả năng lưu giữ và mức nhạy cảm; nếu chưa rõ thì không gửi.
- Ghi schema tối thiểu và cách xóa/đặt lại dữ liệu demo trong Task Record hoặc `ARCHITECTURE.md`, không ghi giá trị nhạy cảm.

## Kiểm tra trước khi commit hoặc mở PR

- [ ] Không có `.env`, credentials, token, private key hay service-account file trong staged files.
- [ ] Không có PII/raw data/model artifact ngoài danh sách đã được team chấp thuận.
- [ ] Log, fixture, screenshot, notebook output và error message không lộ secret.
- [ ] Mọi nguồn dữ liệu mới có license/permission và Task Record/Decision liên kết.
- [ ] `.env.example` chỉ chứa placeholder; tài liệu không chép giá trị thật.

## Nếu nghi ngờ lộ secret hoặc dữ liệu

1. Dừng chia sẻ/commit/push thêm ngay và báo team qua kênh riêng; không dán secret vào Issue công khai để minh họa.
2. Thu hồi/rotate credential ở provider hoặc secret store; coi secret đã lộ là không còn an toàn.
3. Nếu đã commit hoặc push, tạo Issue bảo mật hạn chế quyền truy cập, loại secret khỏi lịch sử theo hướng dẫn phù hợp và cập nhật secret mới trong nơi lưu an toàn.
4. Kiểm tra log, deploy và các bản sao; ghi thời điểm, phạm vi, remediation và kết quả không chứa giá trị secret.
5. Tạo Decision Log nếu sự cố làm thay đổi provider, data policy hoặc demo fallback.
