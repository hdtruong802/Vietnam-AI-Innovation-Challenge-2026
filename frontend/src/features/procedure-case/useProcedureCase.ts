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
  PersistedProcedureCaseState,
} from "./procedureCase.types";

function generateSessionId(): string {
  return "session_" + Math.random().toString(36).slice(2, 15) + Math.random().toString(36).slice(2, 15);
}

function toApiFailureKind(err: unknown): "network" | "timeout" | "aborted" | "http" {
  if (err instanceof ApiError) return err.kind;
  return "network";
}

export function useProcedureCase(initialMessage?: string, initialProcedureId?: string) {
  const [state, dispatch] = useReducer(procedureCaseReducer, undefined, () => {
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
    const persisted: PersistedProcedureCaseState = {
      sessionId: state.sessionId,
      sessionContext: state.sessionContext,
      transcript: state.transcript,
      answeredQuestions: state.answeredQuestions,
      checklist: state.checklist,
      formDraft: state.formDraft,
      lastValidationResponse: state.lastValidationResponse,
      flow: state.flow,
    };
    saveSession(persisted);
  }, [state]);

  const retryHealthCheck = useCallback(async () => {
    const ok = await checkHealth();
    dispatch({ type: "HEALTH_CHECK_RESULT", ok });
    return ok;
  }, []);

  // Initial health probe on mount.
  useEffect(() => {
    void retryHealthCheck();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectStaticProcedure = useCallback((procedureId: string) => {
    dispatch({ type: "SELECT_STATIC_PROCEDURE", procedureId });
  }, []);

  const sendMessage = useCallback(async (rawText: string) => {
    const text = rawText.trim().slice(0, INPUT_MAX_LENGTH);
    if (!text || stateRef.current.isBusy) return;

    dispatch({ type: "SEND_MESSAGE", text });
    dispatch({ type: "INTAKE_REQUEST_STARTED" });

    const controller = new AbortController();
    controllerRef.current = controller;
    try {
      const response = await postIntakeTurn(
        {
          session_id: stateRef.current.sessionId,
          message: text,
          session_context: stateRef.current.sessionContext,
        },
        controller.signal,
      );
      dispatch({ type: "INTAKE_RESPONSE_RECEIVED", response });
    } catch (err) {
      dispatch({ type: "INTAKE_REQUEST_FAILED", kind: toApiFailureKind(err) });
    } finally {
      controllerRef.current = null;
    }
  }, []);

  const fetchChecklist = useCallback(async () => {
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
  }, []);

  // checklist_loading is a transient state meant to trigger a fetch — this
  // is the single place that happens, regardless of which action produced it
  // (U1 confirm with no questions, last clarification answered, or picking
  // a procedure from the static fallback menu).
  useEffect(() => {
    if (state.flow !== "checklist_loading") {
      checklistTriggeredRef.current = false;
      return;
    }
    if (checklistTriggeredRef.current) return;
    checklistTriggeredRef.current = true;
    void fetchChecklist();
  }, [state.flow, fetchChecklist]);

  const confirmU1 = useCallback(() => dispatch({ type: "CONFIRM_U1" }), []);
  const rejectU1 = useCallback(() => dispatch({ type: "REJECT_U1" }), []);

  const answerClarification = useCallback((questionId: string, value: string) => {
    dispatch({ type: "SUBMIT_CLARIFICATION_ANSWER", questionId, value });
  }, []);

  const editClarificationAnswer = useCallback((questionId: string) => {
    dispatch({ type: "EDIT_CLARIFICATION_ANSWER", questionId });
  }, []);

  const confirmU2 = useCallback(() => dispatch({ type: "CONFIRM_U2" }), []);

  const updateFormField = useCallback((key: string, value: FormFieldValue) => {
    dispatch({ type: "UPDATE_FORM_FIELD", key, value });
  }, []);

  const runPrecheck = useCallback(async () => {
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
        },
        controller.signal,
      );
      dispatch({ type: "VALIDATION_RESPONSE_RECEIVED", response });
    } catch (err) {
      dispatch({ type: "VALIDATION_REQUEST_FAILED", kind: toApiFailureKind(err) });
    } finally {
      controllerRef.current = null;
    }
  }, []);

  const confirmU3 = useCallback(() => dispatch({ type: "CONFIRM_U3" }), []);

  const cancelRequest = useCallback(() => {
    controllerRef.current?.abort();
    dispatch({ type: "CANCEL_REQUEST" });
  }, []);

  const recordFeedback = useCallback(
    async (
      context: FeedbackContext,
      vote: "up" | "down",
      reason?: FeedbackReasonCode,
      note?: string,
    ) => {
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
      await submitFeedback(entry);
    },
    [],
  );

  const resetSession = useCallback(() => {
    controllerRef.current?.abort();
    clearSession();
    dispatch({ type: "RESET_SESSION", sessionId: generateSessionId() });
  }, []);

  // One-time handoff from the landing page: an initial message typed into
  // the hero search bar, or a procedure picked from a landing card.
  useEffect(() => {
    if (mountHandoffDone.current) return;
    mountHandoffDone.current = true;
    if (initialProcedureId) {
      selectStaticProcedure(initialProcedureId);
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
