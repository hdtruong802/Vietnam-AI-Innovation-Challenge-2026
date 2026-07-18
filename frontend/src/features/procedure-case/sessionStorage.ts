import { SESSION_STORAGE_KEY } from "./procedureCase.constants";
import type { PersistedProcedureCaseState } from "./procedureCase.types";

export function saveSession(state: PersistedProcedureCaseState): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // sessionStorage can throw in private-browsing/quota-exceeded situations;
    // losing session persistence is not fatal to the flow.
  }
}

export function loadSession(): PersistedProcedureCaseState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as PersistedProcedureCaseState;
  } catch {
    return null;
  }
}

export function clearSession(): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.removeItem(SESSION_STORAGE_KEY);
  } catch {
    // no-op
  }
}
