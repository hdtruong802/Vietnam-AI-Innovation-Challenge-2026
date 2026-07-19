# Kiến trúc — AI Procedure Copilot

> Trạng thái: **hybrid** — scaffold frontend/backend theo D-005 và target trust/RAG/data release/widget/deploy theo D-006 đã được chấp thuận. Capability runtime chỉ được coi là có khi có evidence triển khai riêng.
>
> Cập nhật gần nhất: 2026-07-18
>
> Decision liên quan: D-005, D-006, D-007 và D-008
>
> Input thiết kế: [`diagram_v3.mmd`](../../team_docs/diagram_v3.mmd). Input minh họa không thay thế procedure pack đã review hoặc data governance.

Tài liệu này phân biệt **baseline có trong repo** với **target architecture**. Không capability nào trong target được xem là đã triển khai chỉ vì có sơ đồ, route name hoặc proposal.

## Mục tiêu kiến trúc

- Demo web-first đáng tin cậy trong 48 giờ cho ba procedure pack ở D-007.
- Tách UI, API/orchestration, deterministic validation, approved knowledge và external AI để giảm rủi ro sai hướng dẫn.
- Mọi hướng dẫn quy phạm có evidence/version/freshness; thiếu căn cứ thì fail closed.
- Có pathway để nhúng portal qua widget/iframe và REST API, nhưng không tuyên bố đã tích hợp Cổng DVCQG.
- Không để raw identifier rời trust boundary, xuất hiện trong log, vector index hoặc model request.

## 1. Baseline đã có theo D-005

| Vùng | Bằng chứng source hiện có | Giới hạn hiện tại |
| --- | --- | --- |
| `frontend/` | Web Procedure Copilot có intake/chat, checklist, form và pre-check UI; client giữ `SessionContext` trong browser session. | Chưa có procedure pack K1 đã duyệt; production chỉ được hiển thị fallback fail-closed. |
| `backend/` | FastAPI API foundation, CORS allowlist, request ID/error envelope, health, deterministic rule engine và adapter ports; Cloud Run production-disabled đã smoke. | Không có approved data release, RAG/vector runtime, external LLM hay account storage. |
| API foundation | `GET /health`, `GET /v1/procedures`, `POST /v1/procedures/recommend`, `POST /v1/intake/turn`, `POST /v1/procedures/{id}/checklist`, `POST /v1/applications/validate`. | Dev fixture chỉ cho integration và luôn `official_review_required`; contract vẫn cần peer review trước khi consumer phụ thuộc sâu. |

Dev fixture, seed, citation và rule trong API foundation không tự chứng minh tính chính xác pháp lý. Chỉ Procedure Pack đã qua source governance, K1 và release mới có thể cấp `verified_guidance`.

## 2. Kiến trúc mục tiêu theo D-006

```text
[Người dân / Portal host]
            |
[Standalone Web App / Embeddable Widget / Chat / Form]
            |
[API / Service Boundary]
  - authn/authz, consent, schema/size/rate/scope checks
            |
[Conversation Orchestrator]
  |-- SessionContext / Memory Manager
  |-- PII Guard: minimize + tokenize theo phiên
  |-- Provider-neutral LLM Gateway: clarification + explanation
  |-- Deterministic Rule Engine: field + cross-field findings
  |-- Trust / Response Policy: citation + freshness + escalation
  |-- Redacted Audit
            |
[RAG / Approved Knowledge]
  |-- Structured Procedure Store
  |-- Keyword + Vector Retrieval
  |-- Grounding Verification
            ^
[Curated Offline Ingestion + K1 Human Review]
            |
[Nguồn thủ tục, biểu mẫu và văn bản chính thức]
```

Các khối trên là logical capabilities, không bắt buộc là service deploy riêng. RAG/vector store, LLM gateway, PII guard, memory bền vững, widget production và deploy chưa có evidence runtime trong repo.

## 3. Luồng guided intake và pre-submission check

### Guided intake

1. FE gửi nhu cầu qua service boundary; boundary kiểm tra consent, schema, kích thước, rate và scope.
2. Orchestrator đọc `SessionContext`, xác định câu hỏi làm rõ và tạo `RetrievalQuery` đã giảm thiểu dữ liệu.
3. RAG chỉ trả evidence từ approved procedure packs bằng structured/keyword/vector retrieval.
4. Khi cần LLM cho phân loại, hỏi làm rõ hoặc diễn đạt, PII Guard phải loại/tokenize direct identifiers. Free text không làm sạch an toàn thì không gửi ra ngoài.
5. Trust Policy chỉ phát hành checklist, steps và examples truy về evidence. Người dùng xác nhận procedure (U1) và checklist/nguồn (U2).
6. Thiếu dữ kiện trả `need_more_information`; evidence thiếu, mâu thuẫn hoặc hết hiệu lực trả `official_review_required`.

LLM không tạo giấy tờ bắt buộc, rule hoặc hướng dẫn quy phạm ngoài pack approved.

### Pre-submission checking

1. Form có thể chứa PII nhưng chỉ đi qua FE và trusted backend boundary; không log payload gốc.
2. Rule Engine chạy field/cross-field validation và trả finding có `rule_id`/source reference.
3. Nếu cần diễn giải, LLM chỉ nhận finding/evidence cùng payload đã tối thiểu hóa/tokenize. Nó không thêm, bỏ hoặc đổi finding.
4. Người dùng review finding (U3), sửa và chạy lại validation.
5. PII Guard/model lỗi thì bỏ AI explanation nhưng vẫn trả structured deterministic findings; không gửi raw data để fallback.

## 4. Thành phần và boundary

| Thành phần | Trách nhiệm | Giới hạn |
| --- | --- | --- |
| Web FE / widget | Standalone UI, chat, form, citation/trust display, session delete và portal embedding. | Không tự quyết procedure/checklist/tính hợp lệ; không có native mobile flow. |
| API / Service Boundary | AuthN/AuthZ, consent, schema/size/rate/scope checks và routing. | Không log raw payload hoặc bỏ qua PII policy. |
| Conversation Orchestrator | Intent, clarification, retrieval, validation, memory và response assembly. | Không hard-code facts ngoài approved pack. |
| PII Guard | Minimize/tokenize direct identifiers và quản lý token map. | Token map session-only, không durable. |
| LLM Gateway | Structured clarification/explanation qua adapter trung lập provider. | Không raw identifier, không verdict hoặc rule generation. |
| Rule Engine | Required/type/format/conditional/cross-field checks. | Deterministic findings là nguồn quyết định pre-check. |
| Trust / Response Policy | Citation, freshness, conflict và trust state. | Fail closed nếu evidence không đủ. |
| Redacted Audit | Metadata vận hành đã giảm thiểu. | Không raw form, PII, token map, prompt payload hay session transcript. |
| RAG / Approved Knowledge | Structured lookup, hybrid retrieval, rerank và verification. | Chỉ public knowledge đã approved; không case/chat/PII. |
| Offline ingestion + K1 | Curated acquisition, normalize, checksum, review và release. | Không bulk scrape khi chưa rõ quyền/rate limit. |

## 5. Memory và PII state

| State | Nội dung | Vòng đời / giới hạn |
| --- | --- | --- |
| `SessionContext` | Recent turns, summary, procedure/version, pending questions, form state, evidence refs, findings và review state. | Browser session; backend execution context transient. |
| PII token map | Direct identifier ↔ token tạm của model request/phiên. | In-memory, session-scoped; hủy khi hết phiên; không trong vector index/log/draft. |
| `CaseSnapshot` mục tiêu | Encrypted draft, progress, confirmations, versions và expiry. | Không thuộc MVP; tối đa 30 ngày chỉ sau Decision mới và S1 privacy/security review. |
| Knowledge/RAG | Approved packs, public chunks, rules và examples. | Versioned theo source lifecycle; không chứa PII. |

Không triển khai long-term case memory chỉ từ tài liệu này. Khi resume sau khi procedure/source version đổi, validation cũ phải được coi là stale và yêu cầu user review/revalidate.

## 6. Procedure pack và API contract mục tiêu

Mỗi `ProcedurePack` cần có:

- `procedure_id`, `name`, `jurisdiction`, `authority`.
- `eligibility_conditions`, `intake_questions`.
- `required_documents`, `optional_documents`, `forms`, `steps`, `processing_time`, `fees`.
- `form_schema`, `validation_rules`.
- `legal_sources`, `effective_from`, `effective_to`, `last_verified_at`, `review_status`, checksum và escalation source.

Public contract hướng tới sáu endpoints:

| Endpoint | Mục đích | Trạng thái |
| --- | --- | --- |
| `POST /v1/intake/turn` | Một lượt hội thoại, clarification và proposed `SessionContext`. | Có API foundation; không nhận/lưu full transcript. |
| `POST /v1/procedures/recommend` | Nhận diện procedure. | Có API foundation; adapter thật do data/AI lane bàn giao. |
| `POST /v1/procedures/{id}/checklist` | Checklist theo answers. | Có API foundation; fixture không phải evidence nghiệp vụ. |
| `POST /v1/applications/validate` | Pre-check deterministic. | Có generic rule engine; rule thật cần pack approved. |
| `GET /v1/procedures` | Pack/version đang dùng. | Có API foundation; release metadata thật cần data lane. |
| `GET /health` | Liveness và capability state. | Có API foundation; public smoke chưa tồn tại. |

Mọi response quy phạm mục tiêu phải có `procedure_version`, `source_refs`, `last_verified_at` và đúng một trust state: `verified_guidance`, `need_more_information` hoặc `official_review_required`.

## 7. Widget, data và trust boundary

Widget có thể dùng script tag/iframe; host, CSP/CORS allowlist, origin/versioning, resize/message contract và fallback UI đều `TBD`. Evidence tối thiểu là nhúng thành công trên một static host độc lập. Portal integration thật vẫn cần sandbox, authorization và security review.

| Hạng mục | Lựa chọn mục tiêu | Giới hạn / fallback |
| --- | --- | --- |
| Data source | Cổng DVCQG, biểu mẫu và văn bản chính thức. | Curated-first + K1; nguồn tương lai không phải hiện hành. |
| Retrieval | Structured filters + keyword/vector chunks. | Chỉ pack approved; thiếu/mâu thuẫn → `official_review_required`. |
| LLM/provider | Provider-neutral gateway, provider/model `TBD`. | Clarification/explanation với payload minimized/tokenized. |
| Validation | JSON Schema + deterministic rules. | Finding có rule/source; không thay official review. |
| Storage/deploy | Chọn theo Decision/Task Record follow-up. | Chưa provision URL, database, secret hay CD. |

## 8. Guardrails, observability và fallback

- Input bị block không được ghi raw vào memory/audit.
- Retrieval lỗi chỉ dùng structured approved data khi đủ; nếu không thì fail closed.
- PII Guard lỗi thì không gọi external LLM.
- Model lỗi/timeout thì guided flow dùng structured checklist; pre-check vẫn dùng rule engine.
- Nguồn mâu thuẫn/hết hiệu lực quay về K2 reviewer nghiệp vụ.
- Auth/decryption lỗi không tiết lộ draft/case metadata.
- Log/metric chỉ là metadata redacted hoặc synthetic; không có raw form/identifier/token map.

## 9. Chạy, kiểm chứng và thay đổi

| Việc | Lệnh/bước | Trạng thái |
| --- | --- | --- |
| Bootstrap guard | `python scripts/ci/validate_repo.py` | Có trong repo. |
| Backend local | `uvicorn main:app --port 8000 --reload` từ `backend/` sau khi cài dependencies. | Lệnh có trong source scaffold; kết quả phải ghi Task Record. |
| Frontend local | `npm run dev` từ `frontend/` sau khi cài dependencies. | Lệnh có trong manifest; UI product chưa hoàn thiện. |
| Application lint/test/build | Theo manifest và Task Record. | Chưa có evidence chung cho toàn bộ ứng dụng. |
| Deploy/smoke | Public URL + health/key flow. | Chưa provision. |

Mọi thay đổi shared API/schema/provider/deploy cần Task Record, Context Pack, Decision/peer confirmation theo risk. D-006 đã chấp thuận target contract; evidence runtime và rollback/fallback vẫn cần được peer review cho từng capability.
