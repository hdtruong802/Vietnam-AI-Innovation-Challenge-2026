"use client";

import type { ChecklistItem as ChecklistItemModel, Citation } from "../procedureCase.types";
import { resolveCitations } from "../procedureCase.selectors";
import SourceDrawer from "../trust/SourceDrawer";

const KIND_STYLE: Record<ChecklistItemModel["kind"], { badge: string; border: string; text: string }> = {
  required: { badge: "bg-error-bg text-error border-error-border", border: "border-error-border bg-error-bg/10", text: "text-error" },
  conditional: { badge: "bg-warning-bg text-warning border-warning-border", border: "border-warning-border bg-warning-bg/10", text: "text-warning" },
  optional: { badge: "bg-neutral-bg text-foreground/60 border-border-slate", border: "border-border-slate bg-neutral-bg/40", text: "text-primary" },
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
      className={`p-3.5 border rounded-lg transition-all duration-300 ${
        isHighlighted ? "border-accent bg-blue-50/10 shadow-sm ring-1 ring-accent" : style.border
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <h4 className={`text-xs font-bold ${style.text}`}>{item.label}</h4>
        <span className={`shrink-0 inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold border ${style.badge}`}>
          {KIND_LABEL[item.kind]}
        </span>
      </div>
      <p className="text-xs text-zinc-600 mt-1.5 leading-relaxed">{item.description}</p>
      {citations.length > 0 && (
        <div className="mt-2.5 pt-2 border-t border-zinc-100">
          <SourceDrawer citations={citations} label="Cơ sở pháp lý" />
        </div>
      )}
    </div>
  );
}
