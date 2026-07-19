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
    <div className="bg-[var(--vg-surface)] border border-[var(--vg-border)] rounded-xl p-5 space-y-4 text-left">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-bold text-[var(--vg-text)] uppercase tracking-wider">Kiểm tra sơ bộ</h3>
        <button
          type="button"
          onClick={onRunPrecheck}
          disabled={!canRunPrecheck || isBusy}
          className="px-4 py-2 bg-[var(--vg-accent)] text-white text-xs font-bold rounded-lg hover:bg-[var(--vg-accent-hover)] transition-all disabled:bg-zinc-200 disabled:text-zinc-400"
        >
          {flow === "validating" ? "Đang quét..." : "Tiền kiểm"}
        </button>
      </div>

      {(trustMetadata?.fixture_mode || trustMetadata?.demo_mode) && (
        <p className="text-xs font-medium leading-relaxed text-foreground/60">
          Kết quả này chỉ phục vụ diễn tập demo MVP, không phải xác nhận K1 hoặc kết luận của cơ quan có thẩm quyền.
        </p>
      )}

      {flow === "needs_fix" && lastValidationResponse && (
        <div className="space-y-2.5">
          <p className="text-[10px] font-semibold text-[var(--vg-text-secondary)]">{lastValidationResponse.summary_message}</p>
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
