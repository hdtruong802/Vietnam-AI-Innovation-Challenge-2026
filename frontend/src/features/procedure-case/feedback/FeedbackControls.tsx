"use client";

import { useState } from "react";
import { FEEDBACK_NOTE_MAX_LENGTH, FEEDBACK_REASONS } from "../procedureCase.constants";
import type { FeedbackContext, FeedbackReasonCode } from "../procedureCase.types";
import { ThumbsDownIcon, ThumbsUpIcon } from "../icons";

interface FeedbackControlsProps {
  context: FeedbackContext;
  onSubmit: (vote: "up" | "down", reason?: FeedbackReasonCode, note?: string) => void;
}

export default function FeedbackControls({ context, onSubmit }: FeedbackControlsProps) {
  const [vote, setVote] = useState<"up" | "down" | null>(null);
  const [reason, setReason] = useState<FeedbackReasonCode | null>(null);
  const [note, setNote] = useState("");
  const [submitted, setSubmitted] = useState(false);

  if (submitted) {
    return (
      <p className="text-2xs font-semibold text-[var(--vg-text-muted)]">Cảm ơn bạn đã gửi phản hồi.</p>
    );
  }

  const handleVote = (v: "up" | "down") => {
    if (v === "up") {
      onSubmit("up");
      setSubmitted(true);
      return;
    }
    setVote(v);
  };

  const handleSubmitDown = () => {
    if (!reason) return;
    onSubmit("down", reason, note.trim() || undefined);
    setSubmitted(true);
  };

  return (
    <div className="space-y-2 pt-2 border-t border-[var(--vg-border)]">
      <div className="flex items-center gap-2">
        <span className="text-2xs font-bold text-[var(--vg-text-muted)] uppercase tracking-wide">
          {context === "checklist" ? "Checklist này có hữu ích không?" : "Kết quả tiền kiểm này có hữu ích không?"}
        </span>
        <button
          type="button"
          onClick={() => handleVote("up")}
          aria-label="Hữu ích"
          className="p-1.5 rounded-lg border border-[var(--vg-border)] hover:border-[var(--vg-accent)] hover:bg-[var(--vg-surface-subtle)] focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none"
        >
          <ThumbsUpIcon className="w-3.5 h-3.5" />
        </button>
        <button
          type="button"
          onClick={() => handleVote("down")}
          aria-label="Không hữu ích"
          className="p-1.5 rounded-lg border border-[var(--vg-border)] hover:border-[var(--vg-accent)] hover:bg-[var(--vg-surface-subtle)] focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none"
        >
          <ThumbsDownIcon className="w-3.5 h-3.5" />
        </button>
      </div>

      {vote === "down" && (
        <div className="space-y-2 pl-1">
          <div className="flex flex-wrap gap-1.5">
            {FEEDBACK_REASONS.map((r) => (
              <button
                key={r.code}
                type="button"
                onClick={() => setReason(r.code)}
                className={`px-2.5 py-1 rounded-full border text-2xs font-semibold transition-all ${
                  reason === r.code
                    ? "border-[var(--vg-accent)] bg-[var(--vg-accent-soft)] text-[var(--vg-accent)]"
                    : "border-[var(--vg-border)] text-[var(--vg-text-muted)] hover:border-[var(--vg-accent)]"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value.slice(0, FEEDBACK_NOTE_MAX_LENGTH))}
            maxLength={FEEDBACK_NOTE_MAX_LENGTH}
            placeholder="Góp ý thêm (không bắt buộc)"
            rows={2}
            className="w-full px-2.5 py-1.5 border border-[var(--vg-border)] bg-[var(--vg-surface)] rounded-md text-2xs focus:outline-none focus:border-[var(--vg-accent)]"
          />
          <div className="flex items-center justify-between">
            <span className="text-2xs text-[var(--vg-text-muted)]">{note.length}/{FEEDBACK_NOTE_MAX_LENGTH}</span>
            <button
              type="button"
              onClick={handleSubmitDown}
              disabled={!reason}
              className="px-3 py-1.5 bg-[var(--vg-accent)] text-white text-2xs font-bold rounded-md hover:bg-[var(--vg-accent-hover)] transition-all disabled:bg-zinc-200 disabled:text-zinc-400"
            >
              Gửi phản hồi
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
