# Decision Log

Decision Log lưu các quyết định liên lane hoặc khó đảo ngược: shared API/schema, dependency, model/provider, data policy, deploy, demo flow, resource dùng chung và ngoại lệ scope freeze. Nó không tạo phân cấp; mọi peer đều có thể đề xuất và review Decision.

## Quy trình local-first

1. Tạo entry `Proposed` từ Task Record trước khi thay shared contract hoặc dependency.
2. Liên kết Task Record, nêu lựa chọn, trade-off, rollback và peer xác nhận.
3. Peer xác nhận thì đổi thành `Accepted`; khi bị thay thế thì giữ lịch sử và ghi `Superseded by D-xxx`.
4. Chỉ thêm GitHub Issue/PR khi team quyết định publish.
5. Trong sáu giờ cuối, thay đổi mới cần hai peer xác nhận theo `TEAM_PROTOCOL.md`.

## Chỉ mục

| ID | Trạng thái | Quyết định | Task Record / publish | Ngày |
| --- | --- | --- | --- | --- |
| D-001 | Accepted | Giao thức peer-equal và Task Record local-first | Bootstrap | 2026-07-16 |
| D-002 | Accepted | Hoãn MCP runtime; chỉ xem xét read-only allowlist | Bootstrap | 2026-07-16 |
| D-003 | Accepted | Impeccable CLI advisory portable, không native skill/hook | `local-20260717-impeccable-cli` | 2026-07-17 |
| D-004 | Accepted | Prompt Intake Gate trước task thực chất | `local-20260717-prompt-intake-gate` | 2026-07-17 |
| D-005 | Accepted | Scaffold FastAPI backend và Next.js frontend | `local-20260717-scaffold-vaic` | 2026-07-17 |
| D-006 | Accepted | Trust/RAG architecture, data governance, API maturity và deploy topology | `local-20260717-challenge-proposal` | 2026-07-17 |
| D-007 | Accepted | Ba procedure pack MVP, pack thứ ba là thành lập hộ kinh doanh | `local-20260717-change-third-mvp` | 2026-07-17 |
| D-008 | Accepted | Web-first delivery và portal integration pathway | `local-20260717-web-first-portal-scope` | 2026-07-17 |
| D-009 | Accepted | AI Log prompt-only, provider-neutral và liên kết theo commit | `local-20260717-ai-log` | 2026-07-17 |
| D-010 | Proposed | Fast merge gate và release artifact provider-neutral | `local-20260718-ci-cd-optimization` | 2026-07-18 |
| D-011 | Proposed | RAG in-process (không pgvector), LLM Gateway OpenAI-compatible với offline fallback, PII Guard regex in-memory, tích hợp vào CopilotService/ports adapter | `local-20260718-rag-llm-guardrail` | 2026-07-18 |
| D-012 | Accepted | Cloud Run backend demo foundation, production-disabled | `local-20260718-gcp-backend-deploy` | 2026-07-18 |
| D-013 | Accepted | Prototype read models cho sáu route base và hai route RAG additive | `local-20260718-prototype-api-contract` | 2026-07-18 |
| D-014 | Accepted | Structure-aware chunking contract cho ba procedure pack MVP | `local-20260718-chunking-phase-0`, `local-20260718-chunking-phase-1` | 2026-07-18 |
| D-015 | Accepted | Ngoại lệ bảng màu đỏ-vàng cho landing page marketing, tách biệt VNGov Copilot Navy & Orange | `local-20260718-landing-page-red-gold` | 2026-07-18 |

---

## D-001 — Giao thức peer-equal và Task Record local-first

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-16
- **Phạm vi:** Collaboration process
- **Liên kết:** `TEAM_PROTOCOL.md`

Mọi người/agent dùng Context Pack và Task Record cục bộ, claim resource trong branch/worktree riêng. Owner chỉ là trách nhiệm tạm thời. GitHub Issue/PR chỉ là bản publish của record khi team chọn publish; PR `risk:shared` cần peer confirmation. `main` giữ demo/release ổn định.

Rollback: tạo Decision mới nếu Task Record không đủ phối hợp; không quay lại bắt buộc Issue cho mọi task khi chưa đánh giá chi phí/ích lợi.

---

## D-002 — Hoãn MCP runtime; chỉ xem xét read-only allowlist

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-16
- **Phạm vi:** Tooling / MCP

Không thêm, không yêu cầu cài và không commit cấu hình cho RepoPrompt hay bất kỳ MCP runtime nào trong bootstrap. Chỉ xem xét lại khi team có ít nhất hai bottleneck context lặp lại, stack ứng dụng đã chốt và một Decision mới được peer chấp thuận. Surface ban đầu phải là stdio, cross-platform, opt-in, read-only cho project/task/decision/demo context; cấm shell, write/delete, Git/GitHub mutation, secret/config access, worktree và agent spawning.

Rollback: gỡ local config của thử nghiệm và tiếp tục Context Pack/Task Record.

---

## D-003 — Impeccable CLI advisory portable, không native skill/hook

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Phạm vi:** Tooling / design review
- **Task Record:** `local-20260717-impeccable-cli`

Dùng wrapper chung `scripts/design/impeccable-audit.mjs` để gọi pinned CLI và tạo Markdown report. Không thêm native skill/hook, MCP, browser extension, provider config, package dependency hoặc CI gate. Exit finding là advisory; waiver shared phải hẹp và được peer review.

Rollback: bỏ audit cho task, ghi limitation trong handoff và tiếp tục manual review; không có runtime/remote state cần thu hồi.

---

## D-004 — Prompt Intake Gate trước task thực chất

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Phạm vi:** Process / tooling
- **Task Record:** `local-20260717-prompt-intake-gate`

`AGENTS.md` là source of truth: phân tích, planning, review hoặc hành động cần Goal, Success Criteria, Constraints và Stopping Conditions trong prompt hiện tại hoặc record active được tham chiếu trực tiếp. Nếu thiếu Goal, Success Criteria hoặc Stopping Conditions, agent dừng và hỏi gộp; policy repo là baseline Constraints. Gate không áp dụng cho chào hỏi/status/Q&A ngắn và không vượt system/developer instructions.

Rollback: Decision mới có thể thu hẹp gate; không nới lỏng riêng theo vendor.

---

## D-005 — Khởi tạo scaffold FastAPI backend và Next.js frontend

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Người đề xuất:** Antigravity
- **Phạm vi:** dependency / API / process
- **Task Record:** `local-20260717-scaffold-vaic`
- **Peer xác nhận:** Member 1

### Bối cảnh

Team cần một baseline source chung để triển khai MVP web-first, tách UI khỏi API. Phương án monolith render template đơn giản hơn nhưng làm yếu pathway widget/headless API; phương án frontend/backend tách biệt tăng chi phí chạy local nhưng rõ boundary hơn.

### Quyết định

Chọn scaffold `frontend/` dùng Next.js và `backend/` dùng FastAPI. Backend hiện có health, procedures, intake, checklist và validation routes; frontend hiện là khung khởi tạo. Decision này chấp thuận **scaffold và dependency layout**, không chấp thuận tự động:

- procedure fact, citation hoặc `verified_guidance` trong seed;
- RAG/vector retrieval, external LLM, PII guard, memory bền vững hoặc data release;
- widget/embed contract, auth/rate limit production, deploy URL hoặc CD.

Các năng lực còn lại thuộc D-006 hoặc Task Record/Decision follow-up.

### Hệ quả và kiểm chứng

- Các lệnh local phải lấy từ manifest/source và kết quả chạy phải ghi vào handoff.
- API public phải được version/schema review trước khi consumer phụ thuộc sâu.
- Không coi frontend template hoặc backend seed là demo hoàn chỉnh hay bằng chứng accuracy pháp lý.

### Rollback / fallback

Nếu một khung không chạy được, dùng standalone UI hoặc mock API chỉ theo Task Record và không bỏ deterministic validation/trust constraints. Thay đổi stack/API shared cần Decision mới.

---

## D-006 — Trust/RAG architecture, data governance, API maturity và deploy topology

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Người đề xuất:** Task `local-20260717-challenge-proposal`
- **Phạm vi:** API / data / deploy / demo
- **Task Record:** `local-20260717-challenge-proposal`
- **Peer xác nhận:** `hdtruong802` (user), 2026-07-18. Nếu task diễn ra trong scope freeze, vẫn cần peer thứ hai theo `TEAM_PROTOCOL.md`.

### Bối cảnh

Ba capability của đề bài cần giao tiếp tự nhiên nhưng phải tạo kết quả kiểm chứng được. D-005 đã tạo code baseline, nhưng không giải quyết nguồn pháp lý, data release, grounding, PII boundary, external model, observability, widget/portal contract hay deploy.

### Quyết định đã chấp thuận

Chấp thuận kiến trúc web-first gồm standalone UI + iframe/widget, trust/orchestration backend, approved structured procedure packs, hybrid keyword/vector retrieval, deterministic rules và provider-neutral LLM adapter. Procedure Pack cần source/effective date/review/checksum; mọi response quy phạm cần `procedure_version`, `source_refs`, `last_verified_at` và một trust state: `verified_guidance`, `need_more_information`, `official_review_required`.

LLM chỉ hỏi làm rõ/diễn đạt/giải thích evidence đã có. Nó không quyết định hồ sơ hợp lệ, không tạo giấy tờ/rule ngoài pack approved và không nhận raw direct identifiers. PII Guard phải minimize/tokenize trước model call; token map session-only, không vào disk, log, vector index hay `CaseSnapshot`. Deterministic Rule Engine là nguồn duy nhất tạo field/cross-field findings.

Curated acquisition, checksum, K1 approval, release/rollback và K2 re-review là gate trước runtime knowledge. D-006 chấp thuận kiến trúc mục tiêu và các gate; nó **không** tự chọn hoặc provision storage/vector database, model provider, hosting hay CD cụ thể.

### Hệ quả và kiểm chứng

- D-005 scaffold là điểm xuất phát, không phải acceptance của toàn bộ D-006.
- Mỗi capability phải có Task Record/Context Pack, contract/schema test, data/retrieval/golden-case evidence và rollback/fallback.
- Security evidence phải chứng minh raw identifier không tới external model/log, token map bị hủy theo phiên và rule validation còn hoạt động khi model/retrieval lỗi.
- Long-term `CaseSnapshot` tối đa 30 ngày chỉ sau Decision mới và S1 privacy/security review.

### Rollback / fallback

Không đủ evidence hoặc nguồn mâu thuẫn thì `official_review_required`. Model/retrieval lỗi thì dùng approved structured data/rules khi đủ, nếu không fail closed. Mọi thay đổi shared stack/API/deploy cần Decision thay thế.

---

## D-007 — Ba procedure pack MVP, pack thứ ba là thành lập hộ kinh doanh

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Phạm vi:** Product / data / evaluation / demo
- **Task Record:** `local-20260717-change-third-mvp`

Phạm vi MVP gồm đúng ba procedure pack:

1. Đăng ký khai sinh.
2. Đăng ký thường trú.
3. Đăng ký thành lập hộ kinh doanh.

Mỗi pack cần clarification tree, checklist, steps, form schema, validation rules, citations và golden cases cùng mức hoàn thiện. D-007 không xác nhận trước bất kỳ giấy tờ, điều kiện, biểu mẫu, cơ quan, phí, thời hạn hoặc rule nào; các chi tiết chỉ được vào approved pack sau source discovery, registry, review hiệu lực/quyền sử dụng và K1.

Không đủ source/K1 thì công khai limitation và trả `official_review_required`; không tự thay bằng thủ tục khác.

---

## D-008 — Web-first delivery và portal integration pathway

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Phạm vi:** Product / UX / integration / demo
- **Task Record:** `local-20260717-web-first-portal-scope`

Delivery surface là standalone web app, widget/Web Component bọc iframe và REST API. Không làm native mobile app, PWA install flow hay app-store artifact trong MVP. Acceptance tập trung browser web, keyboard/focus/contrast, browser zoom, portal container/overflow, iframe isolation, CSP/CORS và embed smoke test.

Đây là pathway kiến trúc/pilot, không phải tuyên bố đã được cấp quyền hay tích hợp production với Cổng DVCQG. Widget/API production, sandbox, auth, origin allowlist, contract versioning và security review vẫn là capability follow-up của D-006.

---

## D-009 — AI Log prompt-only, provider-neutral và liên kết theo commit

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-17
- **Phạm vi:** Process / tooling / evidence
- **Task Record:** `local-20260717-ai-log`

Codex, Claude, Cursor và Antigravity dùng chung `PromptEvent`/`CommitEvidence`. Mỗi member onboard một lần cho từng clone/worktree, bind source rõ ràng hoặc dùng manual stdin. Adapter chỉ đọc delta `UserPrompt` của đúng workspace; `.ai-log/` giữ path/checkpoint local và bị ignore. Hook chung stage evidence, thêm `AI-Log`, `AI-Tools`, `AI-Capture` trailer và **không tự push**.

Không lưu assistant response, system/developer prompt, tool traffic, chain-of-thought, transcript/session file, screenshot, cookie hoặc absolute source path. Capture lỗi tạo warning không chặn commit; secret/PII phải redact/omit. Guard enforcement bắt đầu từ commit chứa policy, không backfill legacy history. AI Log prompt-only vẫn là compliance gap nếu ban tổ chức bắt buộc raw desktop session/screenshot; cần xác nhận hoặc một gói ngoài Git được review riêng.

Rollback: gỡ local `core.hooksPath`, xóa `.ai-log/` và ngừng record mới; không fallback sang raw session.

---

## D-010 — Fast merge gate và release artifact provider-neutral

- **Trạng thái:** Proposed
- **Ngày:** 2026-07-18
- **Người đề xuất:** User-requested CI/CD task
- **Phạm vi:** process / dependency / deploy
- **Task Record:** `local-20260718-ci-cd-optimization`
- **Peer xác nhận:** `TBD` trước publish hoặc activation remote

### Bối cảnh

Repository guard trước đây chạy full bootstrap scan và Git range scan trong cùng một job. `data/**` hiện có hàng nghìn raw payload files nhưng không phải runtime knowledge release; đọc từng file trong range làm local preflight chậm. Đồng thời scaffold D-005 chưa có application lint/test/build CI hay release evidence.

### Quyết định đề xuất

- Giữ check tổng hợp tên `repository-guard`, nhưng chạy các job frontend, backend, design và data metadata theo diff scope để merge gate không cài runtime không liên quan.
- Repository guard không đọc payload `data/**`; data job chỉ kiểm path/blob metadata. Data quality/provenance/retrieval vẫn thuộc D-006 và approved release sau này.
- `dev` chỉ sinh frontend/backend artifact cùng manifest checksum; `main` chỉ promote thủ công candidate có source tree khớp. Đây không phải live deploy.
- Không tạo hosting, environment, secret, URL hoặc provider adapter. Live CD chỉ được xem xét sau D-006/Decision follow-up, peer confirmation, provider, secret, smoke check và rollback contract.

### Hệ quả và kiểm chứng

- Fast paths vẫn kiểm tra policy, AI Log history, secret/path checks cho source ngoài `data/**`; app checks chạy khi code/dependency liên quan đổi.
- Candidate manifest chứa commit/tree/digest, không chứa secret hoặc raw data payload. Promotion fail closed khi confirmation, tree hoặc checksum không hợp lệ.
- D-010 chỉ chuyển `Accepted` khi một peer review workflow, check evidence và giới hạn provider-neutral.

### Rollback / fallback

Revert workflow, guard helper và release-manifest changes để quay về repository guard cũ. Không có external deploy state để thu hồi.

---

## D-011 — RAG in-process, LLM Gateway OpenAI-compatible, PII Guard regex in-memory

- **Trạng thái:** Proposed
- **Ngày:** 2026-07-18
- **Người đề xuất:** Cursor theo yêu cầu người dùng hiện tại
- **Phạm vi:** API | dependency | data | process
- **Task Record:** `local-20260718-rag-llm-guardrail`
- **Publish (tùy chọn):** chưa publish
- **Peer xác nhận:** Chưa có peer khác online tại thời điểm thực hiện (roster `TEAM.md` còn `TBD`); cần một peer xác nhận trước khi coi là `Accepted`, đặc biệt nếu bước vào 6 giờ cuối.

### Bối cảnh

`docs/proposal.md` mục 5 đề xuất kiến trúc RAG/Knowledge, LLM Gateway provider-neutral và PII Guard, nhưng đánh dấu framework/model provider/database là `TBD`. `PROJECT_CONTEXT.md` đã chốt `AI/model/provider: Provider-neutral adapter` và `Data/storage: Neon Postgres (pgvector)` ở trạng thái `Proposed` (chưa `Accepted`, chưa provision). Cần triển khai đủ 3 năng lực để demo end-to-end trong thời gian hackathon còn lại mà không chờ hạ tầng Neon/pgvector hoặc secret model provider thật.

### Lựa chọn đã cân nhắc

1. Chờ Neon/pgvector + provider thật được provision trước khi code — an toàn về kiến trúc dài hạn nhưng rủi ro P0 "demo không ổn định" nếu hackathon hết giờ trước khi có infra.
2. Dùng thư viện vector/ML nặng (`numpy`/`scikit-learn`/`sentence-transformers`) cho retrieval — chất lượng ngữ nghĩa tốt hơn nhưng vi phạm rủi ro P0 đã ghi trong `PROJECT_CONTEXT.md` ("không phụ thuộc thư viện native nặng") và tăng thời gian cài đặt/build trên máy giám khảo.
3. RAG in-process bằng pure-Python lexical/TF-IDF hybrid trên `data/Data_DVC` (dataset thật từ nguồn thủ tục hành chính), LLM Gateway dùng client `openai` (đã có trong `requirements.txt`) trỏ `AI_BASE_URL` để provider-neutral, có fallback deterministic khi thiếu `AI_API_KEY`; PII Guard bằng regex + dict in-memory theo session, không dùng KMS/Vault.

### Quyết định

Chọn phương án 3. Cụ thể:

- **RAG:** Structured store nạp `data/Data_DVC/*.txt`, lọc theo 3 procedure MVP bằng khớp `Tên thủ tục`/từ khóa; retrieval hybrid = keyword filter + lexical term-overlap scoring (không numpy/sklearn); trả về evidence kèm `source_ref`, `last_verified_at` (ngày source freeze), `confidence`; dưới ngưỡng confidence hoặc ngoài 3 pack => `official_review_required`. Không index PII, session hay case memory.
- **LLM:** `LLMGateway` dùng `openai` SDK, cấu hình qua `AI_PROVIDER/AI_MODEL/AI_API_KEY/AI_BASE_URL` (đã có trong `.env.example`); system prompt ép model chỉ dùng evidence được cung cấp, chỉ trả JSON structured (intent/clarification/explanation), không tự quyết định checklist/finding. Khi thiếu `AI_API_KEY`, gateway dùng fallback templating deterministic (không gọi model, không bịa nội dung quy phạm) để demo vẫn chạy được offline.
- **Guardrail:** `PIIGuard` regex nhận diện họ tên/số CCCD/SĐT/địa chỉ chi tiết, tokenize trước khi đưa vào LLM, map token chỉ lưu in-memory theo `session_id` với TTL phiên, không log/DB/vector.
- **Tích hợp:** Sau khi `local-20260717-challenge-proposal`/`local-20260718-ci-cd-optimization` refactor backend sang kiến trúc hexagonal (`app/ports.py` + `AppContainer` + `CopilotService`), D-011 hiện thực RAG/LLM bằng adapter mới (`app/adapters/rag_llm.py`) implement `ProcedureRepository`/`RecommendationProvider`/`RetrievalProvider`/`LLMProvider` thay cho bản `Disabled*`; kích hoạt qua `procedure_data_mode=rag`, `rag_mode=rag`, `llm_mode=gateway`. `CopilotService`/`TrustPolicy`/`RuleEngine` gốc của D-006 giữ nguyên, không tạo `TrustPolicy` riêng.
- Không đổi public REST schema hiện có (`ARCHITECTURE.md`); không thêm cột DB hay service ngoài.

### Hệ quả và kiểm chứng

- Chạy được hoàn toàn local, không cần Neon/pgvector hay API key thật; khi có provider thật chỉ cần set env, không đổi code.
- Cần `pytest backend/tests` cho PII Guard tokenize/detokenize, retrieval trên 3 pack, adapter mới và trust policy fail-closed.
- Khi Neon/pgvector hoặc provider thật được Decision riêng chấp thuận, migration retrieval sang pgvector là thay adapter `RetrievalProvider`, không đổi `app/ports.py` contract.

### Rollback / fallback

Nếu retrieval lexical không đủ chất lượng cho demo, đặt lại `procedure_data_mode=fixture`/`rag_mode=disabled`/`llm_mode=disabled` trong `Settings` để `AppContainer` quay về adapter fixture/disabled có sẵn, không cần đổi code service. Nếu LLM provider lỗi/timeout, gateway trả fallback deterministic và `TrustPolicy` chuyển `official_review_required` thay vì chặn toàn bộ luồng.

---

## D-014 — Structure-aware chunking contract cho ba procedure pack MVP

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-18
- **Người đề xuất:** Codex theo Task Record hiện tại
- **Phạm vi:** data | shared logical schema | RAG
- **Task Record:** `local-20260718-chunking-phase-0`
- **Publish (tùy chọn):** chưa publish
- **Peer xác nhận:** Người dùng/repository peer xác nhận ngày 2026-07-18 để triển khai Phase 1 trực tiếp trên `cao`

### Bối cảnh

Corpus local có 5.652 file TXT nhưng raw document không tự động là nguồn đã duyệt. Mẫu phân tầng cho thấy tài liệu có cấu trúc field/bullet và nhiều dòng dài, nên fixed-size character chunking có nguy cơ cắt giữa trường, claim và căn cứ pháp lý. Proposal yêu cầu approved-only RAG, metadata hiệu lực, K1/K2 review và fail-closed; runtime hiện chưa có ingestion/chunking contract chung.

Proposal đang tham chiếu D-006 đến D-008 nhưng các entry đó chưa có trong Decision Log hiện tại tại thời điểm đề xuất; các entry đó nay đã được publish (xem trên). Việc phục hồi nội dung lịch sử của các Decision này là task tài liệu riêng, không chặn fixture-only Phase 1.

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

## D-013 — Prototype read models và RAG routes additive

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-18
- **Người đề xuất:** hdtruong802 / Codex
- **Phạm vi:** API / demo / process
- **Task Record:** `local-20260718-prototype-api-contract`
- **Peer xác nhận:** user — explicit approval “thực hiện plan”

### Bối cảnh

Prototype web cần hiển thị luồng chat, tiến trình năm bước, procedure card, xác nhận thông tin và hành động kế tiếp. Sáu route `/v1` đã có là đủ boundary; chỉ thiếu read model và action stateless để FE tích hợp nhất quán.

### Quyết định

Mở rộng **additive** DTO của sáu route base với journey năm bước, procedure card, confirmed facts, review/next action và turn type cho intake. Đồng thời công khai hai route RAG additive: `/v1/rag/search` và `/v1/rag/answer`; chúng chỉ trả evidence approved hoặc diễn giải grounded có citation, và fail closed khi thiếu evidence/key hoặc provider lỗi. `SessionContext` là structured state do browser giữ và gửi lại; backend không lưu transcript, form draft hay PII. Input DTO từ client dùng `extra=forbid`.

Không thêm route, auth, upload/OCR, support ticket, portal integration, database, dependency hoặc provider. Deterministic Rule Engine vẫn là nguồn duy nhất tạo finding/verdict. Nội dung hướng dẫn/card/checklist chỉ được hiển thị đầy đủ khi Procedure Pack được verified; fixture hoặc runtime disabled giữ fail-closed.

### Hệ quả và kiểm chứng

- FE tích hợp trực tiếp bằng OpenAPI, không cần endpoint prototype riêng.
- Context chỉ chứa procedure/version, câu trả lời clarification, document-review ID và review-gate acknowledgement; không chứa lịch sử chat hoặc form data.
- Test contract phải chứng minh strict input, action flow, approved pack render và fixture/disabled không phát guidance.

### Rollback / fallback

Các trường response mới là optional/additive nên FE có thể bỏ qua. Nếu adapter/pack không sẵn sàng, response dùng `official_review_required` hoặc `need_more_information`, không fallback sang fact fixture.

---

## D-015 — Ngoại lệ bảng màu đỏ-vàng cho landing page marketing

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-18
- **Người đề xuất:** Claude theo yêu cầu người dùng
- **Phạm vi:** UI/design
- **Task Record:** `local-20260718-landing-page-red-gold`
- **Peer xác nhận:** Người dùng xác nhận trực tiếp trong phiên làm việc ngày 2026-07-18

### Bối cảnh

Trang chủ marketing (`frontend/src/app/page.tsx`, khối `view === "landing"`) cần khớp bố cục và màu sắc với ảnh tham chiếu thật `Cổng dịch vụ công Quốc gia.png` (đỏ-vàng, trống đồng vàng kim, hoa sen hồng). `docs/DESIGN.md` hiện quy định hệ màu VNGov Navy & Orange, tối giản, không màu mè — dùng cho giao diện Trợ lý AI Copilot (`view === "copilot"`). Hai yêu cầu xung đột nhau nếu áp dụng cùng một bảng màu cho cả hai view.

### Lựa chọn đã cân nhắc

1. Giữ nguyên Navy & Orange cho cả landing page — không khớp ảnh mẫu người dùng cung cấp.
2. Đổi toàn bộ `docs/DESIGN.md` sang đỏ-vàng — ảnh hưởng cả giao diện Copilot app, không cần thiết và rủi ro cao hơn.
3. Thêm token màu riêng (`--color-gov-red`, `--color-gov-gold`, `--color-gov-cream`) chỉ dùng trong các component `frontend/src/app/components/landing/*`, giữ nguyên token Navy/Orange cho Copilot view.

### Quyết định

Chọn phương án 3. Landing page (Header, Hero, 6 dịch vụ, Dịch vụ nổi bật + Cập nhật, Lợi ích, Footer) dùng token `gov-red`/`gov-gold`/`gov-cream` mới trong `frontend/src/app/globals.css` và ảnh thật có sẵn trong `frontend/src/image/` (quốc huy, logo, nền trống đồng/hoa sen). Giao diện Copilot (`view === "copilot"`) không đổi, vẫn theo `docs/DESIGN.md` Navy & Orange.

Bổ sung ngày 2026-07-18: thêm scoped token `--portal-page`/`--portal-surface`/`--portal-border`/`--portal-text`/`--portal-muted`/`--portal-red`/`--portal-red-dark`/`--portal-orange`/`--portal-gold` dưới class `.portal-home` (không sửa `:root`/`@theme`), và một `.portal-container` utility dùng chung cho mọi section của landing page, để khớp sát hơn ảnh tham chiếu gốc mà không đổi token Copilot.

### Hệ quả và kiểm chứng

- `docs/DESIGN.md` không cần cập nhật vì phạm vi ngoại lệ chỉ giới hạn ở landing page, không phải toàn bộ design system.
- `npm run typecheck`, `npm run build` đã chạy sau các đợt chỉnh sửa; không có lỗi mới phát sinh từ thay đổi này (một lint warning tiền tồn tại trong `layout.tsx`, ngoài phạm vi).
- Đã xác minh bằng `next dev` rằng landing page compile và render đúng nội dung, kể cả sau đợt refine footer/hero/benefits ngày 2026-07-18.

### Rollback / fallback

Xoá token `gov-*`/`portal-*` khỏi `globals.css` và revert các component trong `frontend/src/app/components/landing/` về bản Navy & Orange trước đó nếu cần đồng bộ lại với `docs/DESIGN.md`.

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
