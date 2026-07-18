"use client";

import { GUIDANCE_DISCLAIMER } from "../procedureCase.constants";

export default function GuidanceDisclaimer() {
  return (
    <p className="text-[10px] leading-relaxed text-[var(--vg-text-muted)] font-medium border-t border-[var(--vg-border)] pt-2.5">
      {GUIDANCE_DISCLAIMER}
    </p>
  );
}
