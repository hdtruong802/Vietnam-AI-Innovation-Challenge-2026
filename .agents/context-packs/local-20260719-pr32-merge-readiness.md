# local-20260719-pr32-merge-readiness

## Identity

- Task ID: `local-20260719-pr32-merge-readiness` | GitHub Issue: chưa có
- Owner tạm thời: Codex theo yêu cầu của user
- Mode hiện tại: `implement`
- Base ref / commit: `origin/dev` / `c7f4be7dc0678b07d240298ea239212eed7b0cd2`
- Branch / worktree: `fix/local-20260719-ai-log-waiver` / `.worktrees/ai-log-waiver`
- AI Log member / tool binding / readiness: sẽ dùng manual fallback cho commit của task này; không tạo hay suy diễn evidence cho commit cũ.

## Mục tiêu và ranh giới

- Mục tiêu: làm PR #32 đủ điều kiện policy để review/merge bằng waiver truy vết được cho đúng hai commit lịch sử thiếu AI Log, đồng thời sửa marker merge và ID Decision trùng trong Decision Log.
- Non-goals: không rewrite lịch sử `dev`, không tắt AI Log toàn cục, không sửa `data/**`, RAG/runtime/frontend, không merge `main` hay thay đổi deploy.
- Acceptance criteria:
  - chỉ hai SHA `247311d9e510406642be3b37980131ac02ecbcc5` và `e4ab0b994e2b9510def369ae7ded24a54e064669` được miễn history trailer;
  - commit mới không có trailer/evidence vẫn fail;
  - Decision Log không còn marker Git conflict hay ID trùng;
  - guard unit test, guard range và `git diff --check` pass.
- Constraints: waiver phải có SHA đầy đủ, lý do và Decision/peer confirmation; policy repo vẫn là baseline; user xác nhận cho phép bỏ qua AI Log của hai commit cũ.
- Stop condition / blocker cần hỏi peer: dừng nếu `origin/dev` thay đổi trước khi publish, phát hiện thêm conflict marker ngoài Decision Log, hoặc cách sửa đòi exempt wildcard/tắt enforcement toàn cục.

## Scope đã claim

- Files/areas được phép chạm: `evidence/ai-log/policy.json`, `scripts/ci/validate_repo.py`, `tests/ci/test_validate_repo.py`, `docs/ai/DECISIONS.md`, README/deployment references cần đổi ID demo gate, Context Pack này và AI Log evidence của commit mới.
- API, schema hoặc contract liên quan: AI Log history policy / CI guard; không đổi product API.
- Không được chạm: `data/**`, backend/frontend runtime, secrets, cloud/deploy settings, lịch sử Git của peer.
- Risk: `shared`
- Decision Log liên quan: D-009 và D-020/D-021 sẽ ghi tại task này.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Protocol | `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md` | Shared-risk, AI Log và publish rules. |
| Decision | `docs/ai/DECISIONS.md` D-009 và marker tại index | Chính sách evidence và lỗi tài liệu cần sửa. |
| Guard | `scripts/ci/validate_repo.py:480-486,588-642` | Policy shape và history enforcement hiện hành. |
| Tests | `tests/ci/test_validate_repo.py:120-390` | Fixture và regression cho guard. |
| CI log PR #32 | run `29660448197` | Hai SHA thiếu trailer là blocker thực tế. |

## Dependencies và resource claim

- Depends on / blocked by: user đã xác nhận waiver; cần kiểm tra `origin/dev` không đổi trước publish.
- Shared resource: `evidence/ai-log/policy.json`, CI history guard và Decision Log.
- Claim owner + thời hạn: Codex đến khi handoff/publish fix branch.
- Cách thông báo peer và điều kiện release: PR ghi D-021, hai SHA, test evidence và rollback; release claim sau checks pass.

## Kiểm chứng và handoff

- Commands / manual checks: `python -m unittest discover -s tests/ci -p test_*.py` (21 pass); `python -m unittest discover -s tests/ai_log -p test_*.py` (12 pass); `python scripts/ci/validate_repo.py` và `--range origin/main...HEAD` pass; `git diff --check` trên scope ngoài `data/**` pass.
- Demo impact và rollback: không ảnh hưởng runtime/deploy; revert các commit task này để khôi phục strict policy trước đó.
- Evidence / kết quả: PR #32 không có Git conflict, nhưng trước task có marker conflict trong `docs/ai/DECISIONS.md`; marker và ID trùng đã được xử lý. Full `git diff --check origin/main...HEAD` vẫn báo trailing whitespace trong raw `data/Data_DVC/**` đã có từ PR #32, ngoài claim; CI data metadata hiện pass nhưng data owner vẫn phải review trước merge main.
- AI-Log ID + capture status: `log-28068a92fa804be28939e27b / manual`; `log-265c4077f0874531b15e6f25 / warning` cho Context Pack follow-up không có prompt mới.
- Files, API và resources đã chạm: policy AI Log, repository guard/tests, Decision Log, README/Deployment references và Context Pack; không chạm public API/runtime/data.
- Claims đã release: release sau khi PR fix vào `dev` và CI của PR #32 xanh.
- Việc tiếp theo hoặc peer có thể tiếp nhận: peer review waiver/data/RAG scope của PR #32 trước merge main.
