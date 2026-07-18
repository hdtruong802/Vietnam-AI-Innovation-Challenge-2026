# Project Context — AI Procedure Copilot

> Trạng thái: ba MVP đã chốt; D-005 scaffold và D-006 target architecture được chấp thuận. Runtime trust/RAG/deploy chỉ được coi là có khi có evidence riêng.
>
> Cập nhật gần nhất: 2026-07-18
>
> Decision liên quan: D-005, D-006, D-007, D-008, D-009, D-010 và D-012

Tài liệu này là context sản phẩm tối thiểu cho mọi thành viên và coding agent. Nó phân biệt rõ phần đã có trong source với kiến trúc mục tiêu chưa được xác nhận bằng implementation/evidence.

## Bài toán và người dùng

- **Đề bài:** AI-guided public service procedures.
- **Tổ chức:** National Institute for Digital Technologies and Digital Transformation (NIDit).
- **Lĩnh vực:** Chính phủ Thông minh.
- **Vấn đề:** công dân chưa biết thủ tục, giấy tờ, biểu mẫu và nơi thực hiện; chỉ phát hiện thiếu/sai/xung đột sau khi cán bộ kiểm tra; kênh hỗ trợ quá tải gây nhiều lần đi lại.
- **Người dùng trực tiếp:** công dân làm thủ tục lần đầu, người lớn tuổi, người ít hiểu ngôn ngữ hành chính, người dùng dịch vụ công trực tuyến và người đăng ký thành lập hộ kinh doanh.
- **Người dùng gián tiếp:** cán bộ một cửa, tổng đài hỗ trợ, đơn vị vận hành portal và cơ quan quản lý thủ tục.
- **Giá trị khác biệt:** Procedure Copilot biến nhu cầu tự nhiên thành checklist có nguồn, form phù hợp tình huống và kiểm tra sơ bộ theo quy tắc trước khi nộp.

Nguồn dữ liệu mục tiêu là thủ tục, biểu mẫu và văn bản công khai từ [Cổng Dịch vụ công Quốc gia](https://dichvucong.gov.vn/) cùng nguồn chính thức có thẩm quyền. `raw.md` chỉ là phân tích nội bộ, không phải căn cứ pháp lý.

## MVP và giới hạn

### Ba procedure pack phải demo

1. Đăng ký khai sinh.
2. Đăng ký thường trú.
3. Đăng ký thành lập hộ kinh doanh.

Mỗi pack phải có clarification tree, checklist, quy trình, form schema, validation rules, citations và golden cases với mức hoàn thiện tương đương. D-007 là nguồn scope hiện hành; D-005 không phải quyết định phạm vi MVP.

### Ba năng lực bắt buộc

1. **Guided intake:** hiểu nhu cầu, hỏi làm rõ, đưa checklist cá nhân hóa và hướng dẫn từng bước có nguồn.
2. **Pre-submission checking:** phát hiện thiếu trường, sai định dạng và xung đột bằng schema/rules; gợi ý sửa trước khi nộp.
3. **Seamless integration:** một web app độc lập và đường tích hợp portal qua widget/iframe cùng REST API; không cần cài ứng dụng riêng.

### Happy path

```text
Mô tả nhu cầu
  -> xác định thủ tục và hỏi làm rõ
  -> checklist cá nhân hóa có nguồn
  -> hướng dẫn từng bước
  -> form theo trường hợp
  -> kiểm tra thiếu/sai/xung đột
  -> báo cáo việc cần sửa hoặc đạt kiểm tra sơ bộ
```

Kết quả quy phạm chỉ có ba trust state:

- `verified_guidance`: đủ nguồn và dữ kiện trong phạm vi pack đã review.
- `need_more_information`: cần người dùng cung cấp thêm dữ kiện.
- `official_review_required`: ngoại lệ, nguồn mâu thuẫn/hết hiệu lực hoặc ngoài phạm vi pack.

“Đạt kiểm tra sơ bộ” không phải phê duyệt hành chính và không bảo đảm cơ quan tiếp nhận chấp thuận hồ sơ.

### Thành phần đã có và chưa có

- D-005 đã chấp thuận scaffold `frontend/` và `backend/`. Backend hiện có API foundation gồm health, list/recommend/intake/checklist/validate, typed trust/error contract, deterministic rule engine và dev fixture fail-closed; frontend vẫn là khung giao diện khởi tạo. Đây chưa phải bằng chứng rằng Procedure Pack thật, widget, RAG, external AI hay deploy đã hoàn thành.
- D-006 chấp thuận target RAG/knowledge release, provider-neutral LLM, approved data adapter, PII boundary, widget contract và topology deploy. Backend chỉ tạo port/fallback; từng capability chỉ được tích hợp sau Task Record và evidence riêng. D-012 đã có API Cloud Run backend-only production-disabled tại [`vngov-api`](https://vngov-api-j53prjslqa-as.a.run.app); data/RAG/LLM vẫn disabled và CORS chưa có frontend origin.

### Tiêu chí thành công đề xuất

- Public URL chạy luồng nhập nhu cầu, hướng dẫn và kiểm tra thông tin; không phải mockup.
- Ba procedure pack có citations, version/freshness metadata và cùng contract.
- Ít nhất 30 golden cases phủ happy path, thiếu giấy tờ, sai định dạng, xung đột, ngoại lệ, mơ hồ và ngoài phạm vi.
- Có system diagram, model/API documentation, one-page summary và pilot roadmap.
- KPI trong proposal là **target phải đo**, không phải kết quả đã đạt.

### Ngoài MVP

- Native mobile app, mobile-specific flow, PWA install flow và app-store release.
- OCR/tải giấy tờ, voice, đa ngôn ngữ, analytics vận hành và trợ lý cán bộ.
- Tự động nộp hồ sơ, tích hợp CSDL dân cư hoặc hệ thống nghiệp vụ thật.

## User flow và fallback

| Bước | Người dùng làm gì | Hệ thống phản hồi | Fallback |
| --- | --- | --- | --- |
| 1 | Mô tả nhu cầu bằng tiếng Việt tự nhiên. | Đề xuất thủ tục và hỏi làm rõ. | `need_more_information` hoặc `official_review_required`. |
| 2 | Trả lời câu hỏi về trường hợp cụ thể. | Checklist, nguồn và bước thực hiện. | Chỉ dẫn kênh chính thức thay vì tự điền khoảng trống. |
| 3 | Điền form bằng dữ liệu demo hoặc dữ liệu phiên. | Rule engine báo thiếu/sai/xung đột và cách sửa. | Không dùng LLM để quyết định tính hợp lệ. |
| 4 | Sửa và kiểm tra lại. | Báo việc cần sửa hoặc đạt kiểm tra sơ bộ. | Chuyển `official_review_required` cho ngoại lệ/ngoài pack. |

- **Demo data:** chỉ dùng dữ liệu giả/synthetic, không dùng hồ sơ hoặc dữ liệu người thật.
- **Không hứa hẹn:** nộp hồ sơ tự động, kết quả phê duyệt, truy cập CSDL dân cư thật hoặc tư vấn pháp lý đầy đủ.

## Quyết định kỹ thuật và trạng thái

| Hạng mục | Trạng thái hiện tại | Decision |
| --- | --- | --- |
| Frontend web | Next.js scaffold trong `frontend/`; UI product/widget chưa hoàn tất | D-005 Accepted; D-008 Accepted |
| Backend/API | FastAPI integration foundation trong `backend/`; sáu routes, typed trust/error metadata, deterministic rules và dev fixture có sẵn; external data/RAG/LLM adapter chưa có | D-005 Accepted; D-006 Accepted |
| AI/model/provider | Provider-neutral adapter và provider cụ thể `TBD` | D-006 Accepted; runtime chưa triển khai |
| Data/RAG | Curated procedure packs, structured/vector retrieval và release governance chưa có evidence runtime | D-006 Accepted; runtime chưa triển khai |
| Deploy/demo runtime | Cloud Run backend-only production-disabled public API; public smoke pass, không có frontend URL/secret/CD | D-012 Accepted; frontend CORS/integration là task follow-up |
| Application checks | Lệnh bootstrap có sẵn; lint/test/build ứng dụng cần được xác minh theo Task Record | D-005 / task follow-up |

## Lệnh chuẩn

Chỉ dùng lệnh trong manifest hoặc có evidence local. Không xem việc có lệnh là bằng chứng capability product đã hoàn thiện.

```powershell
# Bootstrap guard
python scripts/ci/validate_repo.py

# Backend (chạy trong backend/ sau khi cài dependencies)
uvicorn main:app --port 8000 --reload
python -m pytest -q
black --check .
flake8 .

# Frontend (chạy trong frontend/ sau khi cài dependencies)
npm run dev
```

Lệnh cài dependency, lint/test/build và kết quả chạy phải được ghi vào Task Record/handoff của task tương ứng. Không đưa secret vào command, prompt hay log.

## Interface hiện có và interface mục tiêu

| Boundary | Consumer | Trạng thái |
| --- | --- | --- |
| `GET /health` | Smoke check | Có trong backend scaffold |
| `/v1/procedures`, `/v1/procedures/recommend`, `/v1/intake/turn`, `/v1/procedures/{id}/checklist`, `/v1/applications/validate` | Web UI / demo consumer | Contract foundation có trong backend; `verified_guidance` chỉ hợp lệ sau pack approved/K1, còn dev fixture luôn fail closed |
| Widget / standalone web app -> REST API | Portal host, web UI | Web-first direction được D-008 chấp thuận; embed contract chưa hoàn tất |
| Orchestrator -> approved procedure pack | Retrieval/checklist/validation | D-006 Proposed |
| LLM adapter -> provider | Orchestrator | D-006 Proposed; không gửi raw PII |

Owner là trách nhiệm tạm thời trong Task Record, không phải chức danh cố định.

## Rubric và ưu tiên

| Ưu tiên | Việc | Rủi ro | Mitigation / fallback |
| --- | --- | --- | --- |
| P0 | Source freeze và procedure-pack accuracy | Nguồn cũ/mâu thuẫn | Metadata hiệu lực, human review, fail closed. |
| P0 | Vertical slice guided intake -> checklist -> validation | Scope phân tán | Làm khai sinh trước, sau đó áp cùng contract cho hai pack còn lại. |
| P0 | Public demo + evidence | Network/provider/deploy lỗi | Smoke check, synthetic seed và rehearsal có fallback. |
| P1 | Widget/headless API integration | CSS/auth/CORS ở portal host | Iframe isolation, static-host embed test và failure UI. |
| P1 | UX web cho người không kỹ thuật | Ngôn ngữ hành chính khó hiểu hoặc container portal hạn chế | Plain Vietnamese, form theo bước, keyboard/focus/contrast, browser zoom và portal-container review. |
| P2 | Mở rộng sau MVP | Scope creep | Giữ các feature ngoài MVP trong roadmap. |

Rubric chính thức được ánh xạ trong `team_docs/proposal.md`: Technical 20, AI-Native Architecture 20, Business Viability 20, AI-Native UX 15, Safety/Grounding/Trust 15, Presentation/Demo/Defensibility 10.

## Cập nhật context

- Data/source freeze mục tiêu: 2026-07-17. Nguồn có hiệu lực tương lai không được dùng như quy định hiện hành.
- Cập nhật tài liệu này khi MVP, user flow, application commands, shared contract hoặc risk quan trọng đổi.
- Mọi chi tiết chưa xác minh là `TBD`; hướng dẫn thiếu nguồn phải chuyển `official_review_required`.
- Thay đổi D-006 cần peer confirmation và Decision mới hoặc cập nhật trạng thái theo protocol.
