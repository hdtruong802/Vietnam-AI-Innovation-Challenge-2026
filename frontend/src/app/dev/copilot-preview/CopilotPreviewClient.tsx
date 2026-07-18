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
    <div className="flex flex-col h-screen">
      <nav
        aria-label="Chọn fixture để xem trước"
        className="flex flex-wrap items-center gap-1.5 p-2 bg-zinc-900 text-zinc-100 text-xs shrink-0 z-30"
      >
        <span className="font-bold px-2 uppercase tracking-wider text-[10px] text-zinc-400">
          Dev preview — read-only
        </span>
        {FIXTURE_KEYS.map((key) => (
          <Link
            key={key}
            href={`/dev/copilot-preview?state=${key}`}
            className={`px-2.5 py-1 rounded font-mono ${
              key === fixtureKey ? "bg-white text-zinc-900 font-bold" : "hover:bg-zinc-700"
            }`}
          >
            {key}
          </Link>
        ))}
      </nav>
      <div className="flex-1 min-h-0">
        <ProcedureWorkspace
          key={fixtureKey}
          fixtureState={getFixtureState(fixtureKey)}
          avatarDisabled
          onGoLanding={() => router.push("/")}
          onOpenComingSoon={() => {
            /* no-op: no coming-soon modal host on this route; the avatar
             * button itself is disabled (see avatarDisabled) so this should
             * be unreachable. */
          }}
        />
      </div>
    </div>
  );
}
