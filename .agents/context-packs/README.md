# Context Pack records

Thư mục này chứa template và Task Record/Context Pack cục bộ của từng thay đổi. Pack đã chuyển sang `done` là **historical record**: giữ nguyên mục tiêu, base ref, đường dẫn và trạng thái tại thời điểm task diễn ra để truy vết quyết định.

Không dùng một pack cũ làm source of truth hiện hành nếu nó mâu thuẫn với:

1. yêu cầu người dùng hiện tại;
2. [Project Context](../../docs/ai/PROJECT_CONTEXT.md);
3. [Architecture](../../docs/ai/ARCHITECTURE.md) và [Decision Log](../../docs/ai/DECISIONS.md);
4. [Team Protocol](../../docs/ai/TEAM_PROTOCOL.md).

Các tham chiếu như `.temp_docs/`, MVP cũ, branch hoặc remote status trong pack hoàn tất chỉ mô tả bối cảnh lịch sử; không cần đổi đường dẫn hoặc viết lại lịch sử. Task mới phải tạo pack mới từ [TEMPLATE.md](TEMPLATE.md), dùng facts hiện hành và ghi pack cũ trong phần context nếu cần truy vết.
