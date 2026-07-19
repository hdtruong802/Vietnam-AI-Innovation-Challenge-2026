import { notFound } from "next/navigation";
import { FIXTURE_KEYS, type FixtureKey } from "@/features/procedure-case/procedureCase.fixtures";
import CopilotPreviewClient from "./CopilotPreviewClient";

// Dev-only Copilot state-preview harness. Server Component so the
// production guard runs before anything renders, with no client-side
// NODE_ENV branching and no hydration risk. This route exists in the build
// output (Next always compiles every route) but serves a 404 body whenever
// visited outside development — the real app ("/") is completely
// unaffected either way.
export default async function CopilotPreviewPage({
  searchParams,
}: {
  searchParams: Promise<{ state?: string }>;
}) {
  if (process.env.NODE_ENV === "production") {
    notFound();
  }

  const { state } = await searchParams;
  const fixtureKey: FixtureKey = FIXTURE_KEYS.includes(state as FixtureKey) ? (state as FixtureKey) : "idle";

  return <CopilotPreviewClient fixtureKey={fixtureKey} />;
}
