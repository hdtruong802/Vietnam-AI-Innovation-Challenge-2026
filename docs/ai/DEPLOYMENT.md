# Deployment contract

> Trạng thái: D-005 scaffold đã có; D-010 đề xuất application CI và provider-neutral release artifact. Live deploy vẫn `Proposed — chưa provision`.
>
> Decision liên quan: D-005 (`Accepted`, scaffold), D-008 (`Accepted`, web-first), D-006 (`Proposed`, capability/deploy target) và D-010 (`Proposed`, CI/release artifact)
>
> Người phối hợp tạm thời: `TBD` theo Task Record deploy

Tài liệu này mô tả topology đề xuất và gate để tạo CD thật. `frontend/` và `backend/` đã có scaffold theo D-005, CI có thể sinh release candidate theo D-010, nhưng chưa có cloud project, public URL, environment, secret hoặc live deploy workflow.

## Topology đề xuất

| Hạng mục | Giá trị đề xuất | Trạng thái / điều kiện |
| --- | --- | --- |
| Standalone web app/widget | Web UI + Web Component/iframe trên public web host | D-005 có frontend scaffold; widget, host/domain vẫn D-006 `Proposed` |
| Backend/API | FastAPI trên hosting theo Task Record deploy | D-005 có backend scaffold; host/runtime production vẫn D-006 `Proposed` |
| Database/vector | Neon PostgreSQL + pgvector | D-006 `Proposed`; schema/migration `TBD` |
| Demo environment | Một public web URL + API URL | Bắt buộc theo đề; hiện chưa tồn tại |
| Preview environment | `TBD` | Chỉ tạo nếu phục vụ review nhanh hơn chi phí vận hành |
| Health/smoke | `GET /health` + key user flow | Route health có trong scaffold; public smoke chưa tồn tại |
| Rollback/fallback | Last-known-good deploy + standalone/demo evidence | Chốt trong Task Record deploy |

## Data flow và privacy khi deploy

- Dữ liệu form ở client hoặc xử lý transient; không lưu raw PII/application payload vào database hoặc log.
- Không gửi giá trị định danh cá nhân vào LLM. Adapter chỉ nhận context tối thiểu đã giảm thiểu.
- UI phải có thao tác xóa phiên; retention/cookie/telemetry mặc định là tắt hoặc `TBD` cho đến khi có Decision.
- Procedure packs, source metadata và golden cases dùng dữ liệu công khai hoặc synthetic, có source/version/checksum.
- CSP, CORS allowlist, rate limit, abuse protection và error redaction phải được chốt trước public launch.
- Portal integration thật cần sandbox/authorization, origin allowlist, versioned embed/message contract và security review; static-host embed chỉ là evidence tương thích ban đầu.

## Secret và quyền

- Chỉ đưa giá trị thật vào secret store của Vercel/Render/Neon sau khi D-006 được Accepted và Task Record deploy được claim.
- Repo chỉ lưu tên biến/placeholder vô hại trong `.env.example`; không dán secret vào Issue/PR/prompt/log.
- Deploy/database token dùng quyền tối thiểu và tách environment nếu nền tảng hỗ trợ.
- Provider/model cụ thể, billing owner và quota đều `TBD`.

## Gate trước application CI/CD

1. D-006 capability/deploy target được peer xác nhận ở phạm vi cần triển khai.
2. Scaffold hiện có chạy local; install/lint/test/build commands có evidence trên worktree sạch.
3. API/schema/rule tests tối thiểu chạy trong application CI; trước public deploy phải mở rộng thành ít nhất 30 golden cases theo D-006.
4. Hosting projects, secret names, environment ownership, CORS/CSP và rollback được ghi trong Task Record/Decision.
5. Preview/demo deploy qua CI, `GET /health` và end-to-end smoke pass.
6. Widget được nhúng trên một static host độc lập, kiểm portal-container/iframe/CSP/CORS; fallback standalone web app trong Demo runbook đã rehearsal.

`repository-guard` theo D-010 có thể chạy application lint/typecheck/build/API test theo changed scope; nó vẫn không chứng minh deploy thành công. Raw `data/**` không bị content-scan trong fast gate; chỉ có metadata guard, còn data release chất lượng thuộc D-006.

## Release candidate provider-neutral

- Push `dev` có thay đổi frontend/backend/data sẽ tạo artifact frontend standalone, backend source và `release-manifest.json` gồm commit, tree và SHA-256.
- Workflow thủ công trên `main` chỉ preserve một `production-candidate` khi confirmation, source tree và checksum đều hợp lệ.
- Artifact là evidence build, **không phải public URL hoặc deployment**. Không có environment, provider credential, database, hosting project hay secret được tạo từ workflow này.
- Khi team chọn provider, adapter phải deploy đúng candidate đã verify, ghi URL/smoke/rollback evidence và fail closed nếu thiếu secret hoặc smoke check.

## Hình dạng CD sau khi được chấp thuận

1. Install/lint/test/build chạy xanh trên đúng commit.
2. Artifact đã kiểm chứng được deploy; không build một source khác ngoài CI contract.
3. Workflow không in secret và ghi environment, commit, URL, smoke result, rollback target.
4. Production/demo deploy dùng explicit approval hoặc release branch theo Decision; sáu giờ cuối cần hai peer.
5. Deploy/provider lỗi thì dùng fallback đã rehearsal, không sửa nóng ngoài Task Record.

## Các giá trị còn TBD

- Runtime versions đã kiểm chứng và install/build/start commands có evidence.
- Project IDs, regions, domains và public URLs.
- Database schema/migration/seed/reset commands.
- Secret names bổ sung ngoài `.env.example` hiện có.
- Observability, quotas, retention và chi phí.
- Rollback command/artifact và owner theo ca demo.
- Portal sandbox, authentication/authorization, origin allowlist và embed versioning cho integration thật.

Không thay `TBD` bằng giá trị suy đoán hoặc tạo tài nguyên cloud chỉ từ tài liệu này.
