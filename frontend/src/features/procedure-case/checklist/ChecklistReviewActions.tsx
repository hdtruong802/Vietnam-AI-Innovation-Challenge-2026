"use client";

interface ChecklistReviewActionsProps {
  canConfirm: boolean;
  onConfirm: () => void;
}

export default function ChecklistReviewActions({ canConfirm, onConfirm }: ChecklistReviewActionsProps) {
  return (
    <div className="pt-2 border-t border-[var(--vg-border)]">
      <button
        type="button"
        onClick={onConfirm}
        disabled={!canConfirm}
        className="w-full px-4 py-2.5 bg-[var(--vg-accent)] text-white text-xs font-bold rounded-lg hover:bg-[var(--vg-accent-hover)] transition-all disabled:bg-zinc-200 disabled:text-zinc-400 focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none"
      >
        Xác nhận checklist, tiếp tục điền form
      </button>
    </div>
  );
}
