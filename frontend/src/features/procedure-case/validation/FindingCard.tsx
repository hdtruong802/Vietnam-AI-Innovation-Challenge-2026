"use client";

import { useState } from "react";
import type { Finding } from "../procedureCase.types";
import { AlertCircleIcon, AlertTriangleIcon, InfoCircleIcon } from "../icons";

const SEVERITY_STYLE: Record<Finding["severity"], { Icon: typeof AlertTriangleIcon; className: string; label: string }> = {
  error: {
    Icon: AlertTriangleIcon,
    className: "border-[var(--vg-error)]/30 bg-[var(--vg-error-soft)] text-[var(--vg-error)]",
    label: "LỖI",
  },
  warning: {
    Icon: AlertCircleIcon,
    className: "border-[var(--vg-warning)]/30 bg-[var(--vg-warning-soft)] text-[var(--vg-warning)]",
    label: "CẢNH BÁO",
  },
  info: {
    Icon: InfoCircleIcon,
    className: "border-[var(--vg-border)] bg-[var(--vg-surface-subtle)] text-[var(--vg-text)]",
    label: "THÔNG TIN",
  },
};

interface FindingCardProps {
  finding: Finding;
  /** Vietnamese label of the field from form_schema; falls back to field_id. */
  fieldLabel?: string;
}

export default function FindingCard({ finding, fieldLabel }: FindingCardProps) {
  const [showFix, setShowFix] = useState(false);
  const style = SEVERITY_STYLE[finding.severity];

  return (
    <div className={`p-3.5 border rounded-lg ${style.className}`}>
      <div className="flex items-start justify-between gap-2">
        <h5 className="text-xs font-bold flex items-center gap-1.5">
          <style.Icon className="w-3.5 h-3.5 shrink-0" />
          {fieldLabel ?? finding.field_id ?? "Chung"}
        </h5>
        <span className="shrink-0 text-2xs font-bold uppercase tracking-wide opacity-70">{style.label}</span>
      </div>
      <p className="text-xs mt-1.5 leading-relaxed font-semibold">{finding.message}</p>
      <span className="text-2xs font-mono opacity-50 block mt-1">{finding.rule_id}</span>

      {finding.fix_hint && (
        <div className="mt-2">
          <button
            type="button"
            onClick={() => setShowFix((v) => !v)}
            aria-expanded={showFix}
            className="text-2xs font-bold underline hover:no-underline focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] rounded outline-none"
          >
            Xem cách sửa
          </button>
          {/* FR-6 (AI explanation) deferred — no backend endpoint yet; this
              only discloses the deterministic rule-engine fix_hint. */}
          {showFix && <p className="text-2xs mt-1 leading-relaxed">{finding.fix_hint}</p>}
        </div>
      )}
    </div>
  );
}
