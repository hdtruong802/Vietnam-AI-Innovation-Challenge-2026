"use client";

import { useState } from "react";
import type { Finding } from "../procedureCase.types";

const SEVERITY_STYLE: Record<Finding["severity"], { icon: string; className: string; label: string }> = {
  error: { icon: "⚠️", className: "border-error-border bg-error-bg/10 text-error", label: "LỖI" },
  warning: { icon: "❗", className: "border-warning-border bg-warning-bg/10 text-warning", label: "CẢNH BÁO" },
  info: { icon: "ℹ️", className: "border-border-slate bg-neutral-bg text-primary", label: "THÔNG TIN" },
};

interface FindingCardProps {
  finding: Finding;
}

export default function FindingCard({ finding }: FindingCardProps) {
  const [showFix, setShowFix] = useState(false);
  const style = SEVERITY_STYLE[finding.severity];

  return (
    <div className={`p-3.5 border rounded-lg ${style.className}`}>
      <div className="flex items-start justify-between gap-2">
        <h5 className="text-xs font-bold flex items-center gap-1.5">
          <span aria-hidden="true">{style.icon}</span>
          {finding.field_id ?? "Chung"}
        </h5>
        <span className="shrink-0 text-[9px] font-bold uppercase tracking-wide opacity-70">{style.label}</span>
      </div>
      <p className="text-xs mt-1.5 leading-relaxed font-semibold">{finding.message}</p>
      <span className="text-[9px] font-mono opacity-50 block mt-1">{finding.rule_id}</span>

      {finding.fix_hint && (
        <div className="mt-2">
          <button
            type="button"
            onClick={() => setShowFix((v) => !v)}
            aria-expanded={showFix}
            className="text-[10px] font-bold underline hover:no-underline focus-visible:ring-2 focus-visible:ring-accent rounded outline-none"
          >
            Xem cách sửa
          </button>
          {/* FR-6 (AI explanation) deferred — no backend endpoint yet; this
              only discloses the deterministic rule-engine fix_hint. */}
          {showFix && <p className="text-[11px] mt-1 leading-relaxed">{finding.fix_hint}</p>}
        </div>
      )}
    </div>
  );
}
