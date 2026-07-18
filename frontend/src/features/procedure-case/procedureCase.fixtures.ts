// Typed preview fixtures for the Copilot workspace dev preview
// (frontend/src/app/dev/copilot-preview). Pure data only, no UI. Deliberately
// not imported from *.test.ts (test files shouldn't ship in the app bundle),
// so the sample-data shape here is a small standalone copy of the shapes
// used in procedureCaseReducer.test.ts.
import { createInitialState, procedureCaseReducer } from "./procedureCaseReducer";
import type {
  ChecklistResponse,
  IntakeResponse,
  ProcedureCaseState,
  ValidationResponse,
} from "./procedureCase.types";

export type FixtureKey =
  | "idle"
  | "procedure_review"
  | "clarifying"
  | "checklist_loading"
  | "checklist_review"
  | "form_editing"
  | "validating"
  | "needs_fix"
  | "pass_preliminary"
  | "official_review_required"
  | "degraded_after_form";

export const FIXTURE_KEYS: FixtureKey[] = [
  "idle",
  "procedure_review",
  "clarifying",
  "checklist_loading",
  "checklist_review",
  "form_editing",
  "validating",
  "needs_fix",
  "pass_preliminary",
  "official_review_required",
  "degraded_after_form",
];

function baseTrust() {
  return {
    trust_state: "verified_guidance" as const,
    procedure_version: "v1",
    source_refs: [
      {
        ref_id: "s1",
        title: "Luật Hộ tịch 2014",
        url_or_ref: "https://dichvucong.gov.vn/",
        effective_from: "2016-01-01",
        effective_to: null,
      },
    ],
    last_verified_at: "2026-07-17",
    review_gate: null,
    fixture_mode: true,
  };
}

function sampleIntakeResponse(overrides: Partial<IntakeResponse> = {}): IntakeResponse {
  return {
    ...baseTrust(),
    session_id: "fixture-session",
    detected_procedure_id: "dang-ky-khai-sinh",
    procedure: {
      procedure_id: "dang-ky-khai-sinh",
      name: "Đăng ký khai sinh",
      reason: "Câu hỏi của bạn khớp với thủ tục đăng ký khai sinh cho trẻ em.",
    },
    message_plain: "Tôi nghĩ bạn cần thực hiện thủ tục Đăng ký khai sinh. Đúng không?",
    clarifying_questions: [
      { id: "q1", prompt: "Trẻ sinh ở đâu?", options: [], why: "Xác định cơ quan tiếp nhận hồ sơ.", required: true },
      { id: "q2", prompt: "Cha mẹ đã đăng ký kết hôn chưa?", options: ["Rồi", "Chưa"], why: null, required: true },
    ],
    proposed_session_context: {
      procedure_id: "dang-ky-khai-sinh",
      procedure_version: "v1",
      clarification_answers: {},
      pending_question_ids: ["q1", "q2"],
      review_state: null,
    },
    ...overrides,
  };
}

function sampleChecklistResponse(overrides: Partial<ChecklistResponse> = {}): ChecklistResponse {
  return {
    ...baseTrust(),
    procedure_id: "dang-ky-khai-sinh",
    procedure_name: "Đăng ký khai sinh",
    required_documents: [
      { id: "doc1", label: "Giấy chứng sinh", kind: "required", description: "Do cơ sở y tế nơi trẻ sinh ra cấp.", source_ref_ids: ["s1"], condition: null },
      { id: "doc2", label: "CCCD của cha/mẹ", kind: "conditional", description: "Bản chính để đối chiếu.", source_ref_ids: ["s1"], condition: null },
    ],
    optional_documents: [
      { id: "doc3", label: "Sổ hộ khẩu", kind: "optional", description: "Nếu có, giúp rút ngắn thời gian xử lý.", source_ref_ids: [], condition: null },
    ],
    steps: [
      { order: 1, title: "Chuẩn bị hồ sơ", detail: "Thu thập đầy đủ giấy tờ theo checklist." },
      { order: 2, title: "Nộp hồ sơ", detail: "Nộp tại UBND cấp xã nơi cư trú." },
    ],
    form_schema: {
      type: "object",
      properties: {
        child_name: { type: "string", title: "Họ tên trẻ" },
        dob: { type: "string", title: "Ngày sinh", format: "date" },
      },
      required: ["child_name", "dob"],
    },
    message_plain: "Đây là checklist hồ sơ cho thủ tục Đăng ký khai sinh.",
    ...overrides,
  };
}

function sampleValidationResponse(overrides: Partial<ValidationResponse> = {}): ValidationResponse {
  return {
    ...baseTrust(),
    procedure_id: "dang-ky-khai-sinh",
    verdict: "needs_fix",
    findings: [
      {
        field_id: "dob",
        severity: "error",
        rule_id: "R-DOB-FORMAT",
        message: "Ngày sinh chưa hợp lệ.",
        fix_hint: "Nhập theo định dạng YYYY-MM-DD.",
        source_ref_ids: ["s1"],
      },
    ],
    summary_message: "Hồ sơ còn 1 lỗi cần sửa trước khi tiếp tục.",
    ...overrides,
  };
}

function idleState(): ProcedureCaseState {
  return createInitialState("fixture-idle");
}

function procedureReviewState(): ProcedureCaseState {
  return procedureCaseReducer(idleState(), {
    type: "INTAKE_RESPONSE_RECEIVED",
    response: sampleIntakeResponse(),
  });
}

function clarifyingState(): ProcedureCaseState {
  return procedureCaseReducer(procedureReviewState(), { type: "CONFIRM_U1" });
}

function checklistLoadingState(): ProcedureCaseState {
  const selected = procedureCaseReducer(idleState(), {
    type: "SELECT_STATIC_PROCEDURE",
    procedureId: "dang-ky-khai-sinh",
  });
  return procedureCaseReducer(selected, { type: "CHECKLIST_REQUEST_STARTED" });
}

function checklistReviewState(): ProcedureCaseState {
  return procedureCaseReducer(checklistLoadingState(), {
    type: "CHECKLIST_RESPONSE_RECEIVED",
    response: sampleChecklistResponse(),
  });
}

function formEditingState(): ProcedureCaseState {
  const confirmed = procedureCaseReducer(checklistReviewState(), { type: "CONFIRM_U2" });
  return procedureCaseReducer(confirmed, {
    type: "UPDATE_FORM_FIELD",
    key: "child_name",
    value: "Nguyễn Văn An",
  });
}

function validatingState(): ProcedureCaseState {
  return procedureCaseReducer(formEditingState(), { type: "RUN_PRECHECK_STARTED" });
}

function needsFixState(): ProcedureCaseState {
  return procedureCaseReducer(validatingState(), {
    type: "VALIDATION_RESPONSE_RECEIVED",
    response: sampleValidationResponse({ verdict: "needs_fix" }),
  });
}

function passPreliminaryState(): ProcedureCaseState {
  return procedureCaseReducer(validatingState(), {
    type: "VALIDATION_RESPONSE_RECEIVED",
    response: sampleValidationResponse({
      verdict: "pass_preliminary",
      findings: [],
      summary_message: "Hồ sơ đã qua kiểm tra sơ bộ, không phát hiện lỗi.",
    }),
  });
}

function officialReviewRequiredState(): ProcedureCaseState {
  return procedureCaseReducer(idleState(), {
    type: "INTAKE_RESPONSE_RECEIVED",
    response: sampleIntakeResponse({
      trust_state: "official_review_required",
      message_plain: "Yêu cầu này nằm ngoài phạm vi 3 thủ tục MVP, cần cơ quan có thẩm quyền xem xét.",
    }),
  });
}

/**
 * form_editing with real checklist/formDraft data, then a failed health
 * check applied on top — the exact regression path fixed via
 * lastStableFlow: the progress rail must resolve to stage 4 ("Tờ khai"),
 * not stage 1, and the form must stay visible under the availability
 * banner.
 */
function degradedAfterFormState(): ProcedureCaseState {
  return procedureCaseReducer(formEditingState(), { type: "HEALTH_CHECK_RESULT", ok: false });
}

const FIXTURE_BUILDERS: Record<FixtureKey, () => ProcedureCaseState> = {
  idle: idleState,
  procedure_review: procedureReviewState,
  clarifying: clarifyingState,
  checklist_loading: checklistLoadingState,
  checklist_review: checklistReviewState,
  form_editing: formEditingState,
  validating: validatingState,
  needs_fix: needsFixState,
  pass_preliminary: passPreliminaryState,
  official_review_required: officialReviewRequiredState,
  degraded_after_form: degradedAfterFormState,
};

export function getFixtureState(key: FixtureKey): ProcedureCaseState {
  return FIXTURE_BUILDERS[key]();
}
