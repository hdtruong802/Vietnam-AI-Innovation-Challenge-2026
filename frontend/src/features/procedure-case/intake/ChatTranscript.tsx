"use client";

import { useEffect, useRef, useState } from "react";
import type { TranscriptMessage } from "../procedureCase.types";
import SourceDrawer from "../trust/SourceDrawer";

interface ChatTranscriptProps {
  messages: TranscriptMessage[];
}

function AssistantIcon() {
  return (
    <span className="shrink-0 w-7 h-7 rounded-full bg-[var(--vg-accent-soft)] flex items-center justify-center">
      <svg
        className="w-4 h-4"
        viewBox="0 0 24 24"
        fill="none"
        stroke="var(--vg-accent)"
        strokeWidth={1.75}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M12 3 13 7 17 8 13 9 12 13 11 9 7 8 11 7 12 3Z" />
        <path d="M5 15v3M3.5 16.5h3M19 15v3M17.5 16.5h3" />
      </svg>
    </span>
  );
}

export default function ChatTranscript({ messages }: ChatTranscriptProps) {
  const endRef = useRef<HTMLDivElement>(null);
  // Messages present on mount (e.g. a restored session) render without an
  // entrance animation; only ones arriving afterward are "new".
  const [initialSeenCount] = useState(() => messages.length);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`flex items-start gap-2 max-w-[90%] ${msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"} ${
            index >= initialSeenCount ? "animate-vg-reveal" : ""
          }`}
        >
          {msg.role === "assistant" && <AssistantIcon />}
          <div className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
            <span className="text-2xs font-bold text-[var(--vg-text-muted)] mb-1">
              {msg.role === "user" ? "Công dân" : "Trợ lý VNGov"}
            </span>
            <div
              className={`px-4 py-3 rounded-xl text-sm leading-relaxed relative ${
                msg.role === "user"
                  ? "bg-[var(--vg-accent)] text-white rounded-tr-none font-medium"
                  : "bg-[var(--vg-surface)] border border-[var(--vg-border)] text-[var(--vg-text)] rounded-tl-none"
              }`}
            >
              <p className="whitespace-pre-line leading-relaxed">{msg.content}</p>
              {msg.sourceRefs && msg.sourceRefs.length > 0 && (
                <div className="mt-3 pt-2 border-t border-[var(--vg-border)]">
                  <SourceDrawer citations={msg.sourceRefs} />
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
