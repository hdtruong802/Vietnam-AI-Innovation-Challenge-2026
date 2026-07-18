# AI Log đa-agent

AI Log liên kết **chỉ `UserPrompt` dùng để phát triển repo này** với từng commit. Codex, Claude, Cursor và Antigravity dùng cùng schema và quyền. Git không nhận assistant response, system/developer prompt, tool traffic, chain-of-thought, transcript/session đầy đủ, screenshot hay absolute source path.

## Onboard một lần cho mỗi clone/worktree

Mỗi thành viên chọn một Task Record và một source JSON/JSONL rõ ràng của coding agent:

```text
python scripts/ai_log/ai_log.py onboard --member member-1 --task local-YYYYMMDD-slug --tool cursor --source <explicit-json-or-jsonl-source>
python scripts/ai_log/ai_log.py doctor --strict
```

`onboard` là idempotent: nó tạo state/checkpoint ignored, bind source, sinh hook executable vào `.ai-log/hooks/`, đặt `core.hooksPath=.ai-log/hooks` và chạy readiness check mà không in prompt. Chạy lại sau `git pull` để refresh hook nếu template hoặc CLI đã đổi. Git không cho phép repo tự kích hoạt hook chỉ bằng checkout/pull, nên bước onboard là bắt buộc trên từng clone/worktree.

Định dạng binary/SQLite hoặc source chưa được nhận diện dùng manual mode:

```text
python scripts/ai_log/ai_log.py onboard --member member-1 --task local-YYYYMMDD-slug --tool antigravity --manual
python scripts/ai_log/ai_log.py record --tool antigravity --stdin
```

Ở manual mode, gọi `record --stdin` ngay tại Prompt Intake cho từng prompt dùng để dev. Không truyền prompt trên command line để tránh shell history. `setup`, `bind` và `set-task` vẫn được giữ để thêm tool thứ hai hoặc cập nhật task:

```text
python scripts/ai_log/ai_log.py bind --tool claude --source <explicit-json-or-jsonl-source>
python scripts/ai_log/ai_log.py set-task --task local-YYYYMMDD-slug
```

AI Log không quét thư mục home và không đoán schema. Source tự động phải có workspace/cwd khớp canonical Git root; mặc định checkpoint bắt đầu tại lúc bind. Chỉ dùng `--from beginning` sau khi đã xác minh source chỉ thuộc repo này.

## Hỗ trợ adapter

| Tool | Event được nhận | Source hỗ trợ |
| --- | --- | --- |
| Codex | `event_msg` / `user_message` | JSONL có `session_meta.cwd` |
| Claude | `type: user`, `message.role: user` | JSON/JSONL có `cwd` |
| Cursor | `UserPrompt`/`user_prompt` với role user | JSON/JSONL export có workspace |
| Antigravity | `UserPrompt`/`user_message` với role human/user | JSON/JSONL export có project/workspace |

## Commit flow

Sau onboarding, `git commit` tự thực hiện:

1. Thu delta prompt mới kể từ checkpoint, sanitize và stage record trong `evidence/ai-log/members/<member-id>/`.
2. Tạo `CommitEvidence` trong namespace của chính thành viên.
3. Thêm trailers `AI-Log`, `AI-Tools` và `AI-Capture` vào commit message.
4. Sau commit thành công, cập nhật checkpoint local.

Hook **không tự push**; `git push` luôn là hành động thủ công riêng. Merge/revert có record `git_operation`. Commit không có prompt mới dùng `no_new_prompt`; adapter/source/manual gap dùng `warning` nhưng không chặn commit. Record sai schema, secret hoặc PII chưa redact vẫn bị repository guard chặn.

Trước commit có thể kiểm tra candidate hoặc loại prompt ngoài scope:

```text
python scripts/ai_log/ai_log.py status
python scripts/ai_log/ai_log.py exclude --prompt-id <id> --reason non_repo
```

`status` có preview đã sanitize; `doctor --strict` chỉ báo metadata/readiness, không in prompt.

## CI history guard và index

History guard dùng `policy.json.historyEnforcement.mode=policy-presence`:

- Commit không có policy là legacy và được bỏ qua.
- Từ commit đầu tiên chứa policy, mỗi non-merge commit phải có trailer/evidence hợp lệ.
- Merge commit do nền tảng tạo được miễn trailer.
- `warning` được báo cáo nhưng không làm fail; malformed record, forbidden session content, secret hoặc PII làm fail.

Dashboard tương lai có thể dùng index local:

```text
python scripts/ai_log/ai_log.py build-index --range dev...HEAD
```

Index nằm ở `.ai-log/index.json` và không được commit. Nó ánh xạ commit trailer thành Time, Tool, Event, Prompt, Model, Member, Branch, Commit và Task Record.

## Giới hạn compliance

AI Log prompt-only không thay thế file desktop session hoặc screenshot nếu ban tổ chức bắt buộc đúng các artifact đó. Team phải xin xác nhận chấp thuận AI Log hoặc chuẩn bị gói nộp ngoài Git đã rà secret/PII; mọi mở rộng phạm vi cần Decision mới.
