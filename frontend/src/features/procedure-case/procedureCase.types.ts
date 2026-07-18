// Types mirror backend/app/models/*.py field-for-field. Do not rename fields
// to "look nicer" in TS — the whole point of this module is to stop the
// frontend/backend contract from drifting again.

export type TrustState =
  | "verified_guidance"
  | "need_more_information"
  | "official_review_required";

export type ReviewGate = "U1" | "U2" | "U3";

export type FindingSeverity = "error" | "warning" | "info";

export type PrecheckVerdict = "pass_preliminary" | "needs_fix";

export interface Citation {
  ref_id: string;
  title: string;
  url_or_ref: string | null;
  effective_from: string | null;
  effective_to: string | null;
}

export interface TrustMetadata {
  trust_state: TrustState;
  procedure_version: string | null;
  source_refs: Citation[];
  last_verified_at: string | null;
  review_gate: ReviewGate | null;
  fixture_mode: boolean;
}

export interface SessionContext {
  procedure_id: string | null;
  procedure_version: string | null;
  clarification_answers: Record<string, unknown>;
  pending_question_ids: string[];
  review_state: string | null;
}

export function emptySessionContext(): SessionContext {
  return {
    procedure_id: null,
    procedure_version: null,
    clarification_answers: {},
    pending_question_ids: [],
    review_state: null,
  };
}

export interface ClarifyingQuestion {
  id: string;
  prompt: string;
  options: string[];
  why: string | null;
  required: boolean;
}

export interface ProcedureCandidate {
  procedure_id: string;
  name: string;
  reason: string;
}

// --- Requests ---

export interface IntakeRequest {
  session_id: string;
  message: string;
  session_context: SessionContext;
}

export interface ChecklistRequest {
  clarification_answers: Record<string, unknown>;
  procedure_version?: string;
}

export interface ValidationRequest {
  procedure_id: string;
  procedure_version?: string;
  form_data: Record<string, unknown>;
}

// --- Responses ---

export interface IntakeResponse extends TrustMetadata {
  session_id: string;
  detected_procedure_id: string | null;
  procedure: ProcedureCandidate | null;
  message_plain: string;
  clarifying_questions: ClarifyingQuestion[];
  proposed_session_context: SessionContext;
}

export type ChecklistItemKind = "required" | "conditional" | "optional";

export interface ChecklistItem {
  id: string;
  label: string;
  kind: ChecklistItemKind;
  description: string;
  source_ref_ids: string[];
  condition: Record<string, unknown> | null;
}

export interface ProcedureStep {
  order: number;
  title: string;
  detail: string;
}

export interface FormSchemaProperty {
  type: string;
  title: string;
  minLength?: number;
  format?: string;
}

export interface FormSchema {
  type: string;
  properties: Record<string, FormSchemaProperty>;
  required?: string[];
}

export interface ChecklistResponse extends TrustMetadata {
  procedure_id: string;
  procedure_name: string;
  required_documents: ChecklistItem[];
  optional_documents: ChecklistItem[];
  steps: ProcedureStep[];
  form_schema: FormSchema;
  message_plain: string;
}

export interface Finding {
  field_id: string | null;
  severity: FindingSeverity;
  rule_id: string;
  message: string;
  fix_hint: string | null;
  source_ref_ids: string[];
}

export interface ValidationResponse extends TrustMetadata {
  procedure_id: string;
  verdict: PrecheckVerdict | null;
  findings: Finding[];
  summary_message: string;
}

export interface ProcedureSummary {
  procedure_id: string;
  name: string;
  version: string | null;
  review_status: string;
  fixture_mode: boolean;
}

// --- Frontend-only case state ---

export type FlowState =
  | "idle"
  | "identifying_procedure"
  | "procedure_review"
  | "clarifying"
  | "checklist_loading"
  | "checklist_review"
  | "form_editing"
  | "validating"
  | "needs_fix"
  | "pass_preliminary"
  | "official_review_required"
  | "degraded";

export type DegradeReason = "ai_unavailable" | "backend_unreachable" | null;

export interface AvailabilityState {
  backendReachable: boolean;
  aiPathAvailable: boolean;
  degradeReason: DegradeReason;
}

export function initialAvailability(): AvailabilityState {
  return { backendReachable: true, aiPathAvailable: true, degradeReason: null };
}

export interface TranscriptMessage {
  role: "user" | "assistant";
  content: string;
  sourceRefs?: Citation[];
}

export type FormFieldValue = string | number | boolean | null;

export interface AnsweredQuestion {
  questionId: string;
  value: string;
  answeredAt: string;
}

export type FeedbackContext = "checklist" | "precheck";

export type FeedbackReasonCode =
  | "sai_thu_tuc"
  | "thieu_thua_giay_to"
  | "kho_hieu"
  | "loi_precheck_sai"
  | "khac";

export interface FeedbackEntry {
  context: FeedbackContext;
  session_id: string;
  procedure_id: string | null;
  procedure_version: string | null;
  trust_state: TrustState | null;
  verdict: PrecheckVerdict | null;
  vote: "up" | "down";
  reason?: FeedbackReasonCode;
  note?: string;
  created_at: string;
}

export interface ProcedureCaseState {
  flow: FlowState;
  // Last flow value that was not "degraded"/"official_review_required".
  // Overlay states use this to keep the progress rail/right pane on the
  // stage the user was actually at, instead of regressing to step 1.
  lastStableFlow: FlowState;
  availability: AvailabilityState;
  sessionId: string;
  sessionContext: SessionContext;
  transcript: TranscriptMessage[];
  activeClarifyingQuestions: ClarifyingQuestion[];
  currentQuestionIndex: number;
  answeredQuestions: AnsweredQuestion[];
  lastIntakeResponse: IntakeResponse | null;
  checklist: ChecklistResponse | null;
  formDraft: Record<string, FormFieldValue>;
  lastValidationResponse: ValidationResponse | null;
  trustMetadata: TrustMetadata | null;
  feedbackLog: FeedbackEntry[];
  isBusy: boolean;
  error: string | null;
}

// Serializable subset persisted to sessionStorage (no AbortController, no functions).
export type PersistedProcedureCaseState = Pick<
  ProcedureCaseState,
  | "sessionId"
  | "sessionContext"
  | "transcript"
  | "answeredQuestions"
  | "checklist"
  | "formDraft"
  | "lastValidationResponse"
  | "flow"
  | "lastStableFlow"
>;
