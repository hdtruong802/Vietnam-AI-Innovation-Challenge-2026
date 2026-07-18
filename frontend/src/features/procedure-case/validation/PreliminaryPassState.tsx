"use client";

import type { FeedbackReasonCode, TrustMetadata } from "../procedureCase.types";
import TrustBadge from "../trust/TrustBadge";
import GuidanceDisclaimer from "../trust/GuidanceDisclaimer";
import FeedbackControls from "../feedback/FeedbackControls";

interface PreliminaryPassStateProps {
  summaryMessage: string;
  trustMetadata: TrustMetadata | null;
  onConfirmU3: () => void;
  onFeedback: (vote: "up" | "down", reason?: FeedbackReasonCode, note?: string) => void;
}

export default function PreliminaryPassState({
  summaryMessage,
  trustMetadata,
  onConfirmU3,
  onFeedback,
}: PreliminaryPassStateProps) {
  return (
    <div className="border border-emerald-200 bg-emerald-50 dark:bg-emerald-950/15 rounded-xl p-4 shadow-sm text-left space-y-3">
      <h5 className="text-xs font-bold flex items-center gap-2 text-emerald-600">
        ✅ HỒ SƠ ĐỦ ĐIỀU KIỆN SƠ BỘ
      </h5>
      <p className="text-[10px] leading-relaxed font-semibold text-emerald-700 dark:text-emerald-400">
        {summaryMessage}
      </p>
      <TrustBadge trustState={trustMetadata?.trust_state ?? null} fixtureMode={trustMetadata?.fixture_mode} />
      <button
        type="button"
        onClick={onConfirmU3}
        className="px-4 py-2 bg-accent text-white text-xs font-bold rounded-lg hover:bg-accent-hover transition-all focus-visible:ring-2 focus-visible:ring-accent outline-none"
      >
        Đã hiểu, hoàn tất xem trước
      </button>
      <FeedbackControls context="precheck" onSubmit={onFeedback} />
      <GuidanceDisclaimer />
    </div>
  );
}
