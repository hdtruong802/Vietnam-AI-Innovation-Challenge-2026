# Context Pack - local-20260718-safe-demo-checklist

## Identity

- Task ID: `local-20260718-safe-demo-checklist`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Base ref / commit: `origin/cao` / `ebdbd69`
- Branch / worktree: `fix/local-20260718-safe-demo-checklist` / `C:\tmp\vaic-safe-demo-checklist`
- AI Log: chua bat

## Muc tieu va ranh gioi

- Muc tieu: cho phep nguoi dung chon mot thu tuc MVP va xem checklist/form fixture trong demo local.
- Non-goals: khong phe duyet K1, khong thay noi dung fixture bang yeu cau phap ly that, khong mo legacy RAG, khong thay provider/deploy.
- Acceptance criteria:
  - `dang-ky-khai-sinh` tra checklist va form fixture co noi dung khi `fixture_mode=true`.
  - Response van la `official_review_required`, `last_verified_at=null`, khong co badge "Da xac minh nguon".
  - Frontend render checklist/form fixture thay vi chuyen thang sang man hinh chan.
  - Pack RAG/disabled khong approved van fail closed va khong lo noi dung.
  - Backend va frontend tests lien quan pass.
- Constraints: ket qua cuoi cung phai dua ve local branch `cao`; khong push; khong cham thay doi local `backend/app/config.py` tai worktree chinh.
- Stop condition: dung neu can suy dien yeu cau phap ly/K1, hoac can thay public API theo cach khong tuong thich.

## Scope da claim

- Files/areas: checklist assembly trong `CopilotService`, trust/config bootstrap, legacy service syntax repair, reducer/selectors/trust UI cua procedure-case, API/RAG regression tests, Decision Log.
- API/contract: giu nguyen DTO; tai su dung `fixture_mode` de phan biet demo content.
- Khong cham: raw data, RAG source, LLM, cloud/CI/CD, `.env`.
- Risk: `shared` vi anh huong demo flow.
- Decision Log: D-006, D-013 production hardening, D-014 synthetic demo; them D-023 cho ngoai le fixture presentation.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Product context | `docs/ai/PROJECT_CONTEXT.md` | Ba pack MVP va fail-closed policy. |
| Architecture | `docs/ai/ARCHITECTURE.md` section 3/6 | Trust boundary va checklist contract. |
| Decisions | `docs/ai/DECISIONS.md` D-006, D-013, D-014 | Cam false verified; synthetic chi cho demo. |
| Backend | `backend/app/services/copilot_service.py` | Noi dung dang bi strip neu khong verified. |
| Frontend | `frontend/src/features/procedure-case/procedureCaseReducer.ts` | Official review dang ghi de flow checklist. |

## Dependencies va resource claim

- Depends on: fixture packs hien co trong `backend/app/adapters/dev_fixture.py`; sua import `AliasChoices` bi thieu tren base `cao` de backend khoi dong.
- Shared resource: none; khong khoi dong port/server trong task.
- Claim release khi commit/test/handoff hoan tat.

## Kiem chung va handoff

- Commands: backend pytest lien quan; frontend Vitest/typecheck; repo validator neu kha dung.
- Demo impact: fixture checklist/form hien thi voi warning; rollback bang revert mot commit task.
- Evidence:
  - `python -m pytest backend/tests -q`: 46 passed, 1 warning.
  - `python -m pytest tests/rag -q`: 62 passed.
  - `npm run test`: 28 passed.
  - `npm run typecheck`: passed sau `next typegen`.
  - `python scripts/ci/validate_repo.py`: blocked boi hai native hook ton tai san tren base `.codex/hooks.json`, `.cursor/hooks.json`.
  - `npm install`: baseline lock co `@eslint-community/eslint-utils@4.9.1` chi cho AIX; tests dung junction local toi dependencies da cai, khong sua lockfile.
- Files/API/resources da cham: backend checklist/trust/config syntax; frontend reducer/checklist/trust/precheck; tests; D-023.
- Claims da release: source claim release sau commit/merge local.
- Viec tiep theo: merge local commit vao `cao`, giu nguyen local change `backend/app/config.py` tai worktree chinh, sau do user test click ba fixture procedure.
