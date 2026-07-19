import { describe, expect, it } from "vitest";

import { resolveDisplayedTrustState } from "./TrustBadge";

describe("resolveDisplayedTrustState", () => {
  it("never displays fixture content as verified guidance", () => {
    expect(resolveDisplayedTrustState("verified_guidance", true)).toBe(
      "official_review_required",
    );
  });

  it("keeps verified guidance for a non-fixture response", () => {
    expect(resolveDisplayedTrustState("verified_guidance", false, false)).toBe(
      "verified_guidance",
    );
  });

  it("never displays demo MVP content as verified guidance", () => {
    expect(resolveDisplayedTrustState("verified_guidance", false, true)).toBe(
      "official_review_required",
    );
  });
});
