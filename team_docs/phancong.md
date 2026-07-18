# Phân công 48 giờ — sáu lane ngang hàng

> Trạng thái: backlog khởi tạo, chưa phải claim thực tế. D-005 scaffold đã có; các task xây dựng capability D-006, data release, deploy và shared contract vẫn `planned / blocked:G0` cho đến khi được peer xác nhận. Mỗi người phải tạo Task Record/Context Pack và onboard AI Log trong clone/worktree của mình trước khi commit.

## Mục tiêu chung và phạm vi

Ba procedure pack hiện hành theo D-007:

1. Đăng ký khai sinh.
2. Đăng ký thường trú.
3. Đăng ký thành lập hộ kinh doanh.

Mỗi pack phải đạt cùng contract: clarification tree, checklist, steps, form schema, deterministic validation rules, citations, effective dates, review status và golden cases. Delivery là web-first theo D-008: standalone web app, widget/iframe và headless API; không có mobile/native deliverable.

Sáu lane là vùng trách nhiệm có thể luân chuyển, không phải cấp bậc. Owner chỉ là writer tạm thời của resource đã claim. Member 6 kiểm tra evidence/CI nhưng không có quyền merge hay quyết định cao hơn peer khác.

## Luồng dữ liệu bắt buộc

```text
Source discovery
  -> allowlist + quyền sử dụng/attribution
  -> curated acquisition
  -> versioned staging
  -> parse / normalize / deduplicate
  -> procedure-pack mapping
  -> K1 human review
  -> approved release
  -> structured store + vector index
  -> retrieval evaluation
  -> source freeze / rollback / K2 re-review
```

Nguyên tắc là **curated-first**: chỉ lấy nguồn cần cho ba MVP, không xây crawler tổng quát trong 48 giờ. Raw snapshot ở staging ignored mặc định và chỉ được track khi quyền sử dụng rõ. Runtime/repo chỉ nhận normalized pack đã approved cùng synthetic golden cases; không ingestion `raw.md`, hồ sơ đã điền, PII hoặc dữ liệu người thật.

### Data contracts nội bộ

| Artifact | Trường tối thiểu | Owner / gate |
| --- | --- | --- |
| `SourceRegistryEntry` | `source_id`, URL/ref, authority, jurisdiction, procedure IDs, effective dates, retrieved/verified dates, license/attribution, checksum, review status | Member 1 facts; Member 2 schema |
| `SourceSnapshotManifest` | snapshot ID, source/version, capture method, content type, staging ref, checksum, parser version | Member 2 |
| `ProcedurePack` | identity, eligibility, documents, steps, fees/time, intake questions, form schema, rules, legal sources, effective dates, review status | Member 2 mapping; K1 Member 1 |
| `ReleaseManifest` | release ID, input checksums, reviewer, approval time, structured/vector versions, previous rollback version | Member 2; K1/K2 |
| `GoldenCase` | synthetic input, category, expected procedure/checklist/findings, source refs, expected trust state | Member 3 format; Members 1/4 expected facts |

Các artifact trên không thêm public API. Sáu endpoint và ba trust state trong D-006 được giữ nguyên ở trạng thái `Proposed`.

## Cặp backup/review

| Lane chính | Owner khởi tạo | Peer review/backup chính |
| --- | --- | --- |
| Procedure research / source governance | Member 1 | Member 2 |
| Data processing / RAG grounding | Member 2 | Member 1 và Member 3 |
| AI orchestration / evaluation | Member 3 | Member 4 |
| Backend / API / deterministic rules | Member 4 | Member 3 và Member 6 |
| Web frontend / widget / UX | Member 5 | Member 6 |
| Quality / security / deploy / docs / demo | Member 6 | Member 5 và peer sở hữu artifact |

Backup chỉ tiếp nhận sau khi owner release claim hoặc cập nhật Task Record; reviewer không sửa trực tiếp resource đang có writer.

## Member 1 — Procedure research và source governance

**Claim:** source registry facts, căn cứ nghiệp vụ và expected facts; không sửa ingestion/index implementation.

| Task | Timebox | Output / Definition of Done | Dependency và review |
| --- | --- | --- | --- |
| `M1-RES-01` | 0–2h | Allowlist nguồn chính thức cho ba thủ tục; mỗi nguồn có authority, jurisdiction, effective date, license/attribution và URL/ref | Member 2 review metadata; dừng nếu quyền dùng chưa rõ |
| `M1-RES-02` | 2–4h | Curated acquisition plan + source freeze; ghi nguồn thiếu, conflict, future-effective và official fallback | Không bulk scrape; G1 |
| `M1-RES-03` | 4–12h | Nội dung pack khai sinh: clarification, checklist, steps, form/rule source mapping | Member 2 normalize; Member 4 review rule mapping |
| `M1-RES-04` | 12–24h | Nội dung pack thường trú và hộ kinh doanh cùng độ sâu | K1 sau normalized candidate |
| `M1-RES-05` | 24–34h | Rà từng checklist/rule/citation, xác nhận không thêm sai giấy tờ bắt buộc | Handoff expected facts cho Member 3 |
| `M1-RES-06` | 34–42h | K1/K2 sign-off, source/version copy và official-review fallback | Pack còn conflict không được approved |
| `M1-RES-07` | 42–48h | Evidence accuracy/source governance/pilot cho presentation | Member 6 tổng hợp, không sửa facts |

**AI Log:** Member 1 tự onboard namespace của mình, bind đúng source coding-agent cho Task Record research và kiểm `doctor --strict` trước commit.

## Member 2 — Data collection, processing và RAG grounding

**Claim:** staging, transforms, release, structured/vector knowledge; không tự sửa facts nghiệp vụ hoặc public API.

| Task | Timebox | Output / Definition of Done | Dependency và review |
| --- | --- | --- | --- |
| `M2-DATA-01` | 0–2h | Schema cho source registry, snapshot, pack và release manifest | Members 1/4 xác nhận; G1 |
| `M2-DATA-02` | 2–4h | Lifecycle raw → parsed → normalized → approved/rejected/superseded; ignored/tracked và rollback policy rõ | Member 6 review security |
| `M2-DATA-03` | 4–8h | Parser/normalizer nhỏ: UTF-8, headings/tables/forms, metadata, checksum, dedupe | Chỉ curated inputs; không crawler |
| `M2-DATA-04` | 8–12h | Normalize pack khai sinh, schema validation và release candidate | K1 Member 1; G2 |
| `M2-DATA-05` | 12–20h | Normalize thường trú + hộ kinh doanh, mapping documents/steps/forms/rules/source refs | Không publish trước K1 |
| `M2-DATA-06` | 20–24h | Approved structured release + synthetic seed, lineage/checksum/previous version | G0 + K1 + G3 |
| `M2-DATA-07` | 24–30h | Chunk approved public content, embeddings/vector index và metadata filters | Không embedding PII/form/chat |
| `M2-DATA-08` | 30–34h | Hybrid retrieval, dedupe/rerank, context budget, freshness/conflict checks | Member 3 evaluation; G4 |
| `M2-DATA-09` | 34–42h | Data-quality suite: metadata, duplicate, citation, future-effective, schema drift và PII scan | Member 6 đưa stable checks vào CI |
| `M2-DATA-10` | 42–48h | Freeze release manifest, checksum, rollback snapshot và K2 procedure | Sau G6 chỉ sửa P0 |

**AI Log:** Member 2 là writer duy nhất của raw staging/release trong task đã claim; prompt evidence vẫn ghi vào namespace riêng của Member 2.

## Member 3 — AI orchestration, model selection và evaluation

**Claim:** intent/clarification, provider-neutral adapter và evaluation harness; không quyết định nghiệp vụ hoặc sửa procedure facts.

| Task | Timebox | Output / Definition of Done | Dependency và review |
| --- | --- | --- | --- |
| `M3-AI-01` | 0–4h | Golden-case contract + ít nhất 30 synthetic cases, tối thiểu 10/pack; phủ happy, missing, format, conflict, ambiguous, exception và out-of-scope | Member 1 expected facts; Member 4 findings |
| `M3-AI-02` | 0–4h | Model/provider benchmark: structured output, tiếng Việt, latency, quota, failure và data policy | Không chọn provider nếu retention/training chưa rõ |
| `M3-AI-03` | 4–12h | Intent + clarification vertical slice khai sinh, schema output và U1 | G0; Member 4 review boundary |
| `M3-AI-04` | 12–24h | Mở rộng ba pack, adapter neutral và model fallback | Model không sinh rule/checklist ngoài pack |
| `M3-AI-05` | 24–30h | Retrieval evaluation: expected source/chunk, citation, conflict/no-evidence | Approved release Member 2 |
| `M3-AI-06` | 30–34h | Báo cáo Top-1, critical-error recall, false-positive, latency, no-extra-document | Tách target và measured; G4 |
| `M3-AI-07` | 34–42h | Provider/retrieval failure và prompt-injection tests; deterministic fallback evidence | Member 6 rehearsal |
| `M3-AI-08` | 42–48h | Freeze prompt/config/model path và evaluation report theo release | Không tune trên holdout sau freeze |

**AI Log:** Member 3 chỉ log prompt dev repo; benchmark/model input chứa dữ liệu synthetic hoặc public approved, không đưa key/model response vào log.

## Member 4 — Backend, API và deterministic rules

**Claim:** public API, shared schema, orchestration boundary và rule engine.

| Task | Timebox | Output / Definition of Done | Dependency và review |
| --- | --- | --- | --- |
| `M4-BE-00` | 0–4h | Reconcile D-006 với kiến trúc mới; khóa sáu endpoint, error shape, trust metadata và pack contract | Members 3/6 review; G0/G1 |
| `M4-BE-01` | 4–8h | Review/hoàn thiện scaffold, health endpoint và check command | D-005 baseline có sẵn; thay shared contract cần G0/G1 |
| `M4-BE-02` | 8–12h | Intake/checklist/validation vertical slice khai sinh | Chỉ approved pack; G2 |
| `M4-BE-03` | 12–24h | Rules/endpoints cho thường trú + hộ kinh doanh; findings gắn field/rule/source | Member 1 review facts; G3 |
| `M4-BE-04` | 24–30h | Response assembler, citation/freshness/conflict và ba trust state | No evidence → `official_review_required` |
| `M4-BE-05` | 30–34h | Error/auth/rate-limit/CORS/OpenAPI boundary và redacted logging | Member 6 security check |
| `M4-BE-06` | 34–42h | API integration/performance hardening; deterministic path khi AI/vector lỗi | Health/key APIs smoke; G5 |
| `M4-BE-P2` | Deferred | `CaseSnapshot` threat model, encryption/key/delete interface và S1 checklist | Không triển khai retention 30 ngày trong MVP |

**AI Log:** Member 4 sở hữu evidence commit của API/rules mình viết; shared schema/API chỉ đổi sau Decision và peer confirmation.

## Member 5 — Web frontend, UX và widget

**Claim:** web UI, widget/iframe và browser session; không tự đổi API/schema.

| Task | Timebox | Output / Definition of Done | Dependency và review |
| --- | --- | --- | --- |
| `M5-FE-01` | 0–4h | Wireflow U1–U3, loading/error/trust, browser/container và accessibility acceptance | API draft; Member 6 review |
| `M5-FE-02` | 4–12h | Vertical slice khai sinh: chat, clarification, checklist, form, citations, findings | G0/G2; Member 6 e2e |
| `M5-FE-03` | 12–24h | Generic form renderer cho ba pack, conditional fields và cross-field errors | Không tự sinh field ngoài schema |
| `M5-FE-04` | 24–30h | Session/delete, source/version display và official-review handoff | Long-term save/resume ngoài MVP |
| `M5-FE-05` | 30–34h | Widget/iframe adapter, CSP/CORS error UI và standalone fallback | Member 4 contract; G5 |
| `M5-FE-06` | 34–40h | Keyboard/focus/contrast/zoom/container checks + Impeccable advisory | Report không thay manual review |
| `M5-FE-07` | 36–42h | Usability test ≥5 người ngoài team bằng synthetic scenarios | Ghi completion/confusion/P0/P1 |
| `M5-FE-08` | 42–48h | Freeze UI, trust copy và demo reset path | Sau G6 chỉ sửa P0 |

**AI Log:** Member 5 ghi prompt UI/widget vào namespace riêng; không commit screenshot nhạy cảm, browser session hoặc Impeccable raw cache.

## Member 6 — Quality, security, deploy, docs và demo

**Claim:** test/deploy evidence và demo runbook; không phải merge captain.

| Task | Timebox | Output / Definition of Done | Dependency và review |
| --- | --- | --- | --- |
| `M6-QA-01` | 0–4h | Test matrix theo rubric: unit, schema, data, retrieval, AI, API, e2e, accessibility, security, deploy | Mỗi check có owner/evidence |
| `M6-QA-02` | 0–4h | Environment readiness: runtime, secret names, quota/billing owner, CSP/CORS, public-host prerequisites | Không ghi secret; G1 |
| `M6-QA-03` | 4–12h | Application CI/check command, vertical-slice e2e và deterministic fallback | Dùng scaffold D-005; capability D-006 theo G0/G1 |
| `M6-QA-04` | 12–24h | Ba-pack regression, API/schema/rule tests và seed/reset | Golden output Members 1/3/4 |
| `M6-QA-05` | 24–34h | Security/PII scan, redacted-log, abuse/rate, failure injection và observability tối thiểu | Không log raw payload; G4 |
| `M6-QA-06` | 34–42h | Public deploy, health/key-flow smoke, static-host widget embed và rollback | G5; ghi URL/commit/release checksum |
| `M6-DOC-01` | 34–42h | Architecture/model/API docs, one-page summary, pilot roadmap và measured KPI evidence | Mỗi lane cung cấp artifact của mình |
| `M6-DEMO-01` | 40–46h | Demo script, speaker handoff, live/fallback và rubric evidence map | Không có quyền cao hơn peer |
| `M6-DEMO-02` | 46–48h | Hai rehearsal, blocker/fallback, preflight và freeze evidence | Thay đổi mới cần hai peer |
| `M6-AILOG-01` | Mỗi gate | Guard kiểm schema/trailer/gap và tổng hợp AI Log evidence | Mỗi member vẫn tự chịu trách nhiệm log của mình |

**AI Log:** Member 6 onboard và ghi prompt của lane mình như mọi peer; việc kiểm evidence của team không cho phép sửa/xóa record của member khác hoặc tự push.

## Shared gates

| Gate | Deadline | Điều kiện qua gate |
| --- | --- | --- |
| `G0 — Architecture` | Trước capability D-006/deploy shared | D-005 scaffold được giữ; RAG/trust/data-release/widget/deploy cần D-006 được Accepted hoặc superseded |
| `G1 — Data/API contract` | 4h | Source schema, ProcedurePack, GoldenCase và public API được khóa |
| `G2 — Birth vertical slice` | 12h | Approved data → retrieval → UI → deterministic validation chạy end-to-end |
| `G3 — Three-pack parity` | 24h | Ba pack cùng contract, K1 và regression |
| `G4 — Trust/evaluation` | 34h | Data quality, retrieval, rules, citations, failure và KPI có evidence |
| `G5 — Public integration` | 42h | Public URL, health, widget embed, accessibility và usability evidence |
| `G6 — Scope freeze` | 42–48h | Chỉ P0/demo reliability; thay đổi mới cần hai peer và rollback |

## Boundary chống conflict

- Member 1 sở hữu source facts; Member 2 sở hữu processing/release; Member 4 sở hữu schema/API.
- Member 3 sở hữu golden-case format/harness; Member 1 cung cấp expected facts, Member 4 cung cấp expected rule findings, Member 6 chạy regression.
- Member 5 sở hữu web UI/widget; Member 6 sở hữu deploy/e2e evidence.
- Raw staging chỉ có một writer là Member 2. Reviewer trả finding qua Task Record, không sửa trực tiếp.
- Mỗi member dùng Task Record, worktree và AI Log namespace riêng. Shared resource chỉ đổi sau Decision/peer confirmation.

## Stopping conditions

- Dừng capability D-006, shared contract hoặc deploy nếu G0 chưa đạt; không coi scaffold D-005 là bằng chứng cho các capability đó.
- Dừng ingestion khi nguồn ngoài allowlist, license/attribution chưa rõ hoặc thao tác vượt rate limit.
- Dừng release nếu thiếu checksum, effective date, source ref, schema validation hoặc K1.
- Dừng retrieval/generation khi evidence thiếu, mâu thuẫn hoặc hết hiệu lực; trả `official_review_required`.
- Dừng nếu phát hiện secret, raw PII, hồ sơ người thật, PII trong log/vector index hoặc prompt evidence chưa sanitize.
- Dừng thay shared API/schema/deploy khi chưa có peer confirmation.
- Dừng long-term memory implementation khi chưa có Decision mới và S1.
- Trong sáu giờ cuối, dừng feature mới không trực tiếp sửa P0 hoặc tăng độ tin cậy demo.

## Definition of Done của backlog

- Mọi P0 task có Task Record với owner, output, dependency, reviewer, check/evidence và stopping condition.
- Ba procedure pack, ít nhất 30 golden cases, public API/widget, public URL, architecture/model/API docs, one-page summary và pilot roadmap đều có owner.
- Data lifecycle có allowlist, license, staging, normalization, K1/K2, release, embeddings, evaluation, versioning và rollback.
- Mỗi member có `doctor --strict` pass trong clone của mình; commit có AI Log trailer/evidence hoặc warning giải thích gap.
- Không resource nào có hai writer đồng thời; mọi claim được release trong handoff.
