import { describe, expect, it } from "vitest";
import { createInitialState } from "./procedureCaseReducer";
import {
  resolveCitations,
  selectAvailabilityBanner,
  selectCanRunPrecheck,
  selectGroupedChecklist,
  selectStepperProgress,
} from "./procedureCase.selectors";
import type { ChecklistResponse, ProcedureCaseState } from "./procedureCase.types";

function checklistResponse(): ChecklistResponse {
  return {
    trust_state: "verified_guidance",
    procedure_version: "v1",
    source_refs: [],
    last_verified_at: "2026-07-17",
    review_gate: null,
    fixture_mode: false,
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

describe("selectStepperProgress", () => {
  it("maps each flow state to a stage in the fixed 5-step, procedure-agnostic sequence", () => {
    const base = createInitialState("s1");
    expect(selectStepperProgress({ ...base, flow: "clarifying" })).toEqual({
      current: 2,
      total: 5,
      label: "Làm rõ thông tin",
    });
    expect(selectStepperProgress({ ...base, flow: "checklist_review" }).current).toBe(3);
    expect(selectStepperProgress({ ...base, flow: "form_editing" }).current).toBe(4);
    expect(selectStepperProgress({ ...base, flow: "needs_fix" }).current).toBe(5);
    expect(selectStepperProgress({ ...base, flow: "pass_preliminary" }).current).toBe(5);
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
