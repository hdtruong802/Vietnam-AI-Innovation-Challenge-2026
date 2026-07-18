"use client";

import { OFFICIAL_PORTAL_URL } from "../procedureCase.constants";
import type { TrustMetadata } from "../procedureCase.types";
import { AlertTriangleIcon } from "../icons";
import TrustBadge from "./TrustBadge";
import SourceDrawer from "./SourceDrawer";
import GuidanceDisclaimer from "./GuidanceDisclaimer";

interface OfficialReviewCardProps {
  message: string;
  trustMetadata: TrustMetadata | null;
}

export default function OfficialReviewCard({ message, trustMetadata }: OfficialReviewCardProps) {
  return (
    <div className="bg-[var(--vg-surface)] border border-[var(--vg-error)]/40 rounded-xl p-5 space-y-4 text-left max-w-2xl mx-auto w-full">
      <div className="flex items-center gap-2">
        <span className="shrink-0 w-7 h-7 rounded-full bg-[var(--vg-error-soft)] flex items-center justify-center">
          <AlertTriangleIcon className="w-4 h-4" stroke="var(--vg-error)" />
        </span>
        <h3 className="text-sm font-bold text-[var(--vg-error)]">Cần cơ quan có thẩm quyền xem xét</h3>
      </div>

      <TrustBadge trustState="official_review_required" fixtureMode={trustMetadata?.fixture_mode} />

      <p className="text-xs text-[var(--vg-text-secondary)] leading-relaxed font-medium">{message}</p>

      {trustMetadata?.source_refs && trustMetadata.source_refs.length > 0 && (
        <SourceDrawer citations={trustMetadata.source_refs} />
      )}

      <a
        href={OFFICIAL_PORTAL_URL}
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center gap-1.5 px-4 py-2 bg-[var(--vg-accent)] text-white text-xs font-bold rounded-lg hover:bg-[var(--vg-accent-hover)] transition-all"
      >
        Tiếp tục qua Cổng Dịch vụ công Quốc gia ↗
      </a>

      <GuidanceDisclaimer />
    </div>
  );
}
