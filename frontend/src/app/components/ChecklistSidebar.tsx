"use client";

import React from "react";

export interface Citation {
  title: string;
  url: string;
  ref_code: string;
}

export interface ChecklistItem {
  id: string;
  title: string;
  required: boolean;
  description: string;
  citations: Citation[];
}

export interface Step {
  step_number: number;
  title: string;
  description: string;
  processing_time: string;
  fees: string;
}

export interface ChecklistData {
  procedure_id: string;
  procedure_name: string;
  required_documents: ChecklistItem[];
  optional_documents: ChecklistItem[];
  steps: Step[];
  sources: Citation[];
}

interface ChecklistSidebarProps {
  checklist: ChecklistData | null;
  activeField?: string | null; // For highlight synchronization
}

export default function ChecklistSidebar({ checklist, activeField }: ChecklistSidebarProps) {
  if (!checklist) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center bg-card-bg text-zinc-500">
        <span className="text-3xl">📋</span>
        <h3 className="text-sm font-semibold mt-3 text-primary">Chưa có dữ liệu thủ tục</h3>
        <p className="text-xs mt-1 max-w-xs">
          Vui lòng trò chuyện với trợ lý hoặc chọn nhanh dịch vụ để tải checklist hồ sơ.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-y-auto p-5 space-y-6 bg-card-bg">
      {/* Header Info */}
      <div className="border-b border-border-slate pb-4 shrink-0">
        <span className="text-[10px] font-bold text-accent tracking-wider uppercase">Cơ sở pháp lý & Tài liệu</span>
        <h2 className="text-base font-bold text-primary mt-1">{checklist.procedure_name}</h2>
      </div>

      {/* Required / Optional Documents */}
      <div className="space-y-4">
        <div>
          <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2">Thành phần hồ sơ</h3>

          <div className="space-y-3">
            {/* Required Documents */}
            {checklist.required_documents.map((doc) => {
              // Simple heuristic to highlight document if it corresponds to active form field
              const isHighlighted = activeField && doc.id.includes(activeField.toLowerCase().replace(/_/g, "-"));

              return (
                <div
                  key={doc.id}
                  className={`p-3.5 border rounded-lg transition-all duration-300 ${
                    isHighlighted
                      ? "border-accent bg-blue-50/10 shadow-sm ring-1 ring-accent"
                      : "border-error-border bg-error-bg/10"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-xs font-bold text-error">{doc.title}</h4>
                    <span className="shrink-0 inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold bg-error-bg text-error border border-error-border">
                      BẮT BUỘC
                    </span>
                  </div>
                  <p className="text-xs text-zinc-600 mt-1.5 leading-relaxed">{doc.description}</p>

                  {doc.citations && doc.citations.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-zinc-100 flex flex-wrap gap-1.5 items-center">
                      <span className="text-[10px] font-bold text-zinc-400">Cơ sở pháp lý:</span>
                      {doc.citations.map((cite, idx) => (
                        <a
                          key={idx}
                          href={cite.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-[10px] font-semibold text-accent underline hover:text-accent-hover"
                        >
                          {cite.title}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}

            {/* Optional Documents */}
            {checklist.optional_documents.map((doc) => {
              const isHighlighted = activeField && doc.id.includes(activeField.toLowerCase().replace(/_/g, "-"));

              return (
                <div
                  key={doc.id}
                  className={`p-3.5 border rounded-lg transition-all duration-300 ${
                    isHighlighted
                      ? "border-accent bg-blue-50/10 shadow-sm ring-1 ring-accent"
                      : "border-warning-border bg-warning-bg/10"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-xs font-bold text-warning">{doc.title}</h4>
                    <span className="shrink-0 inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold bg-warning-bg text-warning border border-warning-border">
                      TÙY CHỌN
                    </span>
                  </div>
                  <p className="text-xs text-zinc-600 mt-1.5 leading-relaxed">{doc.description}</p>

                  {doc.citations && doc.citations.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-zinc-100 flex flex-wrap gap-1.5 items-center">
                      <span className="text-[10px] font-bold text-zinc-400">Cơ sở pháp lý:</span>
                      {doc.citations.map((cite, idx) => (
                        <a
                          key={idx}
                          href={cite.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-[10px] font-semibold text-accent underline hover:text-accent-hover"
                        >
                          {cite.title}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Timeline Steps */}
      <div className="pt-2">
        <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3">Quy trình giải quyết</h3>

        <div className="relative pl-4 border-l-2 border-zinc-200 ml-2 space-y-5">
          {checklist.steps.map((step) => (
            <div key={step.step_number} className="relative">
              {/* Dot */}
              <div className="absolute -left-[25px] top-0 flex items-center justify-center w-5 h-5 rounded-full bg-primary text-white text-[9px] font-bold">
                {step.step_number}
              </div>

              <div className="p-3.5 bg-neutral-bg border border-border-slate rounded-lg">
                <h4 className="text-xs font-bold text-primary">{step.title}</h4>
                <p className="text-xs text-zinc-600 mt-1 leading-relaxed">{step.description}</p>

                <div className="flex flex-wrap gap-3 mt-2.5 pt-2 border-t border-zinc-200/50 text-[10px] font-bold text-zinc-500">
                  <span className="inline-flex items-center gap-1">
                    ⏱ {step.processing_time}
                  </span>
                  <span className="inline-flex items-center gap-1">
                    💰 {step.fees}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
