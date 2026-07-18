import type {
  ChecklistItem,
  Citation,
  Finding,
  FlowState,
  ProcedureCaseState,
  TrustState,
} from "./procedureCase.types";

export interface GroupedChecklist {
  required: ChecklistItem[];
  conditional: ChecklistItem[];
  optional: ChecklistItem[];
}

/**
 * Normalizes the backend's two arrays (required_documents/optional_documents)
 * into three groups keyed by each item's own `kind`, since a `kind:
 * "conditional"` item can appear in either backend array.
 */
export function selectGroupedChecklist(state: ProcedureCaseState): GroupedChecklist {
  const grouped: GroupedChecklist = { required: [], conditional: [], optional: [] };
  if (!state.checklist) return grouped;
  const all = [...state.checklist.required_documents, ...state.checklist.optional_documents];
  for (const item of all) {
    grouped[item.kind].push(item);
  }
  return grouped;
}

// FlowState values that are cross-cutting overlays (can interrupt either
// capability, not a stage of their own) — excluded from the stage/pane
// tables below and resolved via state.lastStableFlow instead.
type StableFlowState = Exclude<FlowState, "degraded" | "official_review_required">;

export interface ProgressStage {
  id: 1 | 2 | 3 | 4 | 5 | 6;
  label: string;
}

const PROGRESS_STAGES: Record<StableFlowState, ProgressStage> = {
  idle: { id: 1, label: "Nhu cầu" },
  identifying_procedure: { id: 1, label: "Nhu cầu" },
  procedure_review: { id: 1, label: "Nhu cầu" },
  clarifying: { id: 2, label: "Điều kiện" },
  checklist_loading: { id: 3, label: "Giấy tờ" },
  checklist_review: { id: 3, label: "Giấy tờ" },
  form_editing: { id: 4, label: "Tờ khai" },
  validating: { id: 5, label: "Kiểm tra" },
  needs_fix: { id: 5, label: "Kiểm tra" },
  pass_preliminary: { id: 6, label: "Hoàn tất" },
};

export const PROGRESS_STAGE_COUNT = 6;

/**
 * Progress-rail stage. degraded/official_review_required are overlays, not
 * stages: they resolve through lastStableFlow so the rail doesn't regress to
 * step 1 while the user's real in-progress data (checklist/form) is still
 * on screen — this is the fix for the stale-form-at-step-1 regression.
 */
export function selectProgressStage(state: ProcedureCaseState): ProgressStage & { total: number } {
  const flow: StableFlowState =
    state.flow === "degraded" || state.flow === "official_review_required"
      ? (state.lastStableFlow as StableFlowState)
      : (state.flow as StableFlowState);
  return { ...(PROGRESS_STAGES[flow] ?? PROGRESS_STAGES.idle), total: PROGRESS_STAGE_COUNT };
}

export type RightPaneMode =
  | "empty"
  | "procedure_review"
  | "clarifying"
  | "checklist_loading"
  | "checklist_review"
  | "form"
  | "official_review";

const RIGHT_PANE_MODES: Record<StableFlowState, RightPaneMode> = {
  idle: "empty",
  identifying_procedure: "empty",
  procedure_review: "procedure_review",
  clarifying: "clarifying",
  checklist_loading: "checklist_loading",
  checklist_review: "checklist_review",
  form_editing: "form",
  validating: "form",
  needs_fix: "form",
  pass_preliminary: "form",
};

export interface RightPaneView {
  mode: RightPaneMode;
  /** true when the current flow is the "degraded" overlay on top of `mode`. */
  degraded: boolean;
}

/**
 * Explicit allow-list of which right-pane mode each FlowState renders.
 * Deliberately does NOT branch on `state.checklist` truthiness: checklist
 * data already exists during checklist_review (before U2), so a
 * checklist-truthy check would leak the form pane one step early.
 */
export function selectRightPaneMode(state: ProcedureCaseState): RightPaneView {
  if (state.flow === "official_review_required") return { mode: "official_review", degraded: false };
  if (state.flow === "degraded") {
    const stableMode = RIGHT_PANE_MODES[state.lastStableFlow as StableFlowState] ?? "empty";
    return { mode: stableMode, degraded: true };
  }
  return { mode: RIGHT_PANE_MODES[state.flow as StableFlowState], degraded: false };
}

/** Form must never render before U2 confirmation (flow >= form_editing). */
export function selectCanRenderForm(state: ProcedureCaseState): boolean {
  return selectRightPaneMode(state).mode === "form";
}

/** Precheck panel is only mounted once the form pane itself is mounted. */
export function selectCanRenderPrecheck(state: ProcedureCaseState): boolean {
  return selectRightPaneMode(state).mode === "form";
}

export function selectChecklistCounts(state: ProcedureCaseState) {
  const grouped = selectGroupedChecklist(state);
  return {
    requiredCount: grouped.required.length,
    conditionalCount: grouped.conditional.length,
    optionalCount: grouped.optional.length,
    filledFieldCount: Object.values(state.formDraft).filter((v) => v !== "" && v !== null && v !== undefined)
      .length,
  };
}

export function selectCanConfirmU1(state: ProcedureCaseState): boolean {
  return state.flow === "procedure_review" && !!state.lastIntakeResponse?.procedure;
}

export function selectCanConfirmU2(state: ProcedureCaseState): boolean {
  return state.flow === "checklist_review" && !!state.checklist;
}

export function selectCanRunPrecheck(state: ProcedureCaseState): boolean {
  if (!state.checklist) return false;
  const required = state.checklist.form_schema.required ?? [];
  return required.every((key) => {
    const value = state.formDraft[key];
    return value !== "" && value !== null && value !== undefined;
  });
}

export function selectFieldFinding(state: ProcedureCaseState, fieldId: string): Finding | undefined {
  return state.lastValidationResponse?.findings.find((f) => f.field_id === fieldId);
}

export function selectActiveTrustState(state: ProcedureCaseState): TrustState | null {
  return state.trustMetadata?.trust_state ?? null;
}

export function resolveCitations(refIds: string[], sourceRefs: Citation[]): Citation[] {
  const byId = new Map(sourceRefs.map((c) => [c.ref_id, c]));
  return refIds.map((id) => byId.get(id)).filter((c): c is Citation => !!c);
}

export interface AvailabilityBanner {
  visible: boolean;
  severity: "blocking" | "warning";
  message: string;
  showStaticMenu: boolean;
}

export function selectAvailabilityBanner(state: ProcedureCaseState): AvailabilityBanner {
  const { degradeReason } = state.availability;
  if (degradeReason === "backend_unreachable") {
    return {
      visible: true,
      severity: "blocking",
      message:
        "Hệ thống tạm thời không khả dụng. Vui lòng thử lại sau ít phút hoặc sử dụng kênh chính thức.",
      showStaticMenu: true,
    };
  }
  if (degradeReason === "ai_unavailable") {
    return {
      visible: true,
      severity: "warning",
      message:
        "Trợ lý AI tạm thời gián đoạn. Bạn vẫn có thể tiếp tục qua danh mục thủ tục có sẵn.",
      showStaticMenu: true,
    };
  }
  return { visible: false, severity: "warning", message: "", showStaticMenu: false };
}
