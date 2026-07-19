import { describe, expect, it } from "vitest";
import { createInitialState } from "./procedureCaseReducer";
import {
  resolveCitations,
  selectAvailabilityBanner,
  selectCanRenderForm,
  selectCanRunPrecheck,
  selectGroupedChecklist,
  selectProgressStage,
  selectRightPaneMode,
} from "./procedureCase.selectors";
import type { ChecklistResponse, FlowState, ProcedureCaseState } from "./procedureCase.types";

function checklistResponse(): ChecklistResponse {
  return {
    trust_state: "verified_guidance",
    procedure_version: "v1",
    source_refs: [],
    last_verified_at: "2026-07-17",
    review_gate: null,
    fixture_mode: false,
    demo_mode: false,
    procedure_id: "dang-ky-khai-sinh",
    procedure_name: "Đăng ký khai sinh",
    required_documents: [
      { id: "doc1", label: "Giấy chứng sinh", kind: "required", description: "d", source_ref_ids: [], condition: null },
      { id: "doc2", label: "CCCD cha", kind: "conditional", description: "d", source_ref_ids: [], condition: null },
    ],
    optional_documents: [
      { id: "doc3", label: "Sổ hộ khẩu", kind: "optional", description: "d", source_ref_ids: [], condition: null },
      { id: "doc4", label: "Giấy xác nhận nơi cư trú", kind: "conditional", description: "d", source_ref_ids: [], condition: null },
    ],
    steps: [{ order: 1, title: "Nộp hồ sơ", detail: "detail" }],
    form_schema: {
      type: "object",
      properties: {
        child_name: { type: "string", title: "Họ tên trẻ" },
        dob: { type: "string", title: "Ngày sinh", format: "date" },
      },
      required: ["child_name", "dob"],
    },
    message_plain: "checklist",
  };
}

describe("selectGroupedChecklist", () => {
  it("groups items from both backend arrays by their own kind, each item appearing exactly once", () => {
    const state = { ...createInitialState("s1"), checklist: checklistResponse() };
    const grouped = selectGroupedChecklist(state);
    expect(grouped.required.map((i) => i.id)).toEqual(["doc1"]);
    expect(grouped.optional.map((i) => i.id)).toEqual(["doc3"]);
    // conditional items sourced from both the required_documents and
    // optional_documents backend arrays land in the same group.
    expect(grouped.conditional.map((i) => i.id).sort()).toEqual(["doc2", "doc4"]);
  });

  it("returns empty groups when no checklist is loaded", () => {
    const grouped = selectGroupedChecklist(createInitialState("s1"));
    expect(grouped).toEqual({ required: [], conditional: [], optional: [] });
  });
});

describe("selectProgressStage", () => {
  const EXPECTED_STAGE: Record<Exclude<FlowState, "degraded" | "official_review_required">, number> = {
    idle: 1,
    identifying_procedure: 1,
    procedure_review: 1,
    clarifying: 2,
    checklist_loading: 3,
    checklist_review: 3,
    form_editing: 4,
    validating: 5,
    needs_fix: 5,
    pass_preliminary: 6,
  };

  it("maps every non-overlay flow state to its stage in the 6-stage rail", () => {
    const base = createInitialState("s1");
    for (const [flow, expectedId] of Object.entries(EXPECTED_STAGE) as [FlowState, number][]) {
      expect(selectProgressStage({ ...base, flow, lastStableFlow: flow }).id, `flow=${flow}`).toBe(expectedId);
      expect(selectProgressStage({ ...base, flow, lastStableFlow: flow }).total).toBe(6);
    }
  });

  it("resolves degraded/official_review_required via lastStableFlow instead of regressing to stage 1", () => {
    const base = createInitialState("s1");
    // Regression case: a user mid form_editing whose backend goes
    // unreachable must keep showing stage 4 ("Tờ khai"), not stage 1 —
    // this is the fix for the stale-form-at-step-1 bug.
    expect(
      selectProgressStage({ ...base, flow: "degraded", lastStableFlow: "form_editing" }).id,
    ).toBe(4);
    expect(
      selectProgressStage({ ...base, flow: "official_review_required", lastStableFlow: "validating" }).id,
    ).toBe(5);
  });
});

describe("selectRightPaneMode", () => {
  const EXPECTED_MODE: Record<Exclude<FlowState, "degraded" | "official_review_required">, string> = {
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

  it("maps every non-overlay flow state to its exact right-pane mode", () => {
    const base = createInitialState("s1");
    for (const [flow, expectedMode] of Object.entries(EXPECTED_MODE) as [FlowState, string][]) {
      expect(selectRightPaneMode({ ...base, flow, lastStableFlow: flow }).mode, `flow=${flow}`).toBe(expectedMode);
    }
  });

  it("official_review_required always renders official_review regardless of checklist data", () => {
    const state = { ...createInitialState("s1"), flow: "official_review_required" as const, checklist: checklistResponse() };
    expect(selectRightPaneMode(state).mode).toBe("official_review");
  });

  it("degraded preserves the last stable pane mode and flags degraded:true", () => {
    const state = {
      ...createInitialState("s1"),
      flow: "degraded" as const,
      lastStableFlow: "form_editing" as const,
      checklist: checklistResponse(),
    };
    const view = selectRightPaneMode(state);
    expect(view.mode).toBe("form");
    expect(view.degraded).toBe(true);
  });

  it("no-form-before-U2: checklist_review never renders the form pane even with a populated checklist", () => {
    const state = { ...createInitialState("s1"), flow: "checklist_review" as const, checklist: checklistResponse() };
    expect(selectRightPaneMode(state).mode).toBe("checklist_review");
    expect(selectCanRenderForm(state)).toBe(false);
  });

  it("selectCanRenderForm is true only from form_editing onward", () => {
    const base = createInitialState("s1");
    for (const flow of ["form_editing", "validating", "needs_fix", "pass_preliminary"] as const) {
      expect(selectCanRenderForm({ ...base, flow, lastStableFlow: flow }), `flow=${flow}`).toBe(true);
    }
    for (const flow of ["idle", "identifying_procedure", "procedure_review", "clarifying", "checklist_loading", "checklist_review"] as const) {
      expect(selectCanRenderForm({ ...base, flow, lastStableFlow: flow }), `flow=${flow}`).toBe(false);
    }
  });
});

describe("selectCanRunPrecheck", () => {
  it("is false until every required schema field is filled", () => {
    const state: ProcedureCaseState = {
      ...createInitialState("s1"),
      checklist: checklistResponse(),
      formDraft: { child_name: "An", dob: "" },
    };
    expect(selectCanRunPrecheck(state)).toBe(false);
    const filled: ProcedureCaseState = { ...state, formDraft: { child_name: "An", dob: "2026-01-01" } };
    expect(selectCanRunPrecheck(filled)).toBe(true);
  });

  it("stays disabled for a demo fixture without verified guidance", () => {
    const checklist = checklistResponse();
    const state: ProcedureCaseState = {
      ...createInitialState("s1"),
      checklist: {
        ...checklist,
        trust_state: "official_review_required",
        fixture_mode: true,
        last_verified_at: null,
      },
      formDraft: { child_name: "An", dob: "2026-01-01" },
    };

    expect(selectCanRunPrecheck(state)).toBe(false);
  });

  it("allows deterministic precheck for demo-approved content without promoting trust", () => {
    const checklist = checklistResponse();
    const state: ProcedureCaseState = {
      ...createInitialState("s1"),
      checklist: {
        ...checklist,
        trust_state: "official_review_required",
        demo_mode: true,
        last_verified_at: null,
      },
      formDraft: { child_name: "An", dob: "2026-01-01" },
    };

    expect(selectCanRunPrecheck(state)).toBe(true);
    expect(state.checklist?.trust_state).toBe("official_review_required");
  });
});

describe("resolveCitations", () => {
  it("resolves ref ids against a citation list, preserving order and dropping unknown ids", () => {
    const sourceRefs = [
      { ref_id: "s1", title: "Luật A", url_or_ref: null, effective_from: null, effective_to: null },
      { ref_id: "s2", title: "Nghị định B", url_or_ref: null, effective_from: null, effective_to: null },
    ];
    expect(resolveCitations(["s2", "s1", "missing"], sourceRefs).map((c) => c.title)).toEqual([
      "Nghị định B",
      "Luật A",
    ]);
  });
});

describe("selectAvailabilityBanner", () => {
  it("distinguishes ai_unavailable (warning, structured flow usable) from backend_unreachable (blocking)", () => {
    const aiDown = {
      ...createInitialState("s1"),
      availability: { backendReachable: true, aiPathAvailable: false, degradeReason: "ai_unavailable" as const },
    };
    const backendDown = {
      ...createInitialState("s1"),
      availability: { backendReachable: false, aiPathAvailable: false, degradeReason: "backend_unreachable" as const },
    };
    expect(selectAvailabilityBanner(aiDown).severity).toBe("warning");
    expect(selectAvailabilityBanner(backendDown).severity).toBe("blocking");
    expect(selectAvailabilityBanner(createInitialState("s1")).visible).toBe(false);
  });
});
