# Chunking Contract — Phase 0 Proposal

> Trạng thái: Accepted
>
> Task Record: `local-20260718-chunking-phase-0`
>
> Decision liên quan: D-017
>
> Source freeze: 17/07/2026

Tài liệu này khóa logical contract cho ingestion và structure-aware chunking. D-017 đã được peer chấp nhận để triển khai fixture/annotation Phase 1; nó chưa cấp quyền thay runtime schema, dependency, database, public API hoặc xử lý toàn bộ corpus.

## 1. Mục tiêu và non-goals

Mục tiêu là tạo evidence chunk có ranh giới nghiệp vụ, provenance và hiệu lực kiểm chứng được cho ba procedure pack MVP: đăng ký khai sinh, đăng ký thường trú và đăng ký thành lập hộ kinh doanh.

Non-goals của Phase 0:

- Không đưa toàn bộ 5.652 raw documents vào index.
- Không tạo embedding, pgvector table hoặc chọn vector database.
- Không sinh checklist, form field hoặc validation rule bằng LLM.
- Không index form data, PII, chat transcript, case memory hoặc nguồn chưa approved.
- Không thay public REST API hoặc response schema hiện tại.

## 2. Phạm vi nguồn và lifecycle

Raw file trong `dataset_raw/` chỉ là staging input local và tiếp tục bị Git ignore. Một raw file không tự động trở thành ground truth.

Nguồn chỉ đủ điều kiện phục vụ khi thuộc allowlist cho ít nhất một trong ba procedure pack và có đủ provenance tối thiểu:

- `source_ref` hoặc URL chính thức có thể kiểm tra.
- Cơ quan ban hành/cung cấp và jurisdiction.
- Phiên bản hoặc định danh văn bản.
- `effective_from`, `effective_to` khi áp dụng và `last_verified_at`.
- Quyền sử dụng/attribution đã được ghi nhận.
- Checksum và reviewer K1.

Lifecycle chuẩn:

```text
staging -> parsed -> needs_review -> approved
                    |              |
                    v              v
                 rejected        stale -> needs_review
```

Chỉ `approved` được phát hành vào retrieval index. Nguồn thiếu, mâu thuẫn, hết hiệu lực, có hiệu lực tương lai hoặc không xác định được provenance phải ở `needs_review`, `rejected` hoặc `stale` và dẫn runtime về `official_review_required`.

## 3. Logical data contract

Contract gồm bốn model provider-neutral. Tên trường dưới đây là logical contract; kiểu Pydantic/SQL cụ thể cần task implement riêng sau Decision.

### `SourceDocument`

| Field | Ý nghĩa / invariant |
| --- | --- |
| `source_id` | ID ổn định, không phụ thuộc đường dẫn máy local. |
| `raw_document_id` | ID raw, ví dụ filename stem; không dùng làm citation cho người dùng. |
| `procedure_ids` | Tập con của đúng ba procedure ID MVP. |
| `title`, `authority`, `jurisdiction` | Metadata định danh và phạm vi áp dụng. |
| `source_ref`, `document_version` | Provenance có thể review. |
| `document_type` | Procedure page, legal document, form hoặc official guidance. |
| `effective_from`, `effective_to`, `last_verified_at` | Cửa sổ hiệu lực và freshness. |
| `permission_status` | Trạng thái quyền sử dụng/attribution. |
| `review_status`, `reviewed_by`, `reviewed_at` | Kết quả gate K1/K2. |
| `raw_checksum`, `normalized_checksum` | Phát hiện thay đổi và bảo đảm rebuild. |
| `normalizer_version`, `parser_version` | Version pipeline tạo dữ liệu. |

### `ParsedSection`

| Field | Ý nghĩa / invariant |
| --- | --- |
| `section_id`, `source_id` | ID ổn định và liên kết source. |
| `section_path`, `parent_section_id`, `ordinal` | Giữ hierarchy và thứ tự gốc. |
| `section_type` | Một trong taxonomy được duyệt. |
| `text` | Nội dung đã normalize, không mất dấu câu hoặc dấu tiếng Việt. |
| `start_line`, `end_line`, `start_char`, `end_char` | Trace ngược về normalized document. |
| `legal_basis_refs` | Quan hệ tới căn cứ pháp lý, không sao chép mơ hồ. |
| `parse_warnings` | Dấu hiệu mojibake, navigation noise, boundary không chắc chắn hoặc metadata thiếu. |

Taxonomy ban đầu:

```text
overview, authority, eligibility, documents, steps,
processing_time, fees, forms, legal_basis,
effective_date, exceptions, other
```

Giá trị `other` không được tự động approved nếu chứa claim quy phạm.

### `EvidenceChunk`

| Field | Ý nghĩa / invariant |
| --- | --- |
| `chunk_id` | Hash ổn định từ source/version, section path, ordinal, text hash và tokenizer ID. |
| `source_id`, `section_ids`, `procedure_ids` | Provenance và scope retrieval. |
| `chunk_type`, `section_path` | Loại evidence và context hierarchy. |
| `context_prefix`, `text` | Prefix ngắn và nội dung evidence; cả hai cùng tính token. |
| `token_count`, `tokenizer_id` | Kết quả từ `TokenCounter` đã khai báo. |
| `jurisdiction`, `effective_from`, `effective_to` | Metadata bắt buộc cho pre-filter. |
| `source_refs`, `legal_basis_refs` | Citation/fact support có thể kiểm chứng. |
| `review_status`, `chunker_version`, `content_checksum` | Release gate và reproducibility. |

### `ChunkBuildReport`

| Field | Ý nghĩa / invariant |
| --- | --- |
| `build_id`, `started_at`, `completed_at` | Định danh lần build. |
| `source_snapshot_id` | Tập source/version đầu vào đã khóa. |
| `normalizer_version`, `parser_version`, `chunker_version`, `tokenizer_id` | Toàn bộ version ảnh hưởng output. |
| `selected`, `approved`, `quarantined`, `rejected` | Số lượng theo lifecycle. |
| `chunk_count`, `token_percentiles`, `warning_counts` | Quality evidence không chứa raw text. |
| `input_manifest_checksum`, `output_manifest_checksum` | Kiểm tra deterministic rebuild. |

Report không ghi raw document content, PII hoặc full model payload.

## 4. Token budget và chunking invariants

Chunking diễn ra sau structural parsing, theo thứ tự:

1. Tạo atomic unit từ section, field/value, bullet, numbered step và legal reference.
2. Giữ nguyên unit nếu nằm trong budget.
3. Ghép các sibling cùng section khi tổng dưới target và không làm lẫn claim/citation.
4. Tách unit quá dài theo bullet con, câu, rồi clause; không cắt giữa số hiệu văn bản, ngày hoặc citation span.
5. Gắn prefix gồm procedure, section path và source/version tối thiểu cần thiết.

Budget đề xuất:

| Tham số | Giá trị |
| --- | ---: |
| Target | 250–350 tokens |
| Hard maximum | 450 tokens, đã gồm context prefix |
| Merge threshold | Dưới 80 tokens thì ưu tiên ghép sibling tương thích |
| Overlap | Không overlap theo phần trăm; tối đa một structural parent/unit khi cần coherence |
| Evidence injection | 3–5 chunk sau filter/ranking; không nhồi cả pack |

`TokenCounter` là interface provider-neutral. Mỗi build phải ghi `tokenizer_id`; đổi tokenizer làm invalid chunk IDs và buộc rebuild. Heuristic counter chỉ được dùng cho fixture/diagnostic, không đủ để phát hành approved index nếu chưa chứng minh hard maximum với tokenizer runtime.

## 5. Quality và release gates

Build phải fail hoặc quarantine source/chunk khi có một trong các điều kiện:

- Encoding không hợp lệ hoặc nghi mojibake chưa review.
- Thiếu provenance, authority, jurisdiction hoặc cửa sổ hiệu lực cần thiết.
- Source conflict, future-effective hoặc stale nhưng được gắn `approved`.
- Chunk vượt 450 tokens hoặc không trace được về source/section.
- Claim quy phạm không có `source_refs`/`legal_basis_refs` phù hợp.
- Chunk trộn nhiều procedure/jurisdiction/version không có quan hệ được review.
- Raw PII, form payload, chat/session data hoặc instruction-like content đi vào knowledge index.

Acceptance criteria cho Phase 1/2 sau này:

- Normalization và chunk build idempotent trên fixtures.
- Section-boundary F1 tối thiểu 95% trên fixture đã gán nhãn.
- 100% released chunk không vượt hard maximum và có provenance.
- Citation coverage 100% cho hướng dẫn quy phạm.
- Nguồn stale/future/conflict lọt vào approved retrieval: 0.
- Retrieval Recall@5 tối thiểu 95% trên claim/query golden set trước khi tích hợp LLM.

## 6. Retrieval boundary và deferred decisions

Baseline sau Phase 0 là structured filter theo `procedure_id`, jurisdiction, effective date và review status, sau đó keyword retrieval trên approved chunks. Vector retrieval chỉ được đề xuất nếu baseline miss golden set và phải có Decision/dependency/storage task riêng.

Các mục cố ý deferred:

- Concrete Pydantic/SQL schema và migration.
- Tokenizer/provider adapter.
- BM25/vector/reranker dependency.
- Neon/pgvector topology và embedding model.
- Public API changes và production ingestion schedule.
- Full-corpus processing ngoài allowlist ba MVP.

## 7. Rollback và handoff

Raw documents không bị sửa. Parsed sections, chunks, manifests và index đều là artifacts có version, có thể bỏ và build lại từ approved source snapshot. Nếu structure-aware chunking không vượt baseline trên golden set, fallback là structured procedure lookup + keyword trên section đã approved; không fallback sang whole-corpus LLM context.

D-017 đã được peer xác nhận ngày 18/07/2026 để triển khai Phase 1. D-006 đến D-008 được giữ reserved theo các tham chiếu trong proposal/PRD và không được tái sử dụng; việc bổ sung nội dung lịch sử của các Decision đó là task tài liệu riêng. Mọi thay đổi runtime schema, dependency, index/database hoặc full-corpus processing vẫn cần Decision/task mới.
