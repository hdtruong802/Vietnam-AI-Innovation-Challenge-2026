# Vietnam AI Innovation Challenge 2026

> Không gian làm việc chung cho team 5 người xây dựng sản phẩm AI-native tại hackathon.

## Trạng thái

- Nhánh tích hợp: `dev`
- Bản demo/release ổn định: `main`
- Đề bài, MVP và stack: sẽ được chốt trong 90 phút đầu sau khi nhận đề
- Nơi theo dõi công việc: Task Record cục bộ; GitHub Issue chỉ được tạo sau khi team chọn publish

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
| [Team roster](docs/ai/TEAM.md) | Khai báo 5 người, lane chính và lane backup. |
| [Demo runbook](docs/ai/DEMO.md) | Chuẩn bị demo, fallback và checklist nộp bài. |
| [Deployment contract](docs/ai/DEPLOYMENT.md) | Chốt hosting, environments, rollback và điều kiện bật CD. |
| [Secrets & data](docs/ai/SECRETS_AND_DATA.md) | Bảo vệ khóa, dữ liệu và nguồn tài nguyên bên thứ ba. |
| [Product design context](docs/PRODUCT.md) | Adapter thiết kế tối thiểu cho UI; source of truth vẫn là Project Context. |
| [Design audit workflow](docs/design/README.md) | Chạy Impeccable CLI advisory, review report và quản lý waiver hẹp. |

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

`repository-guard` là CI guard hiện tại: nó kiểm tra bootstrap artifacts, Markdown links nội bộ, file policy và contract CI bằng Python standard library. Trước khi workflow được publish, chạy local:

```powershell
python scripts/ci/validate_repo.py
```

Trước khi commit hoặc publish sau này, dùng scope Git-aware phù hợp:

```powershell
python scripts/ci/validate_repo.py --staged
python scripts/ci/validate_repo.py --range dev...HEAD
```

Các lệnh chỉ báo file/line; không in giá trị token/secret. `.env` hợp lệ khi bị Git ignore, nhưng sẽ bị chặn nếu được stage hoặc nằm trong phạm vi Git cần kiểm tra.

Khi workflow đã có trên GitHub và chạy xanh trên branch đích, `repository-guard` trở thành required status check. Issue scaffold đầu tiên vẫn phải bổ sung lint/test/build CI riêng cho stack thực tế; CD chỉ được bật sau khi [Deployment contract](docs/ai/DEPLOYMENT.md) hoàn tất. Không có hướng dẫn nào ở đây tự tạo workflow, Issue, PR, push hoặc thay đổi repository settings.

Xem [GitHub branch rules](.github/BRANCH_RULES.md), [labels](.github/LABELS.md), [repository settings](.github/repository-settings.json), và templates trong [`.github/`](.github/).

## UI design audit (Impeccable)

Impeccable hiện là CLI advisory portable, không phải dependency của ứng dụng, native skill/hook, MCP hay CI gate. Trước task UI shared, hoàn thiện [Product design context](docs/PRODUCT.md) và [Design system context](docs/DESIGN.md), claim scope trong Task Record rồi chạy:

```powershell
node scripts/design/impeccable-audit.mjs --task local-20260717-example-ui --target path/to/ui
node scripts/design/impeccable-audit.mjs --task local-20260717-example-ui --url http://localhost:3000 --scope type,layout
```

Report nằm tại `docs/design/reviews/<task-id>-impeccable.md`. Exit `0` và finding exit `2` đều là advisory hợp lệ; lỗi detector hoặc JSON lỗi thì cần xử lý. Xem [design audit workflow](docs/design/README.md) và [playbook](.agents/playbooks/impeccable-audit.md) để review, waiver hẹp và handoff. Chỉ cân nhắc CI sau khi team chốt frontend path, package manager và design system qua Decision mới.
