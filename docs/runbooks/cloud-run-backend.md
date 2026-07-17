# Runbook — Cloud Run backend-only

> Trạng thái: D-006 và D-012 đã được `hdtruong802` (user) peer xác nhận ngày 2026-07-18. Chỉ chạy khi billing/credit, IAM và local/container smoke đạt. Runbook này không tạo CI/CD, không deploy frontend và không bật data/RAG/LLM.

## Phạm vi đã chốt

| Hạng mục | Giá trị |
| --- | --- |
| Region | `asia-southeast1` |
| Artifact Registry | Docker repository `vngov-backend`, immutable tags, cùng region |
| Cloud Run service | `vngov-api` |
| Image | `asia-southeast1-docker.pkg.dev/<project>/vngov-backend/api:<full-commit-sha>`; deploy bằng digest |
| Runtime | 1 vCPU, 512 MiB, request-based CPU, `min-instances=0`, `max-instances=1`, timeout 20 giây |
| Access | `--allow-unauthenticated` cho demo API đã duyệt |
| Runtime service account | `vngov-api-runtime`; user-managed, không gán role hay secret |
| Production data/AI | `PROCEDURE_DATA_MODE=disabled`, `RAG_MODE=disabled`, `LLM_MODE=disabled` |
| Không thuộc task | frontend, database, vector store, storage, Secret Manager, Vertex AI, VPC connector, NAT, workflow CD |

Cloud Run yêu cầu container lắng nghe đúng biến `PORT`; Dockerfile trong repo dùng biến này. Artifact Registry dùng immutable tags và image digest để không triển khai nhầm image. Xem [Cloud Run container contract](https://docs.cloud.google.com/run/docs/container-contract), [Cloud Run deploy](https://docs.cloud.google.com/run/docs/deploying) và [Artifact Registry Docker repositories](https://cloud.google.com/artifact-registry/docs/repositories/create-repos).

## Gate bắt buộc trước cloud mutation

1. D-006 và D-012 có peer confirmation; nếu Decision bị thay thế hoặc scope đổi, **dừng** và review lại.
2. Người deploy xác minh project hiện trong `gcloud` là project của team, billing/credit đúng tài khoản và không có hạn chế tổ chức chặn Cloud Run/Cloud Build/Artifact Registry.
3. Local lint/test/container smoke pass với production-disabled. Nếu fixture có thể chạy ở production, **dừng**.
4. Deployer chỉ nhận role tối thiểu theo thời gian triển khai: Cloud Run Admin, Service Account User, Cloud Build Editor và Artifact Registry Administrator cho lần tạo repository. Runtime service account không nhận các role đó.
5. Không nhập key, database URL, AI provider, raw PII, hồ sơ mẫu thật hay form payload vào biến môi trường/image/log.

## 1. Local preflight (không chạm cloud)

Từ repository root:

```powershell
Push-Location backend
python -m pytest -q
python -m flake8 app tests main.py
Pop-Location

docker build --pull --tag vngov-api:local backend
docker run --rm --volume "${PWD}\backend:/src:ro" --workdir /src --entrypoint python vngov-api:local `
  -m black --check app tests main.py
docker run --rm --entrypoint id vngov-api:local
$imageEnv = docker image inspect --format '{{json .Config.Env}}' vngov-api:local
if ($imageEnv -match 'AI_API_KEY|AI_PROVIDER|DATABASE_URL') { throw 'unexpected sensitive runtime variable name' }
$runtimeContents = docker run --rm --entrypoint sh vngov-api:local -c 'test ! -e /app/.env && test ! -e /app/main.py && test ! -d /app/tests && printf clean'
if ($runtimeContents -ne 'clean') { throw 'runtime image contains excluded source' }
docker run --rm --name vngov-api-smoke -p 8080:8080 `
  -e APP_ENV=production `
  -e PROCEDURE_DATA_MODE=disabled `
  -e RAG_MODE=disabled `
  -e LLM_MODE=disabled `
  -e RATE_LIMIT_ENABLED=true `
  -e RATE_LIMIT_REQUESTS=60 `
  -e RATE_LIMIT_WINDOW_SECONDS=60 `
  -e CORS_ALLOWED_ORIGINS= `
  vngov-api:local
```

Ở PowerShell khác, smoke local:

```powershell
$base = 'http://127.0.0.1:8080'
$health = Invoke-RestMethod "$base/health"
if ($health.status -ne 'degraded' -or $health.environment -ne 'production') { throw 'health must be production/degraded' }
if ($health.capabilities.procedure_data -ne 'disabled' -or $health.capabilities.rag -ne 'disabled' -or $health.capabilities.llm -ne 'disabled') { throw 'all runtime capabilities must be disabled' }

$catalog = Invoke-RestMethod "$base/v1/procedures"
if (($catalog | Where-Object { $_.review_status -ne 'unavailable' -or $_.fixture_mode }).Count -gt 0) { throw 'catalog must only expose unavailable, non-fixture summaries' }

$checklist = Invoke-RestMethod -Method Post -ContentType 'application/json' -Body '{"clarification_answers":{}}' "$base/v1/procedures/dang-ky-khai-sinh/checklist"
if ($checklist.trust_state -ne 'official_review_required' -or $checklist.fixture_mode) { throw 'checklist must fail closed' }

$validation = Invoke-RestMethod -Method Post -ContentType 'application/json' -Body '{"procedure_id":"dang-ky-khai-sinh","form_data":{}}' "$base/v1/applications/validate"
if ($validation.trust_state -ne 'official_review_required' -or $null -ne $validation.verdict) { throw 'validation must fail closed' }

$intake = Invoke-RestMethod -Method Post -ContentType 'application/json' -Body '{"session_id":"production-disabled-smoke","message":"Tôi muốn đăng ký khai sinh"}' "$base/v1/intake/turn"
if ($intake.trust_state -ne 'need_more_information' -or $intake.fixture_mode -or $null -ne $intake.detected_procedure_id -or $null -ne $intake.procedure) { throw 'intake must not expose a fixture procedure' }

docker stop vngov-api-smoke
```

Kiểm tra thủ công thêm: `/openapi.json` có đúng sáu route public, `/docs` mở được, error response có `X-Request-ID`, và lần request thứ 61 tới `/v1/*` trong cùng cửa sổ 60 giây nhận `429`. Rate limit này chỉ có hiệu lực trong một instance, đúng phạm vi demo.

## 2. Xác minh project và billing (sau gate)

```powershell
$ProjectId = (gcloud config get-value project).Trim()
$Region = 'asia-southeast1'
$Repository = 'vngov-backend'
$Service = 'vngov-api'
$RuntimeServiceAccount = 'vngov-api-runtime'
$BuildServiceAccount = (gcloud builds get-default-service-account --project $ProjectId --format='value(serviceAccountEmail)').Trim()

gcloud auth list
gcloud projects describe $ProjectId
gcloud billing projects describe $ProjectId
gcloud services list --enabled --project $ProjectId --filter 'config.name:(run.googleapis.com OR cloudbuild.googleapis.com OR artifactregistry.googleapis.com)'
if (-not $BuildServiceAccount) { throw 'Cloud Build default service account is unresolved' }
Write-Output "Cloud Build default service account: $BuildServiceAccount"
```

Xác minh thủ công trong Cloud Billing rằng credit/billing account thuộc team trước khi enable API. Đây là điều kiện chặn, không thể suy ra chỉ từ CLI.

Tạo budget **cảnh báo**, không phải hard cap, sau khi billing account đã được peer xác nhận. Thay `<billing-account-id>` bằng ID đã review; currency phải khớp billing account:

```powershell
gcloud billing budgets create `
  --billing-account='<billing-account-id>' `
  --display-name='VNGov demo API — 1,000,000 VND alert budget' `
  --budget-amount='1000000VND' `
  --calendar-period=month `
  --threshold-rule=percent=0.10 `
  --threshold-rule=percent=0.25 `
  --threshold-rule=percent=0.50 `
  --threshold-rule=percent=0.80 `
  --threshold-rule=percent=1.00 `
  --filter-projects="projects/$ProjectId"
```

Thiết lập recipient/notification channel theo team trong Cloud Console hoặc cờ notification của CLI đã được review. Budget chỉ gửi cảnh báo; nó không chặn charge tự động. Tham khảo [Cloud Billing budgets](https://docs.cloud.google.com/billing/docs/how-to/budgets) và [gcloud billing budgets create](https://docs.cloud.google.com/sdk/gcloud/reference/billing/budgets/create).

## 3. Provision tối thiểu (sau gate)

```powershell
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --project $ProjectId

gcloud iam service-accounts create $RuntimeServiceAccount `
  --project $ProjectId `
  --display-name 'VNGov API runtime (no roles, no secrets)'

gcloud artifacts repositories create $Repository `
  --project $ProjectId `
  --repository-format=docker `
  --location=$Region `
  --immutable-tags `
  --description='VNGov backend demo images'
```

Trước build đầu tiên, kiểm tra effective access của `$BuildServiceAccount` trên repository. Cloud Build default service account cùng project thường đã có quyền upload/download Artifact Registry; nếu org policy hoặc service-account policy làm nó thiếu quyền, chỉ cấp `roles/artifactregistry.writer` **trên repository này** cho build service account — không cấp cho `$RuntimeServiceAccount` và không cấp role project-wide:

```powershell
gcloud artifacts repositories get-iam-policy $Repository `
  --project $ProjectId `
  --location $Region `
  --flatten='bindings[].members' `
  --filter="bindings.members:serviceAccount:$BuildServiceAccount" `
  --format='table(bindings.role,bindings.members)'

# Chỉ chạy sau khi xác minh default build SA thiếu quyền Writer hiệu lực.
gcloud artifacts repositories add-iam-policy-binding $Repository `
  --project $ProjectId `
  --location $Region `
  --member="serviceAccount:$BuildServiceAccount" `
  --role='roles/artifactregistry.writer'
```

Không tạo Secret Manager, Cloud SQL, application Cloud Storage, Vertex AI, vector DB, VPC connector hay NAT. `gcloud builds submit` có thể dùng vùng staging/log do Cloud Build quản lý; build context đó chỉ được chứa `backend/` đã qua ignore rules và không phải storage runtime của ứng dụng. Không gán role vào `$RuntimeServiceAccount`; gán `iam.serviceAccountUser` cho deployer theo thời gian cần thiết để attach nó.

## 4. Build image immutable và deploy candidate

```powershell
$CommitSha = (git rev-parse --verify HEAD).Trim()
$ImageTag = "$Region-docker.pkg.dev/$ProjectId/$Repository/api:$CommitSha"

gcloud builds submit backend --project $ProjectId --tag $ImageTag

$Digest = (gcloud artifacts docker images describe $ImageTag --project $ProjectId --format='value(image_summary.digest)').Trim()
if (-not $Digest.StartsWith('sha256:')) { throw 'Artifact Registry did not return an image digest' }
$ImageDigest = "$Region-docker.pkg.dev/$ProjectId/$Repository/api@$Digest"

gcloud run deploy $Service `
  --project $ProjectId `
  --region $Region `
  --image $ImageDigest `
  --service-account "$RuntimeServiceAccount@$ProjectId.iam.gserviceaccount.com" `
  --allow-unauthenticated `
  --no-traffic `
  --tag candidate `
  --port 8080 `
  --cpu 1 `
  --memory 512Mi `
  --cpu-throttling `
  --min-instances 0 `
  --max-instances 1 `
  --timeout 20s `
  --set-env-vars '^@^APP_ENV=production@PROCEDURE_DATA_MODE=disabled@RAG_MODE=disabled@LLM_MODE=disabled@RATE_LIMIT_ENABLED=true@RATE_LIMIT_REQUESTS=60@RATE_LIMIT_WINDOW_SECONDS=60@CORS_ALLOWED_ORIGINS='
```

Lệnh trên áp dụng khi service đã có stable revision. `--no-traffic` bảo vệ stable revision. Lưu `$ImageDigest`, revision candidate và timestamp vào Context Pack/handoff; không ghi token hoặc raw request body.

### Bootstrap service đầu tiên

Cloud Run không hỗ trợ `--no-traffic` khi tạo service đầu tiên. Để không mở public API trước application smoke, tạo revision đầu tiên ở chế độ private/authenticated-only; chỉ mở `allUsers` sau khi smoke qua. Thay block deploy ở trên bằng:

```powershell
gcloud run deploy $Service `
  --project $ProjectId `
  --region $Region `
  --image $ImageDigest `
  --service-account "$RuntimeServiceAccount@$ProjectId.iam.gserviceaccount.com" `
  --no-allow-unauthenticated `
  --tag candidate `
  --port 8080 `
  --cpu 1 `
  --memory 512Mi `
  --cpu-throttling `
  --min-instances 0 `
  --max-instances 1 `
  --timeout 20s `
  --set-env-vars '^@^APP_ENV=production@PROCEDURE_DATA_MODE=disabled@RAG_MODE=disabled@LLM_MODE=disabled@RATE_LIMIT_ENABLED=true@RATE_LIMIT_REQUESTS=60@RATE_LIMIT_WINDOW_SECONDS=60@CORS_ALLOWED_ORIGINS='
```

Ngay sau deploy, xác minh mapping tag/traffic thay vì giả định deploy đầu tiên đã có stable traffic. Với service mới, candidate nhận traffic nhưng service vẫn private; với service đã có revision stable, candidate phải có `percent: 0`:

```powershell
gcloud run services describe $Service --project $ProjectId --region $Region --format='yaml(status.latestReadyRevisionName,status.traffic)'
# Lấy revisionName và URL nằm dưới traffic tag `candidate` từ output trên.
$CandidateRevision = '<candidate-revision-name>'
$CandidateUrl = 'https://<candidate-tag-url>'
if ($CandidateRevision -eq '<candidate-revision-name>' -or $CandidateUrl -eq 'https://<candidate-tag-url>') { throw 'capture candidate revision and tagged URL before smoke' }
```

## 5. Candidate smoke, traffic, public access và rollback

Với service đã có stable revision, dùng URL candidate public đã capture ở bước 4:

```powershell
Invoke-WebRequest "$CandidateUrl/health" -UseBasicParsing
Invoke-WebRequest "$CandidateUrl/openapi.json" -UseBasicParsing
Invoke-WebRequest "$CandidateUrl/docs" -UseBasicParsing
```

Với bootstrap service đầu tiên private, lấy ID token cho service URL rồi chạy đúng các smoke production-disabled ở bước 1 với header sau; không log token:

```powershell
$ServiceUrl = (gcloud run services describe $Service --project $ProjectId --region $Region --format='value(status.url)').Trim()
$IdentityToken = (gcloud auth print-identity-token --audiences=$ServiceUrl).Trim()
$AuthHeaders = @{ Authorization = "Bearer $IdentityToken" }
Invoke-WebRequest "$ServiceUrl/health" -Headers $AuthHeaders -UseBasicParsing
Invoke-WebRequest "$ServiceUrl/openapi.json" -Headers $AuthHeaders -UseBasicParsing
Invoke-WebRequest "$ServiceUrl/docs" -Headers $AuthHeaders -UseBasicParsing
```

Chỉ sau smoke bootstrap pass, mở public demo access:

```powershell
gcloud run services add-iam-policy-binding $Service --project $ProjectId --region $Region `
  --member='allUsers' --role='roles/run.invoker'
gcloud run services describe $Service --project $ProjectId --region $Region --format='value(status.url)'
```

Với deploy sau khi service đã có stable revision, chuyển 100% traffic sau candidate smoke:

```powershell
gcloud run services update-traffic $Service --project $ProjectId --region $Region --to-revisions "$CandidateRevision=100"
gcloud run services describe $Service --project $ProjectId --region $Region --format='value(status.url)'
```

Nếu smoke candidate/5xx fail, không chuyển traffic hoặc không mở public access. Với deploy sau đó, rollback là chuyển traffic về revision stable trước:

```powershell
gcloud run revisions list --service $Service --project $ProjectId --region $Region
gcloud run services update-traffic $Service --project $ProjectId --region $Region --to-revisions '<previous-stable-revision>=100'
```

Lần deploy đầu thất bại không có rollback revision: giữ service private hoặc xóa service theo owner quyết định, dùng backend local làm fallback và ghi failure evidence. Public access ở đây chỉ là demo API theo lựa chọn đã chốt, không phải integration production với Cổng DVCQG. Xem [Cloud Run public access](https://docs.cloud.google.com/run/docs/authenticating/public).
