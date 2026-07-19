"use client";

import { useCallback, useEffect, useReducer, useRef } from "react";
import {
  ApiError,
  checkHealth,
  postChecklist,
  postIntakeTurn,
  postValidate,
  submitFeedback,
} from "./api";
import { INPUT_MAX_LENGTH } from "./procedureCase.constants";
import { createInitialState, procedureCaseReducer } from "./procedureCaseReducer";
import { clearSession, loadSession, saveSession } from "./sessionStorage";
import type {
  FeedbackContext,
  FeedbackReasonCode,
  FormFieldValue,
  IntakeRequest,
  PersistedProcedureCaseState,
  ProcedureCaseState,
  ReviewGate,
} from "./procedureCase.types";

function generateSessionId(): string {
  return "session_" + Math.random().toString(36).slice(2, 15) + Math.random().toString(36).slice(2, 15);
}

function toApiFailureKind(err: unknown): "network" | "timeout" | "aborted" | "http" {
  if (err instanceof ApiError) return err.kind;
  return "network";
}

/**
 * @param fixtureState Preview-only. When set, the hook seeds state from this
 * fixture once and becomes read-only: every effect that would touch the
 * network or sessionStorage, and every action that would do the same, is a
 * no-op. This keeps a fixture preview deterministic (state never drifts
 * from the fixture) and side-effect-free (no real API calls, no real
 * session persisted/cleared). When undefined — the only path the real app
 * uses — nothing here changes: zero behavior difference from before.
 */
export function useProcedureCase(
  initialMessage?: string,
  initialProcedureId?: string,
  fixtureState?: ProcedureCaseState,
) {
  const [state, dispatch] = useReducer(procedureCaseReducer, undefined, () => {
    if (fixtureState) return fixtureState;
    const persisted = loadSession();
    if (persisted) {
      const base = createInitialState(persisted.sessionId);
      return procedureCaseReducer(base, { type: "HYDRATE", persisted });
    }
    return createInitialState(generateSessionId());
  });

  const stateRef = useRef(state);
  useEffect(() => {
    stateRef.current = state;
  });

  const controllerRef = useRef<AbortController | null>(null);
  const checklistTriggeredRef = useRef(false);
  const mountHandoffDone = useRef(false);

  // Persist a serializable subset to sessionStorage on every change.
  useEffect(() => {
    if (fixtureState) return;
    const persisted: PersistedProcedureCaseState = {
      sessionId: state.sessionId,
      sessionContext: state.sessionContext,
      transcript: state.transcript,
      answeredQuestions: state.answeredQuestions,
      checklist: state.checklist,
      formDraft: state.formDraft,
      lastValidationResponse: state.lastValidationResponse,
      flow: state.flow,
      lastStableFlow: state.lastStableFlow,
    };
    saveSession(persisted);
  }, [state, fixtureState]);

  const retryHealthCheck = useCallback(async () => {
    if (fixtureState) return false;
    const ok = await checkHealth();
    dispatch({ type: "HEALTH_CHECK_RESULT", ok });
    return ok;
  }, [fixtureState]);

  // Initial health probe on mount.
  useEffect(() => {
    if (fixtureState) return;
    void retryHealthCheck();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const requestIntake = useCallback(
    async (request: IntakeRequest) => {
      if (fixtureState) return null;
      dispatch({ type: "INTAKE_REQUEST_STARTED" });
      const controller = new AbortController();
      controllerRef.current = controller;
      try {
        const response = await postIntakeTurn(request, controller.signal);
        dispatch({ type: "INTAKE_RESPONSE_RECEIVED", response });
        return response;
      } catch (err) {
        dispatch({ type: "INTAKE_REQUEST_FAILED", kind: toApiFailureKind(err) });
        return null;
      } finally {
        controllerRef.current = null;
      }
    },
    [fixtureState],
  );

  const selectStaticProcedure = useCallback(
    async (procedureId: string) => {
      if (fixtureState) return;
      const { sessionId, sessionContext } = stateRef.current;
      if (stateRef.current.isBusy) return;
      await requestIntake({
        session_id: sessionId,
        message: "Người dùng chọn thủ tục từ danh sách MVP.",
        session_context: sessionContext,
        turn_type: "procedure_select",
        selected_procedure_id: procedureId,
      });
    },
    [fixtureState, requestIntake],
  );

  const sendMessage = useCallback(
    async (rawText: string) => {
      if (fixtureState) return;
      const text = rawText.trim().slice(0, INPUT_MAX_LENGTH);
      if (!text || stateRef.current.isBusy) return;

      dispatch({ type: "SEND_MESSAGE", text });
      await requestIntake({
        session_id: stateRef.current.sessionId,
        message: text,
        session_context: stateRef.current.sessionContext,
        turn_type: "free_text",
      });
    },
    [fixtureState, requestIntake],
  );

  const fetchChecklist = useCallback(async () => {
    if (fixtureState) return;
    const { sessionId, sessionContext } = stateRef.current;
    const procedureId = sessionContext.procedure_id;
    if (!procedureId) return;

    dispatch({ type: "CHECKLIST_REQUEST_STARTED" });
    const controller = new AbortController();
    controllerRef.current = controller;
    try {
      const response = await postChecklist(
        procedureId,
        {
          clarification_answers: sessionContext.clarification_answers,
          procedure_version: sessionContext.procedure_version ?? undefined,
          session_context: sessionContext,
        },
        controller.signal,
      );
      dispatch({ type: "CHECKLIST_RESPONSE_RECEIVED", response });
    } catch (err) {
      dispatch({ type: "CHECKLIST_REQUEST_FAILED", kind: toApiFailureKind(err) });
    } finally {
      controllerRef.current = null;
    }
    void sessionId; // retained for symmetry with other actions; not sent to this endpoint
  }, [fixtureState]);

  // checklist_loading is a transient state meant to trigger a fetch — this
  // is the single place that happens, regardless of which action produced it
  // (U1 confirm with no questions, last clarification answered, or picking
  // a procedure from the static fallback menu).
  useEffect(() => {
    if (fixtureState) return;
    if (state.flow !== "checklist_loading") {
      checklistTriggeredRef.current = false;
      return;
    }
    if (checklistTriggeredRef.current) return;
    checklistTriggeredRef.current = true;
    void fetchChecklist();
  }, [state.flow, fetchChecklist, fixtureState]);

  const confirmU1 = useCallback(async () => {
    if (fixtureState) return;
    const { sessionId, sessionContext } = stateRef.current;
    if (stateRef.current.isBusy || !sessionContext.procedure_id) return;
    await requestIntake({
      session_id: sessionId,
      message: "Người dùng xác nhận thủ tục trong phiên hiện tại.",
      session_context: sessionContext,
      turn_type: "review_acknowledgement",
      review_gate_acknowledgement: "U1",
    });
  }, [fixtureState, requestIntake]);

  const rejectU1 = useCallback(() => {
    if (fixtureState) return;
    dispatch({ type: "REJECT_U1" });
  }, [fixtureState]);

  const answerClarification = useCallback(
    async (questionId: string, value: string) => {
      if (fixtureState) return;
      const { sessionId, sessionContext } = stateRef.current;
      if (stateRef.current.isBusy) return;
      await requestIntake({
        session_id: sessionId,
        message: "Người dùng trả lời câu hỏi làm rõ.",
        session_context: sessionContext,
        turn_type: "clarification_answer",
        clarification_answer: { question_id: questionId, value },
      });
    },
    [fixtureState, requestIntake],
  );

  const editClarificationAnswer = useCallback(
    (questionId: string) => {
      if (fixtureState) return;
      dispatch({ type: "EDIT_CLARIFICATION_ANSWER", questionId });
    },
    [fixtureState],
  );

  const acknowledgeReviewGate = useCallback(
    async (reviewGate: ReviewGate) => {
      if (fixtureState) return null;
      const { sessionId, sessionContext } = stateRef.current;
      if (stateRef.current.isBusy || !sessionContext.procedure_id) return null;
      dispatch({ type: "INTAKE_REQUEST_STARTED" });
      const controller = new AbortController();
      controllerRef.current = controller;
      try {
        const response = await postIntakeTurn(
          {
            session_id: sessionId,
            message: "Người dùng xác nhận điểm review trong phiên hiện tại.",
            session_context: sessionContext,
            turn_type: "review_acknowledgement",
            review_gate_acknowledgement: reviewGate,
          },
          controller.signal,
        );
        if (response.trust_state === "official_review_required") {
          dispatch({ type: "INTAKE_RESPONSE_RECEIVED", response });
        } else {
          dispatch({ type: "SESSION_CONTEXT_UPDATED", sessionContext: response.proposed_session_context });
        }
        return response;
      } catch (err) {
        dispatch({ type: "INTAKE_REQUEST_FAILED", kind: toApiFailureKind(err) });
        return null;
      } finally {
        controllerRef.current = null;
      }
    },
    [fixtureState],
  );

  const confirmU2 = useCallback(async () => {
    if (fixtureState) return;
    const response = await acknowledgeReviewGate("U2");
    if (response?.trust_state === "verified_guidance") {
      dispatch({ type: "CONFIRM_U2" });
    }
  }, [fixtureState, acknowledgeReviewGate]);

  const updateFormField = useCallback(
    (key: string, value: FormFieldValue) => {
      if (fixtureState) return;
      dispatch({ type: "UPDATE_FORM_FIELD", key, value });
    },
    [fixtureState],
  );

  const runPrecheck = useCallback(async () => {
    if (fixtureState) return;
    const { checklist, formDraft, sessionContext } = stateRef.current;
    if (!checklist || stateRef.current.isBusy) return;

    dispatch({ type: "RUN_PRECHECK_STARTED" });
    const controller = new AbortController();
    controllerRef.current = controller;
    try {
      const response = await postValidate(
        {
          procedure_id: checklist.procedure_id,
          procedure_version: sessionContext.procedure_version ?? checklist.procedure_version ?? undefined,
          form_data: formDraft,
          session_context: sessionContext,
        },
        controller.signal,
      );
      dispatch({ type: "VALIDATION_RESPONSE_RECEIVED", response });
    } catch (err) {
      dispatch({ type: "VALIDATION_REQUEST_FAILED", kind: toApiFailureKind(err) });
    } finally {
      controllerRef.current = null;
    }
  }, [fixtureState]);

  const confirmU3 = useCallback(async () => {
    if (fixtureState) return;
    const response = await acknowledgeReviewGate("U3");
    if (response?.trust_state === "verified_guidance") {
      dispatch({ type: "CONFIRM_U3" });
    }
  }, [fixtureState, acknowledgeReviewGate]);

  const cancelRequest = useCallback(() => {
    if (fixtureState) return;
    controllerRef.current?.abort();
    dispatch({ type: "CANCEL_REQUEST" });
  }, [fixtureState]);

  const recordFeedback = useCallback(
    async (
      context: FeedbackContext,
      vote: "up" | "down",
      reason?: FeedbackReasonCode,
      note?: string,
    ) => {
      if (fixtureState) return;
      const { sessionId, sessionContext, trustMetadata, lastValidationResponse } = stateRef.current;
      const entry = {
        context,
        session_id: sessionId,
        procedure_id: sessionContext.procedure_id,
        procedure_version: sessionContext.procedure_version,
        trust_state: trustMetadata?.trust_state ?? null,
        verdict: lastValidationResponse?.verdict ?? null,
        vote,
        reason,
        note: note?.slice(0, 200),
        created_at: new Date().toISOString(),
      };
      dispatch({ type: "RECORD_FEEDBACK", entry });
      try {
        await submitFeedback(entry);
      } catch {
        // Feedback is best-effort and must never interrupt the procedure flow.
      }
    },
    [fixtureState],
  );

  const resetSession = useCallback(() => {
    // Guarded first: resetSession touches the real sessionStorage key via
    // clearSession(), which must never run against a fixture preview.
    if (fixtureState) return;
    controllerRef.current?.abort();
    clearSession();
    dispatch({ type: "RESET_SESSION", sessionId: generateSessionId() });
  }, [fixtureState]);

  // One-time handoff from the landing page: an initial message typed into
  // the hero search bar, or a procedure picked from a landing card.
  useEffect(() => {
    if (fixtureState) return;
    if (mountHandoffDone.current) return;
    mountHandoffDone.current = true;
    if (initialProcedureId) {
      void selectStaticProcedure(initialProcedureId);
    } else if (initialMessage) {
      void sendMessage(initialMessage);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    state,
    actions: {
      sendMessage,
      confirmU1,
      rejectU1,
      answerClarification,
      editClarificationAnswer,
      confirmU2,
      updateFormField,
      runPrecheck,
      confirmU3,
      selectStaticProcedure,
      retryHealthCheck,
      cancelRequest,
      recordFeedback,
      resetSession,
    },
  };
}
