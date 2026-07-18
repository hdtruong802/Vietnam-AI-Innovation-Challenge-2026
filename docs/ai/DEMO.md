# Demo runbook

> Trạng thái: `Draft — có scaffold local, chưa có product flow/public URL`
>
> Demo owner tạm thời / Task Record: `TBD`
>
> Bản demo/commit đã kiểm chứng: `TBD`
>
> Lần diễn tập gần nhất: `TBD`

Runbook này chốt narrative và evidence cần có, không tuyên bố demo đã được triển khai. Demo owner chỉ điều phối một Task Record; mọi peer đều có quyền tiếp nhận/review theo protocol.

## Mục tiêu và thông điệp

- **Vấn đề:** công dân không biết chuẩn bị gì, phát hiện lỗi quá muộn và phải hỏi/đi lại nhiều lần.
- **Người dùng:** công dân lần đầu làm thủ tục, người lớn tuổi hoặc ít quen ngôn ngữ hành chính và người đăng ký thành lập hộ kinh doanh; cán bộ/portal operator là người hưởng lợi gián tiếp.
- **Thông điệp:** Procedure Copilot biến một nhu cầu tự nhiên thành checklist có nguồn, hướng dẫn từng bước và pre-check deterministic trước khi nộp.
- **Điểm AI-native:** hội thoại hỏi làm rõ + structured procedure retrieval + giải thích có citations; LLM không phán quyết hồ sơ hợp lệ.
- **Kết quả giám khảo phải thấy:** luồng thật trên public URL, báo lỗi/thiếu/xung đột, trust/freshness evidence và widget/API integration.
- **Delivery surface:** standalone web app + widget/iframe + headless API; không có mobile/native demo path.

## Luồng demo tối thiểu

```text
Mô tả nhu cầu
  -> xác định một trong ba thủ tục và hỏi làm rõ
  -> checklist cá nhân hóa có nguồn
  -> hướng dẫn từng bước
  -> form động
  -> kiểm tra thiếu/sai/xung đột
  -> đạt kiểm tra sơ bộ hoặc danh sách việc cần sửa
```

Ba MVP là đăng ký khai sinh, đăng ký thường trú và đăng ký thành lập hộ kinh doanh. Vertical slice ưu tiên khai sinh; cả ba pack vẫn phải dùng cùng contract/evaluation depth theo D-007.

## Kịch bản demo draft

| Chặng | Hành động | Bằng chứng cần hiện | Fallback cần chuẩn bị |
| --- | --- | --- | --- |
| Problem | Nêu nhu cầu công dân bằng tiếng Việt tự nhiên | Procedure được recommend và lý do/câu hỏi làm rõ | Chọn scenario synthetic cố định |
| Guidance | Trả lời clarification | Checklist/steps cá nhân hóa, source refs, version/date | Approved pack snapshot không phụ thuộc provider |
| Pre-check | Điền cố ý một lỗi thiếu, format hoặc xung đột | Rule finding gắn đúng field và gợi ý sửa | Chạy validation deterministic trực tiếp |
| Resolution | Sửa dữ liệu và validate lại | “Đạt kiểm tra sơ bộ”, không phải “được duyệt” | Hiển thị báo cáo seed đã kiểm chứng |
| Integration | Nhúng widget trên static host độc lập | Portal host nạp được widget; API/health và container behavior hoạt động | Standalone web app + architecture/API evidence |

Mốc thời gian và người trình bày là `TBD` cho đến khi ban tổ chức công bố giới hạn presentation và team phân công.

## Evidence theo rubric

| Rubric | Evidence demo/tài liệu cần có |
| --- | --- |
| Technical — 20 | Public API, schema/rule engine, tests, live deploy. |
| AI-Native Architecture — 20 | Clarification, structured output, grounded retrieval, provider adapter. |
| Business/Pilot — 20 | Widget + headless API, KPI vận hành và roadmap 90 ngày. |
| AI-Native UX — 15 | Chat chuyển thành form, plain Vietnamese, keyboard/focus/contrast, browser zoom và portal-container usability. |
| Safety/Trust — 15 | Citations, effective dates, fail closed, PII minimization. |
| Presentation — 10 | Luồng live, system diagram, evaluation evidence và fallback. |

## Preflight trước diễn tập

- [ ] Đúng branch/commit, public URL và procedure-pack version đã ghi.
- [ ] Application CI, deployment smoke và `GET /health` pass.
- [ ] Scenario dùng dữ liệu synthetic; không có raw PII, token hoặc tab/terminal nhạy cảm.
- [ ] Source refs/effective dates đã review theo mốc dữ liệu hiện hành.
- [ ] Happy path và ít nhất một lỗi deterministic chạy được.
- [ ] Widget nhúng trên static host độc lập; standalone URL là fallback.
- [ ] Có fallback cho network/provider/deploy và một peer biết cách chuyển.
- [ ] Trình duyệt mục tiêu, portal-container/overflow, bàn phím, focus, contrast, browser zoom và thông điệp trust đã review.
- [ ] KPI/evaluation được gọi đúng là target hoặc kết quả đo có evidence, không trộn lẫn.
- [ ] Mỗi member đã chạy AI Log `doctor --strict`; commit evidence/trailer và warning gaps đã được repository guard kiểm tra.
- [ ] Gói bằng chứng AI không chứa raw session, assistant output, secret/PII hoặc absolute source path.

## Bằng chứng sử dụng coding agent

AI Log prompt-only ánh xạ `UserPrompt` đã sanitize với member, tool, Task Record, branch và commit. Dùng `python scripts/ai_log/ai_log.py build-index --range <base...head>` để tạo index local phục vụ tổng hợp; index không được commit mặc định.

Đây là compliance gap nếu ban tổ chức bắt buộc đúng file desktop session và screenshot. Trước khi nộp, team phải có một trong hai bằng chứng: xác nhận ban tổ chức chấp thuận AI Log prompt-only, hoặc một gói ngoài Git được review riêng và không chứa secret/PII. Không tự mở rộng AI Log thành raw transcript.

## Lệnh và evidence đã kiểm chứng

Scaffold đã có, nhưng chưa có evidence chung rằng product flow/local checks/deploy đã pass. Các lệnh source hiện có là:

```text
Backend start: `cd backend; uvicorn main:app --port 8000 --reload`
Frontend start: `cd frontend; npm run dev`
Application test/build: theo manifest và Task Record; chưa có evidence chung
Deploy smoke: TBD
Demo seed/reset: TBD
```

| Kiểm tra | Kết quả mong đợi | Evidence / ngày | Peer |
| --- | --- | --- | --- |
| Guided intake | Đúng procedure/câu hỏi làm rõ | `TBD` | `TBD` |
| Checklist/citations | Có version/source/date/trust | `TBD` | `TBD` |
| Deterministic validation | Bắt đúng lỗi seed, không LLM verdict | `TBD` | `TBD` |
| Provider failure | Guidance seed/rules vẫn giải thích được | `TBD` | `TBD` |
| Fresh startup/deploy | Public URL và health pass | `TBD` | `TBD` |

## Fallback matrix

| Điểm lỗi | Fallback dự kiến | Điều kiện quay lại |
| --- | --- | --- |
| LLM/provider | Scenario clarification đã seed; tiếp tục checklist/rule engine | Provider smoke pass lại |
| Retrieval/source conflict | `official_review_required` + nguồn chính thức | Pack được human-review/version lại |
| Deploy/API | Standalone fallback đã diễn tập hoặc video/screenshot evidence | Health + key API pass |
| Widget host | Mở standalone UI và trình API contract/embed evidence | Static host embed pass |
| Demo data | Reset synthetic scenario | Seed checksum xác nhận |

## Scope freeze và sign-off

- Sáu giờ cuối chỉ nhận thay đổi sửa P0 hoặc làm demo đáng tin hơn.
- Mọi thay đổi mới cần hai peer xác nhận, evidence và rollback/fallback trong Task Record/Decision.
- Mỗi rehearsal cập nhật commit, URL, source versions, lỗi, owner follow-up và phần chưa kiểm chứng; không chỉ ghi “đã test”.
