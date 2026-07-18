# Team roster và lanes

Team gồm sáu peer ngang hàng. Không có chức danh cố định theo người hoặc agent; lane chỉ giúp phân tán công việc ban đầu và có thể đổi theo Task Record. Quyền claim, review và merge/publish tuân theo `TEAM_PROTOCOL.md` là như nhau cho tất cả.

## Roster

| Thành viên | GitHub handle | Agent quen dùng | Lane hiện tại (tạm thời) | Backup lane | Liên hệ/khung giờ |
| --- | --- | --- | --- | --- | --- |
| Member 1 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Member 2 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Member 3 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Member 4 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Member 5 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Member 6 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

Agent quen dùng có thể là Codex, Claude, Cursor, Antigravity hoặc kết hợp. Đây là thông tin phối hợp, không phải sự phân cấp hay giới hạn quyền.

## Sáu lane ban đầu

| Lane | Phạm vi gợi ý | Không bao gồm |
| --- | --- | --- |
| Procedure research | Nguồn chính thức, procedure pack, câu hỏi làm rõ và nghiệp vụ | Tự khẳng định quy định chưa được review |
| Data / grounding | Ingestion, source metadata, freshness, retrieval và citations | Đưa dữ liệu nhạy cảm hoặc nguồn chưa rõ quyền vào repo/prompt |
| AI / evaluation | Orchestration hội thoại, provider adapter, golden cases và đo chất lượng | Cho LLM quyết định tính hợp lệ của hồ sơ |
| Backend / rules | API, JSON Schema, deterministic validation và integration boundary | Tự thay đổi data policy hoặc deploy |
| Frontend / widget | Chat, dynamic form, accessibility và portal embedding | Tự thay đổi backend/API contract |
| Quality / deploy / demo | Test, reliability, public demo, fallback và presentation evidence | Làm merge captain hay chặn peer ngoài checklist chung |

Lanes là gợi ý để chia việc; Task Record/Context Pack là nguồn ownership cục bộ. GitHub Issue chỉ là bản publish của record sau khi team bật remote workflow. Một người có thể chuyển lane hoặc hỗ trợ lane khác khi không chồng phạm vi task đang claim.

Backlog khởi tạo, cặp review/backup, full data lifecycle và gates G0–G6 nằm trong [phân công 48 giờ](../../team_docs/phancong.md). Tài liệu đó không tự claim task; mỗi member vẫn phải tạo Task Record riêng.

## Trách nhiệm AI Log ngang hàng

- Mỗi member tự onboard AI Log trong clone/worktree của mình, bind đúng source coding-agent/Task Record và giữ `doctor --strict` pass.
- Mỗi commit chỉ ghi evidence vào `evidence/ai-log/members/<member-id>/`; không sửa/xóa record của peer.
- Member 6 có thể chạy guard và tổng hợp evidence cho demo, nhưng không có quyền cao hơn hoặc thay trách nhiệm capture của Member 1–5.
- Hook commit không tự push; publish vẫn cần yêu cầu và quyền Git rõ ràng.

## Nhịp phối hợp

- Trong 90 phút đầu, điền roster, lane tạm thời, backup lane và các Task Record P0.
- Sync ngắn khoảng mỗi 2 giờ: cập nhật blocker, dependency, contract chờ xác nhận và demo impact.
- Khi bàn giao, cập nhật Task Record/Context Pack theo mẫu handoff; người nhận claim lại record hoặc tạo record follow-up rõ ràng. Khi đã publish, đồng bộ cùng nội dung sang Issue/PR.
- Sáu giờ cuối: cùng áp dụng scope freeze. Bất kỳ peer nào có thể yêu cầu bằng chứng test, fallback hoặc hai xác nhận cho thay đổi mới.

## Quy tắc giao tiếp ngắn

- Nói bằng Task Record/Decision khi thông tin có ảnh hưởng kỹ thuật hoặc cần lưu lịch sử; chat dùng để báo nhanh và phải link về record nếu cần hành động. Sau publish, Issue/PR là bản công khai tương ứng.
- Ghi rõ `blocked`, dependency, file/API dự kiến chạm và deadline. Không dùng tin nhắn mơ hồ như “đang làm phần backend”.
- Phê bình diff và quyết định, không gán chất lượng cho công cụ hay người dùng agent.
