# Cẩm nang vận hành bootstrap của team

> Tài liệu nội bộ. Đề bài, ba MVP và delivery surface web-first đã được chốt; scaffold frontend/backend đã có theo D-005. Kiến trúc trust/RAG và live deploy topology vẫn `Proposed`. Mọi phần chưa có bằng chứng trong repo được ghi `TBD`, không tự suy diễn.

## Bản đồ nhanh

| Đã có | Giải quyết vấn đề gì | Cách dùng ngắn |
| --- | --- | --- |
| [Protocol đa-agent](../AGENTS.md) cho Codex, Claude, Cursor, Antigravity | Mọi người/agent ngang quyền, không sửa chồng chéo hoặc tự mở rộng scope. | Đọc rule chung, tạo Task Record; task code/config/demo hoặc `risk:shared` cần Context Pack. |
| [Task Record, Context Pack, worktree](../docs/ai/TEAM_PROTOCOL.md) | Làm rõ owner tạm thời, vùng file/API, risk, evidence và handoff; giảm conflict. | Claim một scope, làm trong branch/worktree riêng, rồi handoff khi xong. |
| [Prompt Intake Gate](../AGENTS.md#prompt-intake-gate) | Tránh agent tự suy đoán khi yêu cầu thiếu thông tin. | Trước task thực chất cần Goal, Success Criteria, Constraints, Stopping Conditions; thiếu thì dừng và hỏi gộp. |
| [Bộ context vận hành](../docs/ai/PROJECT_CONTEXT.md) | Giữ đề bài Procedure Copilot, ba MVP, kiến trúc đề xuất, team, demo, dữ liệu/secrets, quyết định và deploy có source of truth rõ ràng. | Đọc Project Context và D-007/D-006 trước task sản phẩm; giữ `TBD` nếu chưa có fact/evidence. |
| [Git & repository guard](../scripts/ci/validate_repo.py) | Chặn secret/path nhạy cảm, link Markdown hỏng, whitespace và drift của bootstrap. | Chạy `python scripts/ci/validate_repo.py` trước handoff; dùng `--staged` hoặc `--range` trước commit/PR. |
| [AI Log prompt-only](../evidence/ai-log/README.md) | Chứng minh prompt coding-agent nào gắn với commit nào mà không commit toàn bộ session. | Onboard một lần mỗi clone; `doctor --strict`; sau đó commit tự stage evidence/trailer nhưng không tự push. |
| [GitHub-ready artifacts](../.github/BRANCH_RULES.md) | Có sẵn labels, branch-rule spec, Issue/PR templates và script sync để publish sau này. | PR #1/#2 và workflow file đã có; labels/protection/required checks vẫn chưa xác minh. |
| [Impeccable CLI advisory](../docs/design/README.md) | Review UI portable, không phụ thuộc native skill/hook/MCP của một tool. | Khi có UI: claim scope, chạy wrapper, đọc report và handoff waiver/finding cần biết. |
| Web-first delivery theo D-008 | Tập trung public web app và khả năng nhúng portal, tránh phân tán sang mobile/native. | Build standalone web app + widget/iframe + headless API; kiểm browser/container/CSP/CORS và không tuyên bố tích hợp Cổng DVCQG khi chưa có sandbox. |

## 1. Context chung — biết cái gì là sự thật

| Tài liệu | Mục đích | Khi dùng / cần cập nhật |
| --- | --- | --- |
| [Project Context](../docs/ai/PROJECT_CONTEXT.md) | Chốt đề bài AI-guided public service procedures, người dùng, ba MVP, non-goals và trust states. | Đã được điền ngày 17/07/2026; cập nhật trước khi thay đổi scope sản phẩm. |
| [Architecture](../docs/ai/ARCHITECTURE.md) | Ghi component, interface, data/runtime và ownership tạm thời. | Khi thêm hoặc đổi contract, data flow hay runtime. |
| [Decision Log](../docs/ai/DECISIONS.md) | Lưu lựa chọn shared/khó đảo ngược và rollback. | Trước shared API/schema, dependency, deploy hoặc demo flow. |
| [Team & Demo](../docs/ai/TEAM.md) / [Demo runbook](../docs/ai/DEMO.md) | Phân lane linh hoạt, rehearsal, happy path và fallback. | Sau khi đề bài/MVP rõ; cập nhật sau mỗi rehearsal. |
| [Phân công 48 giờ](phancong.md) | Chia backlog sáu lane, data lifecycle, gates và cặp review/backup. | Dùng làm backlog khởi tạo; ownership thực tế vẫn phải claim trong Task Record. |
| [Secrets & Data](../docs/ai/SECRETS_AND_DATA.md) / [Deployment](../docs/ai/DEPLOYMENT.md) | Bảo vệ secret, data/license và điều kiện bật deploy thật. | Trước khi dùng provider/data/hosting; không ghi giá trị secret vào repo hoặc prompt. |

**Nguyên tắc:** `PROJECT_CONTEXT.md` là sự thật sản phẩm; `TBD` nghĩa là chưa được quyền tự chọn. Khi có thay đổi shared, ghi Decision thay vì chỉ trao đổi qua chat.

## 2. Protocol đa-agent — làm song song mà không conflict

### Mục đích

Cho sáu peer dùng Codex, Claude, Cursor và Antigravity cùng một workflow; không có merge captain hoặc agent có quyền cao hơn. Owner chỉ chịu trách nhiệm tạm thời cho một scope/task.

### Khi dùng

Dùng cho mọi task thực chất: phân tích, lập kế hoạch, review hoặc thay đổi repo. Chào hỏi, status và Q&A thông tin ngắn không kích hoạt luồng này.

### Cách dùng

1. **Prompt Intake Gate:** xác nhận Goal, Success Criteria, Constraints, Stopping Conditions. Thiếu Goal/Success/Stopping thì dừng, hỏi gộp bằng lựa chọn ngắn; policy repo là Constraints baseline.
2. **Task Record:** ghi owner, mode, base ref, Goal/Success/Constraints/Stopping, file/API/resources dự kiến chạm, risk và blocker. Trước publish dùng ID `local-YYYYMMDD-slug`.
3. **Context Pack:** bắt buộc cho task code, API, data, config, demo hoặc `risk:shared`; chỉ lấy file/line cần thiết, không dán toàn repo hay secret.
4. **Worktree:** tạo branch `feature|fix|chore|spike/<task>-<slug>` từ `dev` (hoặc base đã thống nhất), làm trong worktree/clone riêng. Không copy `.env` hoặc config ignored của peer.
5. **Handoff:** ghi files/API/resources đã chạm, checks, risk/rollback, claims đã release và việc tiếp theo.

```text
Prompt đủ 4 phần
  -> Task Record + resource claim
  -> explore -> Context Pack (nếu cần)
  -> worktree riêng -> implement -> review -> verify-demo
  -> handoff local -> Issue/PR/dev chỉ khi team cho phép publish
```

### Bốn mode

| Mode | Làm gì | Không làm gì |
| --- | --- | --- |
| `explore` | Đọc repo, xác minh fact, hoàn thiện record/context. | Sửa source/config/resource. |
| `implement` | Sửa đúng scope đã claim, cập nhật evidence. | Mở rộng scope âm thầm hoặc nhiều writer. |
| `review` | So diff với pack, contract, risk và test evidence. | Sửa hộ implementer khi chưa có record/ownership mới. |
| `verify-demo` | Chạy check, rehearsal/fallback và hoàn thiện handoff. | Thêm feature/dependency ngoài scope. |

`risk:isolated` chỉ dùng cho thay đổi thật sự cô lập. Shared API/schema, dependency, deploy, demo flow hay resource chung là `risk:shared`: cần Decision Log và peer confirmation; sáu giờ cuối cần hai peers và scope freeze.

## 3. Quality, Git và bảo mật

### Repository guard

**Mục đích:** kiểm tra bootstrap artifacts, UTF-8, whitespace, Markdown links, path/secret policy, Impeccable policy và contract workflow. Guard chỉ in path/line, không in secret value.

| Khi chạy | Lệnh | Phạm vi |
| --- | --- | --- |
| Trước handoff | `python scripts/ci/validate_repo.py` | File tracked + untracked không bị Git ignore. |
| Trước commit | `python scripts/ci/validate_repo.py --staged` | Nội dung trong index. |
| Trước PR/publish | `python scripts/ci/validate_repo.py --range dev...HEAD` | Post-image của Git range. |

Theo D-010 `Proposed`, workflow `repository-guard` được thiết kế lại thành fast merge gate: luôn kiểm policy/AI Log, còn frontend, backend, design và data metadata chỉ chạy khi diff liên quan. `data/**` không bị content-scan; `dev` chỉ tạo artifact có manifest checksum và `main` chỉ promote thủ công candidate hợp lệ. Trạng thái run/required check vẫn phải được xác minh trên GitHub; candidate không phải live deploy.

### Secret và local config

- `.env`, `.env.*`, model artifact lớn, raw experiment output và local cache bị ignore; chỉ template [.env.example](../.env.example) được phép track.
- Không đưa token, raw data nhạy cảm, private key hoặc credential vào Git, Task Record, Issue/PR, prompt, log hay screenshot.
- Dựng worktree local từ `.env.example` và secure channel; không chép `.env`/ignored config giữa peer.

## 4. AI Log — prompt coding-agent theo commit

### Đã tích hợp gì và giải quyết vấn đề gì

- CLI Python standard-library hỗ trợ ngang hàng Codex, Claude, Cursor và Antigravity.
- `PromptEvent` chỉ chứa `UserPrompt` đã sanitize; `CommitEvidence` nối danh sách prompt mới với Task Record, branch và commit trailer.
- Template hook được review trong `.githooks/`; onboarding sinh bản executable machine-local ở ignored `.ai-log/hooks/`.
- Evidence mỗi người nằm ở `evidence/ai-log/members/<member-id>/`, nên hai member không ghi cùng namespace.
- Guard chặn schema hỏng, forbidden session content, secret/PII và trailer không có record. Commit legacy không có policy được bỏ qua; merge commit do nền tảng tạo được miễn trailer.

AI Log giải quyết yêu cầu trace prompt theo commit mà không đưa toàn bộ desktop session, assistant output, system prompt, tool output, screenshot hoặc absolute source path vào Git.

### Khi nào và cách dùng

Mỗi clone/worktree onboard một lần; chạy lại sau pull nếu CLI/hook thay đổi:

```text
python scripts/ai_log/ai_log.py onboard --member member-1 --task local-YYYYMMDD-slug --tool cursor --source <explicit-json-or-jsonl-source>
python scripts/ai_log/ai_log.py doctor --strict
```

Với source binary/SQLite hoặc format chưa nhận diện:

```text
python scripts/ai_log/ai_log.py onboard --member member-1 --task local-YYYYMMDD-slug --tool antigravity --manual
python scripts/ai_log/ai_log.py record --tool antigravity --stdin
```

Sau đó `git commit` tự thu delta prompt, stage evidence và thêm `AI-Log`/`AI-Tools`/`AI-Capture`. Hook **không tự push**. `git push` vẫn cần người thực hiện chủ động và đúng quyền publish.

### Giới hạn

AI Log prompt-only chưa đáp ứng nguyên văn yêu cầu nộp raw desktop session và screenshot nếu ban tổ chức bắt buộc. Team cần xin xác nhận chấp thuận AI Log hoặc tạo gói ngoài Git đã rà secret/PII; không mở rộng log ngầm.

## 5. GitHub-ready — trạng thái đã biết và chưa xác minh

### Đã tích hợp local

- [repository-settings.json](../.github/repository-settings.json) là policy machine-readable cho 18 labels và branch protection dự kiến.
- [BRANCH_RULES.md](../.github/BRANCH_RULES.md), [LABELS.md](../.github/LABELS.md), Issue templates và PR template thống nhất cách publish sau này.
- [sync-repo-settings.ps1](../scripts/github/sync-repo-settings.ps1) mặc định chỉ in local plan, không gọi `gh` hoặc GitHub API.

### Khi nào dùng

Chỉ khi team đồng thuận publish và người chạy có Admin. Khi đó mới tạo labels/protection, Issue/PR, commit/push hoặc thêm required status check.

### Cách dùng sau khi được phép

```powershell
# Chỉ đọc local policy, không gọi GitHub
.\scripts\github\sync-repo-settings.ps1

# Preview sync đã được ủy quyền; không áp dụng thay đổi
.\scripts\github\sync-repo-settings.ps1 -Apply -WhatIf
```

`-Apply` thật yêu cầu `gh` đã đăng nhập bằng tài khoản có Admin. Chỉ dùng `-RequireRepositoryGuard` sau khi workflow đã xuất hiện trên target branch và xanh ít nhất một lần.

### Giới hạn hiện tại

Bootstrap cơ sở đã được merge qua PR #1/#2 và workflow file hiện có trên `main`. Do GitHub connector trả 404 cho workflow và token `gh` hiện không hợp lệ, team **chưa xác minh** workflow run status, labels, branch protection hoặc required checks. Không suy từ file cấu hình rằng các remote settings này đã hoạt động.

## 6. Impeccable — audit UI CLI dùng chung

### Đã tích hợp gì

| Thành phần | Vai trò |
| --- | --- |
| [Wrapper](../scripts/design/impeccable-audit.mjs) | Chạy `npx --yes impeccable@3.2.1 detect --json` mà không thêm dependency vào project, không dùng shell/native hook/MCP. |
| [Design context](../docs/PRODUCT.md) và [DESIGN.md](../docs/DESIGN.md) | Adapter để mô tả product/design cho review UI; Project Context vẫn là source of truth sản phẩm. |
| [.impeccable/config.json](../.impeccable/config.json) | Shared detector config: ignore arrays rỗng; `designSystem.enabled: false` khi tokens/components còn `TBD`. |
| [Playbook](../.agents/playbooks/impeccable-audit.md) và tests | Chuẩn hóa review/handoff cho mọi agent; kiểm tra wrapper không coi finding là lỗi blocking. |

### Giải quyết vấn đề gì

Cho team feedback UI có report review được mà không buộc tất cả dùng cùng vendor hook/skill. Nó phát hiện anti-pattern UI; không tự sửa UI, không thay review accessibility/manual demo và không tạo design system thay team.

### Khi nào dùng

Ở mode `review` hoặc `verify-demo`, sau khi task UI đã claim đúng thư mục/URL, có Task Record/Context Pack, đã đọc `PRODUCT.md` và `DESIGN.md`. Nếu shared tokens/components/layout còn chưa chốt, quay lại `explore` thay vì dùng audit để tự quyết design.

### Cách dùng

Chọn đúng **một** source:

```powershell
# Audit thư mục/file UI nằm trong repo
node scripts/design/impeccable-audit.mjs --task local-20260717-ui-review --target path/to/ui

# Audit local dev server đã chạy
node scripts/design/impeccable-audit.mjs --task local-20260717-ui-review --url http://localhost:3000 --scope type,layout
```

- `--task` chỉ nhận ID an toàn; `--target` phải nằm trong repo. `--url` chỉ nhận local `http(s)` (`localhost`, `127.0.0.1`, `::1`), không credential/query/fragment.
- `--scope` chỉ là nhãn phân loại trong report; detector không có scope flag nên nó **không** giới hạn scan.
- Detector exit `0` (không finding) và `2` (có finding) đều thành công ở advisory mode. Lỗi execution/JSON làm wrapper fail.
- Report reviewable: `docs/design/reviews/<task-id>-impeccable.md`. Raw JSON: `.impeccable/audits/<task-id>-impeccable.json` (ignored).

### Waiver và giới hạn

- Sửa finding trước. Waiver shared phải hẹp, có lý do, peer confirmation và tạo qua `impeccable ignores`; lưu trong tracked `.impeccable/config.json`.
- Waiver thử nghiệm/cá nhân dùng ignored `.impeccable/config.local.json`, không copy/commit sang peer.
- Không dùng `/impeccable init`, `/impeccable craft`, `/impeccable live`, `npx impeccable install`, browser extension, native hook/skill hoặc MCP trong bootstrap này.
- Chưa thêm Impeccable detector vào CI; chỉ cân nhắc sau khi chốt frontend path, package manager, tokens/components và Decision mới.

## 7. Đề bài, deploy, demo và phần chưa có

Định vị hiện tại là **AI Procedure Copilot** cho ba MVP: đăng ký khai sinh, đăng ký thường trú và đăng ký thành lập hộ kinh doanh. Delivery surface theo D-008 là standalone web app + widget/iframe + headless API; mobile/native/PWA install nằm ngoài MVP. Xem [proposal nội bộ](proposal.md), [Project Context](../docs/ai/PROJECT_CONTEXT.md), D-008/D-007 và D-006 trong [Decision Log](../docs/ai/DECISIONS.md).

| Hạng mục | Trạng thái hiện tại | Điều kiện để bắt đầu |
| --- | --- | --- |
| Đề bài và ba MVP hiện hành | Đã chốt trong D-007 | Đổi scope cần Task Record/Decision mới. |
| Web-first delivery | D-008 đã chốt; frontend là scaffold, backend có API foundation sáu endpoint | Cần product flow, static-host widget embed và API evidence; portal thật cần sandbox/authorization. |
| Stack/API/deploy topology | D-005 `Accepted` cho scaffold/API foundation; D-006 `Proposed` cho RAG/trust/widget/deploy | Dev fixture backend luôn fail-closed; peer review capability theo Task Record; provider/model vẫn `TBD`. |
| Application CI/CD | D-010 `Proposed`: application checks theo changed scope và provider-neutral release artifact | Peer review D-010, xác minh workflow xanh; không coi artifact là deploy. |
| Hosting, secrets, deploy/CD | Chưa provision | Accept D-006/follow-up, chọn provider, có environment, smoke check, rollback và demo fallback. |
| Demo runbook | Đã có narrative/evidence draft; chưa rehearsal | Có public app, synthetic demo data và fallback đã kiểm chứng. |
| GitHub remote governance | PR #1/#2 và workflow file đã có; run/labels/protection/required checks chưa xác minh | Có quyền Admin/token hợp lệ và evidence remote trước khi tuyên bố enforcement. |

Không dùng bootstrap như bằng chứng rằng ứng dụng, deploy, data/model hoặc remote settings đã tồn tại. Khi chốt một hạng mục, cập nhật source of truth thay vì viết ghi chú cục bộ mâu thuẫn.

## Bắt đầu trong 5 bước

1. Đọc [AGENTS.md](../AGENTS.md), [Team Protocol](../docs/ai/TEAM_PROTOCOL.md) và context đúng với task.
2. Xác nhận prompt có đủ Goal, Success Criteria, Constraints và Stopping Conditions.
3. Tạo/claim Task Record; task lớn/shared tạo Context Pack từ [template](../.agents/context-packs/TEMPLATE.md).
4. Tạo branch/worktree riêng, onboard AI Log cho clone, chỉ sửa scope đã claim, rồi chạy kiểm tra phù hợp.
5. Commit/handoff evidence, risk và việc tiếp theo; hook không tự push, chỉ publish Issue/PR hoặc thay đổi GitHub khi team cho phép rõ ràng.

## Các tài liệu cần biết

- [Project Context](../docs/ai/PROJECT_CONTEXT.md): đề bài, người dùng, MVP, non-goals và lệnh chạy.
- [Architecture](../docs/ai/ARCHITECTURE.md): component, contract, data/runtime và thay đổi liên lane.
- [Decision Log](../docs/ai/DECISIONS.md): các quyết định shared, khó đảo ngược hoặc có trade-off.
- [Team](../docs/ai/TEAM.md) và [Demo](../docs/ai/DEMO.md): lanes linh hoạt, pitch, happy path/fallback.
- [Phân công 48 giờ](phancong.md): sáu lane, vòng đời data, gates và reviewer/backup.
- [Secrets & Data](../docs/ai/SECRETS_AND_DATA.md) và [Deployment](../docs/ai/DEPLOYMENT.md): giữ secret ngoài Git; chỉ bật CD sau khi stack/hosting được chốt.

## Chưa có chủ đích

- Đề bài và ba MVP đã chốt; model/provider và chi tiết procedure-pack đã review vẫn `TBD`.
- Next.js vẫn là scaffold; FastAPI có API foundation sáu endpoint, typed trust/error metadata, rule engine và dev fixture fail-closed theo D-005. RAG/vector store, model/provider, widget hoàn chỉnh và hosting/deploy vẫn là proposal D-006, chưa provision.
- Live CI/CD hosting, environment, secret thật và deploy thật chưa được tạo. D-010 chỉ thêm fast checks và artifact/promotion provider-neutral.
- GitHub workflow file đã có trên `main`; run status, labels, branch protection và required checks chưa được xác minh.

Khi các phần trên được chốt, cập nhật source of truth tương ứng thay vì đoán hoặc sửa policy cục bộ. Xem [README](../README.md) để có dashboard và lối vào đầy đủ của repo.
