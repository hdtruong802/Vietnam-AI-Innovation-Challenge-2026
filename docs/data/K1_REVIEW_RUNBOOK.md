# K1 Source Review Runbook

Tài liệu này hướng dẫn tạo và kiểm tra gói review cho đúng ba thủ tục MVP.
Tooling chỉ kiểm tính toàn vẹn và độ đầy đủ của metadata; không thay thế người
review nội dung nghiệp vụ/pháp lý.

Gói anchor trong tài liệu này vẫn chỉ có ba source canonical. Với registry 25
source/26 quan hệ và dual-source discovery từ `dataset_raw`, xem
[`PROCEDURE_FAMILY_REGISTRY.md`](PROCEDURE_FAMILY_REGISTRY.md).

## Phạm vi canonical

| Procedure ID | Mã nguồn bắt buộc | Tên thủ tục |
| --- | --- | --- |
| `dang-ky-khai-sinh` | `1.001193` | Thủ tục đăng ký khai sinh |
| `dang-ky-thuong-tru` | `1.004222` | Đăng ký thường trú |
| `dang-ky-ho-kinh-doanh` | `1.001612` | Đăng ký thành lập hộ kinh doanh |

Biến thể đăng ký lại/lưu động, tạm trú, công ty cổ phần hoặc thủ tục có từ khóa
gần giống không thuộc gói này.

## 1. Tạo candidate package

Chạy từ repository root:

```powershell
python scripts/data/prepare_k1_review_package.py
```

Output local, bị Git ignore:

- `artifacts/k1-review/candidate-sources.csv`: manifest cần reviewer hoàn thiện.
- `artifacts/k1-review/provenance-report.json`: snapshot/checksum, không chứa raw text.
- `artifacts/k1-review/review-checklist.md`: checklist cho reviewer.

Prepare fail nếu thiếu, trùng, sai tên/mã, lỗi UTF-8 hoặc output nằm ngoài
`artifacts/`. Mọi row luôn bắt đầu bằng `review_status=needs_review`.

## 2. Human review

Tạo `artifacts/k1-review/reviewed-sources.csv` từ candidate manifest. Reviewer
đối chiếu từng source với trang/văn bản chính thức và điền:

- `authority`, `jurisdiction`, `source_url`, `document_version`.
- `effective_from`, tùy chọn `effective_to`, `last_verified_at`.
- `permission_status`: `official_public` hoặc `permission_recorded`.
- `reviewed_by`, `reviewed_at`, `review_notes` mô tả nội dung đã kiểm tra.
- Chỉ sau khi xử lý mọi conflict mới đặt `review_status=approved`.

Không sửa `source_id`, `raw_path`, mã/tên thủ tục hoặc hai checksum. Nếu raw
source thay đổi, tạo lại candidate package và review lại snapshot mới.

## 3. Kiểm tra manifest đã review

```powershell
python scripts/data/validate_k1_review_package.py `
  --manifest artifacts/k1-review/reviewed-sources.csv `
  --as-of 2026-07-18 `
  --report-output artifacts/k1-review/release-ready-report.json
```

Validator kiểm:

- Exact set ba procedure/source canonical và schema `vaic-k1-review-v1`.
- Raw path chỉ nằm trong `data/Data_DVC`, strict UTF-8 và checksum không đổi.
- Mã, tên thủ tục và số quyết định khớp nội dung raw đã parse.
- URL HTTPS thuộc domain chính thức `.gov.vn`, permission và metadata bắt buộc.
- Ngày review/xác minh/hiệu lực hợp lệ tại `--as-of`.
- Reviewer đã chủ động đặt `approved` và ghi review notes đủ nội dung.

Bất kỳ issue nào cũng trả exit code `1` và không tạo
`release-ready-report.json`. Report thành công mới chỉ có nghĩa manifest đủ điều
kiện kỹ thuật để chuyển sang task release/runtime tiếp theo.

## Rollback

Xóa output local trong `artifacts/k1-review/` và chạy prepare lại. Không có raw
source, runtime pack, API hoặc trạng thái cloud nào bị thay đổi bởi hai CLI này.
