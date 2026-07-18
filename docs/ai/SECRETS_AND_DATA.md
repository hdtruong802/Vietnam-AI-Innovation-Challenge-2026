# Chính sách secrets và dữ liệu

Mục tiêu là bảo vệ credentials và dữ liệu công dân trong khi vẫn cho phép team sáu người phát triển nhanh. Chính sách áp dụng ngang nhau cho mọi người và agent.

## Không được đưa vào Git, Task Record, Issue, PR hay prompt

- API key, token, password, private key, service-account JSON, cookie/session hoặc webhook có secret.
- PII/hồ sơ công dân thật: số định danh, địa chỉ chi tiết, ngày sinh, thông tin cha mẹ, án tích hoặc tài liệu tải lên.
- Raw production export, log application payload, dữ liệu chưa được phép chia sẻ hoặc model/dataset lớn không cần cho demo.
- Screenshot/recording có secret, PII hoặc thông tin tài khoản/cloud không cần thiết.
- Raw coding-agent session, assistant response, system/developer prompt, tool call/output, chain-of-thought, cookie/account metadata hoặc absolute source path.

Chỉ dùng tên biến và placeholder vô hại trong `.env.example`. Không copy `.env` hoặc ignored config giữa worktree/peer.

## AI Log prompt-only

- Chỉ commit `UserPrompt` thực sự phát sinh trong source coding-agent đã bind với đúng workspace repo; Codex, Claude, Cursor và Antigravity dùng cùng schema/quyền.
- Mỗi clone/worktree chạy `onboard` một lần và `doctor --strict`; local source path, hook executable và checkpoint chỉ nằm trong ignored `.ai-log/`. Hook commit tự stage evidence nhưng không tự push.
- Prompt được sanitize trước khi ghi. Token/private key, email, số điện thoại/định danh và user-home path được thay bằng marker; prompt quá giới hạn bị omit và commit chỉ mang warning metadata.
- Source path, checkpoint và exclusion nằm trong `.ai-log/` ignored. Evidence chỉ giữ session hash một chiều, adapter/version, Task Record, branch và prompt đã sanitize.
- Adapter lỗi hoặc workspace thiếu metadata không được fallback sang quét home hay commit raw source; tạo `warning`/gap và tiếp tục commit theo D-009.
- AI Log không phải bằng chứng session/screenshot theo nghĩa đen. Nếu ban tổ chức bắt buộc các artifact đó, team cần chấp thuận gói nộp ngoài Git riêng thay vì mở rộng ngầm log này.

## Nguồn dữ liệu dự kiến

| Nguồn | Mục đích | Tình trạng quyền/độ tin cậy | PII | Nơi truy cập | Task/Decision |
| --- | --- | --- | --- | --- | --- |
| [Cổng Dịch vụ công Quốc gia](https://dichvucong.gov.vn/) | Thủ tục, thành phần hồ sơ, quy trình, biểu mẫu công khai | Nguồn chính thức; từng pack cần review/version | Không thu thập hồ sơ người dùng | Public web/offline ingestion | D-007, D-006 |
| [Cổng Thông tin điện tử Chính phủ](https://chinhphu.vn/) và văn bản Chính phủ | Căn cứ hiệu lực, thay đổi quy định | Nguồn chính thức; kiểm tra effective date | Không | Public web/offline ingestion | D-006 |
| Catalog biểu mẫu theo lĩnh vực | Form schema/reference | URL/license/phiên bản cụ thể `TBD` | Không dùng dữ liệu đã điền | `TBD` | Task procedure research |
| Synthetic demo/golden cases | Test và demo ba thủ tục | Team tự tạo, không mô phỏng người thật | Không | Repo/seed sau scaffold | Task evaluation `TBD` |

`raw.md` là phân tích nội bộ, không phải nguồn quy phạm và không được ingestion như procedure evidence.

## Source governance

- Mốc khóa nguồn ban đầu là 2026-07-17. Văn bản có hiệu lực tương lai không được dùng như quy định hiện hành.
- Procedure pack phải lưu source refs, effective dates, `last_verified_at`, review status và checksum.
- Chỉ pack đã human-review mới phục vụ `verified_guidance`. Nguồn thiếu, cũ hoặc mâu thuẫn phải chuyển `official_review_required`.
- License/quyền tái sử dụng và attribution của từng nguồn/biểu mẫu phải được xác minh trước khi lưu bản sao hoặc phát hành dataset.
- Không scrape vượt điều khoản/rate limit; ingestion mechanism cụ thể là `TBD` và cần Task Record.

## Data minimization cho application đề xuất

- Dữ liệu form ở client hoặc xử lý transient; database không lưu raw application/PII trong MVP.
- Không gửi identifier value hoặc raw form payload vào LLM. LLM chỉ nhận context giảm thiểu cần cho câu hỏi/giải thích.
- Deterministic validation chạy trên structured data; log chỉ lưu metric/finding đã redacted hoặc aggregate.
- UI có nút xóa phiên. Retention, analytics và telemetry là ngoài MVP hoặc mặc định tắt cho đến khi có Decision.
- Demo, tests, screenshots và recordings chỉ dùng synthetic personas/cases.

## Quản lý biến môi trường

- Dùng `.env` local hoặc secret manager của nền tảng; file thật luôn bị ignore.
- Khi thêm variable, cập nhật `.env.example` bằng tên, mô tả và placeholder; không ghi giá trị thật.
- Trước khi gửi dữ liệu cho provider, xác minh retention/training/data residency và mức nhạy cảm. Chưa rõ thì không gửi.
- Deploy secret chỉ được provision sau khi D-006 Accepted, hosting target tồn tại và quyền tối thiểu được xác định.

## Kiểm tra trước commit/PR/deploy

- [ ] Không có `.env`, credentials, token/private key hoặc service-account file trong staged/range.
- [ ] Không có PII/raw form/log/screenshot nhạy cảm.
- [ ] Nguồn mới có URL, effective date, permission/license và Task Record.
- [ ] Golden/demo data là synthetic và không trùng người thật có thể nhận diện.
- [ ] LLM payload test chứng minh không chứa identifier/raw PII.
- [ ] `.env.example` chỉ chứa placeholder; deploy log không in secret.

## Nếu nghi ngờ lộ secret hoặc dữ liệu

1. Dừng chia sẻ/commit/push/deploy và báo team qua kênh riêng; không chép giá trị vào Issue công khai.
2. Rotate credential hoặc cô lập dữ liệu ở provider/secret store.
3. Xác định commit/log/deploy/screenshot bị ảnh hưởng và loại bỏ theo quy trình được peer chấp thuận.
4. Ghi timeline, scope, remediation và evidence đã redacted.
5. Tạo Decision nếu sự cố làm thay đổi provider, data policy hoặc demo fallback.
