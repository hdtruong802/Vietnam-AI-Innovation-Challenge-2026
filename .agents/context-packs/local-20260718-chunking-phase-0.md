# Context Pack — local-20260718-chunking-phase-0

## Identity

- Task ID: `local-20260718-chunking-phase-0` | GitHub Issue: `chưa publish`
- Owner tạm thời: Codex
- Mode hiện tại: `review`
- Status: `handoff`
- Base ref / commit: `cao` / `fe4ff4e`
- Branch / worktree: `chore/local-20260718-chunking-contract` / `C:/tmp/vaic-local-20260718-chunking-contract`

## Mục tiêu và ranh giới

- Mục tiêu: Khóa đề xuất Phase 0 cho structure-aware chunking gồm phạm vi nguồn, lifecycle review, logical data contract, token budget, quality gates, acceptance criteria và rollback.
- Non-goals: Không viết parser/chunker runtime, không xử lý toàn bộ `dataset_raw`, không tạo embedding/index, không thêm dependency, không thay public API và không đánh dấu Decision là `Accepted`.
- Acceptance criteria: Có Decision `Proposed` liên kết task; contract mô tả đủ `SourceDocument`, `ParsedSection`, `EvidenceChunk`, `ChunkBuildReport`; phạm vi chỉ gồm ba procedure pack MVP; token budget và release gates đo được; không chứa raw data/PII; repository validation chạy đạt.
- Constraints: Policy repo là baseline; chỉ tài liệu điều phối và contract đề xuất; raw corpus tiếp tục local/ignored; base tạm dùng `cao` vì `dev` chưa có `docs/proposal.md` và D-005.
- Stop condition / blocker cần hỏi peer: Dừng trước khi đổi Decision sang `Accepted`, sửa shared runtime schema/API, thêm tokenizer/vector dependency, chọn database/index hoặc xử lý toàn bộ 5.652 tài liệu.

## Scope đã claim

- Files/areas được phép chạm: `.agents/context-packs/local-20260718-chunking-phase-0.md`, `docs/ai/CHUNKING_CONTRACT.md`, `docs/ai/DECISIONS.md`.
- API, schema hoặc contract liên quan: Logical ingestion/chunking contract ở trạng thái đề xuất; không thay public REST surface.
- Không được chạm: `backend/`, `frontend/`, dependencies, database, deploy/demo flow, `dataset_raw/` và external provider resources.
- Risk: `shared`
- Decision Log liên quan: `D-009` (`Proposed`); D-006 đến D-008 đang được proposal tham chiếu nhưng chưa có entry trong Decision Log hiện tại.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Project context | `docs/ai/PROJECT_CONTEXT.md` | Ba MVP, KPI và stack/DB còn Proposed. |
| Architecture / decision | `docs/ai/ARCHITECTURE.md`, `docs/ai/DECISIONS.md` | Boundary RAG, shared-contract policy và lịch sử Decision. |
| Product proposal | `docs/proposal.md` — procedure-pack schema, RAG lifecycle, safety/evaluation | Nguồn sự thật cho approved-only RAG, K1/K2 và fail-closed. |
| Data evidence | Phân tích metadata 5.652 file và mẫu phân tầng 122 file | Xác nhận cấu trúc field/bullet, UTF-8 và nhu cầu tách section trước token budget; không ghi raw content vào pack. |

## Dependencies và resource claim

- Depends on / blocked by: Peer review cho D-009; cần giải quyết sự thiếu đồng bộ D-006 đến D-008 trước khi publish Decision numbering.
- Shared resource: Không có runtime resource; claim tạm thời ba file docs nêu trên.
- Claim owner + thời hạn: Codex đến khi handoff Phase 0.
- Cách thông báo peer và điều kiện release: Handoff kèm validation evidence; release khi record chuyển `handoff` hoặc `done`.

## Kiểm chứng và handoff

- Commands / manual checks: `python scripts/ci/validate_repo.py`; `git diff --check`; kiểm tra Markdown links và không có raw data/dependency/API diff.
- Demo impact và rollback: Không ảnh hưởng runtime/demo. Rollback bằng cách bỏ ba thay đổi tài liệu trước khi Decision được chấp nhận.
- Evidence / kết quả: `Repository guard passed: default repository scope is valid.`; `git diff --check` pass; không có diff trong backend/frontend/dependencies/public API/raw data.
- Files, API và resources đã chạm: Context Pack này, `docs/ai/CHUNKING_CONTRACT.md`, `docs/ai/DECISIONS.md`; không chạm API/runtime resource.
- Claims đã release: Đã release khi chuyển `handoff`.
- Việc tiếp theo hoặc peer có thể tiếp nhận: Peer data/grounding và backend review D-009; chỉ sau `Accepted` mới tạo task Phase 1.
