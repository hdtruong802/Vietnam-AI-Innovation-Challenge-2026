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

const STAGE_LABELS: Record<FlowState, { step: number; label: string }> = {
  idle: { step: 1, label: "Xác định thủ tục" },
  identifying_procedure: { step: 1, label: "Xác định thủ tục" },
  procedure_review: { step: 1, label: "Xác định thủ tục" },
  clarifying: { step: 2, label: "Làm rõ thông tin" },
  checklist_loading: { step: 3, label: "Checklist hồ sơ" },
  checklist_review: { step: 3, label: "Checklist hồ sơ" },
  form_editing: { step: 4, label: "Điền tờ khai" },
  validating: { step: 5, label: "Kiểm tra sơ bộ" },
  needs_fix: { step: 5, label: "Kiểm tra sơ bộ" },
  pass_preliminary: { step: 5, label: "Kiểm tra sơ bộ" },
  official_review_required: { step: 5, label: "Kiểm tra sơ bộ" },
  degraded: { step: 1, label: "Xác định thủ tục" },
};

export const STEPPER_TOTAL_STEPS = 5;

export function selectStepperProgress(state: ProcedureCaseState): { current: number; total: number; label: string } {
  const { step, label } = STAGE_LABELS[state.flow];
  return { current: step, total: STEPPER_TOTAL_STEPS, label };
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
