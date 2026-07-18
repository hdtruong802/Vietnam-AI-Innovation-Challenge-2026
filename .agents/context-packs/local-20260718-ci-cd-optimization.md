# local-20260718-ci-cd-optimization

## Identity

- Task ID: `local-20260718-ci-cd-optimization`
- Owner tạm thời: Codex / user-requested implementation
- Mode hiện tại: `review`
- Base ref / commit: `origin/dev` / `dda01a345bb963d390ed4cab5686fb4b7cabefe2`
- Branch / worktree: `chore/local-20260718-ci-cd-optimization`
- AI Log member / tool binding / readiness: chưa bật; không commit trong task này.

## Mục tiêu và ranh giới

- Mục tiêu: tạo fast merge gate theo vùng thay đổi, giảm local range scan, bổ sung application CI và release candidate provider-neutral.
- Non-goals: provision hosting, GitHub Environment/secret, public URL, deploy cloud, thay public API hoặc quét payload `data/**`.
- Acceptance criteria:
  - `validate_repo.py` không đọc content dưới `data/**` ở default, staged hay range mode.
  - workflow chỉ cài Node/Python dependency khi diff cần thiết; check tổng hợp vẫn có tên `repository-guard`.
  - frontend/backend có lint, type/build hoặc API test; dev chỉ sinh artifact/manifest, main chỉ promote thủ công artifact hợp lệ.
  - test local pass, không có secret/PII hoặc remote mutation.
- Constraints: Python standard library cho guard/release helper; npm/pip dependency chỉ dùng trong CI application job; giữ D-006 là `Proposed`; không tạo CD giả.
- Stop condition / blocker cần hỏi peer: dừng activation live deploy khi chưa có D-010 peer confirmation, provider, environment, secret và rollback contract; dừng nếu guard/app test hoặc checksum fail.

## Scope đã claim

- Files/areas được phép chạm: `.github/workflows/`, `scripts/ci/`, `tests/ci/`, `frontend/` scripts/config, `backend/` test/lint support, `README.md`, `docs/ai/`, `team_docs/`, `.github/BRANCH_RULES.md`.
- API, schema hoặc contract liên quan: CI job outputs; release artifact manifest schema v1. Không đổi REST API.
- Không được chạm: `data/**` payload, procedure facts, source legal, cloud account, GitHub settings, application product behavior.
- Risk: `shared`
- Decision Log liên quan: D-005, D-006, D-009; D-010 sẽ được thêm là `Proposed`.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Protocol | `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md` | Task Record, shared change, handoff. |
| Deployment | `docs/ai/DEPLOYMENT.md` | Chưa provision, provider-neutral. |
| Current guard | `.github/workflows/repository-guard.yml`, `scripts/ci/validate_repo.py` | Nút thắt check và CI contract. |
| Application manifests | `frontend/package.json`, `backend/requirements.txt` | Lệnh CI khả dụng. |
| Decisions | `docs/ai/DECISIONS.md` D-005/D-006/D-009 | Boundary scaffold, deploy và AI Log. |

## Dependencies và resource claim

- Depends on / blocked by: D-010 cần peer review trước publish/activation; provider/secret chưa có nên không có live deploy.
- Shared resource: GitHub workflow, CI check name và deploy contract.
- Claim owner + thời hạn: owner hiện tại đến handoff local; release khi test pass hoặc có blocker.
- Cách thông báo peer và điều kiện release: handoff nêu D-010 `Proposed`, check evidence và các remote action bị hoãn.

## Kiểm chứng và handoff

- Commands / manual checks: repository guard tests, changed scope/data/release tests, frontend npm checks, backend lint/test, `git diff --check`.
- Demo impact và rollback: nếu workflow lỗi, revert workflow/script/doc change; không có external deploy state.
- Evidence / kết quả:
  - `python -m unittest discover -s tests/ci -p "test_*.py"` — 17 pass.
  - `python -m unittest discover -s tests/ai_log -p "test_*.py"` — 11 pass.
  - `node --test tests/design/*.mjs` — 6 pass.
  - `python scripts/ci/validate_repo.py` và `--range origin/dev...HEAD` — pass; mỗi lệnh đo local khoảng 0.45 giây.
  - `python scripts/ci/validate_data.py --range <parent-of-data-import>...00fe58d` — pass trong khoảng 0.69 giây cho 5,652 file, không đọc payload.
  - `backend/.venv/Scripts/black.exe --check .`, `flake8 .`, `pytest -q` — pass; 5 API smoke tests pass.
  - `npm run check` trong `frontend/` — lint và production build pass; standalone output tồn tại.
  - `release_manifest.py create/verify` smoke pass; `git diff --check` pass.
- AI-Log ID + capture status: chưa có.
- Files, API và resources đã chạm: guard/workflow/release helper, backend CI support/tests/format, frontend standalone scripts/config và các docs/Decision liên quan. REST API không đổi.
- Claims đã release: local implementation hoàn tất; workflow/deploy contract chờ peer review.
- Việc tiếp theo hoặc peer có thể tiếp nhận: peer review D-010, sau đó publish branch; chỉ enable required check sau hai run xanh và chỉ chọn provider/live deploy theo Decision follow-up.
