# Deployment contract

> Trạng thái: backend production-disabled đã live trên Cloud Run và public smoke pass ngày 2026-07-18. Web app có public host tại `https://vngov.vercel.app`; source production mới chỉ có hiệu lực sau khi CI xanh và merge vào `main`. D-020 dùng demo gate client-side, không cần database, secret hoặc backend auth. RAG, LLM và procedure data vẫn chưa bật.
>
> Decision liên quan: D-005 (`Accepted`, scaffold), D-008 (`Accepted`, web-first), D-006 (`Accepted`, capability/deploy target), D-010 (`Proposed`, CI/release artifact), D-012 (`Accepted`, Cloud Run backend-only), D-020 (`Accepted`, demo gate client-side) và D-026 (`Accepted`, legacy RAG opt-in/offline demo image)
>
> Người phối hợp tạm thời: `TBD` theo Task Record deploy

Tài liệu này mô tả topology và gate để tạo CD thật. `backend/` có một API demo public theo D-012; `frontend/` có web UI nhưng không có secret/CD workflow trong repo. Procedure data runtime vẫn disabled.

## Đề xuất Cloud Run backend-only

D-012 thêm một đường deploy **backend-only** để tạo public demo API, không thay frontend path, CI/CD hay D-006. Candidate dùng Cloud Run và Artifact Registry cùng `asia-southeast1`, service `vngov-api`, runtime service account không có role/secret, public demo access và production-disabled mode. Trong mode này `/health` phải `degraded`, procedure catalog là `unavailable`, và mọi luồng nghiệp vụ fail-closed — không có fixture, RAG, LLM, database hay dữ liệu pháp lý.

D-006 và D-012 đã có peer confirmation. Chỉ provision khi billing/credit đúng project, IAM tối thiểu và local/container smoke pass. Runbook thao tác thủ công, candidate không traffic và rollback nằm tại [Cloud Run backend-only runbook](../runbooks/cloud-run-backend.md).

D-026 thay image default thanh demo offline (`demo_pack`, RAG/LLM/legacy RAG
disabled) de MVP chay duoc khong can secret. Cloud Run D-012 khong ke thua
procedure profile nay: lenh deploy/runbook bat buoc override
`PROCEDURE_DATA_MODE=disabled` va `LEGACY_RAG_ENABLED=false`. Phase 7 khong deploy
lai revision, khong sua traffic va khong tao secret.

## Topology đề xuất

| Hạng mục | Giá trị đề xuất | Trạng thái / điều kiện |
| --- | --- | --- |
| Standalone web app/widget | Web UI + Web Component/iframe trên public web host | Web app live tại `https://vngov.vercel.app`; widget/portal sandbox vẫn `TBD` |
| Backend/API | FastAPI trên Cloud Run theo D-012; production-disabled | Live: [`vngov-api`](https://vngov-api-j53prjslqa-as.a.run.app), public smoke pass; chưa có data/RAG/LLM |
| Database/auth | Không thuộc demo hiện tại | D-020 `Accepted`; không provision database, secret hoặc backend auth |
| Demo environment | Một public web URL + API URL | Web URL và API URL đã có; knowledge capability vẫn fail-closed |
| Preview environment | `TBD` | Chỉ tạo nếu phục vụ review nhanh hơn chi phí vận hành |
| Health/smoke | `GET /health` + key user flow | Public smoke pass cho production-disabled API ngày 2026-07-18 |
| Rollback/fallback | Last-known-good deploy + standalone/demo evidence | Live `vngov-api-00008-hez`; rollback target `vngov-api-00002-hav` |

## Live evidence — backend-only (2026-07-18)

| Hạng mục | Evidence |
| --- | --- |
| Project / region / service | `ringed-choir-424101-t4` / `asia-southeast1` / `vngov-api` |
| Public API URL | [`https://vngov-api-j53prjslqa-as.a.run.app`](https://vngov-api-j53prjslqa-as.a.run.app) |
| Revision / image | `vngov-api-00008-hez` / `sha256:fb87b48df6ec1c54d48b4b467f4579f2fd1ae69dd3b98620ee1a1160068c1b00` |
| Build evidence | Cloud Build `8ef35d72-ee00-4b7b-8f21-d8791d7b4bba`, source commit `b49ca1d31dc5c773a934d003353bc58a72355c08` |
| Runtime guard | 1 vCPU, 512 MiB, min 0/max 1, timeout 20s; procedure data/RAG/LLM disabled; no database, secrets, storage, VPC/NAT or provider key |
| Smoke | `/health` degraded/production; 6 OpenAPI routes; docs 200; disabled catalog; fail-closed workflow/error envelope; rate-limit 429 then reset |
| Cost guard | Monthly budget 1,000,000 VND, scoped to the project, thresholds 10/25/50/80/100% |

Cloud Run không cho service đầu tiên dùng `--no-traffic`. Vì runtime đã production-disabled, bootstrap chỉ mở public access sau local/container guard; direct public smoke phải pass ngay sau deploy. Từ revision thứ hai, bắt buộc candidate `--no-traffic`, smoke rồi mới chuyển traffic.

Theo D-016, `CORS_ALLOWED_ORIGINS` chỉ allowlist `https://vngov.vercel.app`. Preflight từ origin này trả 200 và origin ngoài allowlist trả 400; không dùng `*`. Backend vẫn production-disabled nên browser chỉ nhận fallback `official_review_required` cho luồng nghiệp vụ.

## Data flow và privacy khi deploy

- Dữ liệu form ở client hoặc xử lý transient; không lưu raw PII/application payload vào database hoặc log.
- Không gửi giá trị định danh cá nhân vào LLM. Adapter chỉ nhận context tối thiểu đã giảm thiểu.
- UI phải có thao tác xóa phiên; retention/cookie/telemetry mặc định là tắt hoặc `TBD` cho đến khi có Decision.
- Procedure packs, source metadata và golden cases dùng dữ liệu công khai hoặc synthetic, có source/version/checksum.
- CSP, CORS allowlist, rate limit, abuse protection và error redaction phải được chốt trước public launch.
- Portal integration thật cần sandbox/authorization, origin allowlist, versioned embed/message contract và security review; static-host embed chỉ là evidence tương thích ban đầu.

## Secret và quyền

- Demo gate không dùng secret, database, token, password hay backend auth. Mọi auth thật chỉ được xem xét lại bằng Decision mới sau hackathon/demo scope.
- Repo chỉ lưu tên biến/placeholder vô hại trong `.env.example`; không dán secret vào Issue/PR/prompt/log.
- Deploy/database token dùng quyền tối thiểu và tách environment nếu nền tảng hỗ trợ.
- Provider/model cụ thể, billing owner và quota đều `TBD`.

## Gate trước application CI/CD

1. D-006 capability/deploy target **và D-012 backend-only** được peer xác nhận ở phạm vi cần triển khai.
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
- Billing account/credit ownership, Cloud Run revision, Artifact Registry image digest và rollback target cho D-012.
- Database schema/migration/seed/reset commands chỉ là `TBD` ngoài scope demo.
- Secret names bổ sung ngoài `.env.example` hiện có chỉ là `TBD` ngoài scope demo.
- Observability, quotas, retention và chi phí.
- Rollback command/artifact và owner theo ca demo.
- Portal sandbox, authentication/authorization, origin allowlist và embed versioning cho integration thật.

Không thay `TBD` bằng giá trị suy đoán hoặc tạo tài nguyên cloud chỉ từ tài liệu này.
