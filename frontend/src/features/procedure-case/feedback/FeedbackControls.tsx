"use client";

import { useState } from "react";
import { FEEDBACK_NOTE_MAX_LENGTH, FEEDBACK_REASONS } from "../procedureCase.constants";
import type { FeedbackContext, FeedbackReasonCode } from "../procedureCase.types";

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
      <p className="text-[10px] font-semibold text-foreground/50">Cảm ơn bạn đã gửi phản hồi.</p>
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
    <div className="space-y-2 pt-2 border-t border-border-slate/60">
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold text-foreground/50 uppercase tracking-wide">
          {context === "checklist" ? "Checklist này có hữu ích không?" : "Kết quả tiền kiểm này có hữu ích không?"}
        </span>
        <button
          type="button"
          onClick={() => handleVote("up")}
          aria-label="Hữu ích"
          className="px-2 py-1 rounded-lg border border-border-slate hover:border-accent hover:bg-neutral-bg text-sm focus-visible:ring-2 focus-visible:ring-accent outline-none"
        >
          👍
        </button>
        <button
          type="button"
          onClick={() => handleVote("down")}
          aria-label="Không hữu ích"
          className="px-2 py-1 rounded-lg border border-border-slate hover:border-accent hover:bg-neutral-bg text-sm focus-visible:ring-2 focus-visible:ring-accent outline-none"
        >
          👎
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
                className={`px-2.5 py-1 rounded-full border text-[10px] font-semibold transition-all ${
                  reason === r.code
                    ? "border-accent bg-accent/10 text-accent"
                    : "border-border-slate text-foreground/60 hover:border-accent"
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
            className="w-full px-2.5 py-1.5 border border-border-slate bg-card-bg rounded-md text-[11px] focus:outline-none focus:border-accent"
          />
          <div className="flex items-center justify-between">
            <span className="text-[9px] text-foreground/40">{note.length}/{FEEDBACK_NOTE_MAX_LENGTH}</span>
            <button
              type="button"
              onClick={handleSubmitDown}
              disabled={!reason}
              className="px-3 py-1.5 bg-accent text-white text-[10px] font-bold rounded-md hover:bg-accent-hover transition-all disabled:opacity-50"
            >
              Gửi phản hồi
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
