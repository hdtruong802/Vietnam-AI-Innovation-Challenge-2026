"use client";

import { OFFICIAL_PORTAL_URL } from "../procedureCase.constants";
import type { TrustMetadata } from "../procedureCase.types";
import TrustBadge from "./TrustBadge";
import SourceDrawer from "./SourceDrawer";
import GuidanceDisclaimer from "./GuidanceDisclaimer";

interface OfficialReviewCardProps {
  message: string;
  trustMetadata: TrustMetadata | null;
}

export default function OfficialReviewCard({ message, trustMetadata }: OfficialReviewCardProps) {
  return (
    <div className="bg-card-bg border border-error-border rounded-xl p-5 shadow-sm space-y-4 text-left max-w-2xl mx-auto w-full">
      <div className="flex items-center gap-2">
        <span className="text-lg" aria-hidden="true">
          ⚠️
        </span>
        <h3 className="text-sm font-bold text-error">Cần cơ quan có thẩm quyền xem xét</h3>
      </div>

      <TrustBadge trustState="official_review_required" fixtureMode={trustMetadata?.fixture_mode} />

      <p className="text-xs text-zinc-600 leading-relaxed font-medium">{message}</p>

      {trustMetadata?.source_refs && trustMetadata.source_refs.length > 0 && (
        <SourceDrawer citations={trustMetadata.source_refs} />
      )}

      <a
        href={OFFICIAL_PORTAL_URL}
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center gap-1.5 px-4 py-2 bg-accent text-white text-xs font-bold rounded-lg hover:bg-accent-hover transition-all"
      >
        Tiếp tục qua Cổng Dịch vụ công Quốc gia ↗
      </a>

      <GuidanceDisclaimer />
    </div>
  );
}
