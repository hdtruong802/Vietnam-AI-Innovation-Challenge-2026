# Context Pack — local-20260717-impeccable-cli

> Task Record local cho integration Impeccable ở chế độ CLI advisory. Không ghi credential, output audit thô có dữ liệu nhạy cảm hoặc cấu hình vendor-native.

## Identity

- Task ID: `local-20260717-impeccable-cli` | GitHub Issue: `chưa publish`
- Owner tạm thời: Codex (theo yêu cầu hiện tại của team)
- Mode hiện tại: `handoff`
- Base ref / commit: `b3aac84`
- Branch / worktree: `truong` / workspace local hiện tại

## Mục tiêu và ranh giới

- Mục tiêu: thêm một audit UI portable chạy qua `npx impeccable@3.2.1`, context thiết kế tối thiểu và báo cáo Markdown có thể review bởi mọi agent.
- Non-goals: cài package vào repo, chạy native skill/hook, tạo MCP, cấu hình vendor, thêm CI blocking, audit UI thật hoặc thay đổi remote/GitHub.
- Acceptance criteria:
  - [x] Có adapter `docs/PRODUCT.md` và `docs/DESIGN.md`, được liên kết từ tài liệu vận hành.
  - [x] Wrapper tạo report Markdown, xem exit `0`/`2` là advisory hợp lệ và lỗi rõ khi detector/JSON lỗi.
  - [x] Policy chỉ cho phép shared waiver trong `.impeccable/config.json`; local/raw artifacts bị ignore.
  - [x] Unit tests không gọi network và repository guard vẫn xanh.
- Stop condition / blocker cần hỏi peer: không chọn framework/frontend path; không chạy detector thật cho đến khi có UI target hoặc local URL.

## Scope đã claim

- Files/areas được phép chạm: `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/design/`, `docs/ai/DECISIONS.md`, `docs/ai/TEAM_PROTOCOL.md`, `README.md`, `.gitignore`, `.impeccable/config.json`, `.agents/playbooks/impeccable-audit.md`, `scripts/design/`, `tests/design/`, `scripts/ci/validate_repo.py`, `tests/ci/test_validate_repo.py`, workflow guard khi cần chạy test wrapper.
- API, schema hoặc contract liên quan: CLI contract `--task`, `--target`, `--url`, `--scope`; report `docs/design/reviews/<task-id>-impeccable.md`.
- Không được chạm: application code, dependency manifest, `.codex/hooks.json`, `.cursor/hooks.json`, `.agents/skills/`, MCP config, GitHub remote/settings.
- Risk: `shared`
- Decision Log liên quan: `D-003`

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Quy tắc chung | `AGENTS.md` | Cấm native vendor skill/hook/MCP và yêu cầu Context Pack cho task shared. |
| Quy trình | `docs/ai/TEAM_PROTOCOL.md` — modes, Decision Log, quality gate | Giữ local-first, peer-equal và xác định evidence/handoff. |
| Product / architecture | `docs/ai/PROJECT_CONTEXT.md`, `docs/ai/ARCHITECTURE.md` | Xác nhận product, frontend path và stack đều `TBD`; không hard-code framework. |
| Quyết định trước | `docs/ai/DECISIONS.md` — D-002 | Không mở rộng sang MCP runtime hoặc cấu hình provider. |
| Workflows | `.agents/playbooks/prepare-context.md`, `implement-handoff.md`, `review-merge.md` | Tạo record, thực hiện một writer và chuẩn bị review/handoff. |
| Tham khảo ngoài repo | Impeccable `package.json`, `README.md`, `cli/engine/cli/main.mjs`, `skill/reference/init.md`, `site/content/reference/config.md` | Xác nhận pin `3.2.1`, Node `>=22.12.0`, exit `2` cho finding, docs adapter và policy waiver. |

Chỉ giữ các nguồn trên; không sao chép code, template hay cấu hình native của Impeccable.

## Dependencies và resource claim

- Depends on / blocked by: UI path, framework, package manager và design system chưa được team chốt.
- Shared resource: `none` (không dùng port, DB, model download hay demo environment).
- Claim owner + thời hạn: Codex cho scope bootstrap này, release khi record chuyển `handoff` trong turn hiện tại.
- Cách thông báo peer và điều kiện release: Decision `D-003`, README/playbook và handoff nêu rõ CLI/report chung; peer chỉ cần claim task UI riêng trước khi dùng.

## Kiểm chứng và handoff

- Commands / manual checks: `node --test tests/design`, `python -m unittest discover -s tests/ci -p "test_*.py"`, `python scripts/ci/validate_repo.py`, `git diff --check`.
- Demo impact và rollback: không ảnh hưởng runtime/demo; rollback là bỏ wrapper/docs/config trong local change, không có package hay remote state cần gỡ.
- Evidence / kết quả: `node scripts/design/impeccable-audit.mjs --help`; `node --test tests/design/test_impeccable_audit.mjs tests/design/test_impeccable_policy.mjs` (6/6 pass); `python -m unittest discover -s tests/ci -p "test_*.py"` (7/7 pass); `python scripts/ci/validate_repo.py` pass; `git diff --check` pass. Không gọi detector thật, network, `gh` hay remote.
- Files, API và resources đã chạm: adapters `docs/PRODUCT.md`/`docs/DESIGN.md`; `docs/design/`; D-003/protocol/README; `.impeccable/config.json`/`.gitignore`; playbook; wrapper; Node/Python tests; workflow guard local.
- Claims đã release: `released` — không có port, DB, model hoặc demo resource chung được giữ.
- Việc tiếp theo hoặc peer có thể tiếp nhận: khi có UI, hoàn thiện `docs/PRODUCT.md`/`docs/DESIGN.md`, claim scope UI rồi chạy audit theo playbook; chỉ cân nhắc CI/native integration qua Decision mới.
