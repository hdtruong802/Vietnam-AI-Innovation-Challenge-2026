# Context Pack — local-20260717-prompt-intake-gate

> Task Record local cho Prompt Intake Gate dùng chung. Không chứa prompt nhạy cảm, secret hoặc transcript dài.

## Identity

- Task ID: `local-20260717-prompt-intake-gate` | GitHub Issue: `chưa publish`
- Owner tạm thời: Codex (theo yêu cầu hiện tại của team)
- Mode hiện tại: `handoff`
- Base ref / commit: `b3aac84`
- Branch / worktree: `truong` / workspace local hiện tại

## Mục tiêu và ranh giới

- Mục tiêu: buộc mọi agent dùng cùng Prompt Intake Gate trước task thực chất, với Goal, Success Criteria, Constraints và Stopping Conditions rõ ràng.
- Non-goals: tạo hook/native skill/MCP, thay đổi application code, thêm remote workflow, bắt các câu chào hỏi/status/Q&A ngắn phải theo gate, hoặc kéo dài prompt bằng ví dụ lặp lại.
- Acceptance criteria:
  - [x] `AGENTS.md` là nguồn sự thật ngắn gọn cho gate và nêu hành vi dừng/hỏi gộp.
  - [x] Task Record/Context Pack có trường Constraints; playbook và adapter cùng tham chiếu source chung.
  - [x] Decision D-004 ghi local-only, peer-equal workflow change.
  - [x] Repository guard/test fixture phát hiện thiếu gate hoặc Constraints.
- Constraints: policy hiện có của repo; toàn bộ thay đổi local-only, không commit, push, remote/GitHub mutation hoặc cài công cụ mới.
- Stop condition / blocker cần hỏi peer: nếu thay đổi đòi hỏi vendor-specific rule, prompt history/telemetry hoặc làm gate áp dụng cho status/Q&A ngắn.

## Scope đã claim

- Files/areas được phép chạm: `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md`, `docs/ai/DECISIONS.md`, `.agents/context-packs/TEMPLATE.md`, `.agents/playbooks/claim-task.md`, `.agents/playbooks/prepare-context.md`, `CLAUDE.md`, `.cursor/rules/00-team-protocol.mdc`, `docs/ai/adapters/antigravity.md`, `scripts/ci/validate_repo.py`, `tests/ci/test_validate_repo.py`.
- API, schema hoặc contract liên quan: Prompt Intake Gate và fields của Task Record/Context Pack.
- Không được chạm: application code, provider hook/skill/MCP config, GitHub workflow/remote settings, secrets/data.
- Risk: `shared`
- Decision Log liên quan: `D-004`

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Quy tắc hiện tại | `AGENTS.md` | Nguồn chung, thứ tự ưu tiên và luồng task hiện có. |
| Protocol | `docs/ai/TEAM_PROTOCOL.md` — Task Record, mode, quality gate | Đồng bộ record/context không lặp policy. |
| Template/playbook | `.agents/context-packs/TEMPLATE.md`, `.agents/playbooks/claim-task.md`, `.agents/playbooks/prepare-context.md` | Thêm Constraints và kiểm tra trước explore. |
| Adapter | `CLAUDE.md`, `.cursor/rules/00-team-protocol.mdc`, `docs/ai/adapters/antigravity.md` | Bảo đảm bốn agent nhận cùng rule, không thêm vendor config. |
| Guard | `scripts/ci/validate_repo.py`, `tests/ci/test_validate_repo.py` | Ngăn prompt gate/template bị drift. |

## Dependencies và resource claim

- Depends on / blocked by: không có.
- Shared resource: `none`.
- Claim owner + thời hạn: Codex trong turn hiện tại; release khi handoff.
- Cách thông báo peer và điều kiện release: D-004, Context Pack và handoff local; không cần remote.

## Kiểm chứng và handoff

- Commands / manual checks: `python -m unittest discover -s tests/ci -p "test_*.py"`, `python scripts/ci/validate_repo.py`, `git diff --check`.
- Demo impact và rollback: không ảnh hưởng application/demo; rollback là bỏ thay đổi policy local này.
- Evidence / kết quả: `python -m unittest discover -s tests/ci -p "test_*.py"` (8/8 pass); `python scripts/ci/validate_repo.py` pass; `git diff --check` pass. Không gọi network, `gh`, remote hoặc cài công cụ.
- Files, API và resources đã chạm: `AGENTS.md`; protocol/Decision Log; Context Pack template; claim/prepare playbooks; Claude/Cursor/Antigravity adapters; repository guard và Python tests.
- Claims đã release: `released` — không có port, DB, model hoặc demo resource chung được giữ.
- Việc tiếp theo hoặc peer có thể tiếp nhận: dùng template/task record mới cho prompt thực chất; review wording nếu gate tạo friction không mong muốn.
