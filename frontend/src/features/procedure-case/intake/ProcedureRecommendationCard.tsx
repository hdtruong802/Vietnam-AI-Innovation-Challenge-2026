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
    <div className="mx-4 mb-3 p-4 bg-[var(--vg-surface)] border border-[var(--vg-border-strong)] rounded-xl space-y-3 text-left">
      <div>
        <span className="text-2xs font-bold text-[var(--vg-accent)] tracking-wider uppercase">
          Thủ tục được đề xuất
        </span>
        <h4 className="text-sm font-bold text-[var(--vg-text)] mt-0.5">{candidate.name}</h4>
      </div>

      <TrustBadge
        trustState={trustMetadata?.trust_state ?? null}
        fixtureMode={trustMetadata?.fixture_mode}
        demoMode={trustMetadata?.demo_mode}
      />
      {trustMetadata?.source_refs && trustMetadata.source_refs.length > 0 && (
        <SourceDrawer citations={trustMetadata.source_refs} />
      )}

      <div className="flex gap-2 pt-1">
        <button
          type="button"
          onClick={onConfirm}
          className="px-4 py-2 bg-[var(--vg-accent)] text-white text-xs font-bold rounded-lg hover:bg-[var(--vg-accent-hover)] transition-all focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none"
        >
          Xác nhận thủ tục này
        </button>
        <button
          type="button"
          onClick={onReject}
          className="px-4 py-2 border border-[var(--vg-border)] text-[var(--vg-text)] text-xs font-bold rounded-lg hover:bg-[var(--vg-surface-subtle)] transition-all focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none"
        >
          Không đúng, chọn lại
        </button>
      </div>
    </div>
  );
}
