"use client";

import { GUIDANCE_DISCLAIMER } from "../procedureCase.constants";

export default function GuidanceDisclaimer() {
  return (
    <p className="text-[10px] leading-relaxed text-foreground/50 font-medium border-t border-border-slate pt-2.5">
      {GUIDANCE_DISCLAIMER}
    </p>
  );
}
