"use client";

import React, { useState, useEffect, useRef } from "react";
import ChecklistSidebar from "./components/ChecklistSidebar";

// Simple client-side UUID generator
const generateUUID = () => {
  return "session_" + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

interface Citation {
  title: string;
  url: string;
  ref_code: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Citation[];
}

interface ChecklistItem {
  id: string;
  title: string;
  required: boolean;
  description: string;
  citations: Citation[];
}

interface Step {
  step_number: number;
  title: string;
  description: string;
  processing_time: string;
  fees: string;
}

interface ChecklistResponse {
  procedure_id: string;
  procedure_name: string;
  required_documents: ChecklistItem[];
  optional_documents: ChecklistItem[];
  steps: Step[];
  form_schema: {
    type: string;
    properties: Record<string, { type: string; title: string; minLength?: number; format?: string }>;
    required?: string[];
  };
  sources: Citation[];
}

interface Finding {
  field?: string;
  level: "error" | "warning" | "info" | "success";
  message: string;
  rule_code: string;
  citation?: Citation;
}

interface ValidationResponse {
  is_valid: boolean;
  findings: Finding[];
  summary: string;
}

export default function Home() {
  // State variables
  const [sessionId, setSessionId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentProcedureId, setCurrentProcedureId] = useState<string | null>(null);

  // Checklist & Schema states
  const [checklist, setChecklist] = useState<ChecklistResponse | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [validationResponse, setValidationResponse] = useState<ValidationResponse | null>(null);
  const [isValidating, setIsValidating] = useState<boolean>(false);

  // Navigation / Tabs state
  const [activeLeftTab, setActiveLeftTab] = useState<"chat" | "checklist">("chat");
  const [activeMobileTab, setActiveMobileTab] = useState<"chat" | "form">("chat");
  const [backendHealth, setBackendHealth] = useState<"online" | "offline" | "checking">("checking");
  const [activeField, setActiveField] = useState<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Initialize Session
  useEffect(() => {
    setSessionId(generateUUID());
    // Initial welcome message
    setMessages([
      {
        role: "assistant",
        content: "Xin chào! Tôi là **VNGov**, trợ lý hướng dẫn và tiền kiểm hồ sơ hành chính công trực tuyến của bạn.\n\nTải dữ liệu của tôi được thiết kế theo đúng quy định pháp lý hành chính hiện hành. Bạn đang cần thực hiện thủ tục nào dưới đây?",
      },
    ]);
    checkBackendHealth();
  }, []);

  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const checkBackendHealth = async () => {
    try {
      const res = await fetch("http://localhost:8000/health", { method: "GET" });
      if (res.ok) {
        setBackendHealth("online");
      } else {
        setBackendHealth("offline");
      }
    } catch (e) {
      setBackendHealth("offline");
    }
  };

  // Start a specific procedure
  const handleSelectProcedure = async (procedureId: string) => {
    setCurrentProcedureId(procedureId);
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: `Tôi đã kích hoạt biểu mẫu đăng ký cho thủ tục. Đang tải checklist tài liệu và các trường khai báo phù hợp...`,
      },
    ]);
    await fetchChecklist(procedureId);
    // Switch view
    setActiveLeftTab("checklist");
    setActiveMobileTab("form");
  };

  // Fetch Checklist & Form Schema from Backend
  const fetchChecklist = async (procedureId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/v1/procedures/${procedureId}/checklist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_answers: {} }),
      });
      if (res.ok) {
        const data: ChecklistResponse = await res.json();
        setChecklist(data);
        // Reset form data
        const initialForm: Record<string, string> = {};
        if (data.form_schema && data.form_schema.properties) {
          Object.keys(data.form_schema.properties).forEach((key) => {
            initialForm[key] = "";
          });
        }
        setFormData(initialForm);
        setValidationResponse(null);
      }
    } catch (e) {
      console.error("Failed to fetch checklist", e);
    }
  };

  // Send message to AI Chatbot
  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setIsLoading(true);

    try {
      const chatPayload = {
        session_id: sessionId,
        messages: [
          ...messages.map((m) => ({ role: m.role, content: m.content })),
          { role: "user", content: userMsg },
        ],
        current_procedure_id: currentProcedureId,
      };

      const res = await fetch("http://localhost:8000/v1/intake/turn", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(chatPayload),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: data.message,
            sources: data.sources,
          },
        ]);

        // If the AI classified and detected a procedure id
        if (data.detected_procedure_id && data.detected_procedure_id !== currentProcedureId) {
          setCurrentProcedureId(data.detected_procedure_id);
          await fetchChecklist(data.detected_procedure_id);
          setActiveLeftTab("checklist");
        }
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Rất tiếc, đã có lỗi xảy ra từ máy chủ dịch vụ. Xin hãy thử lại sau.",
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại trạng thái Backend.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Dynamic Form Inputs
  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Pre-check Application Form Data
  const handlePreCheck = async () => {
    if (!currentProcedureId) return;
    setIsValidating(true);
    setValidationResponse(null);

    try {
      const validatePayload = {
        procedure_id: currentProcedureId,
        form_data: formData,
      };

      const res = await fetch("http://localhost:8000/v1/applications/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validatePayload),
      });

      if (res.ok) {
        const data: ValidationResponse = await res.json();
        setValidationResponse(data);
      }
    } catch (e) {
      console.error("Validation failed", e);
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-neutral-bg text-primary font-sans antialiased pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)] pb-[env(safe-area-inset-bottom)]">
      {/* 1. Navbar */}
      <header className="flex items-center justify-between px-6 pr-[max(1.5rem,env(safe-area-inset-right))] pl-[max(1.5rem,env(safe-area-inset-left))] py-4 bg-card-bg border-b border-border-slate shadow-sm shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-md bg-accent text-white font-bold text-sm">
            VN
          </div>
          <div>
            <h1 className="text-base font-semibold leading-tight tracking-tight text-primary">
              VNGov Copilot
            </h1>
            <p className="text-xs text-zinc-500 font-medium">Trợ lý tiền kiểm hồ sơ hành chính</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className="hidden md:inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-zinc-100 text-zinc-800 border border-zinc-200">
            DỊCH VỤ CÔNG QUỐC GIA
          </span>
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                backendHealth === "online"
                  ? "bg-success animate-pulse"
                  : backendHealth === "offline"
                  ? "bg-error"
                  : "bg-warning"
              }`}
            />
            <span className="text-xs font-medium text-zinc-600">
              {backendHealth === "online"
                ? "Hệ thống kết nối"
                : backendHealth === "offline"
                ? "Backend Ngoại tuyến"
                : "Đang kiểm tra kết nối..."}
            </span>
          </div>
        </div>
      </header>

      {/* Mobile view Tabs Switcher */}
      <div className="flex md:hidden border-b border-border-slate bg-card-bg shrink-0">
        <button
          onClick={() => setActiveMobileTab("chat")}
          className={`flex-1 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeMobileTab === "chat"
              ? "border-accent text-accent"
              : "border-transparent text-zinc-500"
          }`}
        >
          Trợ lý Chat & Checklist
        </button>
        <button
          onClick={() => setActiveMobileTab("form")}
          className={`flex-1 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeMobileTab === "form"
              ? "border-accent text-accent"
              : "border-transparent text-zinc-500"
          }`}
        >
          Tờ khai & Tiền kiểm
        </button>
      </div>

      {/* 2. Main Layout Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Column (40% width) - Contains Chat & Checklist */}
        <aside
          className={`${
            activeMobileTab === "chat" ? "flex" : "hidden"
          } md:flex flex-col w-full md:w-[40%] bg-card-bg border-r border-border-slate overflow-hidden`}
        >
          {/* Tabs for Chat vs Checklist */}
          <div className="flex border-b border-border-slate bg-neutral-bg shrink-0">
            <button
              onClick={() => setActiveLeftTab("chat")}
              className={`flex-1 py-3 text-xs uppercase tracking-wider font-bold border-b-2 transition-all ${
                activeLeftTab === "chat"
                  ? "border-primary text-primary bg-card-bg"
                  : "border-transparent text-zinc-500 hover:text-zinc-800"
              }`}
            >
              Trợ lý Hướng dẫn
            </button>
            <button
              onClick={() => setActiveLeftTab("checklist")}
              disabled={!checklist}
              className={`flex-1 py-3 text-xs uppercase tracking-wider font-bold border-b-2 transition-all ${
                !checklist
                  ? "opacity-40 cursor-not-allowed text-zinc-400"
                  : activeLeftTab === "checklist"
                  ? "border-primary text-primary bg-card-bg"
                  : "border-transparent text-zinc-500 hover:text-zinc-800"
              }`}
            >
              Checklist Hồ sơ {!checklist ? "" : `(${checklist.required_documents.length + checklist.optional_documents.length})`}
            </button>
          </div>

          {/* Tab Content 1: Chat Stream */}
          <div className={`${activeLeftTab === "chat" ? "flex" : "hidden"} flex-col flex-1 overflow-hidden bg-card-bg`}>
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex flex-col max-w-[85%] ${
                    msg.role === "user" ? "ml-auto items-end" : "mr-auto items-start"
                  }`}
                >
                  <span className="text-[10px] font-bold text-zinc-400 mb-1">
                    {msg.role === "user" ? "CÔNG DÂN" : "TRỢ LÝ VNGOV"}
                  </span>

                  {/* Bubble */}
                  <div
                    className={`px-4 py-3 rounded-lg text-sm leading-relaxed shadow-sm ${
                      msg.role === "user"
                        ? "bg-[#2563EB] text-white rounded-br-none"
                        : "bg-[#0F172A] text-white rounded-bl-none"
                    }`}
                  >
                    <p className="whitespace-pre-line">{msg.content}</p>

                    {/* Citations / Sources */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-3 pt-2 border-t border-zinc-700/50 text-xs text-zinc-300">
                        <span className="font-bold block mb-1">Nguồn pháp lý trích dẫn:</span>
                        <ul className="list-disc pl-4 space-y-1">
                          {msg.sources.map((src, i) => (
                            <li key={i}>
                              <a
                                href={src.url}
                                target="_blank"
                                rel="noreferrer"
                                className="underline hover:text-white transition-colors"
                              >
                                {src.title} ({src.ref_code})
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Dynamic Empty State suggestions */}
              {messages.length === 1 && (
                <div className="pt-2">
                  <span className="text-xs font-bold text-zinc-500 block mb-2">Chọn nhanh dịch vụ công hỗ trợ:</span>
                  <div className="space-y-2">
                    <button
                      onClick={() => handleSelectProcedure("dang-ky-khai-sinh")}
                      className="w-full text-left px-4 py-3.5 bg-neutral-bg border border-border-slate hover:border-accent hover:bg-zinc-100 rounded-lg transition-all text-xs font-semibold text-primary min-h-[44px]"
                    >
                      👶 Đăng ký khai sinh
                    </button>
                    <button
                      onClick={() => handleSelectProcedure("dang-ky-thuong-tru")}
                      className="w-full text-left px-4 py-3.5 bg-neutral-bg border border-border-slate hover:border-accent hover:bg-zinc-100 rounded-lg transition-all text-xs font-semibold text-primary min-h-[44px]"
                    >
                      🏠 Đăng ký thường trú
                    </button>
                    <button
                      onClick={() => handleSelectProcedure("dang-ky-ho-kinh-doanh")}
                      className="w-full text-left px-4 py-3.5 bg-neutral-bg border border-border-slate hover:border-accent hover:bg-zinc-100 rounded-lg transition-all text-xs font-semibold text-primary min-h-[44px]"
                    >
                      💼 Đăng ký thành lập hộ kinh doanh
                    </button>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <form onSubmit={handleSendMessage} className="p-3 bg-neutral-bg border-t border-border-slate flex gap-2 shrink-0">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
                placeholder="Nhập câu hỏi của bạn tại đây..."
                className="flex-1 px-4 py-2 border border-border-slate bg-card-bg rounded-md text-sm focus:outline-none focus:border-accent"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="px-4 py-2 bg-[#2563EB] text-white text-sm font-semibold rounded-md hover:bg-[#1D4ED8] transition-all disabled:opacity-50"
              >
                Gửi
              </button>
            </form>
          </div>

          {/* Tab Content 2: Checklist display */}
          <div className={`${activeLeftTab === "checklist" ? "flex" : "hidden"} flex-col flex-1 overflow-y-auto bg-white`}>
            <ChecklistSidebar checklist={checklist} activeField={activeField} />
          </div>
        </aside>

        {/* Right Column (60% width) - Contains Form Input & Validation */}
        <main
          className={`${
            activeMobileTab === "form" ? "flex" : "hidden"
          } md:flex flex-col flex-1 bg-[#F8FAFC] overflow-y-auto p-6`}
        >
          {checklist ? (
            <div className="max-w-xl mx-auto w-full space-y-6">
              {/* Form Sheet container */}
              <div className="bg-white border border-border-slate rounded-lg p-6 shadow-sm">
                <div className="border-b border-border-slate pb-4 mb-6">
                  <span className="text-[10px] font-bold text-accent tracking-wider uppercase block">TỜ KHAI ĐIỆN TỬ SƠ BỘ</span>
                  <h2 className="text-lg font-bold text-primary">{checklist.procedure_name}</h2>
                  <p className="text-xs text-zinc-500 mt-1">Vui lòng hoàn thành các trường dưới đây để trợ lý tiền kiểm tra.</p>
                </div>

                <div className="space-y-4">
                  {checklist.form_schema && checklist.form_schema.properties &&
                    Object.entries(checklist.form_schema.properties).map(([key, prop]) => {
                      const isRequired = checklist.form_schema.required?.includes(key);
                      const hasError = validationResponse?.findings.some(f => f.field === key && f.level === "error");
                      const errorMsg = validationResponse?.findings.find(f => f.field === key && f.level === "error")?.message;

                      return (
                        <div key={key} className="flex flex-col">
                          <label
                            htmlFor={`input-${key}`}
                            className="text-xs font-bold text-primary mb-1.5"
                          >
                            {prop.title} {isRequired && <span className="text-error">*</span>}
                          </label>
                          <input
                            id={`input-${key}`}
                            type={prop.format === "date" ? "date" : "text"}
                            value={formData[key] || ""}
                            onChange={(e) => handleInputChange(key, e.target.value)}
                            onFocus={() => setActiveField(key)}
                            onBlur={() => setActiveField(null)}
                            aria-required={isRequired ? "true" : "false"}
                            aria-invalid={hasError ? "true" : "false"}
                            aria-describedby={hasError ? `error-${key}` : undefined}
                            className={`px-3 py-2 border rounded-md text-sm transition-all focus:outline-none focus:border-accent ${
                              hasError ? "border-error bg-error-bg/10" : "border-border-slate bg-white"
                            }`}
                          />
                          {hasError && (
                            <span id={`error-${key}`} className="text-[11px] font-semibold text-error mt-1">
                              ⚠️ {errorMsg}
                            </span>
                          )}
                        </div>
                      );
                    })}
                </div>

                <div className="mt-8 pt-6 border-t border-border-slate flex gap-3">
                  <button
                    onClick={handlePreCheck}
                    disabled={isValidating}
                    className="flex-1 py-2.5 bg-accent text-white text-sm font-semibold rounded-md hover:bg-accent-hover transition-all disabled:opacity-50 flex items-center justify-center gap-2 min-h-[44px]"
                  >
                    {isValidating ? "Đang xử lý..." : "🔍 Bắt đầu tiền kiểm hồ sơ"}
                  </button>
                </div>
              </div>

              {/* Validation Response Panel */}
              {validationResponse && (
                <div className={`border rounded-lg p-5 shadow-sm ${
                  validationResponse.is_valid
                    ? "bg-success-bg border-success-border"
                    : "bg-error-bg border-error-border"
                }`}>
                  <h3 className={`text-sm font-bold flex items-center gap-2 ${
                    validationResponse.is_valid ? "text-success" : "text-error"
                  }`}>
                    {validationResponse.is_valid ? "✅ HỒ SƠ ĐỦ ĐIỀU KIỆN SƠ BỘ" : "⚠️ PHÁT HIỆN LỖI KÊ KHAI HỒ SƠ"}
                  </h3>

                  <p className="text-xs text-zinc-700 mt-2 font-medium leading-relaxed">
                    {validationResponse.summary}
                  </p>

                  {validationResponse.findings && validationResponse.findings.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-zinc-200/50 space-y-2">
                      <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block mb-1">
                        Chi tiết các phát hiện:
                      </span>
                      <div className="space-y-2">
                        {validationResponse.findings.map((finding, idx) => (
                          <div key={idx} className={`p-3 rounded-lg text-xs leading-relaxed ${
                            finding.level === "error"
                              ? "bg-white border border-error-border text-error"
                              : finding.level === "warning"
                              ? "bg-white border border-warning-border text-warning"
                              : "bg-white border border-zinc-200 text-zinc-700"
                          }`}>
                            <div className="font-bold flex items-center gap-1.5">
                              <span className={`w-2 h-2 rounded-full ${
                                finding.level === "error" ? "bg-error" : "bg-warning"
                              }`} />
                              {finding.level === "error" ? "Sai sót bắt buộc sửa" : "Cảnh báo cần lưu ý"}
                            </div>
                            <p className="mt-1 font-medium">{finding.message}</p>
                            {finding.citation && (
                              <span className="block mt-2 text-[10px] font-semibold text-zinc-500">
                                Luật trích dẫn: <a href={finding.citation.url} target="_blank" rel="noreferrer" className="underline">{finding.citation.title} ({finding.citation.ref_code})</a>
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 bg-white border border-border-slate rounded-lg">
              <span className="text-4xl">📋</span>
              <h2 className="text-base font-bold text-primary mt-4">Chưa có tờ khai nào được chọn</h2>
              <p className="text-xs text-zinc-500 mt-2 max-w-xs">
                Vui lòng nhấn chọn các nút thủ tục gợi ý nhanh trong khung chat, hoặc trò chuyện với trợ lý để bắt đầu lập hồ sơ.
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
