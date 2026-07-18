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

const TrongDongPattern = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 400 400" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="200" cy="200" r="25" stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 4" />
    <path d="M200 135L200 175M200 225L200 265M135 200L175 200M225 200L265 200M154 154L182 182M218 218L246 246M154 246L182 218M218 182L246 154" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <circle cx="200" cy="200" r="50" stroke="currentColor" strokeWidth="1" />
    <circle cx="200" cy="200" r="80" stroke="currentColor" strokeWidth="0.75" strokeDasharray="6 3" />
    <circle cx="200" cy="200" r="110" stroke="currentColor" strokeWidth="1.5" />
    <circle cx="200" cy="200" r="140" stroke="currentColor" strokeWidth="0.75" strokeDasharray="8 4" />
    <circle cx="200" cy="200" r="170" stroke="currentColor" strokeWidth="2.5" />
    <circle cx="200" cy="200" r="125" stroke="currentColor" strokeWidth="0.75" opacity="0.3" />
    <g opacity="0.45" stroke="currentColor" strokeWidth="1" fill="none">
      <path d="M280 120 C270 125, 260 120, 255 110 C260 108, 270 110, 280 120 Z" />
      <path d="M255 110 L240 100" />
      <path d="M120 280 C125 270, 120 260, 110 255 C108 260, 110 270, 120 280 Z" />
      <path d="M110 255 L100 240" />
      <path d="M120 120 C125 125, 120 135, 110 140 C108 135, 110 125, 120 120 Z" />
      <path d="M280 280 C275 275, 270 280, 265 290 C270 292, 275 288, 280 280 Z" />
    </g>
  </svg>
);

const LotusFlowerPattern = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g stroke="currentColor" strokeWidth="1.25" fill="none" opacity="0.35">
      <path d="M100 50 C90 70, 90 120, 100 150 C110 120, 110 70, 100 50 Z" />
      <path d="M100 80 C70 90, 50 110, 60 140 C75 140, 90 120, 100 100" />
      <path d="M100 100 C50 110, 30 130, 45 155 C65 150, 85 130, 100 115" />
      <path d="M100 80 C130 90, 150 110, 140 140 C125 140, 110 120, 100 100" />
      <path d="M100 100 C150 110, 170 130, 155 155 C135 150, 115 130, 100 115" />
      <path d="M60 160 C75 175, 125 175, 140 160" />
      <path d="M40 170 C65 190, 135 190, 160 170" />
    </g>
  </svg>
);

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

  // Dynamic Landing/Copilot view state
  const [view, setView] = useState<"landing" | "copilot">("landing");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalText, setModalText] = useState<string>("");

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
    setView("copilot");
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

  const handleOpenComingSoon = (text: string) => {
    setModalText(text);
    setShowModal(true);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    const query = searchQuery.toLowerCase();
    if (query.includes("sinh") || query.includes("birth")) {
      handleSelectProcedure("dang-ky-khai-sinh");
    } else if (query.includes("trú") || query.includes("residence")) {
      handleSelectProcedure("dang-ky-thuong-tru");
    } else if (query.includes("doanh") || query.includes("business")) {
      handleSelectProcedure("dang-ky-ho-kinh-doanh");
    } else {
      setView("copilot");
      setMessages((prev) => [
        ...prev,
        {
          role: "user",
          content: searchQuery,
        },
      ]);
      setSearchQuery("");
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

  if (view === "landing") {
    return (
      <div className="min-h-screen bg-background text-foreground font-sans antialiased flex flex-col relative overflow-x-hidden">
        {/* Header / Navbar */}
        <header className="flex items-center justify-between px-6 md:px-12 py-4 bg-card-bg border-b border-border-slate shadow-sm shrink-0 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-amber-500 via-red-500 to-amber-600" />
          <div className="flex items-center gap-3 relative z-10">
            <div className="relative flex items-center justify-center w-12 h-12 rounded-full border border-border-slate/40 bg-neutral-bg/50 shadow-inner shrink-0">
              <svg className="w-10 h-10" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="46" fill="#DA251D" stroke="#D97706" strokeWidth="2"/>
                <path d="M50 20L58.2 41.5H81L62.6 55.4L69.6 77L50 63.5L30.4 77L37.4 55.4L19 41.5H41.8L50 20Z" fill="#FFFF00"/>
                <circle cx="50" cy="50" r="28" stroke="#FFFF00" strokeWidth="1" strokeDasharray="3 3" opacity="0.6"/>
                <path d="M22 65 C32 80, 68 80, 78 65" stroke="#FFFF00" strokeWidth="1.5" strokeLinecap="round" opacity="0.8"/>
              </svg>
            </div>
            <div>
              <h1 className="text-sm md:text-md font-serif font-extrabold leading-tight tracking-tight text-primary">
                CỔNG DỊCH VỤ CÔNG QUỐC GIA
              </h1>
              <p className="text-[9px] uppercase font-bold text-accent tracking-widest font-sans">Kết nối, cung cấp thông tin và dịch vụ công mọi lúc, mọi nơi</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center gap-6 text-xs font-bold text-foreground/75">
            <button className="text-accent hover:text-accent-hover border-b-2 border-accent pb-1">Trang chủ</button>
            <button className="hover:text-accent pb-1 transition-colors" onClick={() => handleOpenComingSoon("Giới thiệu hệ thống dịch vụ công đang được cập nhật.")}>Giới thiệu</button>
            <button className="hover:text-accent pb-1 transition-colors" onClick={() => setView("copilot")}>Dịch vụ công</button>
            <button className="hover:text-accent pb-1 transition-colors" onClick={() => handleOpenComingSoon("Chức năng tra cứu hồ sơ điện tử đang liên kết với cơ sở dữ liệu quốc gia.")}>Tra cứu hồ sơ</button>
            <button className="hover:text-accent pb-1 transition-colors" onClick={() => handleOpenComingSoon("Cổng thanh toán điện tử phí & lệ phí hành chính đang được bảo trì định kỳ.")}>Thanh toán</button>
            <button className="hover:text-accent pb-1 transition-colors" onClick={() => handleOpenComingSoon("Tổng đài hỗ trợ 1900 1234 phục vụ 24/7.")}>Hỗ trợ</button>
          </nav>

          {/* Auth Button */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleOpenComingSoon("Chức năng đăng nhập thông qua VNeID / Cổng Quốc gia đang được kết nối.")}
              className="px-4 py-2 bg-brand-red text-white text-xs font-bold rounded-lg hover:bg-brand-red-hover transition-all shadow-sm"
            >
              Đăng nhập
            </button>
          </div>
        </header>

        {/* Hero Section */}
        <section className="relative bg-gradient-to-b from-hero-start via-hero-end to-background py-16 md:py-24 px-6 md:px-12 text-center overflow-hidden shrink-0">
          <TrongDongPattern className="absolute w-[450px] h-[450px] md:w-[600px] md:h-[600px] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-white/10 pointer-events-none motion-safe:animate-[spin_180s_linear_infinite]" />
          <LotusFlowerPattern className="absolute w-[200px] h-[200px] bottom-0 left-0 md:left-10 text-white/20 pointer-events-none" />
          <LotusFlowerPattern className="absolute w-[200px] h-[200px] bottom-0 right-0 md:right-10 text-white/20 pointer-events-none" />

          <div className="max-w-3xl mx-auto relative z-10">
            <h2 className="text-3xl md:text-5xl font-serif font-extrabold text-white leading-tight tracking-tight drop-shadow-md">
              Kết nối, cung cấp thông tin và dịch vụ công mọi lúc, mọi nơi
            </h2>
            <p className="text-xs md:text-sm text-white/90 mt-4 max-w-xl mx-auto leading-relaxed font-medium">
              Cổng Dịch vụ công Quốc gia là cầu nối giữa cơ quan nhà nước và người dân, doanh nghiệp trên môi trường số.
            </p>

            {/* Premium Search Bar */}
            <form onSubmit={handleSearchSubmit} className="mt-8 max-w-xl mx-auto flex gap-2 p-1.5 bg-card-bg rounded-xl shadow-lg border border-border-slate/50">
              <input
                id="landing-search-input"
                aria-label="Tìm kiếm dịch vụ công"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Bạn cần tìm dịch vụ công nào? (ví dụ: khai sinh, thường trú...)"
                className="flex-1 px-4 py-3 bg-transparent text-sm focus:outline-none text-foreground placeholder-foreground/50 font-medium"
              />
              <button
                type="submit"
                className="px-5 py-3 bg-brand-red text-white rounded-lg hover:bg-brand-red-hover transition-all flex items-center justify-center gap-2 text-xs font-bold"
              >
                <span>🔍</span>
                <span className="hidden sm:inline">Tìm kiếm</span>
              </button>
            </form>
          </div>
        </section>

        {/* 6 Grid Quick Options */}
        <section className="px-6 md:px-12 -mt-8 relative z-20 shrink-0">
          <div className="max-w-6xl mx-auto bg-card-bg border border-border-slate rounded-2xl shadow-xl p-6 md:p-8 grid grid-cols-2 md:grid-cols-6 gap-6 text-center">
            <button
              onClick={() => setView("copilot")}
              className="flex flex-col items-center justify-center p-3 rounded-xl hover:bg-neutral-bg/50 transition-all group"
            >
              <div className="w-12 h-12 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">📋</div>
              <span className="text-[11px] font-bold text-foreground/80 leading-snug">Đăng ký, quản lý hồ sơ trực tuyến</span>
            </button>

            <button
              onClick={() => handleOpenComingSoon("Thanh toán lệ phí trực tuyến an toàn, tích hợp ngân hàng quốc gia.")}
              className="flex flex-col items-center justify-center p-3 rounded-xl hover:bg-neutral-bg/50 transition-all group"
            >
              <div className="w-12 h-12 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">💳</div>
              <span className="text-[11px] font-bold text-foreground/80 leading-snug">Thanh toán trực tuyến phí, lệ phí</span>
            </button>

            <button
              onClick={() => handleOpenComingSoon("Nhập mã hồ sơ hành chính của bạn để theo dõi tiến độ giải quyết trực tiếp.")}
              className="flex flex-col items-center justify-center p-3 rounded-xl hover:bg-neutral-bg/50 transition-all group"
            >
              <div className="w-12 h-12 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">🔍</div>
              <span className="text-[11px] font-bold text-foreground/80 leading-snug">Tra cứu hồ sơ đã nộp</span>
            </button>

            <button
              onClick={() => handleOpenComingSoon("Ý kiến đóng góp của bạn giúp cải tiến thủ tục hành chính tốt hơn.")}
              className="flex flex-col items-center justify-center p-3 rounded-xl hover:bg-neutral-bg/50 transition-all group"
            >
              <div className="w-12 h-12 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">⭐</div>
              <span className="text-[11px] font-bold text-foreground/80 leading-snug">Đánh giá chất lượng dịch vụ công</span>
            </button>

            <button
              onClick={() => handleOpenComingSoon("Gửi trực tiếp phản ánh, kiến nghị về vướng mắc thủ tục hành chính.")}
              className="flex flex-col items-center justify-center p-3 rounded-xl hover:bg-neutral-bg/50 transition-all group"
            >
              <div className="w-12 h-12 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">💬</div>
              <span className="text-[11px] font-bold text-foreground/80 leading-snug">Phản ánh, kiến nghị</span>
            </button>

            <button
              onClick={() => handleOpenComingSoon("Tài liệu hướng dẫn sử dụng, video trực quan cho công dân.")}
              className="flex flex-col items-center justify-center p-3 rounded-xl hover:bg-neutral-bg/50 transition-all group"
            >
              <div className="w-12 h-12 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">📖</div>
              <span className="text-[11px] font-bold text-foreground/80 leading-snug">Hướng dẫn sử dụng</span>
            </button>
          </div>
        </section>

        {/* Featured Services & Updates */}
        <section className="px-6 md:px-12 py-12 shrink-0">
          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

            {/* Left Column: Featured Services (2/3 width) */}
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-center gap-2 border-b border-border-slate pb-3">
                <span className="text-xl">⚙️</span>
                <h3 className="text-lg font-serif font-extrabold text-primary">Dịch vụ công nổi bật</h3>
              </div>

              {/* 6 procedures grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-sans">
                {/* 1. Khai sinh */}
                <div
                  onClick={() => handleSelectProcedure("dang-ky-khai-sinh")}
                  className="flex items-center justify-between p-4 bg-card-bg border border-border-slate rounded-xl hover:border-accent hover:shadow-md cursor-pointer transition-all duration-200 group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-lg">👶</div>
                    <div>
                      <h4 className="text-xs font-bold text-foreground group-hover:text-accent">Đăng ký khai sinh</h4>
                      <p className="text-[10px] text-foreground/50 font-medium mt-0.5">Thực hiện đăng ký khai sinh trực tuyến cho công dân</p>
                    </div>
                  </div>
                  <span className="text-foreground/50 group-hover:text-accent transition-colors">➔</span>
                </div>

                {/* 2. Thường trú */}
                <div
                  onClick={() => handleSelectProcedure("dang-ky-thuong-tru")}
                  className="flex items-center justify-between p-4 bg-card-bg border border-border-slate rounded-xl hover:border-accent hover:shadow-md cursor-pointer transition-all duration-200 group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-lg">🏠</div>
                    <div>
                      <h4 className="text-xs font-bold text-foreground group-hover:text-accent">Đăng ký thường trú</h4>
                      <p className="text-[10px] text-foreground/50 font-medium mt-0.5">Thủ tục đăng ký cư trú, chuyển khẩu trực tuyến</p>
                    </div>
                  </div>
                  <span className="text-foreground/50 group-hover:text-accent transition-colors">➔</span>
                </div>

                {/* 3. Giấy phép lái xe */}
                <div
                  onClick={() => handleOpenComingSoon("Thủ tục cấp đổi Giấy phép lái xe quốc gia đang được cập nhật luồng AI tiền kiểm.")}
                  className="flex items-center justify-between p-4 bg-card-bg border border-border-slate rounded-xl hover:border-accent hover:shadow-md cursor-pointer transition-all duration-200 group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-lg">🪪</div>
                    <div>
                      <h4 className="text-xs font-bold text-foreground group-hover:text-accent">Cấp đổi giấy phép lái xe</h4>
                      <p className="text-[10px] text-foreground/50 font-medium mt-0.5">Cấp đổi GPLX do ngành Giao thông vận tải cấp</p>
                    </div>
                  </div>
                  <span className="text-foreground/50 group-hover:text-accent transition-colors">➔</span>
                </div>

                {/* 4. Đăng ký kinh doanh */}
                <div
                  onClick={() => handleSelectProcedure("dang-ky-ho-kinh-doanh")}
                  className="flex items-center justify-between p-4 bg-card-bg border border-border-slate rounded-xl hover:border-accent hover:shadow-md cursor-pointer transition-all duration-200 group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-lg">💼</div>
                    <div>
                      <h4 className="text-xs font-bold text-foreground group-hover:text-accent">Đăng ký kinh doanh</h4>
                      <p className="text-[10px] text-foreground/50 font-medium mt-0.5">Đăng ký thành lập hộ kinh doanh cá thể trực tuyến</p>
                    </div>
                  </div>
                  <span className="text-foreground/50 group-hover:text-accent transition-colors">➔</span>
                </div>

                {/* 5. Nộp thuế */}
                <div
                  onClick={() => handleOpenComingSoon("Hệ thống nộp thuế điện tử liên kết trực tiếp với Tổng cục Thuế.")}
                  className="flex items-center justify-between p-4 bg-card-bg border border-border-slate rounded-xl hover:border-accent hover:shadow-md cursor-pointer transition-all duration-200 group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-lg">💸</div>
                    <div>
                      <h4 className="text-xs font-bold text-foreground group-hover:text-accent">Nộp thuế điện tử</h4>
                      <p className="text-[10px] text-foreground/50 font-medium mt-0.5">Khấu trừ thuế cá nhân, phí trước bạ trực tuyến</p>
                    </div>
                  </div>
                  <span className="text-foreground/50 group-hover:text-accent transition-colors">➔</span>
                </div>

                {/* 6. BHXH */}
                <div
                  onClick={() => handleOpenComingSoon("Tra cứu thông tin và quá trình đóng Bảo hiểm xã hội trực tuyến.")}
                  className="flex items-center justify-between p-4 bg-card-bg border border-border-slate rounded-xl hover:border-accent hover:shadow-md cursor-pointer transition-all duration-200 group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-neutral-bg text-accent flex items-center justify-center text-lg">🛡️</div>
                    <div>
                      <h4 className="text-xs font-bold text-foreground group-hover:text-accent">Bảo hiểm xã hội</h4>
                      <p className="text-[10px] text-foreground/50 font-medium mt-0.5">Tra cứu, nộp gia hạn thẻ BHYT, BHXH tự nguyện</p>
                    </div>
                  </div>
                  <span className="text-foreground/50 group-hover:text-accent transition-colors">➔</span>
                </div>
              </div>

              {/* View all button */}
              <div className="pt-2 text-center">
                <button
                  onClick={() => setView("copilot")}
                  className="px-6 py-2.5 bg-brand-red text-white text-xs font-bold rounded-lg hover:bg-brand-red-hover transition-all font-sans"
                >
                  Xem tất cả dịch vụ công
                </button>
              </div>
            </div>

            {/* Right Column: Latest Updates (1/3 width) */}
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-border-slate pb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xl">📰</span>
                  <h3 className="text-lg font-serif font-extrabold text-primary">Cập nhật mới nhất</h3>
                </div>
                <button onClick={() => handleOpenComingSoon("Kho văn bản tin tức đang được đồng bộ.")} className="text-xs font-bold text-accent hover:underline">Xem tất cả</button>
              </div>

              {/* News List */}
              <div className="space-y-4 divide-y divide-amber-200/40 font-sans">
                <div className="pt-1.5 cursor-pointer hover:text-accent transition-colors" onClick={() => handleOpenComingSoon("Chi tiết Nghị định số 42/2024/NĐ-CP hướng dẫn thi hành Dịch vụ công trực tuyến.")}>
                  <h4 className="text-xs font-bold text-foreground leading-snug">Nghị định mới về quản lý, cung cấp dịch vụ công trực tuyến</h4>
                  <span className="text-[10px] text-foreground/50 block mt-1 font-medium">15/05/2024</span>
                </div>

                <div className="pt-3.5 cursor-pointer hover:text-accent transition-colors" onClick={() => handleOpenComingSoon("Tài liệu số hướng dẫn công dân nộp hồ sơ, quét căn cước và xác thực.")}>
                  <h4 className="text-xs font-bold text-foreground leading-snug">Hướng dẫn nộp hồ sơ trực tuyến trên Cổng dịch vụ công Quốc gia</h4>
                  <span className="text-[10px] text-foreground/50 block mt-1 font-medium">10/05/2024</span>
                </div>

                <div className="pt-3.5 cursor-pointer hover:text-accent transition-colors" onClick={() => handleOpenComingSoon("Nâng cấp hạ tầng thanh toán, liên kết mã QR động với các ngân hàng lớn.")}>
                  <h4 className="text-xs font-bold text-foreground leading-snug">Cập nhật tính năng thanh toán trực tuyến trên Cổng DVCQG</h4>
                  <span className="text-[10px] text-foreground/50 block mt-1 font-medium">08/05/2024</span>
                </div>

                <div className="pt-3.5 cursor-pointer hover:text-accent transition-colors" onClick={() => handleOpenComingSoon("Đăng nhập an toàn và bảo mật cao thông qua ứng dụng định danh VNeID.")}>
                  <h4 className="text-xs font-bold text-foreground leading-snug">Tích hợp định danh điện tử VNeID với Cổng Dịch vụ công Quốc gia</h4>
                  <span className="text-[10px] text-foreground/50 block mt-1 font-medium">05/05/2024</span>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* Benefits Section */}
        <section className="bg-neutral-bg/50 border-y border-border-slate py-12 px-6 md:px-12 relative overflow-hidden shrink-0">
          <LotusFlowerPattern className="absolute w-[250px] h-[250px] -bottom-12 -left-12 text-border-slate/20 pointer-events-none" />
          <LotusFlowerPattern className="absolute w-[250px] h-[250px] -bottom-12 -right-12 text-border-slate/20 pointer-events-none" />

          <div className="max-w-6xl mx-auto text-center relative z-10">
            <h3 className="text-xl font-serif font-extrabold text-primary">Lợi ích khi sử dụng dịch vụ công trực tuyến</h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-8 font-sans">
              <div className="flex flex-col items-center p-4">
                <div className="w-14 h-14 rounded-full bg-card-bg border border-border-slate text-accent flex items-center justify-center text-2xl shadow-sm mb-4">⏱️</div>
                <h4 className="text-xs font-bold text-foreground/80">Tiết kiệm thời gian giải quyết hồ sơ</h4>
              </div>

              <div className="flex flex-col items-center p-4">
                <div className="w-14 h-14 rounded-full bg-card-bg border border-border-slate text-accent flex items-center justify-center text-2xl shadow-sm mb-4">📍</div>
                <h4 className="text-xs font-bold text-foreground/80">Mọi lúc, mọi nơi trên mọi thiết bị</h4>
              </div>

              <div className="flex flex-col items-center p-4">
                <div className="w-14 h-14 rounded-full bg-card-bg border border-border-slate text-accent flex items-center justify-center text-2xl shadow-sm mb-4">🔒</div>
                <h4 className="text-xs font-bold text-foreground/80">An toàn, bảo mật thông tin tối đa</h4>
              </div>

              <div className="flex flex-col items-center p-4">
                <div className="w-14 h-14 rounded-full bg-card-bg border border-border-slate text-accent flex items-center justify-center text-2xl shadow-sm mb-4">🍃</div>
                <h4 className="text-xs font-bold text-foreground/80">Giảm chi phí đi lại, in ấn giấy tờ</h4>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-brand-red text-white/90 py-12 px-6 md:px-12 shrink-0 border-t border-border-slate/20 relative overflow-hidden font-sans">
          <TrongDongPattern className="absolute w-[300px] h-[300px] -bottom-10 -right-10 text-white/5 pointer-events-none" />
          
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 relative z-10 text-xs">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <svg className="w-10 h-10 shrink-0" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="50" cy="50" r="46" fill="#DA251D" stroke="#D97706" strokeWidth="2"/>
                  <path d="M50 20L58.2 41.5H81L62.6 55.4L69.6 77L50 63.5L30.4 77L37.4 55.4L19 41.5H41.8L50 20Z" fill="#FFFF00"/>
                </svg>
                <div>
                  <h4 className="font-serif font-extrabold text-sm text-white">CỔNG DỊCH VỤ CÔNG QUỐC GIA</h4>
                  <p className="text-[9px] uppercase font-bold text-amber-400 tracking-wider">Kết nối - Cung cấp - Tiền kiểm</p>
                </div>
              </div>
              <div className="space-y-2 text-white/70 font-medium">
                <p>📞 Điện thoại: 024 1234 5678</p>
                <p>✉️ Email: hotro@dichvucong.gov.vn</p>
                <p>🌐 Website: https://dichvucong.gov.vn</p>
              </div>
            </div>

            <div className="space-y-3 font-medium">
              <h4 className="text-xs uppercase font-extrabold text-amber-400">Về chúng tôi</h4>
              <ul className="space-y-2 text-white/70">
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Giới thiệu về Ban Quản trị Cổng Dịch vụ công Quốc gia.")}>Giới thiệu</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Danh mục văn bản pháp luật quy định hành chính.")}>Văn bản pháp luật</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Câu hỏi thường gặp của người dân.")}>Câu hỏi thường gặp</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Bản đồ trang thông tin.")}>Sitemap</button></li>
              </ul>
            </div>

            <div className="space-y-3 font-medium">
              <h4 className="text-xs uppercase font-extrabold text-amber-400">Hỗ trợ</h4>
              <ul className="space-y-2 text-white/70">
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Tài liệu hướng dẫn kê khai trực tuyến.")}>Hướng dẫn sử dụng</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Tổng đài đường dây nóng 1900 1234.")}>Tổng đài hỗ trợ</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Gửi phản hồi, kiến nghị hành chính.")}>Phản ánh, kiến nghị</button></li>
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="text-xs uppercase font-extrabold text-amber-400">Kết nối với chúng tôi</h4>
              <div className="flex items-center gap-3">
                <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-sm">f</button>
                <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-sm">▶</button>
                <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-sm">🌐</button>
              </div>
            </div>
          </div>

          <div className="max-w-6xl mx-auto mt-8 pt-6 border-t border-white/10 text-center text-[10px] text-white/50 relative z-10 flex flex-col sm:flex-row justify-between items-center gap-3">
            <p>© 2024 Cổng Dịch vụ công Quốc gia. All rights reserved.</p>
            <div className="flex gap-4">
              <button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Chính sách bảo mật thông tin quốc gia.")}>Chính sách bảo mật</button>
              <button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Điều khoản sử dụng dịch vụ công trực tuyến.")}>Điều khoản sử dụng</button>
            </div>
          </div>
        </footer>

        {/* Dynamic Coming Soon Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 font-sans animate-fade-in">
            <div className="bg-card-bg border border-border-slate rounded-2xl p-6 max-w-sm w-full shadow-2xl relative overflow-hidden animate-scale-up">
              <div className="absolute top-0 left-0 w-full h-[4px] bg-brand-red" />
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">🏛️</span>
                <h4 className="text-sm font-serif font-extrabold text-primary">Thông báo từ Cổng DVCQG</h4>
              </div>
              <p className="text-xs text-foreground/75 leading-relaxed font-medium">
                {modalText}
              </p>
              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-brand-red text-white text-xs font-bold rounded-lg hover:bg-brand-red-hover transition-all shadow-sm"
                >
                  Đã hiểu
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-neutral-bg text-primary font-sans antialiased pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)] pb-[env(safe-area-inset-bottom)]">
      {/* 1. Navbar */}
      <header className="flex items-center justify-between px-6 pr-[max(1.5rem,env(safe-area-inset-right))] pl-[max(1.5rem,env(safe-area-inset-left))] py-4 bg-card-bg border-b border-border-slate shadow-sm shrink-0 relative overflow-hidden">
        {/* Subtle top decoration bar */}
        <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-amber-500 via-red-500 to-amber-600" />
        <div className="flex items-center gap-4 relative z-10">
          {/* Vietnam styled Emblem SVG */}
          <div className="relative flex items-center justify-center w-11 h-11 rounded-full border border-amber-300/40 bg-amber-50/50 shadow-inner shrink-0">
            <svg className="w-9 h-9" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="50" cy="50" r="46" fill="#DA251D" stroke="#D97706" strokeWidth="2"/>
              <path d="M50 20L58.2 41.5H81L62.6 55.4L69.6 77L50 63.5L30.4 77L37.4 55.4L19 41.5H41.8L50 20Z" fill="#FFFF00"/>
              <circle cx="50" cy="50" r="28" stroke="#FFFF00" strokeWidth="1" strokeDasharray="3 3" opacity="0.6"/>
              <path d="M22 65 C32 80, 68 80, 78 65" stroke="#FFFF00" strokeWidth="1.5" strokeLinecap="round" opacity="0.8"/>
            </svg>
          </div>
          <div>
            <h1 className="text-md md:text-lg font-serif font-bold leading-tight tracking-tight text-primary">
              CỔNG DỊCH VỤ CÔNG QUỐC GIA
            </h1>
            <p className="text-[10px] uppercase font-bold text-accent tracking-widest font-sans">Trợ lý tiền kiểm hồ sơ thông minh</p>
          </div>
        </div>

        <div className="flex items-center gap-4 relative z-10">
          <button
            onClick={() => setView("landing")}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border-slate bg-neutral-bg hover:bg-neutral-bg/85 text-xs font-bold text-primary transition-all duration-200"
          >
            ← Quay lại Trang chủ
          </button>
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
                    className={`px-4 py-3 rounded-xl text-sm leading-relaxed shadow-sm ${
                      msg.role === "user"
                        ? "bg-accent text-white rounded-br-none font-sans font-medium"
                        : "bg-card-bg border border-border-slate/80 text-primary rounded-bl-none font-sans"
                    }`}
                  >
                    <p className="whitespace-pre-line font-medium leading-relaxed">{msg.content}</p>

                    {/* Citations / Sources */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-3 pt-2 border-t border-border-slate/60 text-xs text-zinc-500">
                        <span className="font-bold block mb-1 text-primary">Nguồn pháp lý trích dẫn:</span>
                        <ul className="list-disc pl-4 space-y-1 font-medium">
                          {msg.sources.map((src, i) => (
                            <li key={i}>
                              <a
                                href={src.url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-accent underline hover:text-accent-hover transition-colors"
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
                className="px-4 py-2 bg-accent text-white text-sm font-semibold rounded-md hover:bg-accent-hover transition-all disabled:opacity-50"
              >
                Gửi
              </button>
            </form>
          </div>

          {/* Tab Content 2: Checklist display */}
          <div className={`${activeLeftTab === "checklist" ? "flex" : "hidden"} flex-col flex-1 overflow-y-auto bg-card-bg`}>
            <ChecklistSidebar checklist={checklist} activeField={activeField} />
          </div>
        </aside>

        {/* Right Column (60% width) - Contains Form Input & Validation */}
        <main
          className={`${
            activeMobileTab === "form" ? "flex" : "hidden"
          } md:flex flex-col flex-1 bg-neutral-bg overflow-y-auto p-6`}
        >
          {checklist ? (
            <div className="max-w-xl mx-auto w-full space-y-6">
              {/* Form Sheet container */}
              <div className="bg-card-bg border border-border-slate rounded-lg p-6 shadow-sm">
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
            <div className="flex-1 flex flex-col items-center justify-center p-8 md:p-12 bg-card-bg border border-border-slate rounded-2xl max-w-2xl mx-auto w-full shadow-md my-auto relative overflow-hidden transition-all duration-300 hover:shadow-lg">
              {/* Decorative Background Elements */}
              <TrongDongPattern className="absolute w-[280px] h-[280px] -top-10 -right-10 text-accent/5 dark:text-accent/5 pointer-events-none" />
              <LotusFlowerPattern className="absolute w-[180px] h-[180px] -bottom-10 -left-10 text-accent/5 dark:text-accent/5 pointer-events-none" />

              {/* Emblem / Logo Icon */}
              <div className="relative flex items-center justify-center w-20 h-20 rounded-full bg-amber-50 dark:bg-amber-950/20 text-accent mb-6 shadow-inner border border-amber-200/40">
                <TrongDongPattern className="absolute inset-0 w-full h-full text-accent/10 dark:text-accent/20 animate-[spin_120s_linear_infinite]" />
                <span className="text-4xl relative z-10">🏛️</span>
              </div>

              {/* Title & Subtitle */}
              <h2 className="text-2xl font-serif font-bold text-primary tracking-tight text-center relative z-10">
                Trợ Lý Tiền Kiểm & Hướng Dẫn Kê Khai
              </h2>
              <p className="text-xs text-zinc-500 mt-3 max-w-md text-center leading-relaxed font-sans relative z-10">
                Hệ thống hỗ trợ công dân chuẩn bị hồ sơ hành chính công trực tuyến theo đúng quy định pháp lý, tự động rà soát sai sót bằng bộ luật thực tế trước khi nộp chính thức.
              </p>

              {/* Steps Flow Diagram */}
              <div className="w-full mt-10 grid grid-cols-1 md:grid-cols-3 gap-4 border-t border-border-slate/60 pt-8 text-left relative z-10 font-sans">
                <div className="p-4 bg-neutral-bg/60 border border-border-slate/50 rounded-xl hover:bg-neutral-bg transition-colors duration-200">
                  <div className="text-xs font-bold text-accent mb-2 flex items-center gap-1.5">
                    <span className="flex items-center justify-center w-5 h-5 rounded-full bg-accent text-white text-[10px] font-bold">1</span>
                    Chọn thủ tục
                  </div>
                  <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
                    Chọn nhanh dịch vụ gợi ý trong khung chat hoặc nhắn tin mô tả nhu cầu của bạn cho trợ lý AI.
                  </p>
                </div>

                <div className="p-4 bg-neutral-bg/60 border border-border-slate/50 rounded-xl hover:bg-neutral-bg transition-colors duration-200">
                  <div className="text-xs font-bold text-accent mb-2 flex items-center gap-1.5">
                    <span className="flex items-center justify-center w-5 h-5 rounded-full bg-accent text-white text-[10px] font-bold">2</span>
                    Khai thông tin
                  </div>
                  <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
                    Nhập dữ liệu vào tờ khai điện tử hiển thị tại đây theo các trường thông tin tối thiểu được yêu cầu.
                  </p>
                </div>

                <div className="p-4 bg-neutral-bg/60 border border-border-slate/50 rounded-xl hover:bg-neutral-bg transition-colors duration-200">
                  <div className="text-xs font-bold text-accent mb-2 flex items-center gap-1.5">
                    <span className="flex items-center justify-center w-5 h-5 rounded-full bg-accent text-white text-[10px] font-bold">3</span>
                    Tiền kiểm lỗi
                  </div>
                  <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
                    Nhấn rà soát để kiểm tra tính hợp lệ pháp lý, nhận cảnh báo sai sót trực tiếp từ Rule Engine.
                  </p>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
