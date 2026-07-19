import { describe, expect, it } from "vitest";
import { FIXTURE_KEYS, getFixtureState, type FixtureKey } from "./procedureCase.fixtures";
import {
  selectCanRenderForm,
  selectProgressStage,
  selectRightPaneMode,
  type RightPaneMode,
} from "./procedureCase.selectors";
import type { FlowState } from "./procedureCase.types";

interface Expectation {
  flow: FlowState;
  mode: RightPaneMode;
  stageId: number;
  canRenderForm: boolean;
}

const EXPECTATIONS: Record<FixtureKey, Expectation> = {
  idle: { flow: "idle", mode: "empty", stageId: 1, canRenderForm: false },
  procedure_review: { flow: "procedure_review", mode: "procedure_review", stageId: 1, canRenderForm: false },
  clarifying: { flow: "clarifying", mode: "clarifying", stageId: 2, canRenderForm: false },
  checklist_loading: { flow: "checklist_loading", mode: "checklist_loading", stageId: 3, canRenderForm: false },
  checklist_review: { flow: "checklist_review", mode: "checklist_review", stageId: 3, canRenderForm: false },
  form_editing: { flow: "form_editing", mode: "form", stageId: 4, canRenderForm: true },
  validating: { flow: "validating", mode: "form", stageId: 5, canRenderForm: true },
  needs_fix: { flow: "needs_fix", mode: "form", stageId: 5, canRenderForm: true },
  pass_preliminary: { flow: "pass_preliminary", mode: "form", stageId: 6, canRenderForm: true },
  official_review_required: { flow: "official_review_required", mode: "official_review", stageId: 1, canRenderForm: false },
  // Regression fixture: degraded on top of form_editing. Stage/mode must
  // resolve via lastStableFlow ("form_editing"), not regress to stage 1.
  degraded_after_form: { flow: "degraded", mode: "form", stageId: 4, canRenderForm: true },
};

describe.each(FIXTURE_KEYS)("fixture: %s", (key) => {
  const expected = EXPECTATIONS[key];

  it(`has flow "${expected.flow}"`, () => {
    expect(getFixtureState(key).flow).toBe(expected.flow);
  });

  it(`resolves RightPaneMode "${expected.mode}"`, () => {
    expect(selectRightPaneMode(getFixtureState(key)).mode).toBe(expected.mode);
  });

  it(`resolves progress stage ${expected.stageId}`, () => {
    expect(selectProgressStage(getFixtureState(key)).id).toBe(expected.stageId);
  });

  it(`selectCanRenderForm is ${expected.canRenderForm}`, () => {
    expect(selectCanRenderForm(getFixtureState(key))).toBe(expected.canRenderForm);
  });
});

describe("fixture required data", () => {
  it("procedure_review carries a detected procedure candidate", () => {
    const state = getFixtureState("procedure_review");
    expect(state.lastIntakeResponse?.procedure).not.toBeNull();
  });

  it("clarifying carries at least one active clarifying question", () => {
    const state = getFixtureState("clarifying");
    expect(state.activeClarifyingQuestions.length).toBeGreaterThan(0);
  });

  it("checklist_review onward carries a loaded checklist", () => {
    for (const key of ["checklist_review", "form_editing", "validating", "needs_fix", "pass_preliminary", "degraded_after_form"] as const) {
      expect(getFixtureState(key).checklist, `key=${key}`).not.toBeNull();
    }
  });

  it("needs_fix/pass_preliminary carry a validation response", () => {
    expect(getFixtureState("needs_fix").lastValidationResponse).not.toBeNull();
    expect(getFixtureState("pass_preliminary").lastValidationResponse).not.toBeNull();
  });

  it("needs_fix has at least one error-severity finding", () => {
    const findings = getFixtureState("needs_fix").lastValidationResponse?.findings ?? [];
    expect(findings.some((f) => f.severity === "error")).toBe(true);
  });

  it("official_review_required trust state matches its flow", () => {
    expect(getFixtureState("official_review_required").trustMetadata?.trust_state).toBe(
      "official_review_required",
    );
  });
});

describe("fixture: degraded_after_form regression proof", () => {
  it("is backend-unreachable but keeps checklist/formDraft/lastStableFlow intact", () => {
    const state = getFixtureState("degraded_after_form");
    expect(state.availability.backendReachable).toBe(false);
    expect(state.availability.degradeReason).toBe("backend_unreachable");
    expect(state.lastStableFlow).toBe("form_editing");
    expect(state.checklist).not.toBeNull();
    expect(Object.values(state.formDraft).some((v) => v !== "" && v !== null)).toBe(true);
  });

  it("right pane stays on the form (not the empty/idle state) while degraded", () => {
    const view = selectRightPaneMode(getFixtureState("degraded_after_form"));
    expect(view.mode).toBe("form");
    expect(view.degraded).toBe(true);
  });
});
