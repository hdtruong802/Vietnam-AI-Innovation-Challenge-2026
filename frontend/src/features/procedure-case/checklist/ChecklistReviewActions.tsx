"use client";

interface ChecklistReviewActionsProps {
  canConfirm: boolean;
  onConfirm: () => void;
}

export default function ChecklistReviewActions({ canConfirm, onConfirm }: ChecklistReviewActionsProps) {
  return (
    <div className="pt-2 border-t border-border-slate">
      <button
        type="button"
        onClick={onConfirm}
        disabled={!canConfirm}
        className="w-full px-4 py-2.5 bg-accent text-white text-xs font-bold rounded-lg hover:bg-accent-hover transition-all disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-accent outline-none"
      >
        Xác nhận checklist, tiếp tục điền form
      </button>
    </div>
  );
}
