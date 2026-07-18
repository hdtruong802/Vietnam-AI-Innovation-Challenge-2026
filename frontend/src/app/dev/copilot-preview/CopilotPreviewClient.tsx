"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import ProcedureWorkspace from "@/features/procedure-case/ProcedureWorkspace";
import { FIXTURE_KEYS, getFixtureState, type FixtureKey } from "@/features/procedure-case/procedureCase.fixtures";

interface CopilotPreviewClientProps {
  fixtureKey: FixtureKey;
}

export default function CopilotPreviewClient({ fixtureKey }: CopilotPreviewClientProps) {
  const router = useRouter();

  return (
    <>
      {/* Floating overlay, not part of document flow — ProcedureWorkspace
       * hardcodes h-screen (100vh) on its own root for the real app, so
       * anything stacked above it in normal flow would push total page
       * height past 100vh and cause outer-page scroll. An overlay avoids
       * that without touching ProcedureWorkspace's production sizing. */}
      <nav
        aria-label="Chọn fixture để xem trước"
        className="fixed top-2 right-2 z-50 flex flex-wrap justify-end gap-1 max-w-[80vw] p-1.5 rounded-lg bg-zinc-900/90 backdrop-blur-sm text-[10px] shadow-lg"
      >
        <span className="w-full text-center font-bold uppercase tracking-wider text-zinc-400 px-1">
          Dev preview — read-only
        </span>
        {FIXTURE_KEYS.map((key) => (
          <Link
            key={key}
            href={`/dev/copilot-preview?state=${key}`}
            className={`px-2 py-1 rounded font-mono ${
              key === fixtureKey ? "bg-white text-zinc-900 font-bold" : "text-zinc-100 hover:bg-zinc-700"
            }`}
          >
            {key}
          </Link>
        ))}
      </nav>
      <ProcedureWorkspace
        key={fixtureKey}
        fixtureState={getFixtureState(fixtureKey)}
        avatarDisabled
        onGoLanding={() => router.push("/")}
      />
    </>
  );
}
