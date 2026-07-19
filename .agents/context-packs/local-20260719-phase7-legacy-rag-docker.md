# Context Pack - local-20260719-phase7-legacy-rag-docker

## Task Record

- Task ID: `local-20260719-phase7-legacy-rag-docker`
- Mode: `verify-demo`
- Status: `handoff`
- Owner tam thoi: Codex
- Base ref: `cao` / `5d5530e`
- Branch/worktree: `fix/local-20260719-phase7-legacy-rag-docker` / `C:\tmp\vaic-phase7-rag-docker`
- Risk: `shared` (public route availability and backend container defaults)
- AI Log: chua bat; no prompt capture for this task

## Goal, Success Criteria, Constraints, Stopping Conditions

- Goal: harden Phase 7 by removing legacy RAG routes from the default public runtime and making the backend container an offline-safe MVP demo runtime.
- Success Criteria:
  - With `LEGACY_RAG_ENABLED=false`, `/v1/rag/search` and `/v1/rag/answer` are not mounted and are absent from OpenAPI.
  - With `LEGACY_RAG_ENABLED=true`, both legacy routes remain available for explicit local debugging.
  - Frontend has no legacy RAG call and continues to use `/v1/intake/turn`.
  - Backend Docker defaults to `PROCEDURE_DATA_MODE=demo_pack`, `RAG_MODE=disabled`, `LLM_MODE=disabled`, and `LEGACY_RAG_ENABLED=false`.
  - Container runs as a non-root user, exposes a healthcheck, and does not copy raw data, generated RAG artifacts, secrets, tests, or model assets.
  - Contract tests, full backend tests, golden evaluation, and repository staged guard pass.
- Constraints: keep legacy source code; no cloud deploy, secret, provider call, dependency addition, model download, raw data copy, or large artifact in the image.
- Stopping Conditions: stop and ask if implementation requires cloud access, a secret, network/model download, a large artifact, destructive Git action, or a backward-incompatible change outside the two legacy routes.

## Resource Claims

- Files/areas: backend app factory/config contract, legacy route tests, backend Dockerfile/.dockerignore, Phase 7 documentation and decision evidence.
- API/schema/contracts: route availability only; canonical `/v1/intake/turn` and response schemas remain unchanged.
- Runtime/data: no shared port/provider/cloud resource; Docker build is optional and only allowed without pulling new images.
- Decision: D-026; user selected Phase 7 Option 1.

## Context Selected

- `docs/ai/PROJECT_CONTEXT.md`: legacy RAG is disabled by default and canonical guided flow uses base REST contract.
- `docs/ai/ARCHITECTURE.md`: frontend-to-orchestrator boundary and fail-closed runtime requirements.
- `docs/ai/DECISIONS.md` D-013/D-017/D-018: legacy routes were additive, demo mode must not imply K1, deterministic intake is canonical.
- `backend/app/main.py`: currently mounts `rag.router` and advertises routes unconditionally.
- `backend/app/config.py`: existing `legacy_rag_enabled=False` kill switch.
- `backend/tests/test_api_contract.py`, `backend/tests/test_demo_pack_adapter.py`: route set currently expects legacy routes by default.
- `backend/Dockerfile`, `backend/.dockerignore`: existing non-root image lacks demo/offline defaults and healthcheck.
- `frontend/src/features/procedure-case/api.ts`: frontend already calls `/v1/intake/turn` only.

## Verification, Rollback, Handoff

- Planned checks: focused route/Docker tests; full backend and evaluation tests; golden CLI; staged repository guard; Docker build/smoke only when local daemon and base image are already available.
- Demo impact: default runtime becomes smaller and fail-closed; normal guided demo remains on `/v1/intake/turn`.
- Rollback: revert task commit or explicitly set `LEGACY_RAG_ENABLED=true` for local debugging; no data migration or cloud state.
- Evidence:
  - Focused route/demo-pack/container contracts: `27 passed`.
  - Full backend + evaluation regression: `90 passed`, one existing Starlette deprecation warning.
  - Golden CLI: 60/60 correct; false/missed/wrong route 0; `false_verified=0`; fail-closed/demo/HTTP errors 0.
  - Static Docker contract after PORT-aware healthcheck: `2 passed`.
  - Flake8 on all changed Python files: pass.
  - Frontend source scan: `/v1/intake/turn` is the only API route call; no `/v1/rag` call.
  - Docker runtime build/smoke: not run because the local Docker daemon was stopped; no pull or network access attempted.
- Resource release: source/API/Docker claims released at handoff; no port, provider, secret, image, or cloud resource was claimed.
- Publish: no push/PR unless explicitly requested.
