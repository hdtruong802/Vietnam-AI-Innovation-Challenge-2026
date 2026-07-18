# Vietnam AI Innovation Challenge 2026

> Không gian làm việc chung cho team 6 người xây dựng sản phẩm AI-native tại hackathon.

## Trạng thái

- Nhánh tích hợp: `dev`
- Bản demo/release ổn định: `main`
- Đề bài và ba MVP hiện hành: đã chốt tại [Project Context](docs/ai/PROJECT_CONTEXT.md) theo D-007
- Delivery surface: web-first theo D-008 — standalone web app, widget/iframe và headless API; không có mobile/native deliverable
- D-005 đã chấp thuận scaffold Next.js/FastAPI; D-010 đề xuất fast CI và provider-neutral release artifact. RAG, trust policy, widget hoàn chỉnh và live deploy topology vẫn `Proposed` trong D-006, chưa provision
- AI Log đa-agent: prompt-only, local source binding và commit trailers theo D-009; không lưu transcript/session đầy đủ
- D-018 dùng demo gate client-side: nút “Vào demo ngay” tạo session theo tab cho `Khách demo`; không có tài khoản, database, token hay backend auth trong phạm vi demo hiện tại.
- Nơi theo dõi công việc: Task Record cục bộ; GitHub Issue chỉ được tạo sau khi team chọn publish
- Bootstrap nền đã được merge qua PR #1 và #2; workflow guard có trong `main`, nhưng run status, labels, branch protection và required checks chưa được xác minh bằng quyền GitHub hợp lệ

## Bắt đầu tại đây

1. Đọc [quy tắc chung cho agent](AGENTS.md), [team protocol](docs/ai/TEAM_PROTOCOL.md) và context phù hợp.
2. Tạo hoặc claim một **Task Record cục bộ**: mode, acceptance criteria, files/API/resources sẽ chạm, risk và dependency. Với task code/API/data/config/demo hoặc `risk:shared`, bắt đầu từ [Context Pack template](.agents/context-packs/TEMPLATE.md).
3. Tạo branch từ `dev`: `feature/<task>-<slug>`, `fix/<task>-<slug>`, `chore/<task>-<slug>` hoặc `spike/<task>-<slug>`.
4. Làm việc trong branch/worktree riêng, kiểm chứng và bàn giao theo Task Record.
5. Chỉ khi team chọn publish: sao chép Task Record sang GitHub Issue, rồi mở PR về `dev`.

Không có vai trò hoặc quyền ưu tiên cố định: mọi thành viên và mọi coding agent cùng tuân thủ một protocol. Owner của Task Record chỉ chịu trách nhiệm tạm thời cho phạm vi đã claim.

Context pack tối thiểu gồm [Project context](docs/ai/PROJECT_CONTEXT.md), [Architecture](docs/ai/ARCHITECTURE.md), [Decision Log](docs/ai/DECISIONS.md) và các tài liệu đúng với task. Bốn mode portable là `explore`, `implement`, `review` và `verify-demo`; xem [protocol](docs/ai/TEAM_PROTOCOL.md) để ghi resource claim và dùng worktree.

## Tài liệu điều hành

| Tài liệu | Dùng khi |
| --- | --- |
| [Project context](docs/ai/PROJECT_CONTEXT.md) | Chốt bài toán, MVP, scope và lệnh chạy. |
| [Architecture](docs/ai/ARCHITECTURE.md) | Ghi thành phần, interface và thay đổi xuyên lane. |
| [Decision log](docs/ai/DECISIONS.md) | Quyết định về shared API, dependency, deploy hoặc demo flow. |
| [Team roster](docs/ai/TEAM.md) | Khai báo 6 người, lane chính và lane backup. |
| [Demo runbook](docs/ai/DEMO.md) | Chuẩn bị demo, fallback và checklist nộp bài. |
| [Deployment contract](docs/ai/DEPLOYMENT.md) | Chốt hosting, environments, rollback và điều kiện bật CD. |
| [Secrets & data](docs/ai/SECRETS_AND_DATA.md) | Bảo vệ khóa, dữ liệu và nguồn tài nguyên bên thứ ba. |
| [Product design context](docs/PRODUCT.md) | Adapter thiết kế tối thiểu cho UI; source of truth vẫn là Project Context. |
| [Design audit workflow](docs/design/README.md) | Chạy Impeccable CLI advisory, review report và quản lý waiver hẹp. |
| [Cẩm nang bootstrap](team_docs/TEAM_BOOTSTRAP_OVERVIEW.md) | Giới thiệu capability, cách dùng và giới hạn hiện tại cho thành viên mới. |
| [Proposal](team_docs/proposal.md) / [Kiến trúc trình bày](team_docs/kientruc.md) | Đề xuất sản phẩm, rubric và kiến trúc vendor-neutral của team. |
| [Phân công 48 giờ](team_docs/phancong.md) | Backlog sáu lane, data lifecycle, gates và ownership ngang hàng. |

## Coding agents

Codex, Claude, Cursor và Antigravity dùng cùng nguồn context và cùng quy tắc bàn giao:

- Codex: [AGENTS.md](AGENTS.md)
- Claude: [CLAUDE.md](CLAUDE.md)
- Cursor: [Cursor rule](.cursor/rules/00-team-protocol.mdc)
- Antigravity: [adapter khởi động](docs/ai/adapters/antigravity.md)
- Playbook dùng chung: [`.agents/playbooks/`](.agents/playbooks/)

## Luồng local-first

```text
Context Pack -> Task Record + resource claims -> explore -> branch/worktree riêng
                                                              -> implement -> review -> verify-demo -> handoff cục bộ
                                                                                                  |-> publish tùy chọn: Issue -> PR vào dev
dev (demo candidate) -> PR/release check -> main (stable demo, khi được publish)
```

- Mọi claim bắt đầu cục bộ; Issue, PR, push, merge và thay đổi GitHub settings không phải điều kiện để bắt đầu task.
- Không tự thực hiện hành động remote. Việc publish chỉ diễn ra khi có yêu cầu/đồng thuận rõ ràng của team.
- Khi đã publish, PR `risk:isolated` có thể self-merge sau khi hoàn tất checklist; `risk:shared` cần một peer xác nhận và Decision Log.
- Sáu giờ cuối: đóng băng scope; thay đổi mới cần hai peer xác nhận.

## Quality gate

`repository-guard` kiểm tra bootstrap artifacts, Markdown links nội bộ, file policy, AI Log history và application checks theo vùng diff. Payload `data/**` không bị content-scan trong fast path; data metadata được kiểm riêng. Luôn chạy local trước handoff:

```powershell
python scripts/ci/validate_repo.py
```

Onboard AI Log một lần cho từng clone/worktree (không tự quét home và không tự push):

```text
python scripts/ai_log/ai_log.py onboard --member member-1 --task local-YYYYMMDD-slug --tool codex --source <explicit-json-or-jsonl-source>
python scripts/ai_log/ai_log.py doctor --strict
```

Source binary/SQLite hoặc chưa có adapter dùng `--manual`, rồi nhập từng prompt bằng `record --stdin`. Onboard sinh hook ignored ở `.ai-log/hooks/`; mỗi `git commit` tự stage evidence trong namespace của member và thêm trailer, còn `git push` luôn thủ công. Xem contract, fallback đa-agent và giới hạn compliance tại [AI Log](evidence/ai-log/README.md).

Trước khi commit hoặc publish sau này, dùng scope Git-aware phù hợp:

```powershell
python scripts/ci/validate_repo.py --staged
python scripts/ci/validate_repo.py --range dev...HEAD
python scripts/ci/validate_data.py --range dev...HEAD
```

Các lệnh chỉ báo file/line; không in giá trị token/secret. `.env` hợp lệ khi bị Git ignore, nhưng sẽ bị chặn nếu được stage hoặc nằm trong phạm vi Git cần kiểm tra.

Chỉ sau khi xác minh workflow chạy xanh trên branch đích và branch protection đã áp dụng thì mới được coi `repository-guard` là required status check. `dev` có thể sinh release candidate checksum-verified; promote trên `main` là thủ công và chưa phải deploy thật. Live CD chỉ được bật sau khi [Deployment contract](docs/ai/DEPLOYMENT.md), D-010 và provider/secret/rollback contract được peer xác nhận. Không có hướng dẫn nào ở đây tự tạo Issue, PR, push hoặc thay đổi repository settings.

Xem [GitHub branch rules](.github/BRANCH_RULES.md), [labels](.github/LABELS.md), [repository settings](.github/repository-settings.json), và templates trong [`.github/`](.github/).

## UI design audit (Impeccable)

Impeccable hiện là CLI advisory portable, không phải dependency của ứng dụng, native skill/hook, MCP hay CI gate. Trước task UI shared, hoàn thiện [Product design context](docs/PRODUCT.md) và [Design system context](docs/DESIGN.md), claim scope trong Task Record rồi chạy:

```powershell
node scripts/design/impeccable-audit.mjs --task local-20260717-example-ui --target path/to/ui
node scripts/design/impeccable-audit.mjs --task local-20260717-example-ui --url http://localhost:3000 --scope type,layout
```

Report nằm tại `docs/design/reviews/<task-id>-impeccable.md`. Exit `0` và finding exit `2` đều là advisory hợp lệ; lỗi detector hoặc JSON lỗi thì cần xử lý. Xem [design audit workflow](docs/design/README.md) và [playbook](.agents/playbooks/impeccable-audit.md) để review, waiver hẹp và handoff. Chỉ cân nhắc CI sau khi team chốt frontend path, package manager và design system qua Decision mới.
