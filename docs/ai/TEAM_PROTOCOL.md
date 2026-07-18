# Giao thức làm việc đa-agent — local-first

Tài liệu này là nguồn sự thật cho cách team sáu người phối hợp cùng Codex, Claude, Cursor và Antigravity trong hackathon 48 giờ. Mọi người và mọi agent là **ngang hàng**: không có merge captain, agent chính, hay quyền quyết định mặc định theo công cụ.

Protocol này bắt đầu ở local. GitHub Issue, PR, push, merge và repository settings chỉ là bước publish tùy chọn sau khi team có yêu cầu/đồng thuận rõ ràng; tài liệu này không tự cấp quyền thực hiện hành động remote.

Luồng chuẩn: [Context Pack](#context-pack-trước-khi-làm-việc) → [Mode](#modes) → [Task Record và resource claim](#task-record-và-resource-claim) → [worktree Git cục bộ](#worktree-và-git-cục-bộ) → handoff hoặc publish tùy chọn.

Trước luồng này, áp dụng [Prompt Intake Gate](../../AGENTS.md#prompt-intake-gate). Gate quyết định có được bắt đầu task thực chất hay không; Task Record chỉ lưu bốn thành phần đã được chốt, không thay thế bước intake.

## Context pack trước khi làm việc

Trước khi lập kế hoạch, review hoặc sửa mã, chọn context pack nhỏ nhất đủ cho task:

| Tài liệu | Dùng khi |
| --- | --- |
| [AGENTS.md](../../AGENTS.md) | Quy tắc dùng chung và thứ tự ưu tiên hướng dẫn. |
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | Task ảnh hưởng bài toán, MVP, scope hoặc lệnh chạy. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Task chạm component, interface, data flow hoặc runtime. |
| [DECISIONS.md](DECISIONS.md) | Task chạm shared API/schema, dependency, deploy hoặc demo flow. |
| [TEAM.md](TEAM.md) | Cần biết lane/backup hiện tại; lane không phải cấp bậc. |
| [DEMO.md](DEMO.md) | Task ảnh hưởng happy path, fallback hoặc diễn tập. |
| [SECRETS_AND_DATA.md](SECRETS_AND_DATA.md) | Task dùng credentials, data, model/provider hoặc asset bên thứ ba. |

Không coi giá trị `TBD` là quyền tự chọn một giải pháp lớn. Ghi rõ giả định, dữ liệu/quyền truy cập thiếu và câu hỏi blocker trong Task Record.

## Modes

Mỗi Task Record có đúng một mode hiện tại. Đổi mode khi mục tiêu thay đổi và cập nhật claim trước khi sửa mã.

| Mode | Mục đích | Giới hạn mặc định |
| --- | --- | --- |
| `explore` | Đọc repo/context, xác minh fact, chọn context và hoàn thiện Task Record/Context Pack. | Không sửa mã, cấu hình hoặc resource. |
| `implement` | Thực hiện một scope đã claim trong branch/worktree riêng. | Chỉ chạm resource đã claim. |
| `review` | Kiểm tra diff, contract, test evidence và rủi ro. | Không mở rộng scope hoặc sửa thay tác giả khi chưa bàn giao. |
| `verify-demo` | Chạy check, diễn tập happy path/fallback và hoàn thiện handoff. | Không thêm feature hoặc dependency mới ngoài scope/risk policy. |

Mode là hành vi, không phải chức danh hay quyền riêng của người/agent nào. Sub-agent chỉ chạy song song ở `explore` hoặc `review`; mỗi Task Record chỉ có một implementer được ghi source trong scope/worktree tại một thời điểm.

## Task Record và resource claim

Task Record thay thế yêu cầu phải có GitHub Issue trước khi bắt đầu. Với task có code, API, data, config, demo hoặc `risk:shared`, nó nằm trong Context Pack; task docs nhỏ có thể dùng working note cục bộ nếu peer kiểm tra được trước khi có thay đổi. Khi publish, sao chép nguyên record vào Issue/PR template thay vì viết lại từ trí nhớ.

```md
# local-YYYYMMDD-<slug>

- Mode: `explore` | `implement` | `review` | `verify-demo`
- Status: `ready` | `active` | `blocked` | `handoff` | `done`
- Owner tạm thời: <person/agent>
- Branch/worktree: `<local branch or path>`
- Context pack đã đọc: <paths / Decision IDs>
- AI Log member / tool binding / readiness: `chưa bật` | `<member-id> / <tool + binding-id|manual> / doctor pass|warning>`

## Mục tiêu, success criteria, constraints và stopping conditions
- Goal:
- Success Criteria:
- Constraints: policy repo là baseline; ghi ràng buộc riêng nếu có.
- Stopping Conditions:

## Resource claims
- Files/areas:
- API/schema/contracts:
- Runtime/data/ports/accounts/assets:

## Dependency, risk và Decision
- Depends on / blocker:
- Risk: `isolated` | `shared`
- Decision Log: `D-XXX` | `Không có`

## Kiểm chứng, rollback và handoff
- Check/manual evidence:
- AI-Log ID + capture status: `chưa có` | `<log-id> / complete|warning|no_new_prompt|manual|git_operation`
- Rollback/fallback:
- Việc tiếp theo / người có thể tiếp nhận:

## Publish (tùy chọn)
- GitHub Issue: `chưa publish` | `#<number>`
- PR: `chưa publish` | `#<number>`
```

- Owner của Task Record chỉ chịu trách nhiệm tạm thời cho scope, cập nhật trạng thái và handoff; owner không có quyền cao hơn peer.
- Một resource claim đang `active` chỉ có một owner. Claim bao gồm file/area, contract, migration, port/runtime, data asset, provider account hoặc demo resource có thể gây chồng lấn; phải ghi owner, thời hạn và điều kiện release trong Context Pack/Task Record.
- Trước khi chạm resource đã claim, tách scope hoặc thống nhất một ranh giới mới với owner hiện tại. Không ghi đè thay đổi chỉ để build qua.
- Claim hết hiệu lực khi record là `handoff`, `blocked` hoặc `done`; người tiếp nhận phải tạo/cập nhật Task Record của mình trước khi tiếp tục.
- `risk:shared` gồm thay đổi shared API/schema, dependency, deploy, demo flow hoặc resource dùng chung. Phải có Decision Log và một peer xác nhận trước khi implement; trong sáu giờ cuối cần hai peers.

## Worktree và Git cục bộ

- `main` dành cho demo/release ổn định; `dev` là điểm tích hợp khi team chọn tích hợp/publish.
- Tạo branch cục bộ từ `dev` (hoặc base ref được peer thống nhất trong bootstrap) theo mẫu:

```text
feature/<task>-<slug>
fix/<task>-<slug>
chore/<task>-<slug>
spike/<task>-<slug>
```

- Dùng worktree hoặc clone riêng cho mỗi task/agent. Không để hai người/agent sửa cùng working tree có thay đổi chưa commit.
- Trước khi implement, kiểm tra `git status --short --branch`, Task Record và resource claims. Commit nhỏ, có mục đích rõ ràng, ưu tiên Conventional Commits.
- Không copy `.env`, token, ignored data hoặc file local của peer sang worktree. Nếu cần local setup, tạo lại từ `.env.example` hoặc dùng kênh bảo mật đã được team chấp thuận.
- Không push, force-push, tạo Issue/PR, merge, thay đổi GitHub settings hoặc cấu hình server/service chỉ vì protocol đề cập đến chúng. Đây là các hành động tách biệt cần quyền hiện tại rõ ràng.

## Shared contract, MCP và thay đổi xuyên lane

- Trước khi thay shared API, schema, dependency, deploy hoặc demo flow, tạo entry trong `DECISIONS.md`, nêu consumer bị ảnh hưởng, compatibility, kiểm chứng và rollback.
- D-002 hoãn mọi MCP runtime/RepoPrompt CE khỏi bootstrap. Không thêm MCP config, package hoặc server như dependency chung. Chỉ xem xét lại theo read-only allowlist và các gate của D-002.
- Lanes `product/demo`, `ui`, `application/api`, `ai-data/evaluation`, `quality/release` chỉ là vùng công việc có thể luân phiên. Không lane hoặc agent nào có quyền tự quyết cross-lane.

## Quality gate cục bộ

- Trước handoff, chạy `python scripts/ci/validate_repo.py` cùng các check trong Context Pack.
- Với task UI đã có `docs/PRODUCT.md`, `docs/DESIGN.md` và scope/URL được claim, dùng [playbook Impeccable advisory](../../.agents/playbooks/impeccable-audit.md) ở mode `review` hoặc `verify-demo`. Đây là report local dùng chung, không phải native skill/hook, MCP hay CI gate.
- Khi đã stage thay đổi, chạy `python scripts/ci/validate_repo.py --staged`; trước PR/publish sau này, chạy `python scripts/ci/validate_repo.py --range dev...HEAD` nếu `dev` là base đã chọn.
- Guard chỉ quét tracked và untracked không bị Git ignore trong mode mặc định. `.env` cục bộ bị ignore không làm fail, nhưng secret file/token sẽ fail nếu được stage hoặc xuất hiện trong Git range.
- Guard chỉ in path/line an toàn, không in giá trị secret. Theo D-010, app lint/test/build có thể chạy theo changed scope; payload `data/**` không bị content-scan trong fast path và được metadata guard riêng. Release candidate không phải deploy; live CD vẫn cần Decision/provider/secret/rollback evidence.

### AI Log prompt-only

- D-009 quy định một contract chung cho Codex, Claude, Cursor và Antigravity. Chỉ `UserPrompt` từ source local được thành viên bind rõ và có workspace khớp repo mới được đưa vào evidence.
- `.ai-log/` chứa path source, checkpoint, exclusion và index sinh ra; thư mục này luôn bị ignore. Git chỉ nhận prompt đã sanitize và commit evidence dưới `evidence/ai-log/`.
- Mỗi clone/worktree chạy một lần `onboard --member ... --task ... --tool ... --source ...` hoặc `--manual`, rồi xác nhận bằng `doctor --strict`. Lệnh idempotent sinh executable hook vào ignored `.ai-log/hooks/` từ template tracked `.githooks/` và đặt local `core.hooksPath`; chạy lại sau pull nếu template/CLI đổi.
- Hook dùng chung tự stage evidence và thêm trailer vào `git commit`, không phải native hook/skill của vendor và không tự push. Mỗi member chỉ ghi namespace của mình; `git push` luôn là bước thủ công có ủy quyền riêng.
- Capture lỗi tạo `warning` nhưng không chặn commit. Secret/PII vẫn không được vào Git: nội dung phải bị redact/omit, không chỉ cảnh báo.
- History guard bỏ qua commit legacy không có policy; từ commit đầu tiên chứa policy, non-merge commit phải có trailer/evidence. Merge commit do nền tảng tạo được miễn trailer.
- AI Log không thay file session desktop hoặc screenshot nếu ban tổ chức bắt buộc chúng; mọi mở rộng evidence cần Decision mới.

## Publish sau khi local task đã rõ

Khi team quyết định publish một task, theo thứ tự:

1. Đảm bảo Task Record có context pack, claims, acceptance criteria, risk, evidence và handoff đầy đủ.
2. Tạo GitHub Issue từ template phù hợp, dán Task Record và dùng labels phản ánh status/area/risk/priority.
3. Mở PR từ branch task về `dev`; liên kết Issue nếu có và dán evidence/rollback từ record.
4. PR `risk:isolated` có thể được tác giả merge khi checklist đủ; PR `risk:shared` cần xác nhận rõ của một peer và Decision Log. Bất kỳ peer nào đủ điều kiện đều có thể merge.

Không có Issue vẫn có thể hoàn tất `explore`, local `implement`, `review`, `verify-demo` và handoff. Issue/PR là bản công bố của record, không phải nguồn ownership duy nhất.

## Conflict, Definition of Done và handoff

Khi claim chồng lấn:

1. Dừng trước khi sửa resource của peer.
2. So sánh Task Records, tách file/API/resource hoặc tạo Decision cho interface chung.
3. Nếu không tách được, một owner bàn giao/release claim trước khi owner còn lại tiếp tục.
4. Nếu ảnh hưởng demo, ghi blocker và fallback nhỏ nhất trong record.

Một Task Record hoàn tất khi:

- Acceptance criteria được xác nhận và thay đổi nằm trong claim.
- Check tự động hoặc manual evidence phù hợp đã được ghi.
- Contract, context, demo runbook hoặc Decision Log được cập nhật khi bị ảnh hưởng.
- Không có secret, token, dữ liệu nhạy cảm, file model lớn hoặc artifact không cần thiết.
- Record có rollback/fallback và handoff rõ; nếu đã publish, Issue/PR phản ánh cùng nội dung.

## Nhịp 48 giờ

- **90 phút đầu:** hoàn thiện `PROJECT_CONTEXT.md`, MVP, non-goals, kiến trúc tối thiểu, các Task Record P0 và shared contract cần thiết.
- **Trong khi build:** sync ngắn khoảng mỗi 2 giờ bằng Task Record/handoff; ưu tiên nêu blocker và release claim sớm.
- **6 giờ cuối:** scope freeze. Chỉ nhận thay đổi trực tiếp phục vụ demo, độ tin cậy, seed/demo data, fallback hoặc lỗi P0. Mọi thay đổi mới cần hai peer xác nhận, evidence kiểm thử và rollback; không thêm API, dependency hoặc tính năng mới nếu chưa có Decision Log.

Bootstrap hoạt động khi một thành viên mới có thể dùng bất kỳ trong bốn agent, chọn đúng context pack, tạo Task Record và resource claim, làm trong worktree riêng, bàn giao evidence mà không tạo conflict. Việc publish Issue/PR chỉ là kiểm chứng bổ sung khi team chọn dùng GitHub.
