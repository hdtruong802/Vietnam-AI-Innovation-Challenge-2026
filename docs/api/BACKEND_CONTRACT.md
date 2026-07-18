# Backend API contract — AI Procedure Copilot

> Trạng thái: backend integration foundation. Đây là contract để FE, data, RAG và AI adapter tích hợp; không xác nhận Procedure Pack pháp lý, RAG, external model hay deploy đã hoàn thành.

## Nguyên tắc

- API giữ prefix `/v1` và ba procedure ID: `dang-ky-khai-sinh`, `dang-ky-thuong-tru`, `dang-ky-ho-kinh-doanh`.
- Mọi response có thể được hiểu là hướng dẫn mang `trust_state`, `procedure_version`, `source_refs`, `last_verified_at`, `review_gate` và `fixture_mode`.
- Chỉ pack `approved` có source, checksum và metadata hiệu lực mới có thể trả `verified_guidance`.
- `PROCEDURE_DATA_MODE=fixture` chỉ phục vụ local integration. Mọi response fixture trả `official_review_required`; không dùng cho hướng dẫn thật hoặc production.
- Runtime production demo dùng `PROCEDURE_DATA_MODE=disabled`, `RAG_MODE=disabled` và `LLM_MODE=disabled`. `/health` trả `degraded`; catalog chỉ là ba summary `unavailable`; checklist/validation không được trả fixture, rule finding hoặc `verified_guidance`.
- Backend không lưu transcript/form draft. `SessionContext` là state có cấu trúc do client gửi lại, không chứa full chat history.

## Routes

| Method | Path | Mục đích |
| --- | --- | --- |
| `GET` | `/health` | Liveness, version và trạng thái capability. |
| `GET` | `/v1/procedures` | Procedure summary/version/readiness; khi runtime disabled chỉ trả catalog `unavailable`. |
| `POST` | `/v1/procedures/recommend` | Nhận diện thủ tục từ `need_text`. |
| `POST` | `/v1/intake/turn` | Một lượt intake stateless. |
| `POST` | `/v1/procedures/{procedure_id}/checklist` | Checklist, steps và form schema. |
| `POST` | `/v1/applications/validate` | Deterministic pre-check. |
| `GET`, `POST` | `/v1/rag/search` | Tìm evidence approved/deterministic cho demo; không có hit thì fail closed. |
| `GET`, `POST` | `/v1/rag/answer` | Diễn giải grounded từ evidence; thiếu evidence/key hoặc provider lỗi thì `official_review_required`. |

`POST /v1/intake/turn` nhận `session_id`, `message` tối đa 500 ký tự và optional `session_context`. Không gửi `messages[]` hay transcript đầy đủ.

`POST /v1/procedures/{procedure_id}/checklist` lấy ID từ path; body chỉ gồm `clarification_answers` và optional `procedure_version`.

`POST /v1/applications/validate` nhận `procedure_id`, optional `procedure_version` và `form_data`. `verdict` chỉ là `pass_preliminary`, `needs_fix` hoặc `null` khi `trust_state=official_review_required`.

## Prototype flow read models (D-018)

Frontend dùng sáu route guided-intake/pre-check và hai route RAG additive. Các route RAG chỉ trả evidence hoặc diễn giải grounded có citation; chúng không thay deterministic validation, trust state hay official review.

### Intake turn

`POST /v1/intake/turn` hỗ trợ bốn `turn_type`:

- `free_text` (mặc định): nhận diện thủ tục từ `message`.
- `procedure_select`: cần `selected_procedure_id` để phản ánh lựa chọn từ ba thẻ MVP.
- `clarification_answer`: cần `{ question_id, value }`; `question_id` phải nằm trong `session_context.pending_question_ids`.
- `review_acknowledgement`: cần `review_gate_acknowledgement` (`U1`, `U2` hoặc `U3`).

Mọi turn vẫn cần `session_id` và `message`. Đây là định danh/request text ngắn trong lần gọi hiện tại, không phải transcript để backend lưu.

`IntakeResponse` có thể trả thêm:

- `journey`: đúng năm bước `procedure`, `personal-information`, `case-information`, `documents`, `precheck`, mỗi bước có `complete`, `current` hoặc `upcoming`.
- `procedure_card`: `authority`, `processing_time`, `fee` chỉ có khi pack được `verified_guidance`.
- `confirmed_facts`: các clarification answer có `question_id` được pack khai báo; client đã sở hữu state này và không nên coi response là nơi lưu draft.
- `next_action`: action UI tiếp theo, ví dụ `answer_clarifications`, `confirm_procedure`, `review_checklist` hoặc `official_review_required`.
- `proposed_session_context`: structured state để browser giữ và gửi lại. Nó chỉ gồm procedure/version, clarification answers, pending question IDs, document-review IDs và review-gate acknowledgements.

### Checklist và pre-check

`ChecklistRequest` và `ValidationRequest` nhận optional `session_context` để tiến trình năm bước nhất quán. `ChecklistResponse` có thể trả `form_sections`, `procedure_card`, `journey`, `next_action`; `ValidationResponse` có thêm `journey`, `next_action`, `proposed_session_context`.

`form_data` chỉ được dùng trong request validation hiện tại. Backend không copy nó vào `SessionContext`, audit log hoặc response state. Verdict/finding vẫn đến duy nhất từ deterministic Rule Engine; LLM chỉ có thể diễn giải finding đã tồn tại theo D-011.

### Input safety and trust boundary

- Mọi request DTO public dùng `extra=forbid`; field ngoài contract trả `422` với error envelope.
- Chỉ pack approved/current có evidence mới hiển thị checklist, form schema, procedure card hoặc `verified_guidance`.
- Fixture và disabled runtime vẫn trả trust state fail-closed; consumer không được dùng để hiển thị hướng dẫn thủ tục thật.
- `SessionContext` là browser-owned state, không chứa full chat history, raw form draft, upload hay credential.

## Error và fallback

Mọi lỗi ứng dụng trả:

```json
{
  "error": {
    "code": "procedure_not_found",
    "message": "Thông báo an toàn cho người dùng",
    "request_id": "opaque-id",
    "details": []
  }
}
```

- `404`: ngoài ba MVP.
- `409`: version conflict.
- `422`: request sai schema hoặc vượt size limit.
- `503`: adapter bắt buộc gặp lỗi kỹ thuật.
- `429`: in-memory demo rate limit khi `RATE_LIMIT_ENABLED=true`; thay bằng adapter hạ tầng trước public scale-out.
- Thiếu/mâu thuẫn/chưa duyệt evidence là response `200` fail-closed với `official_review_required`, không phải `verified_guidance`.
- Disabled runtime không fallback sang fixture. `POST /v1/procedures/recommend` không trả candidate fixture; checklist/validation của ba ID MVP trả trạng thái fail-closed và không có hướng dẫn/rule thực tế.

## Adapter handoff

- **Data lane:** thay `ProcedureRepository` bằng loader chỉ phát pack đã K1/release; backend không đọc raw `data/**`.
- **RAG lane:** cài `RetrievalProvider` qua `RetrievalQuery`/`RetrievalEvidence`; retrieval không được thay rule engine.
- **AI lane:** cài `LLMProvider` chỉ cho clarification/explanation sau PII boundary; không tạo rule, citation hay verdict.
- **FE lane:** dùng `/openapi.json`, trust metadata, `X-Request-ID` và error envelope; không phụ thuộc vào dev fixture cho production UI.

## Local verification

```powershell
cd backend
uvicorn main:app --port 8000 --reload
python -m pytest -q
black --check .
flake8 .
```

Mọi thay đổi public contract, adapter provider hoặc runtime storage vẫn cần Task Record và peer review theo [team protocol](../ai/TEAM_PROTOCOL.md).
