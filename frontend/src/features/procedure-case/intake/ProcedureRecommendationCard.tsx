"use client";

import type { ProcedureCandidate, TrustMetadata } from "../procedureCase.types";
import TrustBadge from "../trust/TrustBadge";
import SourceDrawer from "../trust/SourceDrawer";

interface ProcedureRecommendationCardProps {
  candidate: ProcedureCandidate;
  trustMetadata: TrustMetadata | null;
  onConfirm: () => void;
  onReject: () => void;
}

export default function ProcedureRecommendationCard({
  candidate,
  trustMetadata,
  onConfirm,
  onReject,
}: ProcedureRecommendationCardProps) {
  return (
    <div className="mx-4 mb-3 p-4 bg-card-bg border border-accent/40 rounded-xl shadow-sm space-y-3 text-left">
      <div>
        <span className="text-[10px] font-bold text-accent tracking-wider uppercase">
          Thủ tục được đề xuất (U1)
        </span>
        <h4 className="text-sm font-bold text-primary mt-0.5">{candidate.name}</h4>
        <p className="text-xs text-zinc-600 mt-1 leading-relaxed">{candidate.reason}</p>
      </div>

      <TrustBadge trustState={trustMetadata?.trust_state ?? null} fixtureMode={trustMetadata?.fixture_mode} />
      {trustMetadata?.source_refs && trustMetadata.source_refs.length > 0 && (
        <SourceDrawer citations={trustMetadata.source_refs} />
      )}

      <div className="flex gap-2 pt-1">
        <button
          type="button"
          onClick={onConfirm}
          className="px-4 py-2 bg-accent text-white text-xs font-bold rounded-lg hover:bg-accent-hover transition-all focus-visible:ring-2 focus-visible:ring-accent outline-none"
        >
          Xác nhận thủ tục này
        </button>
        <button
          type="button"
          onClick={onReject}
          className="px-4 py-2 border border-border-slate text-primary text-xs font-bold rounded-lg hover:bg-neutral-bg transition-all focus-visible:ring-2 focus-visible:ring-accent outline-none"
        >
          Không đúng, chọn lại
        </button>
      </div>
    </div>
  );
}
