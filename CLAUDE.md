# Claude adapter

Áp dụng [`AGENTS.md`](AGENTS.md) và [`docs/ai/TEAM_PROTOCOL.md`](docs/ai/TEAM_PROTOCOL.md) như nguồn quy tắc chung.

- Áp dụng Prompt Intake Gate trong `AGENTS.md` trước mọi task thực chất.
- Bắt đầu bằng mode `explore`; chỉ chuyển sang `implement` khi Task Record và Context Pack đã đủ.
- Làm trong branch/worktree riêng, chỉ sửa scope đã claim và kết thúc bằng handoff chuẩn.
- Với task shared, dừng để ghi Decision Log và lấy xác nhận peer theo protocol.
- Không tạo native Claude skill, không commit MCP config/path/credential, không tự publish hay thay đổi remote.

Context Pack, playbook và policy là portable cho mọi agent; không thay thế chúng bằng transcript dài hoặc giả định kiến trúc khi giá trị vẫn là `TBD`.
