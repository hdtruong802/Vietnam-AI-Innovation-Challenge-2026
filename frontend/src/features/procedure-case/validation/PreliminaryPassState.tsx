"use client";

import type { FeedbackReasonCode, TrustMetadata } from "../procedureCase.types";
import { CheckCircleIcon } from "../icons";
import TrustBadge from "../trust/TrustBadge";
import GuidanceDisclaimer from "../trust/GuidanceDisclaimer";
import FeedbackControls from "../feedback/FeedbackControls";

interface PreliminaryPassStateProps {
  summaryMessage: string;
  trustMetadata: TrustMetadata | null;
  onConfirmU3: () => void;
  onFeedback: (vote: "up" | "down", reason?: FeedbackReasonCode, note?: string) => void;
  hasConfirmed?: boolean;
}

export default function PreliminaryPassState({
  summaryMessage,
  trustMetadata,
  onConfirmU3,
  onFeedback,
  hasConfirmed = false,
}: PreliminaryPassStateProps) {
  return (
    <div className="border border-[var(--vg-success)]/30 bg-[var(--vg-success-soft)] rounded-xl p-4 text-left space-y-3">
      <h5 className="text-xs font-bold flex items-center gap-2 text-[var(--vg-success)]">
        <CheckCircleIcon className="w-4 h-4 shrink-0" />
        Đã vượt qua kiểm tra sơ bộ
      </h5>
      {summaryMessage && !summaryMessage.includes("demo MVP") && !summaryMessage.includes("K1") && (
        <p className="text-[10px] leading-relaxed font-semibold text-[var(--vg-success)]">{summaryMessage}</p>
      )}
      <TrustBadge
        trustState={trustMetadata?.trust_state ?? null}
        fixtureMode={trustMetadata?.fixture_mode}
        demoMode={trustMetadata?.demo_mode}
      />

      {hasConfirmed ? (
        <div className="text-xs font-bold text-[var(--vg-success)] flex items-center gap-1.5 py-1">
          <span>✓ Bạn đã hoàn tất xem trước và kiểm tra hồ sơ thành công.</span>
        </div>
      ) : (
        <button
          type="button"
          onClick={onConfirmU3}
          className="px-4 py-2 bg-[var(--vg-accent)] text-white text-xs font-bold rounded-lg hover:bg-[var(--vg-accent-hover)] transition-all focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none"
        >
          Đã hiểu, hoàn tất xem trước
        </button>
      )}
      <FeedbackControls context="precheck" onSubmit={onFeedback} />
      <GuidanceDisclaimer />
    </div>
  );
}
