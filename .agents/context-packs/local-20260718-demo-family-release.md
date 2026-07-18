# Context Pack - local-20260718-demo-family-release

## Identity

- Task ID: `local-20260718-demo-family-release` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `feature/local-20260718-procedure-family-registry` / `809b9d0`
- Branch / worktree: `chore/local-20260718-demo-family-release` / `C:/tmp/vaic-demo-family-release`
- AI Log: `chua bat`

## Muc tieu va ranh gioi

- Goal: Tao release data local phuc vu demo tu 25 procedure-family sources bang metadata synthetic do user chi dinh, validate checksum/UTF-8/registry va build clean RAG chunks.
- Success criteria:
  - 25 source co `review_status=approved`, `document_version=2026`, `source_url=https://dichvucong.gov.vn/`, `reviewed_by=Cao`, `reviewed_at=2026-07-18`.
  - Manifest dung version `vaic-family-demo-release-v1`; report/grouped pack ghi ro `synthetic_demo` va `not_for_production=true`; output chi nam trong ignored `artifacts/`.
  - Builder doc 16 source `data/Data_DVC` trong worktree va 9 source `dataset_raw` qua path cau hinh, khong copy raw data.
  - Checksum, strict UTF-8, exact code/title, exact registry set va dual-family `2.000986` duoc validate fail closed.
  - Flat chunks load duoc boi runtime hien tai va giu approved-only retrieval contract.
- Constraints: Demo local; khong CI/CD/cloud/frontend/public API; khong commit raw data/artifact; khong goi provider; khong sua working tree chinh dang dirty.
- Stopping conditions: Dung neu raw checksum/title/code thay doi trong luc build, thieu source, output ra ngoai `artifacts/`, can production release, hoac can suy dien metadata khac voi gia tri synthetic da chot.

## Scope claim

- Files/areas: family demo release helper/CLI, normalization mojibake detector, tests `tests/rag/`, data docs, Decision Log, Context Pack.
- API/schema/contracts: Khong doi REST. Them local artifact contract `vaic-family-demo-release-v1`.
- Runtime/data: Tao ignored outputs trong `artifacts/demo-family-release/` va `artifacts/chatbot/`.
- Risk: `shared` - demo data flow; user da xac nhan synthetic `approved` va URL chinh thuc.
- Decision Log: D-014.

## Context va handoff

- Depends on: D-006, D-007, D-013; commit `809b9d0`; registry 25 source/26 relationships.
- Rollback: Xoa ignored artifacts va revert tooling/docs commit; runtime/API khong doi.
- Checks: full RAG `62 passed`; Black/flake8 changed scope pass; repository guard pass; `git diff --check` pass; real build 25 source/26 relationship/519 chunk, max 450 tokens; backend load smoke `loaded=519 approved=519`; report khong con false-positive `possible_mojibake`.
- Artifact local: `artifacts/demo-family-release/reviewed-family-sources.csv`, `artifacts/chatbot/{clean-rag-pack.jsonl,clean-rag-chunks.jsonl,clean-rag-report.json}`; tat ca ignored, khong commit.
- Risk / chua kiem chung: metadata la synthetic demo, URL la homepage thay vi deep link; chua test endpoint/LLM/frontend trong task nay; production van can K1 that.
- Claims da release: source/tooling/docs claims release khi commit/handoff; khong co process/provider dang chay.
- Viec tiep theo: merge/publish chi khi user yeu cau; sau tich hop, rebuild artifact tai worktree chay backend roi test `/v1/rag/search` va `/v1/rag/answer`.
- Publish: Khong push/merge neu user chua yeu cau ro.
