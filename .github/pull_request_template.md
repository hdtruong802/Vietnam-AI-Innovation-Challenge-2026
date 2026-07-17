## Tóm tắt

<!-- Nêu thay đổi theo ngôn ngữ sản phẩm; không chỉ liệt kê tên file. -->

## Task Record và context pack cục bộ

- **Task ID:** `T-...`
- **Mode khi bàn giao:** `explore` | `implement` | `review` | `verify-demo`
- **Context/Decision đã dùng:**
- **Resource claims đã hoàn tất hoặc release:**

## Issue liên quan (tùy chọn)

<!-- Chỉ điền khi team đã publish Task Record thành Issue. -->

Closes #

## Thay đổi chính

-

## Cách kiểm thử / demo

<!-- Lệnh đã chạy và kết quả, hoặc các bước thủ công để reviewer xác nhận. -->

## Rủi ro, rollback và việc còn lại

<!-- Ghi "Không có" nếu không áp dụng. -->

## Risk và peer confirmation

- [ ] `risk:isolated`: không thay đổi shared API, schema, dependency, deploy hoặc demo flow.
- [ ] `risk:shared`: đã có peer confirmation và link Decision Log bên dưới.

**Peer confirmation / Decision Log (bắt buộc khi `risk:shared`):**

## Checklist trước khi merge

- [ ] PR chỉ giải quyết một mục tiêu/issue rõ ràng và nhắm vào `dev` (trừ release/hotfix).
- [ ] Task Record có context pack, claims, acceptance criteria và handoff trước khi publish PR.
- [ ] Đã tự review diff, đặc biệt các thay đổi được tạo với agent AI.
- [ ] Không có secret, file `.env`, dữ liệu nhạy cảm hoặc artifact lớn ngoài chủ đích.
- [ ] Đã cập nhật test, hướng dẫn hoặc cấu hình khi thay đổi yêu cầu điều đó.
- [ ] Đã kiểm thử theo phần “Cách kiểm thử / demo”.
- [ ] Nếu là `risk:shared`, đã có xác nhận của ít nhất một peer; nếu ở 6 giờ cuối, đã có hai peer xác nhận.

## Ảnh / video demo

<!-- Bắt buộc khi thay đổi UI hoặc luồng demo; xóa mục này nếu không áp dụng. -->
