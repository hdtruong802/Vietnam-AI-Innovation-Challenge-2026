# Context Pack — local-20260718-gcp-backend-deploy

> Deploy backend-only lên Cloud Run sau peer confirmation. Không deploy frontend, data/RAG/LLM hoặc bất kỳ dữ liệu pháp lý nào.

## Identity

- Task ID: `local-20260718-gcp-backend-deploy` | GitHub Issue: chưa tạo
- Owner tạm thời: `hdtruong802`
- Mode cuối: `verify-demo`; Cloud Run production-disabled đã public-smoke pass
- Base ref / commit: `origin/dev` / `32ea0cdfec793b4a0eef5345ba7539806ec292a9`
- Branch / worktree: `chore/local-20260718-gcp-backend-deploy` / `.worktrees/gcp-backend-deploy`
- AI Log member / tool binding / readiness: `hdtruong802 / codex manual / doctor --strict pass`

## Mục tiêu và ranh giới

- Mục tiêu: thêm container image, ignore rules, runbook và evidence test để FastAPI backend có thể được deploy thủ công lên Cloud Run ở `asia-southeast1` với runtime fail-closed.
- Non-goals: không deploy frontend, database, RAG, LLM, ingestion, Secret Manager, storage, VPC/NAT hoặc CI/CD cloud.
- Acceptance criteria: Docker chạy non-root, dùng `PORT`; production-disabled trả `/health` `degraded`, catalog `unavailable`, checklist/validation không trả fixture hoặc `verified_guidance`; runbook có preflight, candidate/no-traffic smoke, traffic switch, rollback và budget alert.
- Constraints: chỉ `backend/` và tài liệu deploy liên quan; image không chứa `.env`, source test/cache, raw PII hoặc secret; runtime service account không có role/secret; public access chỉ cho demo API sau khi peer cho phép.
- Stop condition / blocker cần hỏi peer: dừng khi Decision/scope bị thay thế, billing/credit không thuộc team, IAM thiếu, local/container/candidate smoke lỗi, hoặc production vẫn có khả năng chạy `fixture`.

## Scope đã claim

- Files/areas được phép chạm: `backend/Dockerfile`, `backend/.dockerignore`, `backend/.gcloudignore`, `backend/tests/test_api_contract.py`, `docs/runbooks/cloud-run-backend.md`, `docs/api/BACKEND_CONTRACT.md`, `docs/ai/DEPLOYMENT.md`, `docs/ai/DECISIONS.md`, Context Pack này.
- API, schema hoặc contract liên quan: sáu route hiện hữu; không thêm route hoặc thay public schema.
- Không được chạm: `frontend/**`, procedure facts/fixture content, `data/**`, RAG/LLM/provider adapter, workflow GitHub, remote/cloud resource.
- Risk: `shared`
- Decision Log liên quan: D-005 (`Accepted`), D-006 (`Accepted`), D-010 (`Proposed`), D-012 (`Accepted`). Peer: `hdtruong802` (user), 2026-07-18.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Project/deploy contract | `docs/ai/DEPLOYMENT.md` | Giữ deploy backend-only production-disabled và không thay CD hiện có. |
| Architecture decision | `docs/ai/DECISIONS.md` — D-005, D-006, D-010, D-012 | Xác định target/deploy backend-only đã được chấp thuận; capability khác vẫn cần evidence riêng. |
| Backend contract | `docs/api/BACKEND_CONTRACT.md` | Giữ nguyên sáu route, error envelope và fail-closed semantics. |
| Runtime code/test | `backend/app/config.py`, `backend/app/dependencies.py`, `backend/app/routers/health.py`, `backend/tests/test_api_contract.py` | Xác nhận `fixture` bị chặn ở production và capability disabled có thể smoke test. |
| Cloud Run / Artifact Registry | Official Cloud Run container contract, deploy guide và Artifact Registry Docker docs | `PORT`, candidate/no-traffic, immutable image tag/digest, same-region repository. |

## Dependencies và resource claim

- Depends on / blocked by: đã hoàn tất billing/credit, IAM tối thiểu, local/container smoke và public smoke của revision đầu tiên.
- Shared resource: deployment contract và backend runtime image.
- Claim owner + thời hạn: `hdtruong802`, chỉ trong Task Record này; release khi handoff review hoàn tất.
- Cách thông báo peer và điều kiện release: peer `hdtruong802` đã xác nhận D-006/D-012; revision đầu tiên dùng public smoke vì Cloud Run không hỗ trợ `--no-traffic` khi tạo service. Revision sau phải dùng candidate `--no-traffic` trước traffic switch.

## Kiểm chứng và handoff

- Commands / manual checks: `python -m pytest -q`, `python -m black --check .`, `python -m flake8 .` từ `backend/`; Docker build/run smoke nếu Docker sẵn sàng; repository guard và `git diff --check`.
- Demo impact và rollback: artifact local không thay demo; deploy sau này dùng revision candidate `--no-traffic`, rollback traffic về revision trước; deploy đầu thất bại giữ fallback local.
- Evidence / kết quả:
  - `$env:PYTHONPATH='backend'; backend/.venv/Scripts/python.exe -m pytest -q backend/tests tests`: `41 passed` (một warning deprecation của dependency test client); đây là full suite hiện có, gồm test production-disabled intake mới.
  - `backend/.venv/Scripts/python.exe -m flake8 app tests main.py`: pass.
  - Black trong image Linux từ lockfile: `30 files would be left unchanged`; Black import trực tiếp từ venv Windows không hoàn thành trong 120 giây nên runbook dùng image đã build để check format ổn định.
  - `docker build --pull --tag vngov-api:local backend`: pass; image chạy `uid=10001(app)`.
  - Production-disabled smoke: health `degraded`, 6 OpenAPI routes, catalog `unavailable`, intake không nhận diện fixture, checklist/validation `official_review_required`, error envelope có `X-Request-ID`, rate limit `429`; test thêm `PORT=18081` pass.
  - Runtime image không có `.env`, `tests/`, `main.py`, `AI_API_KEY`, `AI_PROVIDER` hoặc `DATABASE_URL` trong config environment.
  - `python scripts/ci/validate_repo.py`: pass; `backend/.venv/Scripts/python.exe -m pytest -q tests/ci`: `17 passed`.
  - Cloud preflight pass: project `ringed-choir-424101-t4`, region `asia-southeast1`, billing enabled; deployer là Project Owner và Billing Admin.
  - Budget alert đã tạo: `billingAccounts/0152AE-B51BC4-DCC04A/budgets/0ebd8f24-0de2-40b7-85ec-3977cb0a1269`, 1,000,000 VND/tháng, scoped vào project, ngưỡng 10/25/50/80/100%.
  - Artifact Registry `vngov-backend` cùng region, Docker immutable tags; runtime account `vngov-api-runtime` không có role/secret. Cloud Build `8ef35d72-ee00-4b7b-8f21-d8791d7b4bba` build source backend từ commit `b49ca1d31dc5c773a934d003353bc58a72355c08` thành image digest `sha256:83d9170307385b8bf34247b2d5484c47aa8bf69e666a7661acba68a08ddf74b8`.
  - Cloud Run service `vngov-api`, revision `vngov-api-00001-def`, public URL `https://vngov-api-j53prjslqa-as.a.run.app`. Runtime là 1 vCPU/512 MiB, request-based, min 0/max 1, timeout 20 giây; `APP_ENV=production`, procedure data/RAG/LLM đều `disabled`, CORS rỗng, không có database, Secret Manager, storage, VPC/NAT hay AI provider.
  - Public smoke pass: `/health` production/degraded với ba capability disabled; `/openapi.json` đúng 6 route; `/docs` 200; catalog gồm 3 summary `unavailable` không fixture; recommend/intake/checklist/validation fail-closed; error envelope có `X-Request-ID`; rate limit trả 429 và reset sau window.
- AI-Log ID + capture status: `log-d98438a57f24450daaabfc68` (manual prompt deploy) và `log-120748f2fc394362b05479b9` (no-new-prompt warning) cho hai commit artifact/runbook ban đầu.
- Files, API và resources đã chạm: Docker/ignore files, backend contract test, D-012, deployment contract, Cloud Run runbook và Context Pack; không đổi API/schema.
- Claims đã release: local container/port đã dừng; service, Artifact Registry và budget là state Cloud đã bàn giao, không phải resource claim độc quyền. Không còn smoke identity tạm.
- Việc tiếp theo hoặc peer có thể tiếp nhận: frontend chỉ được thêm origin cụ thể vào `CORS_ALLOWED_ORIGINS` sau Task Record/peer confirmation; data/RAG/LLM vẫn fail-closed cho đến khi có release evidence. Deploy sau dùng candidate `--no-traffic` và rollback về revision stable này.
