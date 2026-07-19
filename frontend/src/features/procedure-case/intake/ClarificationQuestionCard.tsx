"use client";

import { useEffect, useId, useRef, useState } from "react";
import type { AnsweredQuestion, ClarifyingQuestion } from "../procedureCase.types";

interface ClarificationQuestionCardProps {
  questions: ClarifyingQuestion[];
  currentIndex: number;
  answeredQuestions: AnsweredQuestion[];
  onSubmit: (questionId: string, value: string) => void;
  onEdit: (questionId: string) => void;
}

export default function ClarificationQuestionCard({
  questions,
  currentIndex,
  answeredQuestions,
  onSubmit,
  onEdit,
}: ClarificationQuestionCardProps) {
  const question = questions[currentIndex];
  const [freeText, setFreeText] = useState("");
  const firstControlRef = useRef<HTMLButtonElement | HTMLInputElement>(null);
  const headingId = useId();

  // Reset the free-text draft during render when the question changes
  // (React's "adjust state during render" pattern), rather than in an
  // effect; only the focus side effect (a real external-system action)
  // belongs in an effect.
  const [lastQuestionId, setLastQuestionId] = useState(question?.id);
  if (question?.id !== lastQuestionId) {
    setLastQuestionId(question?.id);
    if (freeText !== "") setFreeText("");
  }

  useEffect(() => {
    firstControlRef.current?.focus();
  }, [question?.id]);

  const priorAnswers = answeredQuestions.filter((a) =>
    questions.some((q) => q.id === a.questionId),
  );

  if (!question) return null;

  return (
    <div className="mx-4 mb-3 space-y-3">
      {priorAnswers.length > 0 && (
        <ul className="space-y-1.5">
          {priorAnswers.map((a) => {
            const q = questions.find((q) => q.id === a.questionId);
            return (
              <li
                key={a.questionId}
                className="flex items-center justify-between gap-2 px-3 py-2 bg-[var(--vg-surface-subtle)] border border-[var(--vg-border)] rounded-lg text-xs"
              >
                <span className="text-[var(--vg-text-secondary)] font-medium truncate">
                  {q?.prompt}: <span className="font-bold text-[var(--vg-text)]">{a.value}</span>
                </span>
                <button
                  type="button"
                  onClick={() => onEdit(a.questionId)}
                  className="shrink-0 text-[var(--vg-accent)] font-bold hover:text-[var(--vg-accent-hover)] focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] rounded outline-none"
                >
                  Sửa câu trả lời trước
                </button>
              </li>
            );
          })}
        </ul>
      )}

      <div
        role="group"
        aria-labelledby={headingId}
        className="p-4 bg-[var(--vg-surface)] border border-[var(--vg-border)] rounded-xl space-y-3 text-left"
      >
        <div>
          <span className="text-2xs font-semibold text-[var(--vg-accent)] tracking-wider uppercase">
            Câu hỏi {currentIndex + 1}/{questions.length}
          </span>
          <h4 id={headingId} className="text-sm font-bold text-[var(--vg-text)] mt-0.5 text-pretty">
            {question.prompt}
            {question.required && <span className="text-[var(--vg-error)]"> *</span>}
          </h4>
          {question.why && <p className="text-xs text-[var(--vg-text-muted)] mt-1">{question.why}</p>}
        </div>

        {question.options.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {question.options.map((opt, i) => (
              <button
                key={opt}
                ref={i === 0 ? (firstControlRef as React.RefObject<HTMLButtonElement>) : undefined}
                type="button"
                onClick={() => onSubmit(question.id, opt)}
                className="px-3.5 py-2 border border-[var(--vg-border)] rounded-lg text-xs font-semibold text-[var(--vg-text)] hover:border-[var(--vg-accent)] hover:bg-[var(--vg-surface-subtle)] transition-all focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none"
              >
                {opt}
              </button>
            ))}
          </div>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!freeText.trim()) return;
              onSubmit(question.id, freeText.trim());
            }}
            className="flex gap-2"
          >
            <input
              ref={firstControlRef as React.RefObject<HTMLInputElement>}
              type="text"
              value={freeText}
              onChange={(e) => setFreeText(e.target.value)}
              className="flex-1 px-3 py-2 border border-[var(--vg-border)] bg-[var(--vg-surface)] rounded-md text-xs focus:outline-none focus:border-[var(--vg-accent)] focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)]"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-[var(--vg-accent)] text-white text-xs font-bold rounded-md hover:bg-[var(--vg-accent-hover)] transition-all"
            >
              Tiếp tục
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
