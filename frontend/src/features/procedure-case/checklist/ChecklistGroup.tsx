"use client";

import type { ChecklistItem as ChecklistItemModel, Citation } from "../procedureCase.types";
import ChecklistItem from "./ChecklistItem";

interface ChecklistGroupProps {
  title: string;
  items: ChecklistItemModel[];
  sourceRefs: Citation[];
  activeField?: string | null;
}

export default function ChecklistGroup({ title, items, sourceRefs, activeField }: ChecklistGroupProps) {
  if (items.length === 0) return null;

  return (
    <div>
      <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2">
        {title} ({items.length})
      </h3>
      <div className="space-y-3">
        {items.map((item) => {
          const isHighlighted =
            !!activeField && item.id.includes(activeField.toLowerCase().replace(/_/g, "-"));
          return (
            <ChecklistItem key={item.id} item={item} sourceRefs={sourceRefs} isHighlighted={isHighlighted} />
          );
        })}
      </div>
    </div>
  );
}
