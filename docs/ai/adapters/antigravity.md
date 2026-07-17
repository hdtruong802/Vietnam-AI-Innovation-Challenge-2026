# Antigravity adapter

Nạp [`AGENTS.md`](../../../AGENTS.md) và [`TEAM_PROTOCOL.md`](../TEAM_PROTOCOL.md) làm instruction chung cho workspace, hoặc paste nội dung tương đương vào session nếu Antigravity không hỗ trợ workspace rule.

## Cách khởi động session

1. Áp dụng [Prompt Intake Gate](../../../AGENTS.md#prompt-intake-gate) trước mọi task thực chất.
2. Xác nhận Task Record, mode hiện tại, base ref và scope files/API/resources.
3. Bắt đầu bằng `explore`; với task code/API/data/config/demo hoặc `risk:shared`, tạo/chọn Context Pack từ [template](../../../.agents/context-packs/TEMPLATE.md).
4. Chỉ chuyển sang `implement` trong branch/worktree riêng sau khi context đủ rõ. Không chạy hai writer cho cùng Task Record.
5. Kết thúc bằng handoff chuẩn trong `AGENTS.md`, bao gồm resource claims đã release.

Antigravity có cùng quyền và giới hạn như Codex, Claude, Cursor và mọi peer khác. Không commit config MCP, credential, transcript dài hay workflow riêng cho Antigravity.
