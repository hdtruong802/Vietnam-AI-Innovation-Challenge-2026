---
name: "Lỗi"
about: "Báo cáo lỗi có thể tái hiện và kiểm thử sau khi sửa"
title: "[BUG] "
labels: "type:bug, status:ready"
assignees: ""
---

<!-- Chỉ tạo Issue sau khi Task Record cục bộ đã rõ. Dán record/snapshot bên dưới; Issue là bản publish, không thay thế ownership local. -->

## Task Record và context pack cục bộ

- **Task ID:** `T-...`
- **Mode:** `explore` | `implement` | `review` | `verify-demo`
- **Context pack đã đọc:**
- **Resource claims (files/API/runtime/data):**
- **Risk:** `risk:isolated` | `risk:shared`
- **Decision Log:** `D-XXX` | `Không có`

## Tóm tắt lỗi

<!-- Mô tả ngắn gọn tác động tới người dùng, demo hoặc đội thi. -->

## Môi trường

- Commit / nhánh:
- Hệ điều hành / trình duyệt:
- Phiên bản runtime hoặc dependency liên quan:

## Các bước tái hiện

1.
2.
3.

## Kết quả thực tế

## Kết quả mong đợi

## Mức độ ảnh hưởng

<!-- Chọn priority: p0 (chặn demo), p1 (ảnh hưởng lớn), p2 hoặc p3. -->

## Bằng chứng

<!-- Log đã che secret, ảnh chụp, video hoặc request/response tối thiểu. -->

## Giả thuyết nguyên nhân / hướng xử lý

<!-- Không bắt buộc. -->

## Tiêu chí hoàn tất

- [ ] Có test hoặc kịch bản tái hiện chứng minh lỗi đã được sửa.
- [ ] Không đưa secret, token hoặc dữ liệu nhạy cảm vào issue.

## Claim và publish scope

**Owner:** @

**Branch từ Task Record:** `fix/<task>-<slug>`

**Files/areas dự kiến chạm:**

**API/data contracts dự kiến chạm:**

<!-- Gắn labels khi publish. Peer xác nhận bắt buộc với risk:shared. -->
