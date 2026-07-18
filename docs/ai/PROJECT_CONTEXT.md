# Project Context — AI Procedure Copilot

> Trạng thái: Active
>
> Cập nhật gần nhất: 2026-07-17
>
> Người cập nhật: Antigravity
> Issue/Decision liên quan: D-005

Tài liệu này là context sản phẩm tối thiểu cho tất cả thành viên và agent.

## Bài toán và người dùng

- **Đề bài / challenge:** AI-guided public service procedures
- **Vấn đề cần giải quyết:** Khi thực hiện thủ tục hành chính (đăng ký khai sinh, thường trú, hộ kinh doanh), công dân gặp 3 cản trở: không biết cần chuẩn bị gì, kê khai sai thông tin mà chỉ biết sau khi cán bộ duyệt, hỗ trợ một cửa quá tải.
- **Người dùng chính:** Công dân làm thủ tục lần đầu, người lớn tuổi, cá nhân chuẩn bị thành lập hộ kinh doanh.
- **Bối cảnh sử dụng:** Chuẩn bị hồ sơ trực tuyến trước khi nộp cổng dịch vụ công trực tuyến.
- **Insight hoặc bằng chứng:** Khó khăn lớn nhất không phải thiếu ô chat, mà là thiếu quy trình chuẩn bị hồ sơ cá nhân hóa, kiểm tra và truy nguyên nguồn quy phạm.
- **Giá trị khác biệt trong một câu:** VNGov là trợ lý hướng dẫn và kiểm tra deterministic hồ sơ dịch vụ công dựa trên quy định pháp luật hiện hành và có trích dẫn nguồn cụ thể.

## MVP và giới hạn

## MVP phải demo được

1. **Guided Intake:** Nhận mô tả nhu cầu bằng tiếng Việt tự nhiên, hỏi làm rõ, hiển thị checklist thủ tục cá nhân hóa có trích dẫn nguồn.
2. **Pre-submission Checking:** Phát hiện trường thiếu, sai định dạng, mâu thuẫn chéo trên form kê khai hoặc giấy tờ đính kèm; hiển thị lỗi "đỏ - vàng - xanh" kèm gợi ý sửa.
3. **Integration Widget:** Widget chat có thể nhúng trực tiếp vào các portal hiện có thông qua iframe.

### Tiêu chí thành công

- **Demo end-to-end thành công khi:** Người dùng có thể mô tả nhu cầu, nhận hướng dẫn, điền form và nhận feedback lỗi chính xác trên 3 thủ tục MVP.
- **Chỉ số hoặc tín hiệu đánh giá:** Khớp tối thiểu 90% trên 30 golden cases, 100% citation coverage cho quy phạm trong pack.
- **Thời gian phản hồi/chất lượng tối thiểu:** P95 response cho validation < 1s, AI turn < 5s.

### Không làm trong hackathon

- Tích hợp thật với Cơ sở dữ liệu dân cư quốc gia.
- OCR tự động quét giấy tờ nâng cao.
- Auto-submit hồ sơ thật lên Cổng DVCQG.

## User flow và demo path

| Bước | Người dùng làm gì | Hệ thống phản hồi gì | Fallback nếu lỗi |
| --- | --- | --- | --- |
| 1 | Nhập nhu cầu (ví dụ: "Tôi muốn làm khai sinh cho con") | Gợi ý thủ tục "Đăng ký khai sinh", hiển thị các câu hỏi làm rõ (jurisdiction, mối quan hệ) | Trả về danh mục chung của 3 thủ tục chính |
| 2 | Trả lời câu hỏi làm rõ | Hiển thị checklist giấy tờ cần thiết, các bước thực hiện và form điền tương ứng | Hiển thị checklist đầy đủ nhất (không cá nhân hóa) |
| 3 | Điền thông tin vào form | Chạy validation engine để quét lỗi định dạng, logic chéo, thiếu trường và hiển thị cảnh báo đỏ-vàng-xanh | Trả về kết quả kiểm tra deterministic cơ bản (required fields) |

- **Happy path bắt buộc:** Nhập nhu cầu -> Trả lời câu hỏi làm rõ -> Xem checklist -> Điền biểu mẫu -> Nhận kết quả kiểm tra tiền kiểm.
- **Demo data/seed cố định:** 30 golden cases cho 3 thủ tục MVP.
- **Điều không được hứa hẹn trong demo:** Hoàn thành nộp hồ sơ thật hoặc lấy thông tin từ hệ thống thật của chính phủ.

## Quyết định kỹ thuật tối thiểu

| Hạng mục | Quyết định hiện tại | Chủ sở hữu tạm thời / Issue | Trạng thái |
| --- | --- | --- | --- |
| Frontend | Next.js (App Router, TS, Tailwind) | Antigravity | Accepted |
| Backend/API | Python (FastAPI, Uvicorn) | Antigravity | Accepted |
| AI/model/provider | Provider-neutral adapter | Antigravity | Proposed |
| Data/storage | Neon Postgres (pgvector) | Antigravity | Proposed |
| Deploy/demo runtime | Vercel (FE), Render (BE) | Antigravity | Proposed |
| Kiểm thử/check command | pytest, validate_repo.py | Antigravity | Accepted |

Mọi lựa chọn ảnh hưởng shared API, dependency, deploy hoặc demo flow phải có entry trong `DECISIONS.md`.

## Lệnh chuẩn

Chỉ điền lệnh đã chạy được; không ghi lệnh suy đoán.

```bash
# Prerequisites
- Python >= 3.13
- Node >= 24.0

# Install
# Backend
cd backend && pip install -r requirements.txt
# Frontend
cd frontend && npm install

# Run locally
# Backend (chạy tại port 8000)
cd backend && uvicorn main:app --port 8000 --reload
# Frontend (chạy tại port 3000)
cd frontend && npm run dev

# Check / test
python scripts/ci/validate_repo.py
cd backend && pytest
```

## Interface ownership tạm thời

| Interface / boundary | Consumer | Owner tạm thời | Contract / Decision | Trạng thái |
| --- | --- | --- | --- | --- |
| API REST V1 | Frontend Next.js | Antigravity | D-005 / docs/ai/ARCHITECTURE.md | Proposed |

Owner trong bảng chỉ sở hữu việc phối hợp contract hiện tại, không phải vai trò cố định hay quyền cao hơn peer.

## Priorities, rủi ro và blocker

| Ưu tiên | Việc / Issue | Rủi ro hoặc blocker | Mitigation / fallback |
| --- | --- | --- | --- |
| P0 | Khởi tạo khung dự án | Không chạy được local do môi trường | Đảm bảo code chạy độc lập và không phụ thuộc thư viện native nặng |
| P0 | API Contracts | Thay đổi cấu hình API giữa chừng gây vỡ FE | Khóa API contracts trong ARCHITECTURE.md trước khi dev sâu |
| P1 | UI/Widget | Trình duyệt chặn iframe hoặc xung đột CSS | Sử dụng Web Component để bọc iframe |

## Cập nhật context

- Cập nhật tài liệu này khi MVP, demo flow, lệnh chạy, stack, shared contract hoặc rủi ro quan trọng đổi.
- Liên kết Issue/PR/Decision tương ứng thay vì ghi lại các chi tiết mâu thuẫn ở nhiều nơi.
- Mọi agent phải coi giá trị `TBD` là điều cần làm rõ, không phải quyền tự chọn một giải pháp lớn.
