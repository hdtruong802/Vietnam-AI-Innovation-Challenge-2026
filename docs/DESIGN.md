---
name: VNGov AI Copilot
description: Hệ thống trợ lý hướng dẫn và tiền kiểm hồ sơ hành chính công phong cách hiện đại VNGov (Navy & Orange)
colors:
  primary: "#0D1B3D"       # Deep Navy (Chữ chính, Header, Logo)
  neutral-bg: "#F8FAFC"    # Clean Off-white (Màu nền body)
  accent: "#F97316"        # Brand Orange (CTA chính, Link, Progress active)
  accent-light: "#FDBA40"  # Warm Gold (Màu nhấn phụ)
  warning: "#F59E0B"       # Amber (Cảnh báo vàng)
  error: "#EF4444"         # Red (Lỗi đỏ)
  success: "#10B981"       # Green (Đạt chuẩn xanh)
typography:
  display:
    fontFamily: "Geist Sans, Inter, sans-serif"
    fontSize: "clamp(2rem, 5vw, 3rem)"
    fontWeight: 800
    lineHeight: 1.2
  body:
    fontFamily: "Geist Sans, Inter, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: "6px"
  md: "10px"
  lg: "16px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  card:
    backgroundColor: "#FFFFFF"
    rounded: "{rounded.lg}"
    padding: "20px"
---

# Design System: VNGov AI Copilot (Navy & Orange)

## 1. Overview

**Creative North Star: "VNGov Digital Assistant - Modern Civic Product"**

Hệ thống thiết kế mới của **VNGov** hướng tới một giải pháp công nghệ dịch vụ hành chính công **hiện đại, năng động, và đáng tin cậy**, sử dụng hai tông màu thương hiệu chính là **Xanh Navy đậm (`#0D1B3D`)** và **Cam thương hiệu (`#F97316`)**, kết hợp biểu tượng **Hoa sen cách điệu hình chữ V** (đại diện cho Việt Nam và sự vươn lên phát triển).

**Key Characteristics:**
- **Dual-View Layout:** Hỗ trợ giao diện trang chủ Landing Page giới thiệu năng lực sản phẩm và giao diện workspace 2 cột của Trợ lý AI Copilot.
- **Brand Geometry:** Sử dụng các đường nét bo góc mềm mại vừa phải (`rounded-xl` / 12px), giao diện phẳng tinh giản với bóng mờ siêu nhỏ, giữ giao diện sạch sẽ tối ưu cho đọc biểu mẫu.
- **Cultural Texture:** Giữ các họa tiết Trống đồng Đông Sơn và Hoa sen truyền thống làm hình nền chìm (opacity < 5%) để tạo nét thanh tao Việt Nam mà không làm ảnh hưởng đến trải nghiệm đọc thông tin.

## 2. Colors

Bảng màu thương hiệu VNGov mới, hỗ trợ toàn diện chế độ sáng/tối (System Dark Mode).

### Primary & Foreground
- **Deep Navy** (#0D1B3D / #F8FAFC trong Dark Mode): Màu xanh hải quân đậm biểu thị sự vững chãi, tin cậy và chuyên nghiệp.

### Neutral
- **Clean Off-white** (#F8FAFC / #0A0F1D trong Dark Mode): Màu nền dịu mắt, tránh mỏi mắt cho người dân khi thao tác lâu.
- **Soft Slate Border** (#E2E8F0 / #1E293B trong Dark Mode): Màu viền phân chia các trường dữ liệu và thẻ.
- **Pure White Surface** (#FFFFFF / #111827 trong Dark Mode): Nền của các thẻ card biểu mẫu và khung chat.

### Accent
- **Brand Orange** (#F97316): Tông màu cam nổi bật biểu thị sự thân thiện, hướng ngoại, sử dụng cho các nút hành động chính (CTA) và trạng thái hiện tại.
- **Warm Gold** (#FDBA40): Tông màu phụ hỗ trợ trang trí và cảnh báo.

---

## 3. Typography

**Font Family:** Geist Sans / Inter / System-ui - Phông chữ Sans-serif hiện đại giúp tối ưu hóa khả năng hiển thị biểu mẫu số trên mọi thiết bị.

---

## 4. Components

### Buttons
- **Primary Action:** Nền cam thương hiệu `#F97316`, chữ trắng, bo góc 10px.
- **Secondary Action:** Nền Navy `#0D1B3D` hoặc viền mảnh `#E2E8F0`.

### Chat Bubbles
- **User Bubble:** Màu cam thương hiệu `#F97316`, chữ trắng, góc bo tròn hướng lên góc phải.
- **Assistant Bubble:** Nền trắng `#FFFFFF`, viền mảnh slate `#E2E8F0`, chữ tối màu.

### Stepper Progress
- Vòng tròn hiển thị tỷ lệ tiến độ dạng `2/5` màu cam.
- Cột mốc hoàn thành có tick xanh lá `#10B981`, cột mốc hiện tại có màu cam `#F97316`, các cột mốc tiếp theo có màu xám nhạt.

