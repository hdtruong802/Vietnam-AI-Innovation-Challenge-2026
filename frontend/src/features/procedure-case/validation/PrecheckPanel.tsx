"use client";

import type { FeedbackReasonCode, FlowState, TrustMetadata, ValidationResponse } from "../procedureCase.types";
import FindingCard from "./FindingCard";
import PreliminaryPassState from "./PreliminaryPassState";

interface PrecheckPanelProps {
  flow: FlowState;
  isBusy: boolean;
  canRunPrecheck: boolean;
  lastValidationResponse: ValidationResponse | null;
  trustMetadata: TrustMetadata | null;
  onRunPrecheck: () => void;
  onConfirmU3: () => void;
  onFeedback: (vote: "up" | "down", reason?: FeedbackReasonCode, note?: string) => void;
}

export default function PrecheckPanel({
  flow,
  isBusy,
  canRunPrecheck,
  lastValidationResponse,
  trustMetadata,
  onRunPrecheck,
  onConfirmU3,
  onFeedback,
}: PrecheckPanelProps) {
  return (
    <div className="bg-card-bg border border-border-slate rounded-xl p-5 shadow-sm space-y-4 text-left">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-bold text-primary uppercase tracking-wider">Kiểm tra sơ bộ (U3)</h3>
        <button
          type="button"
          onClick={onRunPrecheck}
          disabled={!canRunPrecheck || isBusy}
          className="px-4 py-2 bg-accent text-white text-xs font-bold rounded-lg hover:bg-accent-hover transition-all shadow-sm flex items-center gap-1.5 disabled:opacity-50"
        >
          {flow === "validating" ? "Đang quét..." : "🔍 Tiền kiểm"}
        </button>
      </div>

      {flow === "needs_fix" && lastValidationResponse && (
        <div className="space-y-2.5">
          <p className="text-[10px] font-semibold text-foreground/60">{lastValidationResponse.summary_message}</p>
          {lastValidationResponse.findings.map((finding, i) => (
            <FindingCard key={`${finding.field_id ?? "general"}-${i}`} finding={finding} />
          ))}
        </div>
      )}

      {flow === "pass_preliminary" && lastValidationResponse && (
        <PreliminaryPassState
          summaryMessage={lastValidationResponse.summary_message}
          trustMetadata={trustMetadata}
          onConfirmU3={onConfirmU3}
          onFeedback={onFeedback}
        />
      )}
    </div>
  );
}
