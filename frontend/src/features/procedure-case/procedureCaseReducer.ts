import { emptySessionContext, initialAvailability } from "./procedureCase.types";
import type {
  ChecklistResponse,
  ClarifyingQuestion,
  FeedbackEntry,
  FlowState,
  FormFieldValue,
  IntakeResponse,
  PersistedProcedureCaseState,
  ProcedureCaseState,
  ValidationResponse,
} from "./procedureCase.types";

export type ApiFailureKind = "network" | "timeout" | "aborted" | "http";

export type ProcedureCaseAction =
  | { type: "HEALTH_CHECK_RESULT"; ok: boolean }
  | { type: "SEND_MESSAGE"; text: string }
  | { type: "INTAKE_REQUEST_STARTED" }
  | { type: "INTAKE_RESPONSE_RECEIVED"; response: IntakeResponse }
  | { type: "INTAKE_REQUEST_FAILED"; kind: ApiFailureKind }
  | { type: "SESSION_CONTEXT_UPDATED"; sessionContext: ProcedureCaseState["sessionContext"] }
  | { type: "CONFIRM_U1" }
  | { type: "REJECT_U1" }
  | { type: "SUBMIT_CLARIFICATION_ANSWER"; questionId: string; value: string }
  | { type: "EDIT_CLARIFICATION_ANSWER"; questionId: string }
  | { type: "CHECKLIST_REQUEST_STARTED" }
  | { type: "CHECKLIST_RESPONSE_RECEIVED"; response: ChecklistResponse }
  | { type: "CHECKLIST_REQUEST_FAILED"; kind: ApiFailureKind }
  | { type: "CONFIRM_U2" }
  | { type: "UPDATE_FORM_FIELD"; key: string; value: FormFieldValue }
  | { type: "RUN_PRECHECK_STARTED" }
  | { type: "VALIDATION_RESPONSE_RECEIVED"; response: ValidationResponse }
  | { type: "VALIDATION_REQUEST_FAILED"; kind: ApiFailureKind }
  | { type: "CONFIRM_U3" }
  | { type: "SELECT_STATIC_PROCEDURE"; procedureId: string }
  | { type: "RECORD_FEEDBACK"; entry: FeedbackEntry }
  | { type: "RESET_SESSION"; sessionId: string }
  | { type: "CANCEL_REQUEST" }
  | { type: "HYDRATE"; persisted: PersistedProcedureCaseState };

export function createInitialState(sessionId: string): ProcedureCaseState {
  return {
    flow: "idle",
    lastStableFlow: "idle",
    availability: initialAvailability(),
    sessionId,
    sessionContext: emptySessionContext(),
    transcript: [
      {
        role: "assistant",
        content:
          "Xin chào! Tôi là VNGov, trợ lý hướng dẫn và tiền kiểm hồ sơ hành chính công trực tuyến của bạn. Bạn đang cần thực hiện thủ tục nào?",
      },
    ],
    activeClarifyingQuestions: [],
    currentQuestionIndex: 0,
    answeredQuestions: [],
    lastIntakeResponse: null,
    checklist: null,
    formDraft: {},
    lastValidationResponse: null,
    dismissedFindingFields: [],
    trustMetadata: null,
    feedbackLog: [],
    isBusy: false,
    error: null,
  };
}

function filterUnansweredQuestions(
  questions: ClarifyingQuestion[],
  answers: Record<string, unknown>,
): ClarifyingQuestion[] {
  return questions.filter((q) => !(q.id in answers));
}

function initFormDraft(response: ChecklistResponse): Record<string, FormFieldValue> {
  const draft: Record<string, FormFieldValue> = {};
  for (const key of Object.keys(response.form_schema?.properties ?? {})) {
    const prop = response.form_schema.properties[key];
    if (prop.type === "boolean") draft[key] = false;
    else if (prop.type === "integer" || prop.type === "number") draft[key] = null;
    else draft[key] = "";
  }
  return draft;
}

const OVERLAY_FLOWS: FlowState[] = ["degraded", "official_review_required"];

export function procedureCaseReducer(
  state: ProcedureCaseState,
  action: ProcedureCaseAction,
): ProcedureCaseState {
  const next = applyAction(state, action);
  if (next.flow === state.flow && next.lastStableFlow === state.lastStableFlow) return next;
  return {
    ...next,
    lastStableFlow: OVERLAY_FLOWS.includes(next.flow) ? next.lastStableFlow : next.flow,
  };
}

function applyAction(
  state: ProcedureCaseState,
  action: ProcedureCaseAction,
): ProcedureCaseState {
  switch (action.type) {
    case "HEALTH_CHECK_RESULT": {
      const backendReachable = action.ok;
      const degradeReason = !backendReachable
        ? "backend_unreachable"
        : state.availability.aiPathAvailable
          ? null
          : "ai_unavailable";
      const stillDegraded = degradeReason !== null;
      return {
        ...state,
        availability: { ...state.availability, backendReachable, degradeReason },
        // On reconnect, resume the stage the user was actually at
        // (lastStableFlow) rather than snapping back to idle — reconnecting
        // must not discard a checklist/form the user already has open.
        flow: stillDegraded ? "degraded" : state.flow === "degraded" ? state.lastStableFlow : state.flow,
      };
    }

    case "SEND_MESSAGE":
      return {
        ...state,
        isBusy: true,
        error: null,
        flow: state.flow === "idle" || state.flow === "degraded" ? "identifying_procedure" : state.flow,
        transcript: [...state.transcript, { role: "user", content: action.text }],
      };

    case "INTAKE_REQUEST_STARTED":
      return { ...state, isBusy: true, error: null };

    case "INTAKE_RESPONSE_RECEIVED": {
      const response = action.response;
      // The API returns the proposed client-owned context after each turn.
      // Do not merge stale client answers back in: that can bypass a newly
      // derived pending-question list or review acknowledgement.
      const sessionContext = response.proposed_session_context;
      const transcript = [
        ...state.transcript,
        { role: "assistant" as const, content: response.message_plain, sourceRefs: response.source_refs },
      ];
      const trustMetadata: ProcedureCaseState["trustMetadata"] = {
        trust_state: response.trust_state,
        procedure_version: response.procedure_version,
        source_refs: response.source_refs,
        last_verified_at: response.last_verified_at,
        review_gate: response.review_gate,
        fixture_mode: response.fixture_mode,
        demo_mode: response.demo_mode,
      };
      const availability: ProcedureCaseState["availability"] = {
        backendReachable: true,
        aiPathAvailable: true,
        degradeReason: null,
      };

      const base: ProcedureCaseState = {
        ...state,
        isBusy: false,
        sessionContext,
        transcript,
        lastIntakeResponse: response,
        trustMetadata,
        availability,
      };

      if (response.trust_state === "official_review_required" && !response.demo_mode) {
        return { ...base, flow: "official_review_required" };
      }
      if (response.detected_procedure_id && response.procedure) {
        const hasConfirmedProcedure = sessionContext.acknowledged_review_gates?.includes("U1");
        if (hasConfirmedProcedure) {
          const unanswered = filterUnansweredQuestions(
            response.clarifying_questions,
            sessionContext.clarification_answers,
          );
          if (unanswered.length > 0) {
            return {
              ...base,
              activeClarifyingQuestions: unanswered,
              currentQuestionIndex: 0,
              flow: "clarifying",
            };
          }
          return { ...base, flow: "checklist_loading" };
        }
        return { ...base, flow: "procedure_review" };
      }
      return { ...base, flow: "identifying_procedure" };
    }

    case "SESSION_CONTEXT_UPDATED":
      return { ...state, isBusy: false, sessionContext: action.sessionContext };

    case "INTAKE_REQUEST_FAILED":
      if (action.kind === "aborted") return { ...state, isBusy: false };
      return {
        ...state,
        isBusy: false,
        error: "Không thể kết nối trợ lý AI. Vui lòng thử lại hoặc chọn thủ tục từ danh mục có sẵn.",
        availability: {
          ...state.availability,
          aiPathAvailable: false,
          degradeReason: state.availability.backendReachable ? "ai_unavailable" : "backend_unreachable",
        },
        flow: "degraded",
      };

    case "CONFIRM_U1": {
      if (!state.lastIntakeResponse) return state;
      const candidate = state.lastIntakeResponse.procedure;
      const sessionContext = {
        ...state.sessionContext,
        procedure_id: candidate?.procedure_id ?? state.sessionContext.procedure_id,
      };
      const unanswered = filterUnansweredQuestions(
        state.lastIntakeResponse.clarifying_questions,
        sessionContext.clarification_answers,
      );
      if (unanswered.length > 0) {
        return {
          ...state,
          sessionContext,
          activeClarifyingQuestions: unanswered,
          currentQuestionIndex: 0,
          flow: "clarifying",
        };
      }
      return { ...state, sessionContext, flow: "checklist_loading" };
    }

    case "REJECT_U1":
      return {
        ...state,
        flow: "identifying_procedure",
        lastIntakeResponse: null,
        sessionContext: { ...state.sessionContext, procedure_id: null },
      };

    case "SUBMIT_CLARIFICATION_ANSWER": {
      const answeredQuestions = [
        ...state.answeredQuestions,
        { questionId: action.questionId, value: action.value, answeredAt: new Date().toISOString() },
      ];
      const sessionContext = {
        ...state.sessionContext,
        clarification_answers: {
          ...state.sessionContext.clarification_answers,
          [action.questionId]: action.value,
        },
      };
      const nextIndex = state.currentQuestionIndex + 1;
      const done = nextIndex >= state.activeClarifyingQuestions.length;
      return {
        ...state,
        answeredQuestions,
        sessionContext,
        currentQuestionIndex: done ? state.currentQuestionIndex : nextIndex,
        // Backend's intake_questions list is static per pack (not
        // progressively re-derived server-side), so once every currently
        // known question is answered we go straight to the checklist
        // instead of round-tripping /v1/intake/turn again.
        flow: done ? "checklist_loading" : "clarifying",
      };
    }

    case "EDIT_CLARIFICATION_ANSWER": {
      const editIndex = state.activeClarifyingQuestions.findIndex((q) => q.id === action.questionId);
      if (editIndex === -1) return state;
      const idsFromEditOnward = state.activeClarifyingQuestions.slice(editIndex).map((q) => q.id);
      const answeredQuestions = state.answeredQuestions.filter(
        (a) => !idsFromEditOnward.includes(a.questionId),
      );
      const clarification_answers = { ...state.sessionContext.clarification_answers };
      for (const id of idsFromEditOnward) delete clarification_answers[id];
      return {
        ...state,
        answeredQuestions,
        sessionContext: { ...state.sessionContext, clarification_answers },
        currentQuestionIndex: editIndex,
        // Changing an earlier answer can change the required document set
        // and form schema entirely, so all downstream progress is discarded.
        checklist: null,
        formDraft: {},
        lastValidationResponse: null,
        dismissedFindingFields: [],
        flow: "clarifying",
      };
    }

    case "CHECKLIST_REQUEST_STARTED":
      return { ...state, isBusy: true, error: null };

    case "CHECKLIST_RESPONSE_RECEIVED": {
      const response = action.response;
      const trustMetadata: ProcedureCaseState["trustMetadata"] = {
        trust_state: response.trust_state,
        procedure_version: response.procedure_version,
        source_refs: response.source_refs,
        last_verified_at: response.last_verified_at,
        review_gate: response.review_gate,
        fixture_mode: response.fixture_mode,
        demo_mode: response.demo_mode,
      };
      const canRenderDemoChecklist =
        (response.fixture_mode || response.demo_mode) &&
        (response.required_documents.length > 0 ||
          response.optional_documents.length > 0 ||
          Object.keys(response.form_schema.properties ?? {}).length > 0);
      const flow: FlowState =
        response.trust_state === "official_review_required" && !canRenderDemoChecklist
          ? "official_review_required"
          : "checklist_review";
      return {
        ...state,
        isBusy: false,
        checklist: response,
        formDraft: initFormDraft(response),
        trustMetadata,
        flow,
        availability: { backendReachable: true, aiPathAvailable: state.availability.aiPathAvailable, degradeReason: null },
      };
    }

    case "CHECKLIST_REQUEST_FAILED":
      if (action.kind === "aborted") return { ...state, isBusy: false };
      return {
        ...state,
        isBusy: false,
        error: "Không thể tải checklist hồ sơ. Vui lòng thử lại.",
        availability: { ...state.availability, backendReachable: false, degradeReason: "backend_unreachable" },
        flow: "degraded",
      };

    case "CONFIRM_U2":
      if (state.flow !== "checklist_review" || !state.checklist) return state;
      return { ...state, flow: "form_editing" };

    case "UPDATE_FORM_FIELD":
      return {
        ...state,
        formDraft: { ...state.formDraft, [action.key]: action.value },
        dismissedFindingFields: state.dismissedFindingFields.includes(action.key)
          ? state.dismissedFindingFields
          : [...state.dismissedFindingFields, action.key],
      };

    case "RUN_PRECHECK_STARTED":
      return { ...state, isBusy: true, error: null, flow: "validating", dismissedFindingFields: [] };

    case "VALIDATION_RESPONSE_RECEIVED": {
      const response = action.response;
      const trustMetadata: ProcedureCaseState["trustMetadata"] = {
        trust_state: response.trust_state,
        procedure_version: response.procedure_version,
        source_refs: response.source_refs,
        last_verified_at: response.last_verified_at,
        review_gate: response.review_gate,
        fixture_mode: response.fixture_mode,
        demo_mode: response.demo_mode,
      };
      let flow: FlowState;
      if (response.trust_state === "official_review_required" && !response.demo_mode) flow = "official_review_required";
      else if (response.verdict === "needs_fix") flow = "needs_fix";
      else flow = "pass_preliminary";
      return {
        ...state,
        isBusy: false,
        lastValidationResponse: response,
        sessionContext: response.proposed_session_context ?? state.sessionContext,
        trustMetadata,
        flow,
        availability: { backendReachable: true, aiPathAvailable: state.availability.aiPathAvailable, degradeReason: null },
      };
    }

    case "VALIDATION_REQUEST_FAILED":
      if (action.kind === "aborted") return { ...state, isBusy: false };
      return {
        ...state,
        isBusy: false,
        error: "Không thể chạy kiểm tra sơ bộ. Vui lòng thử lại.",
        availability: { ...state.availability, backendReachable: false, degradeReason: "backend_unreachable" },
        flow: "degraded",
      };

    case "CONFIRM_U3":
      // U3 is a review acknowledgement; no submission endpoint is in scope.
      return state;

    case "SELECT_STATIC_PROCEDURE":
      return {
        ...state,
        sessionContext: { ...state.sessionContext, procedure_id: action.procedureId },
        flow: "checklist_loading",
      };

    case "RECORD_FEEDBACK":
      return { ...state, feedbackLog: [...state.feedbackLog, action.entry] };

    case "CANCEL_REQUEST":
      return { ...state, isBusy: false };

    case "RESET_SESSION":
      return createInitialState(action.sessionId);

    case "HYDRATE": {
      const persisted = action.persisted;
      const fresh = createInitialState(persisted.sessionId);
      return {
        ...fresh,
        sessionId: persisted.sessionId,
        sessionContext: {
          ...fresh.sessionContext,
          ...persisted.sessionContext,
          acknowledged_review_gates: persisted.sessionContext.acknowledged_review_gates ?? [],
          reviewed_document_ids: persisted.sessionContext.reviewed_document_ids ?? [],
        },
        transcript: persisted.transcript.length > 0 ? persisted.transcript : fresh.transcript,
        answeredQuestions: persisted.answeredQuestions,
        checklist: persisted.checklist,
        formDraft: persisted.formDraft,
        lastValidationResponse: persisted.lastValidationResponse,
        flow: persisted.flow,
        lastStableFlow: persisted.lastStableFlow ?? persisted.flow,
      };
    }

    default:
      return state;
  }
}
