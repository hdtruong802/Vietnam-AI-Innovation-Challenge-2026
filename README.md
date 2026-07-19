# VNGov — Trợ lý AI cho thủ tục hành chính

VNGov là sản phẩm demo cho Vietnam AI Innovation Challenge 2026. Ứng dụng giúp người dân mô tả nhu cầu bằng ngôn ngữ tự nhiên, chuẩn bị hồ sơ theo từng bước và kiểm tra sơ bộ thông tin trước khi nộp.

> Đây là sản phẩm thử nghiệm cho hackathon, không phải Cổng Dịch vụ công Quốc gia và không thay thế quyết định của cơ quan có thẩm quyền.

## Truy cập nhanh

- Web demo: [vngov.vercel.app](https://vngov.vercel.app/)
- API demo: [vngov-api-j53prjslqa-as.a.run.app](https://vngov-api-j53prjslqa-as.a.run.app/)
- API documentation: [Swagger UI](https://vngov-api-j53prjslqa-as.a.run.app/docs)

## Vấn đề và giải pháp

Người dân thường không rõ mình phải thực hiện thủ tục nào, chuẩn bị giấy tờ gì hoặc có điền sai thông tin trước khi nộp hay không. VNGov biến hành trình này thành một luồng rõ ràng:

```text
Nhu cầu tự nhiên
  → nhận diện thủ tục và hỏi làm rõ
  → checklist có nguồn tham chiếu
  → biểu mẫu theo trường hợp
  → tự điền từ mô tả tự nhiên
  → tiền kiểm theo quy tắc
  → hướng dẫn kênh chính thức khi thiếu căn cứ
```

## Phạm vi demo

Ba thủ tục MVP hiện tại là:

1. Đăng ký khai sinh.
2. Đăng ký thường trú.
3. Đăng ký thành lập hộ kinh doanh.

Mỗi luồng có checklist, biểu mẫu demo, kiểm tra các trường bắt buộc/định dạng/xung đột cơ bản và trạng thái tin cậy. Dữ liệu procedure pack trong demo là dữ liệu được tuyển chọn cho phạm vi hackathon; người dùng vẫn phải đối chiếu nguồn chính thức và nhận xác nhận của cơ quan tiếp nhận.

## Kiến trúc ở mức cao

```text
Next.js web app
        │ HTTPS
        ▼
FastAPI orchestration API
  ├─ procedure/demo-pack adapter
  ├─ deterministic pre-check rules
  ├─ retrieval + citation/trust policy
  └─ LLM gateway cho hội thoại và trích xuất có kiểm soát
```

Backend luôn trả trust state cùng nguồn/version khi có căn cứ. Khi thiếu evidence, nguồn mâu thuẫn hoặc chức năng chưa sẵn sàng, hệ thống phải trả `need_more_information` hoặc `official_review_required` thay vì tự khẳng định hồ sơ hợp lệ.

## Chạy local

### Yêu cầu

- Node.js 22+ và npm.
- Python 3.13+.
- Git.

### Backend

Tạo `backend/.env` từ [`.env.example`](.env.example), sau đó dùng cấu hình demo an toàn:

```env
APP_ENV=development
PROCEDURE_DATA_MODE=demo_pack
RAG_MODE=disabled
LLM_MODE=disabled
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

Chạy API:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.lock.txt
uvicorn app.main:app --reload --port 8000
```

API local sẽ có tại `http://localhost:8000`; Swagger UI ở `http://localhost:8000/docs`.

### Frontend

Tạo `frontend/.env.local` từ [frontend/.env.example](frontend/.env.example):

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Sau đó chạy:

```powershell
cd frontend
npm ci
npm run dev
```

Mở `http://localhost:3000`. Chế độ **Vào demo ngay** chỉ tạo session trong tab trình duyệt; không phải cơ chế đăng nhập hoặc lưu tài khoản thật.

## API chính

| Endpoint | Mục đích |
| --- | --- |
| `GET /health` | Kiểm tra trạng thái runtime và capability. |
| `GET /v1/procedures` | Danh sách procedure pack đang có. |
| `POST /v1/procedures/recommend` | Gợi ý thủ tục từ nhu cầu tự nhiên. |
| `POST /v1/intake/turn` | Một lượt hội thoại/hỏi làm rõ. |
| `POST /v1/procedures/{procedure_id}/checklist` | Checklist và form schema theo thủ tục. |
| `POST /v1/applications/prefill` | Đề xuất giá trị biểu mẫu từ mô tả tự nhiên. |
| `POST /v1/applications/validate` | Tiền kiểm deterministic trước khi nộp. |

Xem request/response chính xác trong [OpenAPI](https://vngov-api-j53prjslqa-as.a.run.app/openapi.json) hoặc Swagger UI.

## Kiểm tra chất lượng

```powershell
# Quy ước và tài liệu repository
python scripts/ci/validate_repo.py

# Backend
cd backend
python -m pytest -q
black --check .
flake8 .

# Frontend
cd frontend
npm run test
npm run lint
npm run typecheck
npm run build
```

## Bảo mật và dữ liệu

- Không commit `.env`, API key, token, dữ liệu người thật hoặc hồ sơ đã điền.
- Chỉ dùng dữ liệu tổng hợp khi demo/kiểm thử.
- Không gửi thông tin định danh thật vào mô tả tự do hoặc môi trường demo.
- Kết quả tiền kiểm chỉ hỗ trợ chuẩn bị hồ sơ; không phải quyết định tiếp nhận hay phê duyệt.

Chi tiết xem [Secrets & Data policy](docs/ai/SECRETS_AND_DATA.md) và [Deployment contract](docs/ai/DEPLOYMENT.md).

## Làm việc trong team

Tài liệu vận hành và kiến trúc không nằm trong README này:

- [Project context](docs/ai/PROJECT_CONTEXT.md)
- [Architecture](docs/ai/ARCHITECTURE.md)
- [Decision log](docs/ai/DECISIONS.md)
- [Team protocol](docs/ai/TEAM_PROTOCOL.md)
- [Hướng dẫn đóng góp cho coding agents](AGENTS.md)

Mọi thay đổi code/API/data/deploy dùng Task Record hoặc Context Pack, làm trong branch/worktree riêng và qua `dev` trước khi vào `main`. Xem [cẩm nang team](team_docs/TEAM_BOOTSTRAP_OVERVIEW.md) để onboard nhanh.
