# Decision Log

Decision Log lưu các quyết định liên lane hoặc khó đảo ngược: shared API/schema, dependency, model/provider, data policy, deploy, demo flow, resource dùng chung và ngoại lệ scope freeze. Nó không phải công cụ phân cấp; bất kỳ peer nào cũng có thể đề xuất quyết định.

## Quy trình local-first

1. Tạo entry `Proposed` từ Task Record trước khi thay shared contract hoặc dependency.
2. Liên kết Task Record, nêu lựa chọn, trade-off, rollback và peer xác nhận.
3. Peer xác nhận thì đổi thành `Accepted`; khi bị thay thế, giữ lịch sử và đánh dấu `Superseded by D-xxx`.
4. Chỉ sau khi team chọn publish, thêm GitHub Issue/PR vào entry. Không tạo Issue/PR chỉ để có Decision Log.
5. Trong sáu giờ cuối, entry cho thay đổi mới cần hai peer xác nhận theo `TEAM_PROTOCOL.md`.

## Chỉ mục

| ID | Trạng thái | Quyết định | Task Record / publish | Ngày |
| --- | --- | --- | --- | --- |
| D-001 | Accepted | Giao thức peer-equal và Task Record local-first | Bootstrap | 2026-07-16 |
| D-002 | Accepted | Hoãn MCP runtime; chỉ xem xét lại bằng read-only allowlist | Bootstrap | 2026-07-16 |
| D-003 | Accepted | Impeccable CLI advisory portable, không native skill/hook | `local-20260717-impeccable-cli` | 2026-07-17 |
| D-004 | Accepted | Prompt Intake Gate dùng chung trước task thực chất | `local-20260717-prompt-intake-gate` | 2026-07-17 |
| D-005 | Accepted | Scaffold khung dự án FastAPI (Backend) và Next.js (Frontend) | `local-20260717-scaffold-vaic` | 2026-07-17 |
| D-009 | Accepted | Structure-aware chunking contract cho ba procedure pack MVP | `local-20260718-chunking-phase-0`, `local-20260718-chunking-phase-1` | 2026-07-18 |


---

## D-001 — Giao thức peer-equal và Task Record local-first

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-16
- **Người đề xuất:** Team bootstrap
- **Phạm vi:** Collaboration process
- **Liên kết:** `TEAM_PROTOCOL.md`

### Bối cảnh

Team năm người dùng Codex, Claude, Cursor và Antigravity trong cùng repo, cần tránh conflict nhưng không tạo agent hoặc thành viên có quyền cao hơn. Không phải task nào cũng cần được publish ngay lên GitHub.

### Quyết định

Mọi người/agent bắt đầu bằng Context Pack và Task Record cục bộ, rồi claim resource trong branch/worktree riêng từ `dev`. Owner chỉ tạm thời cho một record. GitHub Issue và PR chỉ được tạo khi team chọn publish; khi đó chúng sao chép record thay vì thay thế nó. PR `risk:shared` cần một peer xác nhận; trong sáu giờ cuối, mọi thay đổi mới cần hai peers xác nhận. `main` giữ cho demo/release ổn định.

### Hệ quả

- Team có thể explore, implement, review, verify/demo và handoff nhanh mà không phụ thuộc vào remote state.
- Resource claims và context được làm rõ trước khi hai agent chạm cùng file/API/runtime.
- Publish vẫn có traceability khi cần, nhưng không cấp quyền tự động cho push, Issue, PR, merge hoặc repository settings.

### Rollback

Nếu Task Record không đủ cho việc phối hợp, tạo Decision mới bổ sung một local artifact tối thiểu. Không quay lại bắt buộc Issue cho mọi task mà chưa đánh giá chi phí/ích lợi.

---

## D-002 — Hoãn MCP runtime; chỉ xem xét lại bằng read-only allowlist

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-16
- **Người đề xuất:** Team bootstrap
- **Phạm vi:** Tooling / MCP
- **Liên kết:** `TEAM_PROTOCOL.md`

### Bối cảnh

RepoPrompt CE cho thấy một MCP surface mạnh cho context, edit, worktree và orchestration, nhưng nó là native macOS app với local CLI/socket lifecycle. Bootstrap cần portable cho Codex, Claude, Cursor và Antigravity trong 48 giờ, không thêm runtime, platform hoặc quyền mới.

### Quyết định

Không thêm, không yêu cầu cài đặt và không commit cấu hình cho RepoPrompt CE hay bất kỳ MCP runtime nào trong bootstrap. Context Pack, Task Record, worktree và Git cục bộ là cơ chế chung hiện tại.

Chỉ có thể xem xét lại khi **tất cả** điều kiện sau đúng và một Decision mới được peer chấp thuận:

1. Team ghi nhận ít nhất hai bottleneck context lặp lại mà Context Pack và tool sẵn có không đáp ứng, đồng thời stack ứng dụng đã được chốt.
2. MCP là `stdio`, cross-platform và opt-in theo từng người; không có endpoint/server dùng chung, không có secret trong config/prompt, và config cá nhân không được commit.
3. Bề mặt ban đầu chỉ cho phép đọc bốn resource: `get_project_context`, `get_task_context`, `get_decisions` và `get_demo_status`.
4. Không cho phép shell/process execution, ghi/xóa file, Git/GitHub mutation, secret/config access, worktree management, agent spawning/delegation hoặc bất kỳ tool edit/orchestration nào.
5. Hai peer xác nhận ít nhất hai agent client cần dùng được surface đó và nó không sửa repo, remote state, worktree, dependency hay demo flow.
6. Có local smoke evidence, giới hạn resource rõ ràng và cách gỡ bỏ không làm hỏng workflow đang chạy.

### Hệ quả

- Không biến hệ thống context thành một dependency/platform risk trong thời gian hackathon.
- Team vẫn có thể đánh giá MCP sau MVP bằng capability allowlist hẹp, thay vì nhập toàn bộ server/orchestrator.

### Rollback

Nếu một thử nghiệm MCP opt-in không đáp ứng gate, gỡ cấu hình local của người thử nghiệm và tiếp tục chỉ dùng Context Pack/Task Record. Không cần thay đổi remote hoặc lịch sử Git.

---

## D-003 — Impeccable CLI advisory portable, không native skill/hook

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Người đề xuất:** Team bootstrap theo yêu cầu hiện tại
- **Phạm vi:** Tooling / design review
- **Task Record:** `local-20260717-impeccable-cli`
- **Publish (tùy chọn):** chưa publish
- **Peer xác nhận:** Quy ước peer-equal vẫn áp dụng cho từng task UI, shared waiver và thay đổi CI; không có quyền vendor riêng.

### Bối cảnh

Impeccable có detector UI hữu ích nhưng cơ chế cài native skill/hook có thể tạo cấu hình khác nhau giữa Codex, Claude, Cursor và Antigravity. Repo chưa có frontend path, framework, package manager hay design system được chốt. Team cần feedback UI có thể review chung, không thêm dependency runtime, MCP hoặc automation blocking vào bootstrap.

### Lựa chọn đã cân nhắc

1. Cài full skill/hook theo từng provider — nhanh cho một tool nhưng làm lệch capability, tạo config vendor và khó audit trên nhiều hệ điều hành.
2. Không dùng Impeccable — đơn giản nhưng bỏ qua detector UI có ích khi bắt đầu có frontend.
3. Dùng wrapper CLI portable, report Markdown và design context chung — có thêm một lệnh local nhưng cùng contract cho mọi người/agent.

### Quyết định

Chọn phương án 3. Chỉ gọi `npx --yes impeccable@3.2.1 detect --json` thông qua `scripts/design/impeccable-audit.mjs`; Node `22.16.0` local đáp ứng yêu cầu Node `>=22.12.0` của package. Wrapper chỉ audit path UI được claim hoặc local URL, chấp nhận exit `0`/`2` ở advisory mode và tạo report Markdown để handoff.

Không thêm `.agents/skills`, `.codex/hooks.json`, `.cursor/hooks.json`, MCP, browser extension, provider-specific config, package manifest dependency hoặc GitHub Actions job cho Impeccable. Không dùng `/impeccable init`, `/impeccable craft`, `/impeccable live` hay `npx impeccable install` trong bootstrap.

`docs/ai/PROJECT_CONTEXT.md` vẫn là product source of truth; `docs/PRODUCT.md` và `docs/DESIGN.md` chỉ là adapter context thiết kế. `.impeccable/config.json` được track cho waiver shared hẹp có lý do/peer review; `config.local.json`, screenshot, cache/live state và raw audit JSON bị ignore. Design-system checks giữ tắt đến khi tokens/components được chốt và có task review để bật chúng.

### Hệ quả và kiểm chứng

- Mọi agent có thể thực hiện cùng review flow bằng CLI/report thay vì native skill/hook.
- Audit là local advisory, không chặn commit/CI và không thay thế accessibility review hay demo rehearsal.
- Unit test wrapper mô phỏng exit `0`, `2`, JSON lỗi và lỗi thực thi; repository guard kiểm tra artifact/policy.
- Chỉ xem xét CI gate sau khi team chốt frontend path, package manager và ổn định design system qua Decision mới.

### Rollback / fallback

Nếu CLI không phù hợp hoặc package không chạy trên môi trường của peer, bỏ qua audit cho task đó, ghi limitation trong handoff và tiếp tục manual review theo Context Pack. Có thể gỡ wrapper/docs/config như một local change; không có package, hook, remote state hay secret cần thu hồi.

---

## D-004 — Prompt Intake Gate dùng chung trước task thực chất

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Người đề xuất:** Team bootstrap theo yêu cầu hiện tại
- **Phạm vi:** Process / tooling
- **Task Record:** `local-20260717-prompt-intake-gate`
- **Publish (tùy chọn):** chưa publish
- **Peer xác nhận:** Áp dụng ngang hàng cho Codex, Claude, Cursor, Antigravity và mọi peer; không tạo quyền hoặc workflow riêng theo tool.

### Bối cảnh

Task thiếu mục tiêu, tiêu chí xong hoặc điều kiện dừng khiến agent tự suy đoán và mở rộng scope. Team cần một intake ngắn, dùng chung trước khi bất kỳ agent bắt đầu task thực chất, nhưng không muốn template prompt dài dòng hoặc chặn Q&A/status đơn giản.

### Quyết định

`AGENTS.md` là source of truth cho Prompt Intake Gate. Mọi task phân tích, lập kế hoạch, review hoặc hành động phải có Goal, Success Criteria, Constraints và Stopping Conditions trong prompt hiện tại hoặc Task Record/Context Pack active được tham chiếu trực tiếp. Policy repo hiện có đáp ứng Constraints baseline. Nếu thiếu Goal, Success Criteria hoặc Stopping Conditions, agent dừng và hỏi gộp bằng lựa chọn ngắn; không vào `explore`, planning, tool call hoặc ghi resource.

Gate không áp dụng cho chào hỏi, status hoặc Q&A thông tin ngắn. Nó không vượt system/developer instructions, không suy diễn dữ liệu từ task khác, không tạo hook/MCP/vendor config và không yêu cầu ghi lại prompt dài.

### Hệ quả và kiểm chứng

- Task Record/Context Pack thêm Constraints để lưu intake đã chốt; adapters chỉ tham chiếu source chung.
- Repository guard kiểm tra gate và template/playbook để ngăn drift.
- Kiểm chứng bằng unit tests guard, validation local và `git diff --check`; không có remote mutation.

### Rollback / fallback

Nếu gate tạo friction không chấp nhận được, tạo Decision mới để thu hẹp phạm vi hoặc thay đổi câu hỏi intake. Không nới lỏng cục bộ theo vendor và không cần rollback remote.

---

## D-005 — Khởi tạo stack FastAPI (Backend) và Next.js (Frontend)

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Người đề xuất:** Antigravity
- **Phạm vi:** API | dependency | deploy | process
- **Task Record:** `local-20260717-scaffold-vaic`
- **Publish (tùy chọn):** chưa publish
- **Peer xác nhận:** Member 1

### Bối cảnh
Để thực hiện MVP cho 3 thủ tục theo đề bài và đảm bảo tiến độ của hackathon 48 giờ, team cần thống nhất và khởi tạo cấu trúc khung dự án (Scaffold) cho cả phần backend và frontend.

### Lựa chọn đã cân nhắc
1. Dùng cấu trúc monolith (FastAPI render Jinja2 templates) - Lợi: Đơn giản, deploy nhanh; Hại: Khó tách biệt giao diện widget và headless API.
2. Dùng Next.js (Frontend) + FastAPI (Backend) riêng biệt - Lợi: Đúng thiết kế đề xuất ở proposal.md, tách biệt giao diện và API rõ ràng, hỗ trợ widget nhúng qua iframe; Hại: Phải quản lý 2 server chạy song song ở local.

### Quyết định
Chọn phương án 2. Khởi tạo FastAPI trong thư mục `backend/` và Next.js trong thư mục `frontend/`. 

### Hệ quả và kiểm chứng
- Cả hai phần backend và frontend đều có thể chạy độc lập ở local.
- Cần cập nhật `PROJECT_CONTEXT.md` và `ARCHITECTURE.md` với các cổng chạy local tương ứng.

### Rollback / fallback
Nếu một trong hai phần không hoạt động hoặc không deploy được, team sẽ hạ cấp xuống chạy standalone hoặc fallback mock API trực tiếp tại FE.

---

## D-009 — Structure-aware chunking contract cho ba procedure pack MVP

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-18
- **Người đề xuất:** Codex theo Task Record hiện tại
- **Phạm vi:** data | shared logical schema | RAG
- **Task Record:** `local-20260718-chunking-phase-0`
- **Publish (tùy chọn):** chưa publish
- **Peer xác nhận:** Người dùng/repository peer xác nhận ngày 2026-07-18 để triển khai Phase 1 trực tiếp trên `cao`

### Bối cảnh

Corpus local có 5.652 file TXT nhưng raw document không tự động là nguồn đã duyệt. Mẫu phân tầng cho thấy tài liệu có cấu trúc field/bullet và nhiều dòng dài, nên fixed-size character chunking có nguy cơ cắt giữa trường, claim và căn cứ pháp lý. Proposal yêu cầu approved-only RAG, metadata hiệu lực, K1/K2 review và fail-closed; runtime hiện chưa có ingestion/chunking contract chung.

Proposal đang tham chiếu D-006 đến D-008 nhưng các entry đó chưa có trong Decision Log hiện tại. D-009 được dùng để tránh chiếm các ID đã được tham chiếu; D-006 đến D-008 được giữ reserved và không tái sử dụng. Việc phục hồi nội dung lịch sử của các Decision này là task tài liệu riêng, không chặn fixture-only Phase 1.

### Lựa chọn đã cân nhắc

1. Whole-document retrieval — ít preprocessing nhưng context lớn, khó filter claim/citation và dễ trộn phiên bản.
2. Fixed token windows với overlap — đơn giản nhưng cắt structure và nhân bản claim/citation không kiểm soát.
3. Structure-aware parsing rồi áp token budget — cần parser/fixtures nhưng giữ provenance, hierarchy và legal basis để review/test.

### Quyết định

Chọn phương án 3 theo contract tại `docs/ai/CHUNKING_CONTRACT.md`:

- Chỉ allowlist nguồn cho ba procedure pack MVP; không index toàn corpus.
- Dùng lifecycle `staging -> parsed -> needs_review -> approved`, có `rejected` và `stale`; chỉ `approved` được retrieval.
- Logical contract gồm `SourceDocument`, `ParsedSection`, `EvidenceChunk` và `ChunkBuildReport`.
- Chunk target 250–350 tokens, hard maximum 450 tokens đã gồm prefix; không overlap theo phần trăm.
- `TokenCounter` provider-neutral và tokenizer ID là một phần build identity.
- Baseline là structured filter + keyword; vector/pgvector chỉ qua Decision riêng nếu golden set chứng minh cần thiết.
- Không thay public API, dependency, database hoặc runtime schema trong Decision proposal này.

### Hệ quả và kiểm chứng

- Phase 1 phải tạo fixtures có section boundaries và parser deterministic trước khi build chunk.
- Chỉ source/chunk có provenance, hiệu lực và review state hợp lệ mới được phát hành.
- Chunk build phải reproducible; đổi source, parser, chunker hoặc tokenizer buộc version/rebuild.
- Gate đánh giá gồm section-boundary F1 >= 95%, hard-cap pass 100%, citation coverage 100%, stale/future leakage 0 và Retrieval Recall@5 >= 95%.
- Acceptance hiện chỉ cấp quyền triển khai fixtures, annotations và validator/test Phase 1; chưa cấp quyền thay runtime schema/dependency/index.

### Rollback / fallback

Không sửa raw corpus. Mọi parsed/chunk/index artifact có thể bỏ và build lại từ approved source snapshot. Nếu structure-aware retrieval không vượt baseline trên golden set, fallback về structured procedure lookup + keyword trên approved sections, không đưa whole corpus vào LLM.

---

## Mẫu quyết định mới

```md
## D-XXX — <title>

- **Trạng thái:** Proposed | Accepted | Superseded | Rejected
- **Ngày:** YYYY-MM-DD
- **Người đề xuất:** <person/agent>
- **Phạm vi:** API | dependency | data | deploy | demo | process | tooling
- **Task Record:** `local-YYYYMMDD-<slug>`
- **Publish (tùy chọn):** Issue #<number>, PR #<number>
- **Peer xác nhận:** <peer> (và peer thứ hai nếu ở scope freeze)

### Bối cảnh
<Vấn đề, consumer/resource bị ảnh hưởng và deadline.>

### Lựa chọn đã cân nhắc
1. <Lựa chọn A — lợi/hại>
2. <Lựa chọn B — lợi/hại>

### Quyết định
<Lựa chọn, contract/giới hạn chính xác và ownership tạm thời.>

### Hệ quả và kiểm chứng
<Migration, local check/demo evidence, context/tài liệu cần cập nhật.>

### Rollback / fallback
<Cách quay lại hoặc cách demo nếu phương án lỗi.>
```
