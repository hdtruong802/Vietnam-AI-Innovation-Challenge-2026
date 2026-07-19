import { describe, expect, it } from "vitest";
import { createInitialState, procedureCaseReducer } from "./procedureCaseReducer";
import type {
  ChecklistResponse,
  IntakeResponse,
  ValidationResponse,
} from "./procedureCase.types";

function baseTrust() {
  return {
    trust_state: "verified_guidance" as const,
    procedure_version: "v1",
    source_refs: [],
    last_verified_at: "2026-07-17",
    review_gate: null,
    fixture_mode: false,
    demo_mode: false,
  };
}

function intakeResponse(overrides: Partial<IntakeResponse> = {}): IntakeResponse {
  return {
    ...baseTrust(),
    session_id: "s1",
    detected_procedure_id: "dang-ky-khai-sinh",
    procedure: { procedure_id: "dang-ky-khai-sinh", name: "Đăng ký khai sinh", reason: "match" },
    message_plain: "Đã nhận diện thủ tục.",
    clarifying_questions: [
      { id: "q1", prompt: "Trẻ sinh ở đâu?", options: [], why: null, required: true },
      { id: "q2", prompt: "Cha mẹ đã kết hôn chưa?", options: ["Rồi", "Chưa"], why: null, required: true },
    ],
    proposed_session_context: {
      procedure_id: "dang-ky-khai-sinh",
      procedure_version: "v1",
      clarification_answers: {},
      pending_question_ids: ["q1", "q2"],
      acknowledged_review_gates: [],
      reviewed_document_ids: [],
    },
    ...overrides,
  };
}

function checklistResponse(overrides: Partial<ChecklistResponse> = {}): ChecklistResponse {
  return {
    ...baseTrust(),
    procedure_id: "dang-ky-khai-sinh",
    procedure_name: "Đăng ký khai sinh",
    required_documents: [
      { id: "doc1", label: "Giấy chứng sinh", kind: "required", description: "d", source_ref_ids: [], condition: null },
      { id: "doc2", label: "CCCD cha", kind: "conditional", description: "d", source_ref_ids: [], condition: null },
    ],
    optional_documents: [
      { id: "doc3", label: "Sổ hộ khẩu", kind: "optional", description: "d", source_ref_ids: [], condition: null },
    ],
    steps: [{ order: 1, title: "Nộp hồ sơ", detail: "detail" }],
    form_schema: {
      type: "object",
      properties: { child_name: { type: "string", title: "Họ tên trẻ" } },
      required: ["child_name"],
    },
    message_plain: "checklist",
    ...overrides,
  };
}

function validationResponse(overrides: Partial<ValidationResponse> = {}): ValidationResponse {
  return {
    ...baseTrust(),
    procedure_id: "dang-ky-khai-sinh",
    verdict: "needs_fix",
    findings: [
      { field_id: "child_name", severity: "error", rule_id: "R1", message: "thiếu", fix_hint: "điền vào", source_ref_ids: [] },
    ],
    summary_message: "cần sửa",
    ...overrides,
  };
}

describe("procedureCaseReducer — gates U1/U2/U3", () => {
  it("moves to procedure_review on intake response with a candidate, not straight to checklist", () => {
    const state = procedureCaseReducer(
      createInitialState("s1"),
      { type: "INTAKE_RESPONSE_RECEIVED", response: intakeResponse() },
    );
    expect(state.flow).toBe("procedure_review");
    expect(state.checklist).toBeNull();
  });

  it("CONFIRM_U1 goes to clarifying when questions are pending", () => {
    let state = procedureCaseReducer(createInitialState("s1"), {
      type: "INTAKE_RESPONSE_RECEIVED",
      response: intakeResponse(),
    });
    state = procedureCaseReducer(state, { type: "CONFIRM_U1" });
    expect(state.flow).toBe("clarifying");
    expect(state.activeClarifyingQuestions).toHaveLength(2);
  });

  it("CONFIRM_U1 skips straight to checklist_loading when there are no questions", () => {
    let state = procedureCaseReducer(createInitialState("s1"), {
      type: "INTAKE_RESPONSE_RECEIVED",
      response: intakeResponse({ clarifying_questions: [] }),
    });
    state = procedureCaseReducer(state, { type: "CONFIRM_U1" });
    expect(state.flow).toBe("checklist_loading");
  });

  it("answering the last clarification question advances to checklist_loading", () => {
    let state = procedureCaseReducer(createInitialState("s1"), {
      type: "INTAKE_RESPONSE_RECEIVED",
      response: intakeResponse(),
    });
    state = procedureCaseReducer(state, { type: "CONFIRM_U1" });
    state = procedureCaseReducer(state, { type: "SUBMIT_CLARIFICATION_ANSWER", questionId: "q1", value: "Hà Nội" });
    expect(state.flow).toBe("clarifying");
    state = procedureCaseReducer(state, { type: "SUBMIT_CLARIFICATION_ANSWER", questionId: "q2", value: "Rồi" });
    expect(state.flow).toBe("checklist_loading");
    expect(state.sessionContext.clarification_answers).toEqual({ q1: "Hà Nội", q2: "Rồi" });
  });

  it("checklist requires explicit CONFIRM_U2 before entering form_editing", () => {
    let state = procedureCaseReducer(createInitialState("s1"), {
      type: "CHECKLIST_RESPONSE_RECEIVED",
      response: checklistResponse(),
    });
    expect(state.flow).toBe("checklist_review");
    state = procedureCaseReducer(state, { type: "CONFIRM_U2" });
    expect(state.flow).toBe("form_editing");
    expect(state.formDraft).toEqual({ child_name: "" });
  });

  it("CONFIRM_U2 is a no-op without a loaded checklist", () => {
    const state = procedureCaseReducer(createInitialState("s1"), { type: "CONFIRM_U2" });
    expect(state.flow).toBe("idle");
  });

  it("validation verdict needs_fix vs pass_preliminary maps to distinct flow states", () => {
    const needsFix = procedureCaseReducer(createInitialState("s1"), {
      type: "VALIDATION_RESPONSE_RECEIVED",
      response: validationResponse({ verdict: "needs_fix" }),
    });
    expect(needsFix.flow).toBe("needs_fix");

    const pass = procedureCaseReducer(createInitialState("s1"), {
      type: "VALIDATION_RESPONSE_RECEIVED",
      response: validationResponse({ verdict: "pass_preliminary" }),
    });
    expect(pass.flow).toBe("pass_preliminary");
  });
});

describe("procedureCaseReducer — official_review_required override", () => {
  it("renders a non-verified fixture checklist for the safe demo flow", () => {
    const state = procedureCaseReducer(createInitialState("s1"), {
      type: "CHECKLIST_RESPONSE_RECEIVED",
      response: checklistResponse({
        trust_state: "official_review_required",
        fixture_mode: true,
        last_verified_at: null,
      }),
    });

    expect(state.flow).toBe("checklist_review");
    expect(state.checklist?.required_documents).toHaveLength(2);
    expect(state.trustMetadata?.trust_state).toBe("official_review_required");
  });

  it("still blocks a non-fixture checklist that requires official review", () => {
    const state = procedureCaseReducer(createInitialState("s1"), {
      type: "CHECKLIST_RESPONSE_RECEIVED",
      response: checklistResponse({
        trust_state: "official_review_required",
        fixture_mode: false,
      }),
    });

    expect(state.flow).toBe("official_review_required");
  });

  it("keeps a demo-approved checklist and precheck in the demo flow without verified trust", () => {
    let state = procedureCaseReducer(createInitialState("s1"), {
      type: "CHECKLIST_RESPONSE_RECEIVED",
      response: checklistResponse({
        trust_state: "official_review_required",
        demo_mode: true,
        last_verified_at: null,
      }),
    });
    expect(state.flow).toBe("checklist_review");
    expect(state.trustMetadata?.trust_state).toBe("official_review_required");

    state = procedureCaseReducer(state, {
      type: "VALIDATION_RESPONSE_RECEIVED",
      response: validationResponse({
        trust_state: "official_review_required",
        demo_mode: true,
        verdict: "pass_preliminary",
        last_verified_at: null,
      }),
    });
    expect(state.flow).toBe("pass_preliminary");
    expect(state.trustMetadata?.trust_state).toBe("official_review_required");
  });

  it("overrides regardless of current flow for intake responses", () => {
    const state = procedureCaseReducer(
      { ...createInitialState("s1"), flow: "clarifying" },
      {
        type: "INTAKE_RESPONSE_RECEIVED",
        response: intakeResponse({ trust_state: "official_review_required" }),
      },
    );
    expect(state.flow).toBe("official_review_required");
  });

  it("overrides for validation responses even mid form_editing", () => {
    const state = procedureCaseReducer(
      { ...createInitialState("s1"), flow: "form_editing" },
      {
        type: "VALIDATION_RESPONSE_RECEIVED",
        response: validationResponse({ trust_state: "official_review_required", verdict: null }),
      },
    );
    expect(state.flow).toBe("official_review_required");
  });
});

describe("procedureCaseReducer — clarification answer editing invalidates downstream state", () => {
  it("editing an earlier answer clears checklist/formDraft/validation and re-opens that question", () => {
    let state = procedureCaseReducer(createInitialState("s1"), {
      type: "INTAKE_RESPONSE_RECEIVED",
      response: intakeResponse(),
    });
    state = procedureCaseReducer(state, { type: "CONFIRM_U1" });
    state = procedureCaseReducer(state, { type: "SUBMIT_CLARIFICATION_ANSWER", questionId: "q1", value: "Hà Nội" });
    state = procedureCaseReducer(state, { type: "SUBMIT_CLARIFICATION_ANSWER", questionId: "q2", value: "Rồi" });
    state = procedureCaseReducer(state, { type: "CHECKLIST_RESPONSE_RECEIVED", response: checklistResponse() });
    state = procedureCaseReducer(state, { type: "CONFIRM_U2" });
    state = procedureCaseReducer(state, { type: "UPDATE_FORM_FIELD", key: "child_name", value: "An" });
    state = procedureCaseReducer(state, {
      type: "VALIDATION_RESPONSE_RECEIVED",
      response: validationResponse({ verdict: "pass_preliminary" }),
    });
    expect(state.flow).toBe("pass_preliminary");

    state = procedureCaseReducer(state, { type: "EDIT_CLARIFICATION_ANSWER", questionId: "q1" });

    expect(state.flow).toBe("clarifying");
    expect(state.currentQuestionIndex).toBe(0);
    expect(state.sessionContext.clarification_answers).toEqual({});
    expect(state.checklist).toBeNull();
    expect(state.formDraft).toEqual({});
    expect(state.lastValidationResponse).toBeNull();
  });
});

describe("procedureCaseReducer — availability separates AI failure from backend outage", () => {
  it("an intake failure marks only the AI path unavailable, keeping backend reachable", () => {
    const state = procedureCaseReducer(createInitialState("s1"), {
      type: "INTAKE_REQUEST_FAILED",
      kind: "timeout",
    });
    expect(state.flow).toBe("degraded");
    expect(state.availability.degradeReason).toBe("ai_unavailable");
    expect(state.availability.backendReachable).toBe(true);
  });

  it("a checklist/validate failure marks the whole backend unreachable", () => {
    const state = procedureCaseReducer(createInitialState("s1"), {
      type: "CHECKLIST_REQUEST_FAILED",
      kind: "network",
    });
    expect(state.flow).toBe("degraded");
    expect(state.availability.degradeReason).toBe("backend_unreachable");
  });

  it("a failed health check marks backend unreachable and enters degraded", () => {
    const state = procedureCaseReducer(createInitialState("s1"), {
      type: "HEALTH_CHECK_RESULT",
      ok: false,
    });
    expect(state.flow).toBe("degraded");
    expect(state.availability.degradeReason).toBe("backend_unreachable");
  });

  it("a successful health check clears degraded when AI path is fine", () => {
    let state = procedureCaseReducer(createInitialState("s1"), { type: "HEALTH_CHECK_RESULT", ok: false });
    state = procedureCaseReducer(state, { type: "HEALTH_CHECK_RESULT", ok: true });
    expect(state.flow).toBe("idle");
    expect(state.availability.degradeReason).toBeNull();
  });

  it("selecting a static procedure while AI-degraded still proceeds to checklist_loading", () => {
    let state = procedureCaseReducer(createInitialState("s1"), { type: "INTAKE_REQUEST_FAILED", kind: "network" });
    expect(state.flow).toBe("degraded");
    state = procedureCaseReducer(state, { type: "SELECT_STATIC_PROCEDURE", procedureId: "dang-ky-khai-sinh" });
    expect(state.flow).toBe("checklist_loading");
  });
});

describe("procedureCaseReducer — needs_fix to validating re-run loop", () => {
  it("re-running precheck from needs_fix goes back through validating", () => {
    let state = procedureCaseReducer(createInitialState("s1"), {
      type: "VALIDATION_RESPONSE_RECEIVED",
      response: validationResponse({ verdict: "needs_fix" }),
    });
    expect(state.flow).toBe("needs_fix");
    state = procedureCaseReducer(state, { type: "UPDATE_FORM_FIELD", key: "child_name", value: "An" });
    state = procedureCaseReducer(state, { type: "RUN_PRECHECK_STARTED" });
    expect(state.flow).toBe("validating");
    state = procedureCaseReducer(state, {
      type: "VALIDATION_RESPONSE_RECEIVED",
      response: validationResponse({ verdict: "pass_preliminary" }),
    });
    expect(state.flow).toBe("pass_preliminary");
  });
});

describe("procedureCaseReducer — session reset", () => {
  it("RESET_SESSION returns a fresh initial state with a new session id", () => {
    let state = procedureCaseReducer(createInitialState("s1"), {
      type: "CHECKLIST_RESPONSE_RECEIVED",
      response: checklistResponse(),
    });
    state = procedureCaseReducer(state, { type: "RESET_SESSION", sessionId: "s2" });
    expect(state.sessionId).toBe("s2");
    expect(state.checklist).toBeNull();
    expect(state.flow).toBe("idle");
  });
});
