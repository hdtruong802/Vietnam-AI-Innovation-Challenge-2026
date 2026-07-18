import { API_BASE_URL, REQUEST_TIMEOUT_MS, RETRY_BACKOFF_MS } from "./procedureCase.constants";
import type {
  ChecklistRequest,
  ChecklistResponse,
  FeedbackEntry,
  IntakeRequest,
  IntakeResponse,
  ProcedureSummary,
  ValidationRequest,
  ValidationResponse,
} from "./procedureCase.types";

export type ApiErrorKind = "network" | "timeout" | "http" | "aborted";

export class ApiError extends Error {
  kind: ApiErrorKind;
  status?: number;

  constructor(kind: ApiErrorKind, message: string, status?: number) {
    super(message);
    this.kind = kind;
    this.status = status;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function combineSignals(a: AbortSignal, b?: AbortSignal): AbortSignal {
  if (!b) return a;
  const anyFn = (AbortSignal as unknown as { any?: (signals: AbortSignal[]) => AbortSignal }).any;
  if (typeof anyFn === "function") return anyFn([a, b]);
  const controller = new AbortController();
  const abort = () => controller.abort();
  if (a.aborted || b.aborted) controller.abort();
  a.addEventListener("abort", abort);
  b.addEventListener("abort", abort);
  return controller.signal;
}

/**
 * POST helper with an 8s soft timeout (PRD §15), a single retry with a short
 * fixed backoff on network/timeout failure only (never on a 4xx rejection —
 * PRD §12 retry policy), and support for external cancellation via signal.
 */
async function postJson<TResponse>(
  path: string,
  body: unknown,
  externalSignal?: AbortSignal,
): Promise<TResponse> {
  let lastError: ApiError | null = null;

  for (let attempt = 0; attempt < 2; attempt += 1) {
    const timeoutController = new AbortController();
    const timeoutId = setTimeout(() => timeoutController.abort(), REQUEST_TIMEOUT_MS);
    const signal = combineSignals(timeoutController.signal, externalSignal);

    try {
      const res = await fetch(`${API_BASE_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal,
      });
      clearTimeout(timeoutId);

      if (!res.ok) {
        // 4xx/5xx are policy/validation responses from a reachable server —
        // do not retry them, surface immediately.
        throw new ApiError("http", `Request failed with status ${res.status}`, res.status);
      }
      return (await res.json()) as TResponse;
    } catch (err) {
      clearTimeout(timeoutId);

      if (externalSignal?.aborted) {
        throw new ApiError("aborted", "Request was cancelled by the user");
      }
      if (err instanceof ApiError) {
        throw err; // http error — no retry
      }
      const isTimeout = timeoutController.signal.aborted;
      lastError = new ApiError(
        isTimeout ? "timeout" : "network",
        isTimeout ? "Request timed out" : "Network request failed",
      );
      if (attempt === 0) {
        await sleep(RETRY_BACKOFF_MS);
        continue;
      }
    }
  }

  throw lastError ?? new ApiError("network", "Network request failed");
}

export async function checkHealth(): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    const res = await fetch(`${API_BASE_URL}/health`, { method: "GET", signal: controller.signal });
    clearTimeout(timeoutId);
    return res.ok;
  } catch {
    return false;
  }
}

export function postIntakeTurn(
  req: IntakeRequest,
  signal?: AbortSignal,
): Promise<IntakeResponse> {
  return postJson<IntakeResponse>("/v1/intake/turn", req, signal);
}

export function postChecklist(
  procedureId: string,
  req: ChecklistRequest,
  signal?: AbortSignal,
): Promise<ChecklistResponse> {
  return postJson<ChecklistResponse>(
    `/v1/procedures/${encodeURIComponent(procedureId)}/checklist`,
    req,
    signal,
  );
}

export function postValidate(
  req: ValidationRequest,
  signal?: AbortSignal,
): Promise<ValidationResponse> {
  return postJson<ValidationResponse>("/v1/applications/validate", req, signal);
}

export async function listProcedures(): Promise<ProcedureSummary[]> {
  const res = await fetch(`${API_BASE_URL}/v1/procedures`, { method: "GET" });
  if (!res.ok) throw new ApiError("http", `Request failed with status ${res.status}`, res.status);
  return (await res.json()) as ProcedureSummary[];
}

// No backend feedback endpoint exists yet (FR-8). This stub keeps the call
// site shape stable so wiring a real POST later is a one-line swap; it must
// not attempt a network call to a URL that doesn't exist.
export async function submitFeedback(entry: FeedbackEntry): Promise<void> {
  // TODO: no backend endpoint yet — logs locally only; swap body for a real
  // POST /v1/feedback (or similar) once available.
  console.debug("[procedure-case] feedback recorded (local only)", entry);
}
