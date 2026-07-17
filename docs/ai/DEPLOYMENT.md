# Deployment contract

> Trạng thái: `Blocked — chưa chốt stack và hosting`
>
> Decision/Issue liên quan: `TBD`
> Người phối hợp tạm thời: `TBD`

Tài liệu này là điều kiện để thêm CD thật. Nó không tạo environment, secret, deploy workflow hoặc URL từ xa. Mọi peer có thể cập nhật và đề xuất quyết định; người phối hợp tạm thời không có quyền ưu tiên ngoài Issue triển khai hiện tại.

## Quyết định cần chốt trước khi tạo CD

| Hạng mục | Giá trị đã chốt | Decision/Issue | Ghi chú |
| --- | --- | --- | --- |
| Stack / runtime | `TBD` | `TBD` | Phải chạy được local trước. |
| Hosting target | `TBD` | `TBD` | Ví dụ: Vercel, Render, Cloud Run hoặc VPS. |
| Environment preview | `TBD` | `TBD` | Chỉ tạo nếu phục vụ review/demo. |
| Environment production/demo | `TBD` | `TBD` | URL dùng khi trình diễn hoặc nộp bài. |
| Build command | `TBD` | `TBD` | Không ghi lệnh chưa chạy. |
| Health/smoke check | `TBD` | `TBD` | Endpoint hoặc thao tác có thể kiểm chứng. |
| Rollback/fallback | `TBD` | `TBD` | Commit, artifact, preview hoặc demo fallback. |

## Secrets và quyền

- Secret chỉ được đưa vào GitHub Environments/Secrets hoặc secret store của nền tảng sau khi hosting target được chốt.
- Không commit secret, không dán secret vào Issue/PR/agent prompt, và chỉ liệt kê **tên biến** trong `.env.example`.
- Deploy token phải có quyền tối thiểu cần thiết; không tái dùng token cá nhân có quyền rộng nếu nền tảng hỗ trợ service token.
- Mọi thay đổi provider, domain, data egress hoặc deploy flow là `risk:shared` và cần Decision Log cùng peer confirmation.

## Hình dạng CD bắt buộc sau khi chốt target

1. CI ứng dụng (install, lint, test, build) chạy xanh trước deploy.
2. Deploy preview chỉ nhận artifact/commit đã qua CI; deploy production/demo dùng `workflow_dispatch` hoặc merge vào nhánh release đã được team chấp thuận.
3. Workflow ghi rõ environment, URL kết quả, smoke check và rollback target; không in secret.
4. Nếu deploy hoặc provider lỗi, demo phải chuyển sang fallback trong `DEMO.md` thay vì sửa nóng không có peer confirmation.

## Checklist kích hoạt CD

- [ ] Project Context và Architecture có stack, lệnh build/test và runtime đã kiểm chứng.
- [ ] Một Decision Log chốt hosting, environments, rollback và owner tạm thời của deploy task.
- [ ] CI ứng dụng đã chạy xanh trên PR.
- [ ] Secret names đã có trong `.env.example`; giá trị thật chỉ có trong secret store.
- [ ] Có smoke check và fallback demo đã diễn tập.
- [ ] Hai peers xác nhận nếu việc bật CD diễn ra trong sáu giờ cuối hackathon.
