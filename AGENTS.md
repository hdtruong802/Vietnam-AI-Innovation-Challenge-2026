# Quy tắc chung cho coding agent

`AGENTS.md` là điểm vào chung cho Codex, Claude, Cursor và Antigravity. Mọi người và mọi agent là peer: không có agent, lane hay người điều phối nào có quyền ưu tiên cố định.

## Prompt Intake Gate

Trước mọi **task thực chất** (phân tích, lập kế hoạch, review hoặc hành động), kiểm tra đủ bốn thành phần trước khi vào `explore`, planning, gọi tool hoặc sửa bất kỳ resource nào:

- **Goal:** kết quả cần đạt.
- **Success Criteria:** điều kiện xác nhận đã xong.
- **Constraints:** ràng buộc riêng của task; policy hiện có của repo được tính là baseline nếu không có ràng buộc bổ sung.
- **Stopping Conditions:** khi nào phải dừng và hỏi thay vì tự quyết.

Chỉ dùng nội dung trong prompt hiện tại hoặc Task Record/Context Pack **đang active được tham chiếu trực tiếp**; không suy diễn từ task/context khác. Gate không áp dụng cho chào hỏi, status hoặc Q&A thông tin ngắn.

Nếu thiếu Goal, Success Criteria hoặc Stopping Conditions, dừng: nêu đúng mục thiếu và hỏi gộp bằng 2–3 lựa chọn ngắn, phù hợp task. Không bắt đầu task cho tới khi người dùng chốt. System/developer instructions luôn có ưu tiên cao hơn quy tắc này.

## Đọc trước khi sửa

1. Đọc [`docs/ai/TEAM_PROTOCOL.md`](docs/ai/TEAM_PROTOCOL.md).
2. Đọc [`docs/ai/PROJECT_CONTEXT.md`](docs/ai/PROJECT_CONTEXT.md), [`docs/ai/ARCHITECTURE.md`](docs/ai/ARCHITECTURE.md) và Decision Log liên quan khi task ảnh hưởng sản phẩm, kiến trúc hoặc demo.
3. Mở playbook phù hợp trong [`.agents/playbooks/`](.agents/playbooks/) trước khi chuẩn bị context, tạo worktree, implement, review hoặc chuẩn bị demo.
4. Với task có code, API, data, config, demo hoặc `risk:shared`, tạo/chọn Context Pack theo [template](.agents/context-packs/TEMPLATE.md) trước khi chuyển sang mode `implement`.

Ưu tiên hướng dẫn theo thứ tự: yêu cầu hiện tại của người dùng > hướng dẫn cục bộ gần mã nguồn hơn > Context Pack/Decision Log của task > tệp này > `TEAM_PROTOCOL.md` > template.

## Quy tắc không thương lượng

- Mỗi task có một **Task Record**. Trước khi publish, dùng ID `local-YYYYMMDD-slug`; khi có GitHub Issue, ghi số Issue vào record nhưng không cần đổi tên branch.
- Owner chỉ là trách nhiệm tạm thời cho scope và handoff, không phải vai trò cấp trên. Chỉ một phiên `implement` được sửa source trong scope/worktree của Task Record tại một thời điểm.
- Trước khi sửa, kiểm tra `git status --short --branch`, base ref, Context Pack, vùng files/API/resources đã claim và thay đổi đang tồn tại.
- Không sửa cùng working tree có thay đổi chưa commit của peer. Dùng branch/worktree hoặc clone riêng; không copy `.env`, token, ignored data hay file local sang worktree khác.
- Không đưa secret, token, dữ liệu nhạy cảm, dữ liệu doanh nghiệp thô hoặc file model lớn vào Git, Task Record, Issue, PR, prompt hay log.
- Mỗi clone/worktree dùng AI Log phải chạy onboarding local một lần và `doctor --strict`; sau đó chỉ ghi `UserPrompt` đã sanitize từ source được bind rõ với repo hoặc manual stdin. Không ghi assistant response, system/developer prompt, tool traffic, chain-of-thought, transcript/session file, screenshot hoặc absolute source path; hook commit không cấp quyền tự push.
- Giữ adapter theo tool mỏng và cùng trỏ về protocol chung; không thêm native skill, MCP config hoặc quyền riêng theo vendor trong bootstrap.
- Không tự ý thay đổi shared API, schema, dependency, deploy flow hoặc demo flow. Ghi Decision Log và nhận xác nhận của peer theo mức `risk` trước khi implement.
- Không push, force-push, merge PR, thay đổi GitHub settings hoặc xóa lịch sử Git trừ khi yêu cầu hiện tại cho phép rõ ràng.

## Bốn mode hành vi

| Mode | Được làm | Không được làm |
| --- | --- | --- |
| `explore` | Đọc repo, xác minh facts, chọn context và hoàn thiện Task Record/Context Pack. | Sửa source, config hoặc resource. |
| `implement` | Sửa đúng scope đã claim trong worktree riêng và cập nhật evidence. | Mở rộng scope âm thầm hoặc chạy nhiều writer trong cùng task. |
| `review` | Đối chiếu diff với Context Pack, contracts, risk và evidence. | Sửa hộ implementer trừ khi nhận Task Record mới rõ ràng. |
| `verify-demo` | Chạy check, kiểm thử demo/fallback và hoàn thiện handoff. | Thêm feature/dependency mới ngoài scope freeze hoặc Task Record. |

Mode là cách làm việc, không phải chức danh hay quyền riêng của một công cụ. Sub-agent chỉ được chạy song song ở mode `explore` hoặc `review`; mọi ghi source phải do một implementer đã claim scope thực hiện.

## Luồng task tối thiểu

1. Tạo/claim Task Record, ghi owner, mode, base ref, files/API/resources dự kiến chạm, acceptance criteria, dependency và `risk:isolated` hoặc `risk:shared`.
2. Chuẩn bị Context Pack nếu task thuộc diện bắt buộc; dùng nguồn được chọn lọc theo file/line, không dán transcript hay toàn bộ repo.
3. Tạo branch từ `dev`: `feature/<task>-<slug>`, `fix/<task>-<slug>`, `chore/<task>-<slug>` hoặc `spike/<task>-<slug>`; làm trong worktree riêng.
4. Implement đúng scope, chạy kiểm tra phù hợp và để một peer review khi policy yêu cầu.
5. Handoff trong Task Record; chỉ khi team quyết định publish thì sao chép record vào GitHub Issue/PR.

## Handoff bắt buộc

```text
Task Record / Issue / branch:
Mode cuối cùng và kết quả đạt được:
Context Pack + base ref:
Files, API và resources đã chạm:
Kiểm tra đã chạy + kết quả:
Risk / rollback / phần chưa kiểm chứng:
Resource claims đã release:
AI-Log ID + tools/capture status (nếu đã bật):
Việc tiếp theo hoặc handoff cho peer:
```

Chi tiết về conflict, review, publish và scope freeze nằm trong [`docs/ai/TEAM_PROTOCOL.md`](docs/ai/TEAM_PROTOCOL.md).
