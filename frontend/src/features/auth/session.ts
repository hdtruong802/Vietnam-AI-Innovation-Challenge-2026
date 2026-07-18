import type { AuthUser, StoredDemoSession } from "./types";

const DEMO_SESSION_KEY = "vngov.demoSession.v1";
const DEMO_USER: AuthUser = {
  id: "demo-guest",
  username: "demo-guest",
  display_name: "Khách demo",
};

function browserStorage(): Storage | null {
  return typeof window === "undefined" ? null : window.sessionStorage;
}

export function readDemoSession(): StoredDemoSession | null {
  const storage = browserStorage();
  if (!storage) return null;
  const raw = storage.getItem(DEMO_SESSION_KEY);
  if (!raw) return null;
  try {
    const session = JSON.parse(raw) as StoredDemoSession;
    if (session.user?.id !== DEMO_USER.id || !Number.isFinite(session.startedAt)) {
      storage.removeItem(DEMO_SESSION_KEY);
      return null;
    }
    return session;
  } catch {
    storage.removeItem(DEMO_SESSION_KEY);
    return null;
  }
}

export function startDemoSession(): StoredDemoSession {
  const session: StoredDemoSession = {
    user: DEMO_USER,
    startedAt: Date.now(),
  };
  browserStorage()?.setItem(DEMO_SESSION_KEY, JSON.stringify(session));
  return session;
}

export function clearDemoSession(): void {
  browserStorage()?.removeItem(DEMO_SESSION_KEY);
}
