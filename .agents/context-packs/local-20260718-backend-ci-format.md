# Context Pack — local-20260718-backend-ci-format

> Sửa lỗi CI backend đã xác minh từ GitHub Actions; không sửa frontend hoặc thay đổi workflow/API.

## Identity

- Task ID: `local-20260718-backend-ci-format`
- Owner tạm thời: `hdtruong802 / Codex`
- Mode hiện tại: `review`
- Base ref / commit: `origin/dev` / `169404cf9f39655106e18c7ea5570183601fe609`
- Branch / worktree: `fix/local-20260718-backend-ci-format` / `.worktrees/backend-ci-format`
- AI Log member / tool binding / readiness: chưa bật; không commit/push trong task này.

## Mục tiêu và ranh giới

- Mục tiêu: đưa bốn module RAG backend về định dạng Black mà không thay đổi hành vi, để backend CI vượt qua bước `black --check .`.
- Non-goals: sửa frontend, workflow CI, public API/schema, logic RAG, dependency, data hoặc deploy.
- Acceptance criteria:
  - `black --check .` trong `backend/` pass.
  - `flake8 .` và `pytest -q` trong `backend/` pass.
  - Diff chỉ gồm định dạng ở bốn module RAG và Context Pack này.
- Constraints: chỉ sửa format; policy repo là baseline; không commit hoặc push khi chưa có yêu cầu mới.
- Stop condition / blocker cần hỏi peer: dừng nếu Black thay đổi hành vi rõ ràng, lint/test phát hiện lỗi không thuần format, hoặc cần chạm frontend/workflow/API.

## Scope đã claim

- Files/areas được phép chạm:
  - `backend/app/rag/normalization.py`
  - `backend/app/rag/parsing.py`
  - `backend/app/rag/chunking.py`
  - `backend/app/rag/retrieval.py`
  - `.agents/context-packs/local-20260718-backend-ci-format.md`
- API, schema hoặc contract liên quan: không có; chỉ định dạng mã nguồn.
- Không được chạm: `frontend/**`, `.github/workflows/**`, `data/**`, deploy/config provider, REST API và dependency manifest.
- Risk: `isolated`
- Decision Log liên quan: D-005 (backend scaffold); không cần Decision mới vì không đổi behavior/contract.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| CI failure | GitHub Actions runs `29629835235`, `29629850220` | Xác nhận Black báo đúng bốn file RAG. |
| Protocol | `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md` | Worktree, scope và handoff. |
| Backend boundary | `docs/ai/PROJECT_CONTEXT.md`, `docs/ai/ARCHITECTURE.md`, D-005 | Không mở rộng sang RAG capability/API. |
| Source | Bốn module RAG được nêu ở scope | Giới hạn thay đổi ở formatting. |

## Dependencies và resource claim

- Depends on / blocked by: không có; frontend CI fail được ghi nhận nhưng ngoài scope task.
- Shared resource: `none` — không đổi contract hay behavior.
- Claim owner + thời hạn: `hdtruong802 / Codex` tới khi hoàn tất verify local.
- Cách thông báo peer và điều kiện release: handoff nêu rõ frontend vẫn còn lỗi riêng; release claim sau khi Black/lint/test backend pass.

## Kiểm chứng và handoff

- Commands / manual checks: `black --check .`, `flake8 .`, `pytest -q` trong `backend/`; `git diff --check`.
- Demo impact và rollback: không ảnh hưởng demo/API; rollback bằng revert formatting diff.
- Evidence / kết quả:
  - Black `26.5.1` đã reformat đúng bốn file scope; peer review xác nhận AST trước/sau giống nhau, không đổi API hay logic.
  - `flake8 .` trong `backend/`: pass.
  - `pytest -q` trong `backend/`: `12 passed`; còn một cảnh báo deprecation từ dependency `TestClient`/Starlette, không liên quan diff.
  - `python scripts/ci/validate_repo.py` và `git diff --check`: pass.
  - `black --check .` cục bộ bị timeout không có error output trên Windows sau 120 giây; CI Linux trước đó chỉ báo bốn file này sai format. Chưa khẳng định check full-scope local đã hoàn thành.
- AI-Log ID + capture status: chưa có.
- Files, API và resources đã chạm: bốn module RAG trong scope; REST API/schema/resources không đổi.
- Claims đã release: backend formatting đã sẵn sàng peer review; không có resource runtime cần release.
- Việc tiếp theo hoặc peer có thể tiếp nhận: Member 2 hoặc peer review diff; sau khi commit/push được yêu cầu, rerun backend CI. Owner frontend sửa lint riêng trước khi toàn bộ PR xanh.
