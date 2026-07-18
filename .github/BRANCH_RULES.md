# Quy ước nhánh và cấu hình GitHub

Mục tiêu là giữ `main` luôn ở trạng thái demo/release ổn định, dùng `dev` để tích hợp, và để mỗi công việc có một owner/nhánh riêng. Mọi thành viên là peer ngang hàng: không có team lead hoặc merge captain cố định.

Tài liệu này áp dụng khi team đã chọn publish GitHub workflow. Trước đó, dùng Task Record/Context Pack local-first theo `TEAM_PROTOCOL.md`; Issue/PR là bản publish của record.

## Quy ước làm việc

| Nhánh | Mục đích | Cách merge |
| --- | --- | --- |
| `main` | Bản demo/release ổn định | PR release từ `dev`; cần 1 peer approval và CI xanh khi đã có CI thật |
| `dev` | Nhánh tích hợp hằng ngày | PR từ nhánh công việc; áp dụng review theo `risk` |
| `feature/<task>-<slug>` | Tính năng mới | PR vào `dev` khi publish |
| `fix/<task>-<slug>` | Sửa lỗi | PR vào `dev` khi publish |
| `chore/<task>-<slug>` | Cấu hình, tooling hoặc bảo trì | PR vào `dev` khi publish |
| `spike/<task>-<slug>` | Thử nghiệm có timebox, chưa cam kết vào MVP | PR vào `dev` hoặc handoff với kết luận |

- `<task>` là `local-YYYYMMDD-slug` trước publish hoặc số Issue sau khi team chọn publish; không cần đổi tên branch khi Issue được tạo. `<slug>` viết thường, dùng dấu gạch nối và không dấu.
- Một Task Record đang thực hiện có đúng một owner tạm thời và một nhánh đang sửa. Owner phải ghi files/API dự kiến chạm vào record trước khi sửa vùng chung.
- Luôn cập nhật `dev` trước khi tạo nhánh. Mở Draft PR sớm nếu thay đổi đụng API, schema, cấu hình, dependency hoặc UI chung.
- Mỗi PR có phạm vi nhỏ, liên kết Task Record/Issue đã publish và dùng mẫu PR. Không dùng chung một nhánh làm việc giữa người hoặc agent.
- Owner của hai Task Record cùng conflict phối hợp cách giải quyết; không người nào tự ghi đè thay đổi của peer để “cho qua build”.
- Dùng squash merge vào `dev`; xóa branch nguồn sau merge khi không còn cần điều tra.
- Không dùng nhánh hotfix riêng đẩy thẳng vào `main`. Lỗi demo khẩn cấp vẫn sửa qua `fix/*` → `dev` → PR release vào `main`, trừ khi team ghi một Decision Log được hai peer xác nhận trong scope freeze.

## Chính sách review và merge

- `risk:isolated`: tác giả có thể self-merge sau khi PR checklist hoàn tất, kiểm tra phù hợp đã xanh và thay đổi không ảnh hưởng shared contract.
- `risk:shared`: cần xác nhận rõ ràng từ ít nhất một peer; shared API, dependency, deploy hoặc demo flow phải có Decision Log liên kết.
- Sáu giờ cuối: mọi thay đổi mới cần hai peer xác nhận, bằng chứng kiểm tra và rollback/fallback rõ ràng.
- Mọi peer có cùng quyền review và merge khi điều kiện tương ứng đã đủ; không có quyền merge đặc biệt cho một người hay một agent.

## Cấu hình GitHub thủ công

Người có quyền quản trị cấu hình trong **Settings → Rules** (Rulesets) hoặc **Settings → Branches** (Branch protection), sau khi các file này đã được push:

1. Bật **Issues** và **Pull requests** trong **Settings → General → Features**.
2. Tạo rule cho `main`: yêu cầu pull request, ít nhất 1 approval, hội thoại đã resolve, chặn direct push, force-push và xóa nhánh.
3. Tạo rule cho `dev`: yêu cầu pull request, chặn direct push, force-push và xóa nhánh. Không bắt buộc approval toàn cục vì review phụ thuộc `risk` theo policy ở trên.
4. Bật tự động xóa head branch sau merge nếu giao diện GitHub cho phép.
5. **Không bật “Require status checks”** cho đến khi workflow `repository-guard` đã nằm trên branch đích và check đó đã chạy xanh ít nhất hai lần. Khi đó thêm đúng check tổng hợp `repository-guard`; các job frontend/backend/data có thể thay đổi theo diff nhưng check tổng hợp luôn tồn tại.
6. Tạo các nhãn đúng theo [LABELS.md](LABELS.md). Người tạo Issue bổ sung `priority`, `area`, `status` và `risk` trước khi bắt đầu.

## Đồng bộ có kiểm soát sau khi publish

Nguồn máy đọc được nằm tại [`repository-settings.json`](repository-settings.json). Script [`scripts/github/sync-repo-settings.ps1`](../scripts/github/sync-repo-settings.ps1) không gọi GitHub khi chạy mặc định; chỉ dùng `-Apply` sau khi có quyền Admin và yêu cầu publish rõ ràng. Chạy `-Apply -WhatIf` để xem trước, và chỉ thêm required check bằng `-RequireRepositoryGuard` sau khi workflow đã xanh trên branch đích.

GitHub không tự áp dụng điều kiện review theo label trong branch rule cơ bản. Vì vậy peer xác nhận cho `risk:shared` được ghi trong PR checklist/approval và là quy tắc team bắt buộc.

## Fallback khi không cấu hình được protection rule

Nếu thiếu quyền quản trị hoặc gói GitHub không hỗ trợ rule mong muốn, áp dụng kỷ luật tương đương: không ai push trực tiếp `main`/`dev`; mọi thay đổi có Issue và PR; self-merge chỉ dành cho `risk:isolated`; `risk:shared` cần peer xác nhận; `main` luôn cần một peer approval. Ghi rõ mọi ngoại lệ trong PR và Decision Log, không trao quyền merge cố định cho bất kỳ người nào.
