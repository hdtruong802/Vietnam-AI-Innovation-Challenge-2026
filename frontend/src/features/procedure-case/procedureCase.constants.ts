import type { FeedbackReasonCode } from "./procedureCase.types";

// Only official-source reference that exists anywhere in this repo
// (docs/ai/PROJECT_CONTEXT.md, docs/ai/SECRETS_AND_DATA.md). The backend
// contract has no per-response official_channel_url field.
export const OFFICIAL_PORTAL_URL = "https://dichvucong.gov.vn/";

const CLOUD_RUN_API_BASE_URL = "https://vngov-api-j53prjslqa-as.a.run.app";

// The explicit environment variable always wins. The production fallback keeps
// the public Vercel build usable while its owner configures project variables;
// local development continues to use the local FastAPI port by default.
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  (process.env.NODE_ENV === "production" ? CLOUD_RUN_API_BASE_URL : "http://localhost:8000");

export const INPUT_MAX_LENGTH = 500;
export const FEEDBACK_NOTE_MAX_LENGTH = 200;
export const REQUEST_TIMEOUT_MS = 8000;
export const RETRY_BACKOFF_MS = 400;
export const SESSION_STORAGE_KEY = "vngov.procedureCase.v2";

export const FEEDBACK_REASONS: { code: FeedbackReasonCode; label: string }[] = [
  { code: "sai_thu_tuc", label: "Sai thủ tục" },
  { code: "thieu_thua_giay_to", label: "Thiếu/thừa giấy tờ" },
  { code: "kho_hieu", label: "Khó hiểu" },
  { code: "loi_precheck_sai", label: "Lỗi pre-check sai" },
  { code: "khac", label: "Khác" },
];

export const STATIC_PROCEDURES = [
  {
    procedure_id: "dang-ky-khai-sinh",
    label: "Đăng ký khai sinh",
    description: "Thủ tục đăng ký khai sinh cho trẻ em",
    icon: "birth",
  },
  {
    procedure_id: "dang-ky-thuong-tru",
    label: "Đăng ký thường trú",
    description: "Thủ tục đăng ký thường trú tại nơi cư trú",
    icon: "residence",
  },
  {
    procedure_id: "dang-ky-ho-kinh-doanh",
    label: "Đăng ký thành lập hộ kinh doanh",
    description: "Thủ tục đăng ký thành lập hộ kinh doanh",
    icon: "business",
  },
] as const;

export const GUIDANCE_DISCLAIMER =
  "Đây là hướng dẫn chuẩn bị hồ sơ dựa trên các nguồn trích dẫn, không thay thế quyết định của cơ quan có thẩm quyền.";
