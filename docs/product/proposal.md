# Proposal v2 — AI Procedure Copilot

> Đề bài: **AI-guided public service procedures**
> Tổ chức: **National Institute for Digital Technologies and Digital Transformation (NIDit)**
> Lĩnh vực: **Chính phủ Thông minh**
> Trạng thái: D-005 có scaffold source; ba MVP theo D-007, web-first theo D-008 đã chốt; trust/RAG/deploy D-006 đang `Proposed`
> Source freeze: **17/07/2026**

Delivery surface theo D-008 là **web-first**: standalone web app trên public URL, widget/iframe nhúng portal và headless API. MVP không có native mobile, PWA install flow hoặc app-store artifact; integration với Cổng DVCQG thật vẫn cần sandbox và authorization.

## One-page summary

### Vấn đề

Khi thực hiện thủ tục hành chính, công dân thường gặp ba điểm nghẽn:
- Không biết chính xác phải chuẩn bị giấy tờ/biểu mẫu/nơi thực hiện nào;
- Chỉ phát hiện thiếu, sai hoặc mâu thuẫn sau khi cán bộ kiểm tra;
- Và phải hỏi hoặc đi lại nhiều lần vì kênh hỗ trợ quá tải.

Khó khăn lớn nhất không phải thiếu một ô chat, mà là thiếu một quy trình chuẩn bị hồ sơ có thể cá nhân hóa, kiểm tra và truy nguyên nguồn.

### Giải pháp

**VNGov** là trợ lý chuẩn bị thủ tục, không phải chatbot hỏi đáp tổng quát. Người dùng mô tả nhu cầu bằng tiếng Việt; Copilot xác định thủ tục, hỏi các câu làm rõ tối thiểu, tạo checklist có nguồn, hướng dẫn từng bước, sinh form theo trường hợp và kiểm tra deterministic các trường thiếu/sai/xung đột trước khi nộp.

```text
Mô tả nhu cầu
  -> AI xác định thủ tục và hỏi làm rõ
  -> Checklist cá nhân hóa có nguồn
  -> Hướng dẫn từng bước
  -> Form cố định theo trường quy định nhà nước
  -> Đọc dữ liệu kê khai/tệp đính kèm, phát hiện trường thiếu, sai định dạng, mâu thuẫn chéo và giấy tờ chưa đạt chất lượng; hiển thị “đỏ - vàng - xanh” cùng cách sửa. (AI)
  -> “Đạt kiểm tra sơ bộ” hoặc danh sách việc cần sửa
  -> Chỉnh sửa hoặc submit (HITL)
```

LLM chỉ đảm nhiệm giao tiếp, hỏi lại và giải thích. Nội dung quy phạm đến từ **procedure pack đã review**; checklist và validation dựa trên structured data, JSON Schema và deterministic rules. Mọi hướng dẫn mang theo phiên bản, nguồn, ngày xác minh và trust state. Thiếu căn cứ thì hệ thống fail closed và chuyển về kênh chính thức.

### Phạm vi MVP

Ba procedure pack MVP hiện hành:

1. Đăng ký khai sinh.
2. Đăng ký thường trú.
3. Đăng ký thành lập hộ kinh doanh.

Mỗi thủ tục phải có cùng độ sâu: clarification tree, checklist, quy trình, form schema, validation rules, citations và golden cases. OCR/tải giấy tờ, voice, đa ngôn ngữ, analytics, trợ lý cán bộ, tự động nộp hồ sơ và kết nối CSDL dân cư thật chỉ nằm trong roadmap.

### Người dùng và giá trị

- **Trực tiếp:** công dân làm thủ tục lần đầu, người lớn tuổi, người ít hiểu ngôn ngữ hành chính, người dùng dịch vụ công trực tuyến và người đăng ký thành lập hộ kinh doanh.
- **Gián tiếp:** cán bộ một cửa, tổng đài hỗ trợ, đơn vị vận hành portal và cơ quan quản lý thủ tục.
- **Giá trị cho người dùng:** chuẩn bị đúng hơn, hiểu vì sao cần từng thông tin và sửa lỗi trước khi nộp.
- **Giá trị cho cơ quan:** giảm câu hỏi lặp lại/hồ sơ thiếu cơ bản và có một integration surface kiểm soát được.

### Sản phẩm và integration

Standalone Next.js UI và Web Component bọc iframe gọi FastAPI qua REST. Runtime tách intent/clarification, retrieval, checklist, rule validation, citation/freshness/escalation và provider-neutral LLM adapter. Procedure packs, metadata nguồn, schema/rules, chunks và golden cases được đề xuất lưu trong Neon PostgreSQL + pgvector. Offline ingestion luôn qua human review.

Public integration gồm widget và headless API; portal hiện hữu không yêu cầu người dân cài ứng dụng mới. Topology deploy đề xuất: Vercel (UI/widget), Render (API), Neon (database). Chưa có dịch vụ, URL, model/provider hoặc KPI thực đo nào được provision/khẳng định ở thời điểm proposal.

### Bằng chứng cần đạt

- Public live demo, không phải mockup: nhu cầu -> guidance -> pre-check.
- Tối thiểu 30 golden cases và rule/API tests.
- Citation coverage 100% cho hướng dẫn quy phạm trong phạm vi pack.
- Widget nhúng trên một static host độc lập.
- Architecture diagram, model/API documentation, one-page summary và pilot 90 ngày.
- UX test với ít nhất 5 người không thuộc team phát triển.

Các ngưỡng định lượng trong tài liệu là **target đề xuất**, chưa phải kết quả đã đạt.

## 1. Định vị: Procedure Copilot, không phải chatbot

Một chatbot tổng quát có thể trả lời trôi chảy nhưng khó bảo vệ ba câu hỏi: “nguồn nào?”, “đang áp dụng phiên bản nào?” và “vì sao báo hồ sơ sai?”. Procedure Copilot biến hội thoại thành trạng thái có cấu trúc và bằng chứng có thể review:

| Lớp | Nhiệm vụ | Không được làm |
| --- | --- | --- |
| LLM conversation | Hiểu cách diễn đạt, hỏi làm rõ, giải thích đơn giản | Tự thêm giấy tờ/quy định hoặc phán quyết hợp lệ |
| Retrieval/RAG | Tìm đúng đoạn trong approved pack theo jurisdiction/version | Truy hồi nguồn chưa review như ground truth |
| Structured procedure data | Giữ điều kiện, checklist, steps, form schema, nguồn/hiệu lực | Trộn nhiều phiên bản không có provenance |
| Deterministic rules | Kiểm tra required/format/cross-field/conflict | Dùng “cảm giác” của model thay rule/evidence |
| Trust policy | Gắn trạng thái, citations, freshness và escalation | Che giấu thiếu nguồn hoặc suy đoán để hoàn tất câu trả lời |

Ba trust state duy nhất:

- `verified_guidance`: đủ nguồn và dữ kiện trong phạm vi procedure pack đã review.
- `need_more_information`: cần người dùng trả lời thêm trước khi cá nhân hóa.
- `official_review_required`: ngoại lệ, ngoài phạm vi, nguồn mâu thuẫn/hết hiệu lực hoặc chưa đủ căn cứ.

Không hiển thị phần trăm “sẵn sàng” thiếu mô hình đo đã được hiệu chuẩn. Kết quả cuối chỉ là “đạt kiểm tra sơ bộ” hoặc danh sách việc cần sửa; cơ quan có thẩm quyền vẫn là bên quyết định.

## 2. SWOT và chiến lược

| Nhóm | Nhận định cô đọng |
| --- | --- |
| Strengths | Đề bài có user pain rõ, output có thể kiểm chứng; hội thoại + structured checklist + rule engine tạo khác biệt với search/chatbot. |
| Weaknesses | Dữ liệu thủ tục phân tán, thay đổi theo thời gian/jurisdiction; 48 giờ không đủ bao phủ mọi ngoại lệ hoặc tích hợp hệ thống thật. |
| Opportunities | Widget/API có thể pilot trên portal hiện hữu; procedure-pack contract mở đường thêm thủ tục mà không viết lại toàn bộ UX. |
| Threats | Hướng dẫn sai gây mất niềm tin; nguồn cũ/mâu thuẫn; PII leakage; model/provider/network latency; demo quá rộng nhưng thiếu evidence. |

Chiến lược chuyển hóa SWOT:

1. **Cá nhân hóa checklist, không trả danh sách chung:** clarification tree quyết định điều kiện áp dụng và required/optional items.
2. **Chỉ dùng procedure pack đã review:** không cho web search/live LLM biến nội dung chưa kiểm chứng thành hướng dẫn.
3. **Tách LLM, RAG, structured data và rules:** từng lỗi có thể quan sát, test và bảo vệ trước giám khảo.
4. **Widget lẫn headless API:** chứng minh business/pilot viability thay vì chỉ làm một màn hình demo.
5. **Fail closed:** khi thiếu/mâu thuẫn/ngoài phạm vi, nêu giới hạn và dẫn kênh chính thức.

## 3. Ba procedure pack MVP

Mỗi pack dùng cùng schema, evaluation contract và depth. Các yêu cầu giấy tờ/quy tắc cụ thể chỉ được điền sau khi procedure research peer xác minh nguồn đang có hiệu lực tại source freeze.

| Pack | Clarification cần xây | Form/validation cần chứng minh | Evidence bắt buộc |
| --- | --- | --- | --- |
| Đăng ký khai sinh | Trường hợp/người yêu cầu, jurisdiction và các điều kiện làm thay đổi checklist | Required fields, format, quan hệ logic và trường hợp cần official review | Checklist/steps/forms/citations + happy/missing/conflict/exception cases |
| Đăng ký thường trú | Nơi đăng ký, quan hệ/chỗ ở và điều kiện áp dụng theo pack đã review | Required/conditional fields, format và cross-field consistency | Cùng contract; không suy diễn điều kiện cư trú chưa có nguồn |
| Đăng ký thành lập hộ kinh doanh | Trường hợp đăng ký, chủ thể và các điều kiện làm thay đổi hồ sơ theo pack đã review | Required/conditional fields, format và cross-field conflicts theo form schema đã review | Cùng contract; chi tiết nghiệp vụ giữ `TBD` cho đến khi source registry và K1 hoàn tất |

Procedure-pack schema:

```text
procedure_id, name, jurisdiction, authority
eligibility_conditions
required_documents, optional_documents
steps, processing_time, fees, forms
intake_questions, form_schema, validation_rules
legal_sources, effective_from, effective_to, last_verified_at
review_status, checksum, conflict_fallback_sources
```

### Source governance

- Mốc dữ liệu ban đầu: 17/07/2026.
- Mỗi nguồn lưu URL/ref, authority, ngày hiệu lực, ngày hết hiệu lực nếu có, ngày xác minh và checksum.
- Nguồn có hiệu lực tương lai không được mô tả như quy định hiện hành. Ví dụ, [Luật Hộ tịch số 03/2026/QH16](https://xaydungchinhsach.chinhphu.vn/toan-van-luat-ho-tich-so-03-2026-qh16-119260527163142286.htm) được Cổng TTĐT Chính phủ công bố có hiệu lực từ 01/03/2027, nên phải tách khỏi pack hiện hành tại source freeze.
- Pack đăng ký thành lập hộ kinh doanh phải có source registry riêng, review authority/effective date/quyền sử dụng và K1 trước khi thêm checklist, form fields hoặc validation rules; thiếu căn cứ thì giữ `TBD` hoặc `official_review_required`.
- Nếu DVCQG, biểu mẫu và văn bản có nội dung mâu thuẫn, pack không đạt `approved`; chuyển `official_review_required` và đưa nguồn chính thức để người dùng kiểm tra.

## 4. UX và user flow

### Guided intake

1. Người dùng mô tả nhu cầu bằng câu tự nhiên.
2. Hệ thống recommend một procedure hoặc hỏi lại nếu chưa đủ tín hiệu.
3. Clarification theo progressive disclosure: chỉ hỏi điều làm thay đổi checklist/form.
4. Kết quả hiển thị tên thủ tục, cơ quan/jurisdiction, source/version/freshness và trust state.

### Checklist và hướng dẫn

- Chia required/conditional/optional rõ ràng.
- Mỗi mục giải thích ngắn “vì sao cần” và source liên quan.
- Steps dùng tiếng Việt đơn giản, có trạng thái tiến độ nhưng không tạo tỷ lệ “đủ điều kiện”.
- Khi cần xác minh chính thức, đưa link/kênh phù hợp thay vì câu trả lời tự tin giả.

### Dynamic form và pre-check

- Form sinh từ schema của pack, không để LLM tự tạo field runtime không có contract.
- Validation gồm required, type/format, conditional và cross-field conflict.
- Findings gắn field/rule/source, severity và gợi ý sửa có thể hành động.
- LLM có thể diễn giải finding nhưng không được đổi verdict của rule engine.

### Thiết kế cho người không kỹ thuật

- Web app hỗ trợ keyboard/focus-visible, contrast, browser zoom, portal-container widths/overflow và lỗi không chỉ dựa vào màu.
- Câu hỏi ngắn, một nhóm logic tại một thời điểm; giải thích thuật ngữ hành chính bằng ngôn ngữ phổ thông.
- Cho phép xem lại câu trả lời, xóa phiên và mở nguồn chính thức.
- Impeccable CLI dùng như audit advisory; không thay kiểm tra accessibility và usability thủ công.

## 5. Kiến trúc đề xuất

> **Trạng thái:** working proposal ở mức capability, chưa phải kiến trúc đã triển khai. Việc chọn framework, database, model provider và hosting được tách khỏi thiết kế này và vẫn `TBD` cho đến khi có Decision được peer xác nhận.

Kiến trúc mới tách rõ bốn vùng trách nhiệm: **Web FE**, **BE / Trust & Orchestration**, **RAG / Knowledge** và **Memory / Security**. Web FE gồm standalone web app và widget/iframe dùng cùng headless API để tạo đường tích hợp portal trong tương lai. [`diagram_v3.mmd`](../../team_docs/diagram_v3.mmd) được dùng làm input cho API Gateway, PII Guard, LLM Gateway và redacted audit; các ví dụ thủ tục/scrape trong sơ đồ không thay ba MVP hoặc quy trình dữ liệu đã chốt. RAG chỉ lưu tri thức thủ tục công khai đã được duyệt; memory chỉ lưu trạng thái phiên/case của người dùng. Mô hình ngôn ngữ hỗ trợ hội thoại và giải thích, không quyết định hồ sơ hợp lệ.

```mermaid
%%{init: {"theme":"base","themeVariables":{"actorBkg":"#F8FAFC","actorBorder":"#64748B","actorTextColor":"#0F172A","signalColor":"#334155","signalTextColor":"#0F172A","labelBoxBkgColor":"#FFF7ED","labelBoxBorderColor":"#FB923C","labelTextColor":"#7C2D12","noteBkgColor":"#FEFCE8","noteBorderColor":"#EAB308","noteTextColor":"#422006","activationBkgColor":"#DBEAFE","activationBorderColor":"#2563EB"},"sequence":{"mirrorActors":true,"useMaxWidth":false,"wrap":true,"diagramMarginX":20,"diagramMarginY":10,"actorMargin":50,"width":170,"height":55,"boxMargin":10,"boxTextMargin":5,"noteMargin":10,"messageMargin":32}}}%%
sequenceDiagram
    autonumber
    actor U as Người dùng / Portal host

    box rgb(236,254,255) Tầng FE
        participant FE as Chat / Form / Trust UI
    end

    box rgb(255,247,237) Tầng BE — Trust & Orchestration
        participant BND as API Gateway / Service Boundary
        participant ID as Identity & Access
        participant ORCH as Conversation Orchestrator
        participant MEM as Memory Manager
        participant PG as Session-scoped PII Guard
        participant LLM as Provider-neutral LLM Gateway
        participant RULE as Deterministic Rule Engine
        participant POL as Trust / Response Policy
        participant AUD as Redacted Audit
    end

    box rgb(245,243,255) Memory & Security
        participant SM as Browser Session Memory
        participant LM as Encrypted Case Memory
        participant KEY as Key Management
    end

    box rgb(240,253,244) Tầng RAG / Knowledge
        participant Q as Query Preparation
        participant RET as Hybrid Retrieval
        participant STRUCT as Structured Procedure Store
        participant VEC as Vector Database
        participant VERIFY as Grounding Verification
    end

    U->>FE: Mô tả nhu cầu / nhập dữ liệu form
    FE->>+BND: SessionContext + input có cấu trúc
    Note over FE,BND: Consent, schema, size, scope và rate checks
    BND->>+ID: Xác thực account và quyền truy cập case
    ID-->>-BND: Identity / authorization result
    BND->>AUD: Ghi request metadata đã redacted
    BND->>+ORCH: Chuyển input đã xác thực

    ORCH->>+MEM: Đọc trạng thái phiên
    MEM->>SM: Lấy short-term context
    SM-->>MEM: Recent turns + form/review state
    opt Người dùng yêu cầu resume case
        MEM->>LM: Lấy encrypted CaseSnapshot
        LM->>KEY: Kiểm tra key reference và quyền giải mã
        KEY-->>LM: Decryption authorization
        LM-->>MEM: Structured case state
    end
    MEM-->>-ORCH: Session / case context

    ORCH->>+Q: RetrievalQuery đã giảm thiểu dữ liệu
    Note over Q,VERIFY: Không PII, chỉ approved sources và metadata hợp lệ
    Q->>+RET: Query + procedure / jurisdiction / effective-date filters
    par Structured / keyword path
        RET->>STRUCT: Lookup procedure pack và rules
        STRUCT-->>RET: Versioned structured evidence
    and Semantic path
        RET->>VEC: Vector similarity trên approved knowledge
        VEC-->>RET: Ranked public-source chunks
    end
    RET->>+VERIFY: Fused / reranked evidence
    VERIFY-->>-RET: Citations + freshness + conflict state
    RET-->>-Q: RetrievalEvidence
    Q-->>-ORCH: Grounded evidence

    alt Evidence đủ và không mâu thuẫn
        ORCH->>+RULE: Form state + deterministic rules
        RULE-->>-ORCH: Findings + rule references
        opt Cần clarification hoặc giải thích
            ORCH->>PG: Minimize và tokenize direct identifiers
            PG-->>ORCH: Safe context + token map in-memory theo phiên
            ORCH->>LLM: Evidence + findings + context đã tokenize
            LLM-->>ORCH: Structured clarification / explanation
            ORCH->>PG: Khôi phục token cho trusted response
            PG-->>ORCH: Display-safe model output
        end
        ORCH->>+POL: Guidance + evidence + deterministic findings
        Note over PG,POL: Raw identifier không tới external LLM; token map không vào log, DB, vector hoặc CaseSnapshot
        Note over RULE,POL: Model không tạo/đổi finding hoặc quyết định hồ sơ hợp lệ; output quy phạm bắt buộc có citations
        POL->>AUD: Ghi trust outcome đã redacted
        POL-->>-ORCH: GroundedResponse + trust state
    else Thiếu evidence / nguồn mâu thuẫn
        ORCH->>+POL: Yêu cầu fail-closed escalation
        POL->>AUD: Ghi official-review signal
        POL-->>-ORCH: official_review_required
    end

    ORCH->>MEM: Proposed memory update
    MEM->>SM: Cập nhật short-term state
    ORCH-->>-BND: GroundedResponse
    BND-->>-FE: Guidance / checklist / findings / review gate
    FE-->>U: Hiển thị kết quả có nguồn và yêu cầu người dùng review
```

### Trách nhiệm theo tầng

| Tầng | Năng lực chính | Không được làm |
| --- | --- | --- |
| Web FE | Standalone web app, widget/iframe, chat, dynamic form, citations/trust display, consent và review checkpoints | Tạo mobile/native flow hoặc tự quyết định procedure, checklist/tính hợp lệ |
| BE / Trust & Orchestration | API Gateway, identity/access, orchestration, PII Guard, LLM Gateway, memory manager, deterministic rules, response policy và redacted audit | Ghi raw PII/token map vào log/storage, gửi raw identifier ra model hoặc cho model thay đổi finding |
| RAG / Knowledge | Source registry, staging, structured procedure store, keyword/vector retrieval, metadata filtering, reranking và grounding verification | Đưa nguồn chưa approved, chat memory hoặc PII vào vector index |
| Memory / Security | Browser session, encrypted case memory, key management, tenant isolation, expiry và explicit deletion | Dùng case memory làm knowledge base hoặc semantic search |

Hai critical path được khóa như sau:

- **Guided intake:** Gateway kiểm input → Orchestrator truy xuất approved evidence → PII Guard giảm thiểu/tokenize trước external LLM → LLM chỉ trả structured intent/clarification/explanation → Trust Policy kiểm citations/freshness → người dùng review ở U1/U2.
- **Pre-check:** raw form chỉ ở trusted boundary → Rule Engine tạo field/cross-field findings → nếu cần, LLM giải thích findings trên payload đã tokenize → de-tokenize chỉ cho response → người dùng review ở U3. PII Guard/model lỗi thì giữ deterministic output, không gửi raw data để fallback.

### RAG lifecycle và vector database

```text
Nguồn chính thức
  -> Source registry + staging
  -> Chuẩn hóa / chunk / metadata / checksum
  -> K1: reviewer nghiệp vụ duyệt pack, schema và rules
  -> Approved release
  -> Structured procedure store + embeddings/vector index
  -> Metadata filter + keyword/vector retrieval
  -> Evidence fusion / reranking
  -> Citation, freshness và conflict verification
  -> Grounded context hoặc official_review_required
```

- Vector database chỉ chứa embeddings của nguồn công khai đã approved; không chứa form, định danh, chat transcript hoặc case memory.
- Structured store giữ procedure pack, checklist, form schema, validation rules, source/version và golden cases.
- Nguồn hết hiệu lực hoặc mâu thuẫn phải quay lại gate K2; runtime không tự hợp nhất nhiều phiên bản để tạo câu trả lời.

### Memory và resume

| Loại state | Nội dung phù hợp | Vòng đời |
| --- | --- | --- |
| Knowledge/RAG | Procedure packs, nguồn, rules và public-source chunks đã review | Versioned theo source lifecycle |
| Short-term `SessionContext` | Recent turns, structured summary, procedure/version, pending questions, form state, evidence refs, findings và trust/review state | Browser session; xóa khi logout, explicit delete hoặc kết thúc phiên |
| PII token map | Direct identifier ↔ token tạm phục vụ một model request/session | In-memory trong trusted BE; hủy cuối phiên; không nằm trong log, DB, vector, `SessionContext` durable hoặc `CaseSnapshot` |
| Long-term `CaseSnapshot` | Full form draft đã mã hóa, clarification answers, checklist/progress, findings, confirmations, procedure/source versions và expiry metadata | Tối đa 30 ngày sau hoạt động cuối; chỉ khi user consent và S1/Decision đã được chấp thuận |

Long-term memory dùng envelope encryption với key riêng theo user/case. Khi resume, hệ thống so sánh procedure/source version; nếu thay đổi thì đánh dấu kết quả cũ `stale`, yêu cầu U5 review và chạy validation lại. Không lưu chain-of-thought, token map hoặc model payload và không tạo embedding từ PII.

### Human review gates

| Gate | Người xác nhận | Nội dung |
| --- | --- | --- |
| U1 | Người dùng | Procedure và jurisdiction/trường hợp áp dụng |
| U2 | Người dùng | Checklist, conditional items, steps và nguồn |
| U3 | Người dùng | Dữ liệu form, findings và cách sửa trước khi coi là đạt kiểm tra sơ bộ |
| U4 | Người dùng | Consent lưu draft, account scope, retention 30 ngày và quyền xóa |
| U5 | Người dùng | Thay đổi procedure/source version khi resume |
| K1/K2 | Reviewer nghiệp vụ | Duyệt pack/rules trước publish; xử lý nguồn mâu thuẫn, hết hiệu lực hoặc thay phiên bản |
| S1 | Privacy/security peer | Account memory, encryption, access, retention, deletion và audit trước khi bật long-term memory |

### Public REST surface đề xuất

| Method/path | Mục đích | Trust/evidence |
| --- | --- | --- |
| `POST /v1/intake/turn` | Hội thoại, clarification và form state | structured output + sources/state |
| `POST /v1/procedures/recommend` | Xác định thủ tục từ nhu cầu | ranked IDs + evidence |
| `POST /v1/procedures/{id}/checklist` | Checklist cá nhân hóa | versioned documents/steps/refs |
| `POST /v1/applications/validate` | Deterministic pre-check | field/rule findings + fixes |
| `GET /v1/procedures` | Danh sách pack/version đang phục vụ | review/freshness metadata |
| `GET /health` | Smoke check deploy | redacted service status |

Mọi response quy phạm phải có `procedure_version`, `source_refs`, `last_verified_at` và trust state. Error schema, auth/rate limit, CORS và OpenAPI examples được chốt khi scaffold; không được suy đoán từ proposal.

Các logical contract nội bộ gồm `SessionContext`, `CaseSnapshot`, `RetrievalQuery`, `RetrievalEvidence` và `GroundedResponse`. Chúng làm rõ boundary, không bổ sung hoặc thay đổi public API trên.

### Tích hợp portal

```html
<script src="https://<demo-host>/widget.js"></script>
<dvc-ai-assistant api-base="https://<api-host>" locale="vi"></dvc-ai-assistant>
```

Widget bọc iframe giúp tránh xung đột CSS của portal host; headless API cho phép portal dùng UI riêng. Target demo là nhúng widget trên một static host độc lập, không chỉ render trong standalone demo.

## 6. Safety, grounding và privacy

| Lớp | Guardrail | Khi vi phạm / evidence cần có |
| --- | --- | --- |
| Input | Consent, authentication, schema/type/size validation, scope detection và prompt-injection handling | Từ chối hoặc yêu cầu sửa input; không commit blocked content vào memory |
| Retrieval | Chỉ allowlisted/approved sources; lọc jurisdiction, effective date và review status | Loại evidence không hợp lệ; thiếu/mâu thuẫn thì `official_review_required` |
| Generation | Structured output, grounded context và citations bắt buộc | Không phát hành hướng dẫn quy phạm không nguồn |
| Validation | Rule engine deterministic, finding gắn rule/source | Mô hình chỉ giải thích, không đổi finding hoặc quyết định hồ sơ hợp lệ |
| Output | Citation/freshness/conflict verification, trust state và disclaimer rõ | Fail closed; golden cases không được thêm sai giấy tờ bắt buộc |
| Memory | Tenant isolation, envelope encryption, explicit consent/delete và expiry tối đa 30 ngày | Không save/resume; audit event phải được redacted |
| Operations | Rate limit, abuse control, redacted logs, access audit, health monitoring và kill switch | Degrade về structured/rule path hoặc tạm ngừng AI path |

### Chính sách PII và long-term case memory

- Demo và evaluation chỉ dùng dữ liệu synthetic; không dùng hồ sơ công dân thật.
- Short-term state ưu tiên nằm trong browser session; backend chỉ giữ execution context transient cho request hiện tại.
- Proposal chấp nhận long-term `CaseSnapshot` tối đa **30 ngày sau lần hoạt động cuối**, nhưng chỉ khi người dùng chủ động chọn lưu tại U4.
- Full form draft được mã hóa trước khi ghi bằng envelope encryption, dùng key riêng theo user/case; ciphertext và wrapped-key reference được tách biệt.
- Backend chỉ giải mã sau authentication, authorization đúng account/case và audit đã redacted. User delete hoặc expiry phải xóa ciphertext, key reference và session copies.
- Không gửi raw identifier hoặc giá trị định danh vào mô hình; không lưu raw PII trong logs, analytics, audit, search index hoặc vector database.
- Không lưu chain-of-thought, system prompt, hidden model state hoặc full transcript nếu structured summary đã đủ để resume.
- Nếu procedure/source version thay đổi, draft được giữ nhưng checklist/validation cũ phải `stale`, hiển thị U5 và revalidate trước khi tiếp tục.

Long-term memory **không được triển khai chỉ dựa trên proposal này**. Trước khi bật cần một Decision mới và gate S1 xác nhận encryption/key lifecycle, tenant isolation, retention, deletion, recovery, data residency và access audit. Nếu chưa đạt gate, hệ thống chỉ dùng short-term session hoặc luồng synthetic/transient và vẫn phải cung cấp explicit delete.

## 7. Evaluation và KPI

### Golden set tối thiểu

Ít nhất 30 cases, phân bố đủ ba pack và bao phủ:

- Happy path.
- Thiếu giấy tờ/trường bắt buộc.
- Sai type/format.
- Xung đột cross-field.
- Conditional/exception path.
- Nhu cầu/câu trả lời mơ hồ.
- Ngoài phạm vi hoặc source conflict/future-effective.

### Target đề xuất — chưa phải kết quả

| Chỉ số | Target |
| --- | --- |
| Top-1 procedure identification | >= 90% trên golden set đã khóa |
| Citation coverage cho hướng dẫn quy phạm | 100% |
| Sai thêm giấy tờ bắt buộc | 0 case trong golden set |
| Critical-error detection recall | >= 90% |
| False-positive validation | <= 10% |
| Deterministic validation p95 | < 1 giây |
| AI turn p95 | < 5 giây, không tính cold start |
| Integration | Widget nhúng thành công trên một static host độc lập |
| Usability | >= 5 người không thuộc team phát triển hoàn thành luồng test |

Mỗi kết quả sau này phải ghi dataset/commit/procedure versions, số mẫu, môi trường và ngày đo. Không biến target thành achievement khi chưa có evidence.

## 8. Ánh xạ rubric 100 điểm

| Rubric | Điểm | Bằng chứng chính cần trình bày |
| --- | ---: | --- |
| Technical Implementation & Engineering Depth | 20 | API thật, procedure schema, deterministic rule engine, tests và public deploy. |
| AI-Native Architecture & Innovation | 20 | Conversational clarification, structured output, grounded RAG và provider-neutral adapter. |
| Business Viability & Pilot Pathway | 20 | Widget/headless API, portal sandbox, KPI vận hành và pilot 90 ngày. |
| AI-Native UX & Design Thinking | 15 | Chat chuyển thành form, plain Vietnamese, web accessibility, browser/container compatibility và usability evidence. |
| AI Safety, Grounding & Trust | 15 | Citations, effective dates, fail closed, PII minimization và trust states. |
| Presentation, Demo & Defensibility | 10 | Live flow, system diagram, evaluation evidence, source/version display và fallback. |

Nguyên tắc ưu tiên: accuracy/trust và vertical slice chạy thật trước; breadth chỉ được thêm khi không làm yếu evidence của ba MVP.

## 9. Kế hoạch 48 giờ

| Thời gian | Kết quả cần khóa |
| --- | --- |
| 0–4h | Source freeze, procedure schema, API contract và golden cases. |
| 4–12h | Vertical slice đăng ký khai sinh end-to-end. |
| 12–24h | Đăng ký thường trú và đăng ký thành lập hộ kinh doanh theo cùng contract. |
| 24–34h | Grounding, citations, provider adapter và evaluation. |
| 34–42h | Standalone web app, widget embed, public deploy, portal-container compatibility và accessibility. |
| 42–48h | Scope freeze, tests, tài liệu, demo rehearsal và fallback. |

Đây là kế hoạch proposal; task breakdown/owner cụ thể chỉ được tạo sau khi D-006 được peer xác nhận.

### Sáu lane ngang hàng

1. Procedure research.
2. Data/grounding.
3. AI/evaluation.
4. Backend/rules.
5. Frontend/widget.
6. Quality/deploy/demo.

Lane có thể luân chuyển; không lane hoặc agent nào có quyền cao hơn. Mỗi Task Record chỉ có một owner/writer trong scope tại một thời điểm. Shared API/schema/deploy/demo changes cần Decision và peer confirmation; sáu giờ cuối cần hai peer.

## 10. Pilot 90 ngày

| Giai đoạn | Mục tiêu | Exit evidence |
| --- | --- | --- |
| Ngày 0–30 | Cán bộ nghiệp vụ review procedure packs, nguồn và quy trình cập nhật | Approved pack criteria, review SLA, freshness/conflict workflow |
| Ngày 31–60 | Sandbox portal dùng widget/API, đo completion, lỗi và escalation | Integration/security test, usage metrics không lưu raw PII |
| Ngày 61–90 | Pilot giới hạn với nhóm người dùng/đơn vị xác định | KPI report, incident/feedback review, go/no-go trước mở rộng thủ tục |

Roadmap sau MVP có thể lần lượt thử OCR, voice/đa ngôn ngữ, analytics, staff copilot, auto-submission và integration thật. Mỗi mục cần business owner, data/privacy review và Decision riêng; không được coi là năng lực hiện có.

## 11. Rủi ro, TBD và điều không tuyên bố

### Rủi ro ưu tiên

- **P0 — nguồn sai/cũ:** human review, effective dates, checksum và fail closed.
- **P0 — scope quá rộng:** một vertical slice trước; dùng chung schema/evaluation cho ba pack.
- **P0 — demo không ổn định:** rule path độc lập provider, smoke/fallback và rehearsal.
- **P1 — PII/security:** synthetic data, transient processing, redaction, delete session.
- **P1 — UX web khó dùng:** plain-language/content review, keyboard/focus/contrast, browser/container checks và 5 usability testers.
- **P1 — integration chỉ trên giấy:** static-host widget embed + public API evidence.

### TBD cần chốt khi triển khai

- Model/provider và chính sách retention/data residency.
- Package manager, runtime versions, install/test/build/run commands.
- Chi tiết/legal source đã review cho từng field/rule trong ba pack.
- Error/auth/rate-limit/CORS/OpenAPI contracts.
- Project IDs, domain, public URLs, secrets, quotas và rollback artifact.
- Exact demo duration, speakers, datasets/commit và KPI thực đo.

Proposal không tuyên bố đã có application code, model, public URL, cloud project, procedure pack approved, KPI đạt target hoặc deployment đang chạy.

## 12. Nguồn và tài liệu liên quan

### Nguồn chính thức

- [Vietnam AI Innovation Challenge](https://www.vietnamaichallenge.com/) — thông tin cuộc thi.
- [Cổng Dịch vụ công Quốc gia](https://dichvucong.gov.vn/) — nguồn thủ tục/biểu mẫu mục tiêu; từng pack cần lưu URL/version cụ thể sau review.
- [Cổng Thông tin điện tử Chính phủ](https://chinhphu.vn/) — văn bản và thông tin hiệu lực chính thức.
- [Luật Hộ tịch số 03/2026/QH16](https://xaydungchinhsach.chinhphu.vn/toan-van-luat-ho-tich-so-03-2026-qh16-119260527163142286.htm) — ví dụ nguồn tương lai phải tách khỏi pack hiện hành tại 17/07/2026.

### Source-of-truth nội bộ

- [Project Context](../ai/PROJECT_CONTEXT.md)
- [Architecture](../ai/ARCHITECTURE.md)
- [Decision Log](../ai/DECISIONS.md)
- [Demo runbook](../ai/DEMO.md)
- [Deployment contract](../ai/DEPLOYMENT.md)
- [Secrets & Data policy](../ai/SECRETS_AND_DATA.md)

`raw.md` được tham khảo như phân tích nội bộ cho SWOT/positioning, không phải nguồn pháp lý và không được sửa/stage/commit trong task này.
