"use client";

import type { TrustState } from "../procedureCase.types";
import { AlertTriangleIcon, CheckCircleIcon, FlaskIcon, HelpCircleIcon } from "../icons";

const VARIANTS: Record<TrustState, { Icon: typeof CheckCircleIcon; label: string; className: string }> = {
  verified_guidance: {
    Icon: CheckCircleIcon,
    label: "Đã xác minh nguồn",
    className: "bg-[var(--vg-success-soft)] border-[var(--vg-success)]/30 text-[var(--vg-success)]",
  },
  need_more_information: {
    Icon: HelpCircleIcon,
    label: "Cần thêm thông tin",
    className: "bg-[var(--vg-warning-soft)] border-[var(--vg-warning)]/30 text-[var(--vg-warning)]",
  },
  official_review_required: {
    Icon: AlertTriangleIcon,
    label: "Cần cơ quan xem xét",
    className: "bg-[var(--vg-error-soft)] border-[var(--vg-error)]/30 text-[var(--vg-error)]",
  },
};

interface TrustBadgeProps {
  trustState: TrustState | null;
  fixtureMode?: boolean;
  demoMode?: boolean;
}

export function resolveDisplayedTrustState(
  trustState: TrustState,
  fixtureMode?: boolean,
  demoMode?: boolean,
): TrustState {
  if ((fixtureMode || demoMode) && trustState === "verified_guidance") {
    return "official_review_required";
  }
  return trustState;
}

export default function TrustBadge({ trustState, fixtureMode, demoMode }: TrustBadgeProps) {
  if (!trustState) return null;
  const variant = VARIANTS[resolveDisplayedTrustState(trustState, fixtureMode, demoMode)];

  return (
    <div className="inline-flex items-center gap-1.5 flex-wrap">
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl border text-[10px] font-bold ${variant.className}`}
      >
        <variant.Icon className="w-3.5 h-3.5" />
        <span>{variant.label}</span>
      </span>
      {fixtureMode && (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-xl border border-[var(--vg-border)] bg-[var(--vg-surface-subtle)] text-[10px] font-bold text-[var(--vg-text-muted)]">
          <FlaskIcon className="w-3.5 h-3.5" />
          <span>Chế độ demo dữ liệu mẫu</span>
        </span>
      )}
      {demoMode && (
        <>
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg border border-amber-300 bg-amber-50 text-[10px] font-bold text-amber-900">
            <span>Đã kiểm thử cho demo MVP</span>
          </span>
          <span className="text-[10px] font-bold text-error">Không phải K1</span>
        </>
      )}
    </div>
  );
}
