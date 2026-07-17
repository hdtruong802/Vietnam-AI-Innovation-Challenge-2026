# Team roster và lanes

Team gồm năm peer ngang hàng. Không có chức danh cố định theo người hoặc agent; lane chỉ giúp phân tán công việc ban đầu và có thể đổi theo Task Record. Quyền claim, review và merge/publish tuân theo `TEAM_PROTOCOL.md` là như nhau cho tất cả.

## Roster

| Thành viên | GitHub handle | Agent quen dùng | Lane hiện tại (tạm thời) | Backup lane | Liên hệ/khung giờ |
| --- | --- | --- | --- | --- | --- |
| Member 1 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Member 2 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Member 3 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Member 4 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |
| Member 5 | `TBD` | `TBD` | `TBD` | `TBD` | `TBD` |

Agent quen dùng có thể là Codex, Claude, Cursor, Antigravity hoặc kết hợp. Đây là thông tin phối hợp, không phải sự phân cấp hay giới hạn quyền.

## Lanes ban đầu

| Lane | Phạm vi gợi ý | Không bao gồm |
| --- | --- | --- |
| Product / demo | Product brief, journey, pitch, demo script, acceptance criteria | Quyết định một mình về shared contract |
| UI | Giao diện, accessibility, presentation state | Tự thay đổi backend/API contract |
| Application / API | App logic, endpoint, integration boundary | Tự thay đổi data policy hoặc deploy |
| AI / data / evaluation | Prompt/model wiring, dataset policy, evaluation, fallback quality | Đưa secret hoặc dữ liệu nhạy cảm vào repo/prompt |
| Quality / release | Test strategy, demo readiness, reliability, release checks | Làm merge captain hay chặn peer ngoài checklist chung |

Lanes là gợi ý để chia việc; Task Record/Context Pack là nguồn ownership cục bộ. GitHub Issue chỉ là bản publish của record sau khi team bật remote workflow. Một người có thể chuyển lane hoặc hỗ trợ lane khác khi không chồng phạm vi task đang claim.

## Nhịp phối hợp

- Trong 90 phút đầu, điền roster, lane tạm thời, backup lane và các Task Record P0.
- Sync ngắn khoảng mỗi 2 giờ: cập nhật blocker, dependency, contract chờ xác nhận và demo impact.
- Khi bàn giao, cập nhật Task Record/Context Pack theo mẫu handoff; người nhận claim lại record hoặc tạo record follow-up rõ ràng. Khi đã publish, đồng bộ cùng nội dung sang Issue/PR.
- Sáu giờ cuối: cùng áp dụng scope freeze. Bất kỳ peer nào có thể yêu cầu bằng chứng test, fallback hoặc hai xác nhận cho thay đổi mới.

## Quy tắc giao tiếp ngắn

- Nói bằng Task Record/Decision khi thông tin có ảnh hưởng kỹ thuật hoặc cần lưu lịch sử; chat dùng để báo nhanh và phải link về record nếu cần hành động. Sau publish, Issue/PR là bản công khai tương ứng.
- Ghi rõ `blocked`, dependency, file/API dự kiến chạm và deadline. Không dùng tin nhắn mơ hồ như “đang làm phần backend”.
- Phê bình diff và quyết định, không gán chất lượng cho công cụ hay người dùng agent.
