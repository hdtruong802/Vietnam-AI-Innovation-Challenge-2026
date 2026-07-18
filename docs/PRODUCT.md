# Product design context

> Adapter thiết kế tối thiểu cho Impeccable. Source of truth về bài toán, MVP và scope là [Project Context](ai/PROJECT_CONTEXT.md); delivery surface theo D-008, product scope theo D-007 và kiến trúc/UI stack vẫn theo D-006 `Proposed`.

## Register and platform

- **Product register:** tin cậy, bình tĩnh, rõ ràng và phục vụ công dân; tránh giọng điệu quảng cáo hoặc khẳng định chắc chắn thay cơ quan có thẩm quyền.
- **Platform:** web-first gồm standalone web app và widget/iframe nhúng portal; không có native mobile/PWA install/app-store deliverable. D-005 đã có scaffold Next.js/FastAPI; UI product, widget và các capability D-006 vẫn chưa hoàn tất.
- **Locale and content:** tiếng Việt đơn giản là ưu tiên MVP; dùng dữ liệu synthetic trong demo/audit, không dùng PII thật.

## Users and job to be done

- **Primary users:** công dân làm thủ tục lần đầu, người lớn tuổi, người ít hiểu ngôn ngữ hành chính, người sử dụng dịch vụ công trực tuyến và người đăng ký thành lập hộ kinh doanh.
- **Indirect users:** cán bộ một cửa, tổng đài hỗ trợ, đơn vị vận hành portal và cơ quan quản lý thủ tục.
- **Critical journey:** mô tả nhu cầu -> trả lời câu hỏi làm rõ -> nhận checklist/steps có nguồn -> điền form động -> sửa thiếu/sai/xung đột.
- **Demo-critical state:** checklist cá nhân hóa có citations và báo cáo kiểm tra sơ bộ theo rule.
- **Failure/empty state:** hỏi thêm thông tin hoặc chuyển `official_review_required`; không tự sinh hướng dẫn quy phạm khi thiếu căn cứ.

## Positioning

- **Value proposition:** Procedure Copilot giúp người dùng chuẩn bị đúng hơn trước khi nộp và giúp kênh hỗ trợ giảm các câu hỏi lặp lại.
- **Điểm khác biệt:** hội thoại chỉ là đầu vào; đầu ra là structured checklist, dynamic form, deterministic validation và nguồn có phiên bản.
- **Điều phải quen thuộc:** ngôn ngữ, thứ tự bước, biểu mẫu và kênh chính thức; không tạo thuật ngữ AI khó hiểu.
- **Non-goals:** không tự nộp hồ sơ, không thay cán bộ phê duyệt, không hiển thị “độ sẵn sàng” phần trăm thiếu căn cứ và không đưa OCR/voice/đa ngôn ngữ vào MVP.
- **Integration posture:** thiết kế cho portal sandbox và integration contract trong tương lai; không tuyên bố đã tích hợp Cổng DVCQG khi chưa có authorization/evidence.

## UX states bắt buộc

| Trust state | Cách thể hiện |
| --- | --- |
| `verified_guidance` | Hiển thị nguồn, ngày xác minh, phiên bản pack và bước tiếp theo. |
| `need_more_information` | Hỏi một nhóm câu ngắn, giải thích vì sao cần thông tin đó. |
| `official_review_required` | Nêu rõ giới hạn và đưa người dùng về nguồn/kênh chính thức. |

Thông báo cuối luồng chỉ được dùng “đạt kiểm tra sơ bộ”, không dùng ngôn ngữ “được duyệt” hoặc “hồ sơ chắc chắn hợp lệ”.

## Accessibility baseline

- Hỗ trợ bàn phím, focus-visible, cấu trúc semantic và văn bản dễ đọc.
- Kiểm tra contrast, reduced motion, browser zoom, portal-container widths và overflow/iframe resizing sau khi tokens/components được chốt.
- Progressive disclosure cho câu hỏi làm rõ và lỗi form; lỗi phải gắn với trường, có mô tả bằng chữ, không chỉ dựa vào màu.
- Impeccable chỉ là audit advisory, không thay accessibility/manual usability review.

## Visual system còn TBD

Tokens, typography, component variants, spacing, color palette và motion vẫn `TBD`. Chúng chỉ được chốt trong Task Record UI `risk:shared` và đồng bộ sang [DESIGN.md](DESIGN.md); nội dung ở đây không cấp quyền thêm dependency hoặc tự chọn design system.

## Update contract

1. Product/demo peer cập nhật Project Context khi problem, audience, MVP hoặc non-goal đổi.
2. Owner UI task đồng bộ phần bị ảnh hưởng ở đây và trong DESIGN.md.
3. Shared visual change cần Task Record, peer review và Decision Log theo protocol.
