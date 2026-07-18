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
| D-004 | Accepted | Prompt Intake Gate dùng chung trước task thực chất | `local-20260717-prompt-intake-gate` | 2026-07-17 |
| D-005 | Accepted | Scaffold khung dự án FastAPI (Backend) và Next.js (Frontend) | `local-20260717-scaffold-vaic` | 2026-07-17 |
| D-009 | Accepted | Structure-aware chunking contract cho ba procedure pack MVP | `local-20260718-chunking-phase-0`, `local-20260718-chunking-phase-1` | 2026-07-18 |
| D-010 | Accepted | OpenAI grounded RAG adapter mac dinh `gpt-4o-mini` | `local-20260718-openai-grounded-rag` | 2026-07-18 |


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

## D-013 — Production hardening local, fail closed trước K1

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-18
- **Người đề xuất:** User và Codex theo review hệ thống chatbot
- **Phạm vi:** API | data | model/provider | demo
- **Task Record:** `local-20260718-production-hardening-p0`
- **Publish (tùy chọn):** chưa publish
- **Peer xác nhận:** User chọn lộ trình Option 3, loại CI/CD/cloud và cho phép Codex review tài liệu kỹ thuật; xác nhận này không phải K1 human/legal approval.

### Bối cảnh

Hai RAG stack đang cùng tồn tại. Stack legacy đọc artifact từng được gắn approved tự động và có source lẫn ngoài phạm vi. Stack D-011 đọc nguồn thô rồi tự gắn `approved`/`last_verified_at` theo ngày freeze dù `PROJECT_CONTEXT.md` ghi rõ chưa qua K1. Lexical recommendation cũng luôn chọn một trong ba thủ tục cho greeting, câu chung và nhiều intent ngoài phạm vi, tạo precheck false-positive.

### Quyết định

- Nguồn trực tiếp chỉ là candidate: chỉ chấp nhận đúng cặp tên/mã canonical `1.001193`, `1.004222`, `1.001612`, gắn `needs_review`, không có `last_verified_at` và không tạo `verified_guidance`/verdict trước K1.
- Thêm intent gate xác định rõ ba thủ tục; greeting, câu chung, nhiều intent hoặc intent ngoài phạm vi phải abstain.
- Giữ nguyên URL/schema `/v1/rag/search` và `/v1/rag/answer`, nhưng khóa stack legacy mặc định bằng `LEGACY_RAG_ENABLED=false`. Chỉ bật lại có chủ đích sau khi artifact được review.
- `Settings` đọc `.env` root và backend; gateway mới ưu tiên `AI_*` và fallback `OPENAI_*`. Health tách liveness khỏi readiness và báo `degraded` khi guidance chưa approved, RAG/LLM chưa sẵn sàng.
- Task này chỉ harden local runtime; không triển khai CI/CD, cloud, deploy, gọi provider trả phí hoặc sửa dữ liệu thô.

### Hệ quả và kiểm chứng

Luồng hiện tại an toàn hơn nhưng chưa phải sản phẩm hoàn thiện: trước K1, UI phải hiển thị `official_review_required` thay vì checklist/precheck chắc chắn. Contract REST giữ nguyên; enum/capability chỉ được mở rộng. Test dùng source local và fake/offline provider, không gọi OpenAI thật.

### Rollback / fallback

Legacy route vẫn tồn tại và có thể bật có chủ đích bằng config sau review artifact. Revert D-013 sẽ khôi phục hành vi cũ nhưng đồng thời khôi phục rủi ro auto-approved và false-positive, nên không phải fallback demo được khuyến nghị.

---

## D-014 - Synthetic approved family release cho demo local

- **Trạng thái:** Accepted
- **Ngày:** 2026-07-18
- **Người đề xuất:** User theo Task Record hiện tại
- **Phạm vi:** data | demo
- **Task Record:** `local-20260718-demo-family-release`
- **Publish (tùy chọn):** chưa publish
- **Peer xác nhận:** User yêu cầu giữ `review_status=approved`, dùng `https://dichvucong.gov.vn/`, version `2026`, reviewer `Cao`, ngày review `2026-07-18`.

### Bối cảnh

Registry 25 source/26 quan hệ đã có candidate package nhưng chưa có metadata K1
thật. Demo local cần kiểm thử chunking/retrieval trên đủ family trước khi hoàn tất
review nghiệp vụ. D-013 vẫn là policy production mặc định và không cho phép suy
diễn K1 approval từ parser/checksum.

### Quyết định

Cho phép tạo một release **synthetic demo** bị Git ignore với
`review_status=approved` theo chỉ định rõ của user. Manifest phải dùng version
`vaic-family-demo-release-v1` và review notes nêu đây không phải K1/pháp lý;
report/grouped pack phải ghi `approval_mode=synthetic_demo` và
`not_for_production=true`. Tool chỉ nhận output dưới `artifacts/`, kiểm exact
registry/code/title, strict UTF-8 và checksum trước khi build. Không commit raw
data, reviewed manifest hay chunks; không đổi REST API hoặc production defaults.

### Hệ quả và kiểm chứng

- Artifact cho phép chạy approved-only retrieval trong demo local.
- `approved` trong artifact này chỉ là cờ kỹ thuật của demo, không phải bằng chứng
  `verified_guidance` production hoặc human K1.
- `2.000986` giữ hai procedure IDs; source `dataset_raw` được đọc bằng path cấu
  hình và không copy vào worktree.
- Production release vẫn phải thay metadata synthetic bằng URL sâu, effective
  date và review evidence thật theo D-006/D-013.

### Rollback / fallback

Xóa `artifacts/demo-family-release/` và `artifacts/chatbot/` được sinh bởi CLI.
Không có migration, cloud state, secret hoặc API contract cần thu hồi.

---

## Mẫu quyết định mới

## D-010 - OpenAI grounded RAG adapter mac dinh `gpt-4o-mini`

- **Trang thai:** Accepted
- **Ngay:** 2026-07-18
- **Nguoi de xuat:** User theo Task Record hien tai
- **Pham vi:** API | dependency | model/provider | demo
- **Task Record:** `local-20260718-openai-grounded-rag`
- **Publish tuy chon:** chua publish
- **Peer xac nhan:** User xac nhan dung OpenAI API key va model `gpt-4o-mini`

### Boi canh

Runtime RAG da co clean approved chunks va endpoint search evidence, nhung chatbot chua goi LLM that. Demo can cau tra loi tieng Viet tu nhien dua tren evidence da duyet, dong thoi khong duoc suy doan khi retrieval khong co bang chung.

### Lua chon da can nhac

1. Giu keyword RAG khong LLM - on dinh nhung chatbot khong tu nhien.
2. Goi LLM truc tiep tren user query - nhanh nhung vi pham fail-closed/citation policy.
3. Goi OpenAI sau retrieval approved-only - can API key runtime nhung giu grounding va citation enforcement.

### Quyet dinh

Chon phuong an 3. Backend them OpenAI adapter doc `OPENAI_API_KEY` tu environment, `OPENAI_MODEL` mac dinh `gpt-4o-mini`, va endpoint additive `/v1/rag/answer`. Prompt chi cho phep tra loi dua tren evidence hits. Neu khong co evidence, thieu key hoac provider loi, API tra `official_review_required` thay vi sinh cau tra loi.

### He qua va kiem chung

Tests dung fake LLM client de khong goi network hay commit secret. Smoke that can chay local voi `.env` cua nguoi dung. `/v1/rag/search` giu nguyen lam fallback deterministic.

### Rollback / fallback

Go bo route/service/model answer se dua he thong ve keyword RAG search va checklist citations hien co. Khong co migration, database hay secret can thu hoi.

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
