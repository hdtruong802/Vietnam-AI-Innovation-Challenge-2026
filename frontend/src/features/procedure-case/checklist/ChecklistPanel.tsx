"use client";

import type { ChecklistResponse, FeedbackReasonCode } from "../procedureCase.types";
import { selectGroupedChecklist } from "../procedureCase.selectors";
import type { ProcedureCaseState } from "../procedureCase.types";
import TrustBadge from "../trust/TrustBadge";
import GuidanceDisclaimer from "../trust/GuidanceDisclaimer";
import FeedbackControls from "../feedback/FeedbackControls";
import ChecklistGroup from "./ChecklistGroup";
import ChecklistReviewActions from "./ChecklistReviewActions";

interface ChecklistPanelProps {
  state: ProcedureCaseState;
  checklist: ChecklistResponse;
  activeField: string | null;
  canConfirmU2: boolean;
  onConfirmU2: () => void;
  onFeedback: (vote: "up" | "down", reason?: FeedbackReasonCode, note?: string) => void;
}

export default function ChecklistPanel({
  state,
  checklist,
  activeField,
  canConfirmU2,
  onConfirmU2,
  onFeedback,
}: ChecklistPanelProps) {
  const grouped = selectGroupedChecklist(state);
  const answeredEntries = Object.entries(state.sessionContext.clarification_answers);

  return (
    <div className="flex-1 flex flex-col overflow-y-auto p-5 space-y-6 bg-[var(--vg-surface)]">
      <div className="border-b border-[var(--vg-border)] pb-4 shrink-0 space-y-2">
        <span className="text-[10px] font-bold text-[var(--vg-accent)] tracking-wider uppercase">
          Cơ sở pháp lý & Tài liệu
        </span>
        <h2 className="text-base font-bold text-[var(--vg-text)]">{checklist.procedure_name}</h2>
        <TrustBadge trustState={checklist.trust_state} fixtureMode={checklist.fixture_mode} />
        {checklist.fixture_mode && (
          <p className="text-[10px] text-[var(--vg-text-muted)] font-medium">{checklist.message_plain}</p>
        )}
      </div>

      {answeredEntries.length > 0 && (
        <div className="pb-2 border-b border-[var(--vg-border)]">
          <h3 className="text-xs font-bold text-[var(--vg-text-muted)] uppercase tracking-wider mb-2">
            Thông tin đã xác định
          </h3>
          <dl className="space-y-1 text-[11px]">
            {answeredEntries.map(([key, value]) => (
              <div key={key} className="flex justify-between gap-2">
                <dt className="text-[var(--vg-text-muted)]">{key}</dt>
                <dd className="font-bold text-[var(--vg-text)]">{String(value)}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      <div className="space-y-4">
        <ChecklistGroup title="Bắt buộc" items={grouped.required} sourceRefs={checklist.source_refs} activeField={activeField} />
        <ChecklistGroup title="Có điều kiện" items={grouped.conditional} sourceRefs={checklist.source_refs} activeField={activeField} />
        <ChecklistGroup title="Tùy chọn" items={grouped.optional} sourceRefs={checklist.source_refs} activeField={activeField} />
      </div>

      <div className="pt-2">
        <h3 className="text-xs font-bold text-[var(--vg-text-muted)] uppercase tracking-wider mb-3">Quy trình giải quyết</h3>
        <div className="relative pl-4 border-l-2 border-[var(--vg-border)] ml-2 space-y-5">
          {checklist.steps.map((step) => (
            <div key={step.order} className="relative">
              <div className="absolute -left-[25px] top-0 flex items-center justify-center w-5 h-5 rounded-full bg-[var(--vg-accent)] text-white text-[9px] font-bold">
                {step.order}
              </div>
              <div className="p-3.5 bg-[var(--vg-surface-subtle)] border border-[var(--vg-border)] rounded-lg">
                <h4 className="text-xs font-bold text-[var(--vg-text)]">{step.title}</h4>
                <p className="text-xs text-[var(--vg-text-secondary)] mt-1 leading-relaxed">{step.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <FeedbackControls context="checklist" onSubmit={onFeedback} />
      <GuidanceDisclaimer />
      <ChecklistReviewActions canConfirm={canConfirmU2} onConfirm={onConfirmU2} />
    </div>
  );
}
