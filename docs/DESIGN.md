---
name: AI Procedure Copilot
description: Hệ thống trợ lý hướng dẫn và tiền kiểm hồ sơ hành chính công phong cách di sản Việt Nam (Heritage style)
colors:
  primary: "#2E1A16"       # Deep Terracotta (Chữ chính & Header)
  neutral-bg: "#FAF6F0"    # Ivory Cream (Màu nền body)
  accent: "#B45309"        # Refined Bronze Gold (CTA chính & Link)
  warning: "#D97706"       # Amber (Cảnh báo vàng)
  error: "#DC2626"         # Red (Lỗi đỏ)
  success: "#16A34A"       # Green (Đạt chuẩn xanh)
typography:
  display:
    fontFamily: "Lora, Georgia, serif"
    fontSize: "clamp(2rem, 5vw, 3rem)"
    fontWeight: 700
    lineHeight: 1.2
  body:
    fontFamily: "Inter, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: "12px 24px"
  card:
    backgroundColor: "#FFFDFB"
    rounded: "{rounded.lg}"
    padding: "24px"
---

# Design System: AI Procedure Copilot (Heritage Version)

## 1. Overview

**Creative North Star: "The Digital Registry Bureau - Heritage & Culture Edition"**

Hệ thống thiết kế kết hợp hài hòa giữa tính **thực dụng (utilitarian)** của cổng dịch vụ công trực tuyến và **bản sắc văn hóa di sản Việt Nam**. Chúng tôi sử dụng các họa tiết hoa văn truyền thống như Trống đồng Đông Sơn và Hoa sen xanh/hồng kết hợp với bảng màu di sản ấm áp nhằm mang lại cảm giác trang trọng, đáng tin cậy và gần gũi với người dân Việt Nam.

**Key Characteristics:**
- **Dual-View Layout:** Hỗ trợ màn hình trang chủ cổng dịch vụ công đẹp mắt truyền thống và chuyển cảnh sang không gian Trợ lý tiền kiểm hồ sơ (Copilot Workspace) 2 cột tinh tế.
- **Họa tiết Vector Văn hóa:** Nhúng trực tiếp các hình vẽ Trống đồng Đông Sơn xoay vô cực và Hoa sen cách điệu bằng SVG để đảm bảo tải cực nhanh và sắc nét.
- **Độ rộng văn bản tối ưu:** Dòng văn bản giới hạn ở mức dễ đọc (65-75ch).

## 2. Colors

Bảng màu di sản Việt Nam (Heritage palette) với độ tương phản cao, hỗ trợ toàn diện chế độ sáng/tối (System Dark Mode).

### Primary & Foreground
- **Deep Terracotta** (#2E1A16 / #F5EFEB trong Dark Mode): Màu đất nung đậm cho văn bản và tiêu đề chính.

### Neutral
- **Ivory Cream** (#FAF6F0 / #1C0F0B trong Dark Mode): Màu nền giấy mỹ thuật ngà nhẹ nhàng, thanh tao.
- **Soft Warm Clay** (#EADBC8 / #3D251E trong Dark Mode): Màu viền nhẹ nhàng phân chia nội dung.
- **Ivory White** (#FFFDFB / #261611 trong Dark Mode): Màu nền cho các thẻ card, container biểu mẫu và khung chat.

### Accent
- **Bronze Gold** (#B45309 / #F59E0B trong Dark Mode): Màu nhấn vàng đồng thau cổ kính dùng cho nút bấm chính và biểu tượng quan trọng.

### Semantic
- **Amber Warning** (#D97706): Chỉ định các cảnh báo thiếu thông tin hoặc cần lưu ý.
- **Red Error** (#DC2626): Chỉ định các lỗi định dạng hoặc mâu thuẫn bắt buộc phải sửa.
- **Green Success** (#16A34A): Chỉ định các trường dữ liệu và hồ sơ đã đạt kiểm tra sơ bộ.

---

## 3. Typography

**Display Font:** Lora (Google Fonts Serif) - Mang lại sự trang trọng và tính pháp lý của cơ quan nhà nước.
**Body Font:** Inter / Geist Sans (Sans-serif) - Mang lại sự sạch sẽ, trực quan cho các ô nhập liệu và nhãn form.

### Hierarchy
- **Display** (700, Lora, clamp(2rem, 5vw, 3rem), 1.2): Tiêu đề trang chính và chào hỏi đầu trang.
- **Headline** (600, Lora, 1.5rem, 1.3): Tiêu đề các phần lớn (Checklist, Form).
- **Title** (600, Inter, 1.125rem, 1.4): Tên trường thông tin và các đề mục nhỏ.
- **Body** (400, Inter, 1rem, 1.6): Văn bản hướng dẫn, mô tả hồ sơ.
- **Label** (500, Inter, 0.875rem, 1.2): Nhãn phụ, ngày tháng, và trích dẫn nguồn luật.

---

## 4. Elevation & Shapes

- **Corner Style:** Các thẻ và khung giao diện chính dùng bo góc mềm mại `rounded-xl` (12px) hoặc `rounded-2xl` (16px) để tạo phong cách thân thiện, bay bổng.
- **Flat-ish Design:** Sử dụng màu nền phân lớp (ivory white trên nền ivory cream) kết hợp viền đất sét nhạt để phân tách chiều sâu, hạn chế dùng đổ bóng lớn gây cảm giác bồng bềnh phi thực tế.

---

## 5. Components

### Buttons
- **Primary:** Sử dụng màu đỏ đất đô (#7C1E14) hoặc vàng đồng (#B45309), chữ trắng (#FFFFFF), góc bo 8px.
- **Hover / Focus:** Hover tăng độ tương phản, hiển thị vòng focus-visible.

### Chat Bubbles
- **User Bubble:** Màu nền vàng đồng (#B45309), chữ trắng.
- **Assistant Bubble:** Nền trắng ngà (#FFFDFB), viền đất sét nhạt, chữ nâu đất.

### Form Inputs
- Nền trắng, viền đất sét nhạt (#EADBC8), focus chuyển sang vàng đồng thau với vòng sáng nhẹ 2px.

---

## 6. Do's and Don'ts

### Do:
- **Do** Luôn giữ liên kết trích dẫn luật định hành chính bên cạnh các hồ sơ.
- **Do** Đảm bảo độ tương phản màu văn bản trên nền kem luôn đạt WCAG AA.
- **Do** Sử dụng họa tiết Trống đồng và Hoa sen với độ mờ cao (opacity < 10%) để làm nền trang trí, không gây nhiễu chữ đọc.

### Don't:
- **Don't** Sử dụng chữ gradient nhiều màu hoặc các hiệu ứng kính mờ (glassmorphism) mặc định.
- **Don't** Dùng góc bo thẻ card quá lớn (>16px) gây cảm giác giống đồ chơi trẻ em.
- **Don't** Thay đổi bảng màu di sản ấm áp sang các tông lạnh xanh dương kiểu SaaS thông thường.
