"use client";

import { useState } from "react";
import { INPUT_MAX_LENGTH, STATIC_PROCEDURES } from "../procedureCase.constants";
import { BirthIcon, BusinessIcon, ChevronRightIcon, ResidenceIcon } from "../icons";

interface MessageComposerProps {
  isBusy: boolean;
  showQuickPicks: boolean;
  onSend: (text: string) => void;
  onSelectStaticProcedure: (procedureId: string) => void;
  onCancel: () => void;
}

type ProcedureIconName = (typeof STATIC_PROCEDURES)[number]["icon"];

const PROCEDURE_ICONS: Record<ProcedureIconName, typeof BirthIcon> = {
  birth: BirthIcon,
  residence: ResidenceIcon,
  business: BusinessIcon,
};

function ProcedureIcon({ name }: { name: ProcedureIconName }) {
  const Icon = PROCEDURE_ICONS[name];
  return <Icon className="w-5 h-5" />;
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
    <div className="shrink-0 bg-[var(--vg-surface-subtle)] border-t border-[var(--vg-border)]">
      {showQuickPicks && (
        <div className="p-4 pb-0 text-left">
          <span className="text-xs font-bold text-[var(--vg-text-muted)] block mb-2">
            Chọn nhanh dịch vụ công hỗ trợ
          </span>
          <div className="space-y-2">
            {STATIC_PROCEDURES.map((p) => (
              <button
                key={p.procedure_id}
                type="button"
                onClick={() => onSelectStaticProcedure(p.procedure_id)}
                className="w-full flex items-center gap-3 text-left px-4 py-3.5 min-h-[76px] bg-[var(--vg-surface)] border border-[var(--vg-border)] hover:border-[var(--vg-accent)] hover:bg-[var(--vg-accent-soft)] rounded-xl transition-all focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none"
              >
                <span className="shrink-0 w-10 h-10 rounded-lg bg-[var(--vg-gold-soft)] flex items-center justify-center">
                  <ProcedureIcon name={p.icon} />
                </span>
                <span className="flex-1 min-w-0">
                  <span className="block text-sm font-semibold text-[var(--vg-text)]">{p.label}</span>
                  <span className="block text-xs text-[var(--vg-text-muted)] mt-0.5">{p.description}</span>
                </span>
                <ChevronRightIcon className="w-4 h-4 shrink-0 text-[var(--vg-text-muted)]" />
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
            className="flex-1 px-4 py-2 border border-[var(--vg-border)] bg-[var(--vg-surface)] text-[var(--vg-text)] rounded-lg text-sm focus:outline-none focus:border-[var(--vg-accent)] focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)]"
          />
          {isBusy ? (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 bg-[var(--vg-surface)] border border-[var(--vg-border)] text-[var(--vg-text)] text-sm font-semibold rounded-lg hover:bg-[var(--vg-surface-subtle)] transition-all animate-vg-reveal"
            >
              Hủy
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim() || overLimit}
              className="px-4 py-2 bg-[var(--vg-accent)] text-white text-sm font-semibold rounded-lg hover:bg-[var(--vg-accent-hover)] transition-all disabled:bg-zinc-200 disabled:text-zinc-400 animate-vg-reveal"
            >
              Gửi
            </button>
          )}
        </div>
        <span
          className={`text-2xs font-semibold self-end ${overLimit ? "text-[var(--vg-error)]" : "text-[var(--vg-text-muted)]"}`}
        >
          {input.length}/{INPUT_MAX_LENGTH}
        </span>
      </form>
    </div>
  );
}
