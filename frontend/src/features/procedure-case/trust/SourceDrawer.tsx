"use client";

import { useState } from "react";
import type { Citation } from "../procedureCase.types";

interface SourceDrawerProps {
  citations: Citation[];
  label?: string;
}

export default function SourceDrawer({ citations, label = "Nguồn pháp lý trích dẫn" }: SourceDrawerProps) {
  const [open, setOpen] = useState(false);
  if (citations.length === 0) return null;

  return (
    <div className="text-xs">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="inline-flex items-center gap-1 font-bold text-[var(--vg-accent)] hover:text-[var(--vg-accent-hover)] focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] rounded outline-none"
      >
        {label} ({citations.length}) {open ? "▲" : "▼"}
      </button>
      {open && (
        <ul className="list-disc pl-4 mt-1.5 space-y-1 font-medium text-[var(--vg-text-secondary)]">
          {citations.map((c) => (
            <li key={c.ref_id}>
              {c.url_or_ref ? (
                <a
                  href={c.url_or_ref}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[var(--vg-accent)] underline hover:text-[var(--vg-accent-hover)]"
                >
                  {c.title}
                </a>
              ) : (
                <span>{c.title}</span>
              )}
              {(c.effective_from || c.effective_to) && (
                <span className="text-[var(--vg-text-muted)]">
                  {" "}
                  ({c.effective_from ?? "?"} – {c.effective_to ?? "hiện tại"})
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
