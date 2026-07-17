# Playbook: Impeccable advisory audit

## Mục tiêu

Chạy Impeccable như một CLI audit chung, review được và không ưu tiên vendor nào. Playbook này áp dụng như nhau cho Codex, Claude, Cursor và Antigravity; nó không tạo native skill, hook, MCP server hoặc provider-specific config.

## Điều kiện trước khi chạy

1. Đọc `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md`, `docs/PRODUCT.md`, `docs/DESIGN.md` và Context Pack của task UI.
2. Task Record phải claim đúng thư mục UI hoặc local URL, nêu viewport/state cần kiểm chứng, `risk` và người chịu trách nhiệm handoff.
3. Khi tokens/components/layout còn shared hoặc `TBD`, chuyển lại `explore` để hoàn thiện design context và Decision cần thiết. Không tự suy ra token hay framework.
4. Không audit URL có credential/query nhạy cảm, screenshot/data nhạy cảm hoặc local config ngoài Git.

## Chạy ở mode `review` hoặc `verify-demo`

```text
node scripts/design/impeccable-audit.mjs --task <task-id> --target <ui-path> [--scope type,layout]
node scripts/design/impeccable-audit.mjs --task <task-id> --url <local-url> [--scope type,layout]
```

- Chọn **một** `--target` hoặc `--url`. `--target` phải ở trong repo; `--url` chỉ dùng local dev server khi đã sẵn sàng.
- Wrapper pin `impeccable@3.2.1`, gọi `detect --json` và tạo `docs/design/reviews/<task-id>-impeccable.md`.
- `--scope` chỉ phân loại review trong report (ví dụ `type,layout`); nó không lọc detector vì CLI `detect` không có scope flag.
- Exit `0` và `2` từ detector là kết quả advisory hợp lệ. Lỗi chạy detector hoặc JSON không hợp lệ phải được xử lý trước handoff.
- Chỉ sửa finding nằm trong scope Task Record. Không mở rộng sang shared tokens/components, dependency, deploy hoặc demo flow khi chưa có Decision/claim phù hợp.

## Waiver

- Ưu tiên sửa finding. Waiver chỉ dành cho ngoại lệ cụ thể đã có lý do và peer xác nhận theo mức risk.
- Tạo waiver chung qua CLI `impeccable ignores`; lưu trong `.impeccable/config.json` có track.
- Waiver cá nhân/experiment dùng `.impeccable/config.local.json` bị ignore. Không copy sang peer, không commit và không tắt rule toàn cục tùy tiện.

## Handoff

Ghi vào Task Record: report path, scope/URL đã audit, finding đã sửa, waiver + lý do, state/viewport chưa kiểm chứng, lệnh đã chạy và rollback/fallback. `impeccable-audit` là advisory local, không phải CI gate hay lý do để bỏ accessibility/manual demo review.
