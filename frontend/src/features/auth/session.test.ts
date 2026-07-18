import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { clearDemoSession, readDemoSession, startDemoSession } from "./session";

function createStorage(): Storage {
  const values = new Map<string, string>();
  return {
    get length() {
      return values.size;
    },
    clear: () => values.clear(),
    getItem: (key) => values.get(key) ?? null,
    key: (index) => [...values.keys()][index] ?? null,
    removeItem: (key) => values.delete(key),
    setItem: (key, value) => values.set(key, value),
  };
}

describe("demo session", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { sessionStorage: createStorage() });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("creates and restores the fixed demo profile without a token", () => {
    const session = startDemoSession();

    expect(session.user).toEqual({
      id: "demo-guest",
      username: "demo-guest",
      display_name: "Khách demo",
    });
    expect("accessToken" in session).toBe(false);
    expect(readDemoSession()).toEqual(session);
  });

  it("clears the local session on logout", () => {
    startDemoSession();
    clearDemoSession();

    expect(readDemoSession()).toBeNull();
  });

  it("rejects a stored profile other than the demo profile", () => {
    window.sessionStorage.setItem(
      "vngov.demoSession.v1",
      JSON.stringify({ user: { id: "other", username: "other", display_name: "Other" }, startedAt: 1 }),
    );

    expect(readDemoSession()).toBeNull();
  });
});
