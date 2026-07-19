"use client";

import type { ChecklistItem as ChecklistItemModel, Citation } from "../procedureCase.types";
import { resolveCitations } from "../procedureCase.selectors";
import SourceDrawer from "../trust/SourceDrawer";

const KIND_STYLE: Record<ChecklistItemModel["kind"], { badge: string; border: string; text: string }> = {
  required: {
    badge: "bg-[var(--vg-error-soft)] text-[var(--vg-error)] border-[var(--vg-error)]/30",
    border: "border-[var(--vg-error)]/30 bg-[var(--vg-error-soft)]/40",
    text: "text-[var(--vg-error)]",
  },
  conditional: {
    badge: "bg-[var(--vg-warning-soft)] text-[var(--vg-warning)] border-[var(--vg-warning)]/30",
    border: "border-[var(--vg-warning)]/30 bg-[var(--vg-warning-soft)]/40",
    text: "text-[var(--vg-warning)]",
  },
  optional: {
    badge: "bg-[var(--vg-surface-subtle)] text-[var(--vg-text-muted)] border-[var(--vg-border)]",
    border: "border-[var(--vg-border)] bg-[var(--vg-surface-subtle)]/60",
    text: "text-[var(--vg-text)]",
  },
};

const KIND_LABEL: Record<ChecklistItemModel["kind"], string> = {
  required: "BẮT BUỘC",
  conditional: "CÓ ĐIỀU KIỆN",
  optional: "TÙY CHỌN",
};

interface ChecklistItemProps {
  item: ChecklistItemModel;
  sourceRefs: Citation[];
  isHighlighted?: boolean;
}

export default function ChecklistItem({ item, sourceRefs, isHighlighted }: ChecklistItemProps) {
  const style = KIND_STYLE[item.kind];
  const citations = resolveCitations(item.source_ref_ids, sourceRefs);

  return (
    <div
      className={`p-3.5 border rounded-lg transition-[border-color,background-color,box-shadow] duration-200 ${
        isHighlighted ? "border-[var(--vg-accent)] bg-[var(--vg-accent-soft)] ring-1 ring-[var(--vg-accent)]" : style.border
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <h4 className={`text-xs font-bold ${style.text}`}>{item.label}</h4>
        <span className={`shrink-0 inline-flex items-center px-1.5 py-0.5 rounded text-2xs font-bold border ${style.badge}`}>
          {KIND_LABEL[item.kind]}
        </span>
      </div>
      <p className="text-xs text-[var(--vg-text-secondary)] mt-1.5 leading-relaxed">{item.description}</p>
      {citations.length > 0 && (
        <div className="mt-2.5 pt-2 border-t border-[var(--vg-border)]">
          <SourceDrawer citations={citations} label="Cơ sở pháp lý" />
        </div>
      )}
    </div>
  );
}
