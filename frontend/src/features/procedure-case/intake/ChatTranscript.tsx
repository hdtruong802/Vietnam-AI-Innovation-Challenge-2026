"use client";

import { useEffect, useRef } from "react";
import type { TranscriptMessage } from "../procedureCase.types";
import SourceDrawer from "../trust/SourceDrawer";

interface ChatTranscriptProps {
  messages: TranscriptMessage[];
}

export default function ChatTranscript({ messages }: ChatTranscriptProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`flex flex-col max-w-[85%] ${msg.role === "user" ? "ml-auto items-end" : "mr-auto items-start"}`}
        >
          <span className="text-[10px] font-bold text-foreground/50 mb-1 flex items-center gap-1">
            {msg.role === "user" ? "CÔNG DÂN" : "🤖 TRỢ LÝ VNGOV"}
          </span>
          <div
            className={`px-4 py-3 rounded-xl text-sm leading-relaxed shadow-sm relative ${
              msg.role === "user"
                ? "bg-accent text-white rounded-br-none font-sans font-medium"
                : "bg-card-bg border border-border-slate text-primary rounded-bl-none font-sans"
            }`}
          >
            <p className="whitespace-pre-line font-medium leading-relaxed">{msg.content}</p>
            {msg.sourceRefs && msg.sourceRefs.length > 0 && (
              <div className="mt-3 pt-2 border-t border-border-slate/60">
                <SourceDrawer citations={msg.sourceRefs} />
              </div>
            )}
          </div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
