"use client";

import { useState } from "react";
import { INPUT_MAX_LENGTH, STATIC_PROCEDURES } from "../procedureCase.constants";

interface MessageComposerProps {
  isBusy: boolean;
  showQuickPicks: boolean;
  onSend: (text: string) => void;
  onSelectStaticProcedure: (procedureId: string) => void;
  onCancel: () => void;
}

export default function MessageComposer({
  isBusy,
  showQuickPicks,
  onSend,
  onSelectStaticProcedure,
  onCancel,
}: MessageComposerProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isBusy) return;
    onSend(text);
    setInput("");
  };

  const overLimit = input.length > INPUT_MAX_LENGTH;

  return (
    <div className="shrink-0 bg-neutral-bg border-t border-border-slate">
      {showQuickPicks && (
        <div className="p-4 pb-0 text-left">
          <span className="text-xs font-bold text-zinc-500 block mb-2">Chọn nhanh dịch vụ công hỗ trợ:</span>
          <div className="space-y-2">
            {STATIC_PROCEDURES.map((p) => (
              <button
                key={p.procedure_id}
                type="button"
                onClick={() => onSelectStaticProcedure(p.procedure_id)}
                className="w-full text-left px-4 py-3.5 bg-card-bg border border-border-slate hover:border-accent hover:bg-zinc-100 rounded-lg transition-all text-xs font-semibold text-primary min-h-[44px] focus-visible:ring-2 focus-visible:ring-accent outline-none"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="p-3 flex flex-col gap-1.5">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isBusy}
            maxLength={INPUT_MAX_LENGTH}
            placeholder="Nhập câu hỏi của bạn tại đây..."
            aria-label="Nhập câu hỏi"
            className="flex-1 px-4 py-2 border border-border-slate bg-card-bg rounded-md text-sm focus:outline-none focus:border-accent focus-visible:ring-2 focus-visible:ring-accent"
          />
          {isBusy ? (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 bg-neutral-bg border border-border-slate text-primary text-sm font-semibold rounded-md hover:bg-zinc-100 transition-all"
            >
              Hủy
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim() || overLimit}
              className="px-4 py-2 bg-accent text-white text-sm font-semibold rounded-md hover:bg-accent-hover transition-all disabled:opacity-50"
            >
              Gửi
            </button>
          )}
        </div>
        <span className={`text-[10px] font-semibold self-end ${overLimit ? "text-error" : "text-foreground/40"}`}>
          {input.length}/{INPUT_MAX_LENGTH}
        </span>
      </form>
    </div>
  );
}
