"use client";

import React, { useState, useEffect, useRef } from "react";
import ChecklistSidebar from "./components/ChecklistSidebar";

import trongDongImg from "@/image/trongdong.jpg";
import hoaSenImg from "@/image/hoasen.png";
import quocHuyImg from "@/image/quochuy.png";
import dvcImg from "@/image/dvc.png";
import trongDong3Img from "@/image/trongdong3.png";

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
    <defs>
      <radialGradient id="goldGrad" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#FFFBEB" stopOpacity="0.8" />
        <stop offset="35%" stopColor="#F59E0B" stopOpacity="0.65" />
        <stop offset="70%" stopColor="#D97706" stopOpacity="0.5" />
        <stop offset="100%" stopColor="#78350F" stopOpacity="0.2" />
      </radialGradient>
    </defs>

    {/* Base bronze drum circle */}
    <circle cx="200" cy="200" r="185" fill="url(#goldGrad)" stroke="#B45309" strokeWidth="2" opacity="0.85" />

    {/* Inner decorative circles */}
    <circle cx="200" cy="200" r="170" stroke="#FFF" strokeWidth="1" opacity="0.3" />
    <circle cx="200" cy="200" r="150" stroke="#B45309" strokeWidth="1" strokeDasharray="3 3" opacity="0.7" />
    <circle cx="200" cy="200" r="135" stroke="#B45309" strokeWidth="1.5" opacity="0.8" />
    <circle cx="200" cy="200" r="110" stroke="#FFF" strokeWidth="1" opacity="0.25" />
    <circle cx="200" cy="200" r="95" stroke="#B45309" strokeWidth="1" strokeDasharray="4 2" opacity="0.75" />
    <circle cx="200" cy="200" r="70" stroke="#B45309" strokeWidth="1.5" opacity="0.8" />

    {/* Central sun with 12 rays */}
    <circle cx="200" cy="200" r="20" fill="#FCD34D" stroke="#B45309" strokeWidth="1" opacity="0.9" />
    <g transform="translate(200, 200)">
      {Array.from({ length: 12 }).map((_, i) => (
        <path
          key={i}
          d="M 0 0 L -4 -22 L 0 -35 L 4 -22 Z"
          fill="#FFF"
          stroke="#B45309"
          strokeWidth="0.5"
          transform={`rotate(${i * 30})`}
          opacity="0.9"
        />
      ))}
    </g>

    {/* Concentric motifs: Ring of flying birds (Chim Lạc) */}
    <g transform="translate(200, 200)">
      {Array.from({ length: 6 }).map((_, i) => (
        <g key={i} transform={`rotate(${i * 60})`}>
          <path
            d="M 0 -82 C -8 -85 -16 -78 -24 -72 C -20 -68 -12 -73 -4 -73 L -2 -68 L -8 -60 L 2 -63 L 8 -74 Z"
            fill="#FFF"
            stroke="#B45309"
            strokeWidth="0.5"
            opacity="0.85"
          />
        </g>
      ))}
    </g>

    {/* Concentric motifs: Ring of running deers */}
    <g transform="translate(200, 200)">
      {Array.from({ length: 8 }).map((_, i) => (
        <g key={i} transform={`rotate(${i * 45})`}>
          <path
            d="M 0 -120 Q -4 -123 -8 -118 L -6 -113 L -10 -108 L -5 -110 L 0 -116 Z"
            fill="#FFF"
            stroke="#B45309"
            strokeWidth="0.5"
            opacity="0.8"
          />
        </g>
      ))}
    </g>

    {/* Outer geometric sawtooth patterns */}
    <g transform="translate(200, 200)">
      {Array.from({ length: 48 }).map((_, i) => (
        <path
          key={i}
          d="M 0 -160 L -2.5 -165 L 2.5 -165 Z"
          fill="#FCD34D"
          stroke="#B45309"
          strokeWidth="0.5"
          transform={`rotate(${i * 7.5})`}
          opacity="0.75"
        />
      ))}
    </g>
  </svg>
);

const LotusFlowerPattern = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="lotusPink" x1="0%" y1="100%" x2="0%" y2="0%">
        <stop offset="0%" stopColor="#BE185D" />
        <stop offset="50%" stopColor="#EC4899" />
        <stop offset="100%" stopColor="#FBCFE8" />
      </linearGradient>
      <linearGradient id="leafGreen" x1="0%" y1="100%" x2="0%" y2="0%">
        <stop offset="0%" stopColor="#065F46" />
        <stop offset="100%" stopColor="#10B981" />
      </linearGradient>
    </defs>

    {/* Green lotus leaves in the background */}
    <path d="M40 150 C 20 120, 80 100, 100 130 C 120 100, 180 120, 160 150 C 140 180, 60 180, 40 150 Z" fill="url(#leafGreen)" opacity="0.85" stroke="#047857" strokeWidth="0.75" />
    <path d="M10 130 C -10 100, 50 80, 70 110 C 90 80, 150 100, 130 130 Z" fill="url(#leafGreen)" opacity="0.6" transform="scale(0.8) translate(30, 40)" />

    {/* Beautiful layered pink lotus petals */}
    <g fill="url(#lotusPink)" stroke="#9D174D" strokeWidth="0.5">
      <path d="M100 60 C80 90, 60 120, 100 150 C140 120, 120 90, 100 60 Z" />
      <path d="M100 70 C70 95, 50 120, 90 145 C130 120, 110 95, 100 70 Z" transform="rotate(-25, 100, 145)" />
      <path d="M100 70 C70 95, 50 120, 90 145 C130 120, 110 95, 100 70 Z" transform="rotate(25, 100, 145)" />
      <path d="M100 80 C60 105, 40 130, 85 145 C130 130, 110 105, 100 80 Z" transform="rotate(-50, 100, 145)" />
      <path d="M100 80 C60 105, 40 130, 85 145 C130 130, 110 105, 100 80 Z" transform="rotate(50, 100, 145)" />
    </g>

    {/* Front petals */}
    <g fill="#FBCFE8" stroke="#BE185D" strokeWidth="0.5" opacity="0.95">
      <path d="M100 90 C85 110, 75 130, 100 148 C125 130, 115 110, 100 90 Z" />
      <path d="M100 95 C88 112, 80 130, 95 146 C110 130, 102 112, 100 95 Z" transform="rotate(-15, 100, 146)" />
      <path d="M100 95 C88 112, 80 130, 95 146 C110 130, 102 112, 100 95 Z" transform="rotate(15, 100, 146)" />
    </g>

    {/* Yellow lotus bud / center */}
    <circle cx="100" cy="138" r="7" fill="#FBBF24" stroke="#D97706" strokeWidth="0.75" />
    <circle cx="98" cy="136" r="0.75" fill="#78350F" />
    <circle cx="102" cy="136" r="0.75" fill="#78350F" />
    <circle cx="100" cy="140" r="0.75" fill="#78350F" />
  </svg>
);

const QuocHuyEmblem = ({ className = "w-10 h-10" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="46" fill="#DA251D" stroke="#D97706" strokeWidth="2.5"/>
    <circle cx="50" cy="50" r="40" stroke="#FFFF00" strokeWidth="1" strokeDasharray="4 2" opacity="0.6"/>
    <path d="M22 65 C20 40, 42 22, 50 22 C58 22, 80 40, 78 65" stroke="#D97706" strokeWidth="3" fill="none" strokeLinecap="round" />
    <path d="M26 65 C24 45, 42 26, 50 26 C58 26, 76 45, 74 65" stroke="#FFFF00" strokeWidth="1.5" fill="none" strokeLinecap="round" opacity="0.9" />
    <path d="M35 75 L50 68 L65 75 L60 84 L50 81 L40 84 Z" fill="#DA251D" stroke="#FFFF00" strokeWidth="1.5"/>
    <circle cx="50" cy="66" r="8" fill="#D97706" />
    <circle cx="50" cy="66" r="5" fill="#DA251D" />
    <path d="M50 28 L55 43 H70 L58 52 L62 67 L50 58 L38 67 L42 52 L30 43 H45 Z" fill="#FFFF00"/>
  </svg>
);

const VNGovLogo = ({ className = "w-8 h-8" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M50 85 C25 80, 20 55, 18 45 C35 48, 45 65, 50 78 C55 65, 65 48, 82 45 C80 55, 75 80, 50 85 Z" fill="#0D1B3D" />
    <path d="M48 70 C40 50, 22 35, 15 32 C28 25, 45 35, 48 55 Z" fill="#F97316" />
    <path d="M52 70 C60 50, 78 35, 85 32 C72 25, 55 35, 52 55 Z" fill="#F97316" />
    <path d="M50 15 L52 23 L60 25 L52 27 L50 35 L48 27 L40 25 L48 23 Z" fill="#FDBA40" />
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
      <div className="min-h-screen bg-[#FAF6F0] text-[#333333] font-sans antialiased flex flex-col relative overflow-x-hidden">
        {/* Header / Navbar */}
        <header className="flex items-center justify-between px-6 md:px-12 py-4 bg-white border-b border-[#EADBC8] shadow-sm shrink-0 relative z-30 font-sans">
          <div className="flex items-center gap-3 font-sans">
            <img src={quocHuyImg.src} className="w-12 h-12 shrink-0 object-contain animate-fade-in" alt="Quốc huy Việt Nam" />
            <img src={dvcImg.src} className="h-10 w-auto shrink-0 object-contain hidden sm:block" alt="Logo Cổng Dịch vụ công Quốc gia" />
            <div className="text-left sm:hidden">
              <h1 className="text-xs font-serif font-extrabold leading-tight tracking-tight text-[#7C1E14]">
                CỔNG DỊCH VỤ CÔNG QUỐC GIA
              </h1>
              <p className="text-[7px] uppercase font-bold text-amber-700 mt-0.5">Dịch vụ công mọi lúc, mọi nơi</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center gap-6 text-xs font-bold text-zinc-700 font-sans">
            <button className="text-[#7C1E14] border-b-2 border-[#7C1E14] pb-1">Trang chủ</button>
            <button className="hover:text-[#7C1E14] pb-1 transition-colors" onClick={() => handleOpenComingSoon("Giới thiệu Cổng Dịch vụ công Quốc gia.")}>Giới thiệu</button>
            <button className="hover:text-[#7C1E14] pb-1 transition-colors" onClick={() => setView("copilot")}>Dịch vụ công</button>
            <button className="hover:text-[#7C1E14] pb-1 transition-colors" onClick={() => handleOpenComingSoon("Chức năng tra cứu tiến độ hồ sơ hành chính.")}>Tra cứu hồ sơ</button>
            <button className="hover:text-[#7C1E14] pb-1 transition-colors" onClick={() => handleOpenComingSoon("Thanh toán nghĩa vụ tài chính trực tuyến.")}>Thanh toán</button>
            <button className="hover:text-[#7C1E14] pb-1 transition-colors" onClick={() => handleOpenComingSoon("Tổng đài hỗ trợ và đường dây nóng phản ánh kiến nghị.")}>Hỗ trợ</button>
          </nav>

          {/* Header Search and Auth Button */}
          <div className="flex items-center gap-3 font-sans">
            <form onSubmit={handleSearchSubmit} className="hidden md:flex items-center bg-zinc-50 border border-zinc-200 rounded-lg px-2 py-1 focus-within:border-amber-700 transition-all max-w-[180px]">
              <input
                id="header-portal-search"
                aria-label="Tìm nhanh dịch vụ công"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm kiếm..."
                className="w-full bg-transparent text-xs text-zinc-800 placeholder-zinc-400 focus:outline-none font-medium"
              />
              <button type="submit" className="text-zinc-400 hover:text-[#7C1E14] transition-colors ml-1 text-xs">
                🔍
              </button>
            </form>
            <button
              onClick={() => handleOpenComingSoon("Đăng nhập thông qua tài khoản định danh điện tử VNeID.")}
              className="px-4 py-2 bg-[#7C1E14] text-white text-xs font-bold rounded-lg hover:bg-red-950 transition-all shadow-sm"
            >
              Đăng nhập
            </button>
          </div>
        </header>

        {/* Hero Section */}
        <section className="relative bg-[#201B13] pt-16 pb-24 md:pt-20 md:pb-28 px-6 md:px-12 overflow-hidden shrink-0 font-sans min-h-[560px]">
          {/* Background Gold Dong Son Drum (Mockup style) */}
          <div className="absolute right-0 top-0 h-full w-[45%] md:w-[60%] z-0 pointer-events-none overflow-hidden select-none">
            <img src={trongDong3Img.src} className="w-full h-full object-cover object-center opacity-70 md:opacity-85" alt="Trống đồng" />
            <div className="absolute inset-y-0 left-0 w-32 md:w-64 bg-gradient-to-r from-[#201B13] via-[#201B13]/70 to-transparent z-10" />
          </div>

          <div className="max-w-6xl mx-auto relative z-10">
            {/* Left Content */}
            <div className="max-w-2xl text-left space-y-6 animate-fade-in-up">
              <h2 className="text-3xl md:text-5xl font-serif font-extrabold text-white leading-tight drop-shadow-md">
                Kết nối, cung cấp thông tin<br />và dịch vụ công mọi lúc, mọi nơi
              </h2>
              <p className="text-xs md:text-sm text-zinc-300 max-w-xl leading-relaxed font-medium">
                Cổng Dịch vụ công Quốc gia là cầu nối giữa cơ quan nhà nước và người dân, doanh nghiệp trên môi trường số.
              </p>
            </div>

            {/* Horizontal 6 Grid Quick Services Block at bottom of hero */}
            <div className="mt-16 w-full animate-scale-in">
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                <button
                  onClick={() => setView("copilot")}
                  className="bg-white/95 backdrop-blur-sm border border-zinc-200/50 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-lg hover-lift hover:border-[#7C1E14] transition-all group"
                >
                  <div className="w-12 h-12 rounded-full bg-rose-50 text-[#7C1E14] flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">📋</div>
                  <span className="text-[11px] font-bold text-zinc-800 leading-snug">Đăng ký, quản lý hồ sơ trực tuyến</span>
                </button>

                <button
                  onClick={() => handleOpenComingSoon("Thanh toán trực tuyến nghĩa vụ tài chính đất đai, án phí, đóng BHXH.")}
                  className="bg-white/95 backdrop-blur-sm border border-zinc-200/50 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-lg hover-lift hover:border-[#7C1E14] transition-all group"
                >
                  <div className="w-12 h-12 rounded-full bg-rose-50 text-[#7C1E14] flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">💳</div>
                  <span className="text-[11px] font-bold text-zinc-800 leading-snug">Thanh toán trực tuyến phí, lệ phí</span>
                </button>

                <button
                  onClick={() => handleOpenComingSoon("Nhập mã hồ sơ của bạn vào hệ thống để tra cứu tiến độ xử lý trực tiếp.")}
                  className="bg-white/95 backdrop-blur-sm border border-zinc-200/50 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-lg hover-lift hover:border-[#7C1E14] transition-all group"
                >
                  <div className="w-12 h-12 rounded-full bg-rose-50 text-[#7C1E14] flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">🔍</div>
                  <span className="text-[11px] font-bold text-zinc-800 leading-snug">Tra cứu hồ sơ đã nộp</span>
                </button>

                <button
                  onClick={() => handleOpenComingSoon("Khảo sát mức độ hài lòng của người dân về sự phục vụ của cơ quan hành chính.")}
                  className="bg-white/95 backdrop-blur-sm border border-zinc-200/50 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-lg hover-lift hover:border-[#7C1E14] transition-all group"
                >
                  <div className="w-12 h-12 rounded-full bg-rose-50 text-[#7C1E14] flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">⭐</div>
                  <span className="text-[11px] font-bold text-zinc-800 leading-snug">Đánh giá chất lượng dịch vụ công</span>
                </button>

                <button
                  onClick={() => handleOpenComingSoon("Gửi phản ánh, kiến nghị về vướng mắc hành chính công.")}
                  className="bg-white/95 backdrop-blur-sm border border-zinc-200/50 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-lg hover-lift hover:border-[#7C1E14] transition-all group"
                >
                  <div className="w-12 h-12 rounded-full bg-rose-50 text-[#7C1E14] flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">💬</div>
                  <span className="text-[11px] font-bold text-zinc-800 leading-snug">Phản ánh, kiến nghị</span>
                </button>

                <button
                  onClick={() => handleOpenComingSoon("Tài liệu số hướng dẫn kê khai, nộp phí, lệ phí trực tuyến.")}
                  className="bg-white/95 backdrop-blur-sm border border-zinc-200/50 rounded-xl p-4 flex flex-col items-center justify-center text-center shadow-lg hover-lift hover:border-[#7C1E14] transition-all group"
                >
                  <div className="w-12 h-12 rounded-full bg-rose-50 text-[#7C1E14] flex items-center justify-center text-xl mb-3 shadow-inner group-hover:scale-110 transition-transform">📖</div>
                  <span className="text-[11px] font-bold text-zinc-800 leading-snug">Hướng dẫn sử dụng</span>
                </button>
              </div>

              {/* Centered Pill Button: Xem tất cả dịch vụ công */}
              <div className="mt-8 text-center">
                <button
                  onClick={() => setView("copilot")}
                  className="px-8 py-3 bg-[#7C1E14] text-white text-xs font-bold rounded-full hover:bg-red-950 transition-all shadow-md inline-block font-sans font-extrabold uppercase tracking-wide border border-[#7C1E14] hover:scale-105 transform duration-200"
                >
                  Xem tất cả dịch vụ công
                </button>
              </div>
            </div>
          </div>

          {/* Floating Lotuses at the bottom corner edges (Mockup style) */}
          <img src={hoaSenImg.src} className="absolute bottom-0 left-0 w-[240px] md:w-[350px] h-auto object-contain pointer-events-none z-20 animate-float-lotus" alt="Hoa sen" />
          <img src={hoaSenImg.src} className="absolute bottom-0 right-0 w-[240px] md:w-[350px] h-auto object-contain pointer-events-none z-20 animate-float-lotus [animation-delay:3s]" alt="Hoa sen" />
        </section>

        {/* Featured Services & Updates (2 columns layout) */}
        <section className="px-6 md:px-12 py-16 shrink-0 bg-[#FAF6F0] font-sans">
          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

            {/* Left Column: Featured Services (2/3 width) */}
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-center gap-2 border-b border-[#EADBC8] pb-3 text-left">
                <span className="text-xl text-[#7C1E14]">⚙️</span>
                <h3 className="text-lg font-serif font-extrabold text-[#7C1E14]">Dịch vụ công nổi bật</h3>
              </div>

              {/* Grid of 6 procedures */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-sans text-left">
                {/* 1. Khai sinh */}
                <div
                  onClick={() => handleSelectProcedure("dang-ky-khai-sinh")}
                  className="flex items-center justify-between p-4 bg-white border border-[#EADBC8] rounded-xl hover:border-[#7C1E14] hover:shadow-md cursor-pointer transition-all duration-200 group hover-lift"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center text-lg">👶</div>
                    <div>
                      <h4 className="text-xs font-bold text-[#7C1E14] group-hover:text-red-900">Đăng ký khai sinh</h4>
                      <p className="text-[10px] text-zinc-400 font-medium mt-0.5">Thủ tục đăng ký khai sinh trực tuyến cho công dân</p>
                    </div>
                  </div>
                  <span className="text-zinc-400 group-hover:text-[#7C1E14] transition-colors">➔</span>
                </div>

                {/* 2. Thường trú */}
                <div
                  onClick={() => handleSelectProcedure("dang-ky-thuong-tru")}
                  className="flex items-center justify-between p-4 bg-white border border-[#EADBC8] rounded-xl hover:border-[#7C1E14] hover:shadow-md cursor-pointer transition-all duration-200 group hover-lift"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center text-lg">🏠</div>
                    <div>
                      <h4 className="text-xs font-bold text-[#7C1E14] group-hover:text-red-900">Đăng ký thường trú</h4>
                      <p className="text-[10px] text-zinc-400 font-medium mt-0.5">Thủ tục đăng ký thường trú trực tuyến</p>
                    </div>
                  </div>
                  <span className="text-zinc-400 group-hover:text-[#7C1E14] transition-colors">➔</span>
                </div>

                {/* 3. Giấy phép lái xe */}
                <div
                  onClick={() => handleOpenComingSoon("Thủ tục đổi Giấy phép lái xe quốc gia đang được nâng cấp.")}
                  className="flex items-center justify-between p-4 bg-white border border-[#EADBC8] rounded-xl hover:border-[#7C1E14] hover:shadow-md cursor-pointer transition-all duration-200 group hover-lift"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center text-lg">🪪</div>
                    <div>
                      <h4 className="text-xs font-bold text-[#7C1E14] group-hover:text-red-900">Cấp đổi giấy phép lái xe</h4>
                      <p className="text-[10px] text-zinc-400 font-medium mt-0.5">Thủ tục cấp đổi giấy phép lái xe trực tuyến</p>
                    </div>
                  </div>
                  <span className="text-zinc-400 group-hover:text-[#7C1E14] transition-colors">➔</span>
                </div>

                {/* 4. Đăng ký kinh doanh */}
                <div
                  onClick={() => handleSelectProcedure("dang-ky-ho-kinh-doanh")}
                  className="flex items-center justify-between p-4 bg-white border border-[#EADBC8] rounded-xl hover:border-[#7C1E14] hover:shadow-md cursor-pointer transition-all duration-200 group hover-lift"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center text-lg">💼</div>
                    <div>
                      <h4 className="text-xs font-bold text-[#7C1E14] group-hover:text-red-900">Đăng ký kinh doanh</h4>
                      <p className="text-[10px] text-zinc-400 font-medium mt-0.5">Thủ tục đăng ký thành lập doanh nghiệp</p>
                    </div>
                  </div>
                  <span className="text-zinc-400 group-hover:text-[#7C1E14] transition-colors">➔</span>
                </div>

                {/* 5. Nộp thuế */}
                <div
                  onClick={() => handleOpenComingSoon("Hệ thống nộp thuế trực tuyến liên kết Tổng cục Thuế.")}
                  className="flex items-center justify-between p-4 bg-white border border-[#EADBC8] rounded-xl hover:border-[#7C1E14] hover:shadow-md cursor-pointer transition-all duration-200 group hover-lift"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center text-lg">💸</div>
                    <div>
                      <h4 className="text-xs font-bold text-[#7C1E14] group-hover:text-red-900">Nộp thuế điện tử</h4>
                      <p className="text-[10px] text-zinc-400 font-medium mt-0.5">Nộp thuế trực tuyến mọi lúc, mọi nơi</p>
                    </div>
                  </div>
                  <span className="text-zinc-400 group-hover:text-[#7C1E14] transition-colors">➔</span>
                </div>

                {/* 6. BHXH */}
                <div
                  onClick={() => handleOpenComingSoon("Tra cứu thông tin, nộp hồ sơ Bảo hiểm xã hội tự nguyện.")}
                  className="flex items-center justify-between p-4 bg-white border border-[#EADBC8] rounded-xl hover:border-[#7C1E14] hover:shadow-md cursor-pointer transition-all duration-200 group hover-lift"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center text-lg">🛡️</div>
                    <div>
                      <h4 className="text-xs font-bold text-[#7C1E14] group-hover:text-red-900">Bảo hiểm xã hội</h4>
                      <p className="text-[10px] text-zinc-400 font-medium mt-0.5">Tra cứu và nộp hồ sơ bảo hiểm xã hội</p>
                    </div>
                  </div>
                  <span className="text-zinc-400 group-hover:text-[#7C1E14] transition-colors">➔</span>
                </div>
              </div>

              {/* View all button */}
              <div className="pt-4 text-center">
                <button
                  onClick={() => setView("copilot")}
                  className="px-6 py-2.5 bg-[#7C1E14] text-white text-xs font-bold rounded-full hover:bg-red-950 transition-all font-sans font-extrabold"
                >
                  Xem tất cả dịch vụ công
                </button>
              </div>
            </div>

            {/* Right Column: Latest Updates (1/3 width) */}
            <div className="space-y-6 text-left font-sans">
              <div className="flex items-center justify-between border-b border-[#EADBC8] pb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xl text-[#7C1E14]">📰</span>
                  <h3 className="text-lg font-serif font-extrabold text-[#7C1E14]">Cập nhật mới nhất</h3>
                </div>
                <button onClick={() => handleOpenComingSoon("Hồ sơ tài liệu tin tức của Cổng Dịch vụ công Quốc gia.")} className="text-xs font-bold text-amber-800 hover:underline">Xem tất cả</button>
              </div>

              {/* News List */}
              <div className="space-y-4 divide-y divide-amber-200/40 font-sans">
                <div className="pt-1.5 cursor-pointer hover:text-amber-800 transition-colors" onClick={() => handleOpenComingSoon("Chi tiết Nghị định quản lý dịch vụ trực tuyến mới ban hành.")}>
                  <h4 className="text-xs font-bold text-zinc-800 leading-snug">Nghị định mới về quản lý, cung cấp dịch vụ công trực tuyến</h4>
                  <span className="text-[10px] text-zinc-400 block mt-1 font-medium">15/05/2024</span>
                </div>

                <div className="pt-3.5 cursor-pointer hover:text-amber-800 transition-colors" onClick={() => handleOpenComingSoon("Tài liệu số hướng dẫn kê khai nộp hồ sơ.")}>
                  <h4 className="text-xs font-bold text-zinc-800 leading-snug">Hướng dẫn nộp hồ sơ trực tuyến trên Cổng Dịch vụ công Quốc gia</h4>
                  <span className="text-[10px] text-zinc-400 block mt-1 font-medium">10/05/2024</span>
                </div>

                <div className="pt-3.5 cursor-pointer hover:text-amber-800 transition-colors" onClick={() => handleOpenComingSoon("Cập nhật tính năng thanh toán trực tuyến trên Cổng DVCQG.")}>
                  <h4 className="text-xs font-bold text-zinc-800 leading-snug">Cập nhật tính năng thanh toán trực tuyến trên Cổng DVCQG</h4>
                  <span className="text-[10px] text-zinc-400 block mt-1 font-medium">08/05/2024</span>
                </div>

                <div className="pt-3.5 cursor-pointer hover:text-amber-800 transition-colors" onClick={() => handleOpenComingSoon("Tích hợp an toàn danh tính định danh điện tử VNeID.")}>
                  <h4 className="text-xs font-bold text-zinc-800 leading-snug">Tích hợp định danh điện tử với Cổng Dịch vụ công Quốc gia</h4>
                  <span className="text-[10px] text-zinc-400 block mt-1 font-medium">05/05/2024</span>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* Benefits Section */}
        <section className="bg-amber-50/40 border-y border-[#EADBC8] py-16 px-6 md:px-12 relative overflow-hidden shrink-0 font-sans">
          <LotusFlowerPattern className="absolute w-[220px] h-[220px] -bottom-12 -left-12 text-[#DA70D6]/10 pointer-events-none" />
          <LotusFlowerPattern className="absolute w-[220px] h-[220px] -bottom-12 -right-12 text-[#DA70D6]/10 pointer-events-none" />

          <div className="max-w-6xl mx-auto text-center relative z-10 space-y-10">
            <h3 className="text-xl font-serif font-extrabold text-[#7C1E14]">Lợi ích khi sử dụng dịch vụ công trực tuyến</h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-8 font-sans">
              <div className="flex flex-col items-center p-4">
                <div className="w-14 h-14 rounded-full bg-white border border-amber-200 text-[#7C1E14] flex items-center justify-center text-2xl shadow-sm mb-4">⏱️</div>
                <h4 className="text-xs font-bold text-zinc-700">Tiết kiệm thời gian giải quyết hồ sơ</h4>
              </div>

              <div className="flex flex-col items-center p-4">
                <div className="w-14 h-14 rounded-full bg-white border border-amber-200 text-[#7C1E14] flex items-center justify-center text-2xl shadow-sm mb-4">📍</div>
                <h4 className="text-xs font-bold text-zinc-700">Mọi lúc, mọi nơi trên mọi thiết bị</h4>
              </div>

              <div className="flex flex-col items-center p-4">
                <div className="w-14 h-14 rounded-full bg-white border border-amber-200 text-[#7C1E14] flex items-center justify-center text-2xl shadow-sm mb-4">🔒</div>
                <h4 className="text-xs font-bold text-zinc-700">An toàn, bảo mật thông tin</h4>
              </div>

              <div className="flex flex-col items-center p-4">
                <div className="w-14 h-14 rounded-full bg-white border border-amber-200 text-[#7C1E14] flex items-center justify-center text-2xl shadow-sm mb-4">🍃</div>
                <h4 className="text-xs font-bold text-zinc-700">Giảm chi phí đi lại, giấy tờ</h4>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-[#7C1E14] text-white/95 py-12 px-6 md:px-12 shrink-0 border-t border-amber-600/20 relative overflow-hidden font-sans">
          <TrongDongPattern className="absolute w-[300px] h-[300px] -bottom-10 -right-10 text-white/5 pointer-events-none" />

          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 relative z-10 text-xs text-left">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <QuocHuyEmblem className="w-12 h-12 shrink-0" />
                <div>
                  <h4 className="font-serif font-extrabold text-sm text-white">CỔNG DỊCH VỤ CÔNG QUỐC GIA</h4>
                  <p className="text-[9px] uppercase font-bold text-amber-400 tracking-wider">Kết nối - Cung cấp - Tiền kiểm</p>
                </div>
              </div>
              <div className="space-y-2 text-white/80 font-medium">
                <p>📞 Điện thoại: 024 1234 5678</p>
                <p>✉️ Email: hotro@dichvucong.gov.vn</p>
                <p>🌐 Website: https://dichvucong.gov.vn</p>
              </div>
            </div>

            <div className="space-y-3 font-medium">
              <h4 className="text-xs uppercase font-extrabold text-amber-400 font-sans">Về chúng tôi</h4>
              <ul className="space-y-2 text-white/80">
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Giới thiệu về Ban Quản trị Cổng Dịch vụ công Quốc gia.")}>Giới thiệu</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Danh mục văn bản pháp luật quy định hành chính.")}>Văn bản pháp luật</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Câu hỏi thường gặp của người dân.")}>Câu hỏi thường gặp</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Bản đồ trang thông tin.")}>Sitemap</button></li>
              </ul>
            </div>

            <div className="space-y-3 font-medium">
              <h4 className="text-xs uppercase font-extrabold text-amber-400 font-sans">Hỗ trợ</h4>
              <ul className="space-y-2 text-white/70">
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Tài liệu hướng dẫn kê khai trực tuyến.")}>Hướng dẫn sử dụng</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Tổng đài đường dây nóng hỗ trợ công dân.")}>Tổng đài hỗ trợ</button></li>
                <li><button className="hover:text-white transition-colors" onClick={() => handleOpenComingSoon("Gửi phản hồi, kiến nghị hành chính.")}>Phản ánh, kiến nghị</button></li>
              </ul>
            </div>

            <div className="space-y-3 font-sans">
              <h4 className="text-xs uppercase font-extrabold text-amber-400">Kết nối với chúng tôi</h4>
              <div className="flex items-center gap-3">
                <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-sm font-sans">f</button>
                <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-sm font-sans">▶</button>
                <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-sm font-sans">🌐</button>
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
            <div className="bg-white border border-[#EADBC8] rounded-2xl p-6 max-w-sm w-full shadow-2xl relative overflow-hidden animate-scale-up">
              <div className="absolute top-0 left-0 w-full h-[4px] bg-[#7C1E14]" />
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">🏛️</span>
                <h4 className="text-sm font-serif font-extrabold text-[#2E1A16]">Thông báo từ Cổng DVCQG</h4>
              </div>
              <p className="text-xs text-zinc-600 leading-relaxed font-medium">
                {modalText}
              </p>
              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-[#7C1E14] text-white text-xs font-bold rounded-lg hover:bg-red-950 transition-all shadow-sm"
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
    <div className="flex flex-col h-screen bg-background text-foreground font-sans antialiased pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)] pb-[env(safe-area-inset-bottom)]">
      {/* 1. Navbar */}
      <header className="flex items-center justify-between px-6 pr-[max(1.5rem,env(safe-area-inset-right))] pl-[max(1.5rem,env(safe-area-inset-left))] py-4 bg-card-bg border-b border-border-slate shadow-sm shrink-0 relative z-20">
        <div className="flex items-center gap-3">
          <VNGovLogo className="w-7 h-7" />
          <div className="flex items-center gap-2">
            <span className="text-md font-bold font-sans tracking-tight text-[#0D1B3D] dark:text-white">
              VN<span className="text-[#F97316]">Gov</span> Copilot
            </span>
            <span className="text-zinc-300 dark:text-zinc-700 font-light">|</span>
            <span className="text-[10px] font-bold text-foreground/60 font-sans tracking-wide">Trợ lý AI cho dịch vụ công</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setView("landing")}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-border-slate bg-neutral-bg hover:bg-neutral-bg/85 text-xs font-bold text-primary transition-all duration-200"
          >
            ← Quay lại Trang chủ
          </button>

          <button
            onClick={() => handleOpenComingSoon("Liên kết với Cổng DVC Quốc gia.")}
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border-slate bg-card-bg hover:bg-neutral-bg text-xs font-bold text-foreground/80 transition-all"
          >
            <span className="w-2 h-2 rounded-full bg-brand-red" />
            Dịch vụ công quốc gia
          </button>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200/40 text-emerald-600 dark:text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-bold">Hệ thống kết nối</span>
          </div>

          {/* User profile */}
          <div className="w-8 h-8 rounded-full bg-neutral-bg border border-border-slate flex items-center justify-center font-bold text-xs text-primary shadow-sm cursor-pointer" onClick={() => handleOpenComingSoon("Tài khoản người dùng đang đăng nhập.")}>
            NT
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
                  <span className="text-[10px] font-bold text-foreground/50 mb-1 flex items-center gap-1">
                    {msg.role === "user" ? "CÔNG DÂN" : "🤖 TRỢ LÝ VNGOV"}
                  </span>

                  {/* Bubble */}
                  <div
                    className={`px-4 py-3 rounded-xl text-sm leading-relaxed shadow-sm relative ${
                      msg.role === "user"
                        ? "bg-accent text-white rounded-br-none font-sans font-medium"
                        : "bg-card-bg border border-border-slate text-primary rounded-bl-none font-sans"
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
                <div className="pt-2 text-left">
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

        {/* Right Column (60% width) - Stepper Progress and Form/AI Result split layout */}
        <main
          className={`${
            activeMobileTab === "form" ? "flex" : "hidden"
          } md:flex flex-col flex-1 bg-neutral-bg overflow-y-auto p-6`}
        >
          {checklist ? (
            <div className="max-w-4xl mx-auto w-full">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

                {/* Stepper Progress Left Panel (5/12 width) */}
                <div className="lg:col-span-5 space-y-6 text-left">
                  {/* Step progress card */}
                  <div className="flex items-center gap-4 p-4 bg-card-bg border border-border-slate rounded-xl shadow-sm">
                    <div className="relative w-12 h-12 flex items-center justify-center rounded-full border-2 border-accent text-accent font-bold text-xs bg-accent/5">
                      {currentProcedureId ? "2/5" : "0/5"}
                    </div>
                    <div>
                      <h4 className="text-xs font-extrabold text-primary">
                        {currentProcedureId ? "Hồ sơ của bạn đang hình thành" : "Hồ sơ chưa bắt đầu"}
                      </h4>
                      <p className="text-[10px] text-foreground/60 font-semibold mt-0.5">
                        {currentProcedureId ? "2 / 5 bước hoàn thành" : "0 / 5 bước hoàn thành"}
                      </p>
                    </div>
                  </div>

                  {/* Vertical Timeline stepper */}
                  <div className="bg-card-bg border border-border-slate rounded-xl p-5 shadow-sm space-y-5">
                    <div className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-emerald-500 text-white flex items-center justify-center text-[10px] font-bold">✓</div>
                      <div>
                        <h5 className="text-xs font-bold text-emerald-600">1. Xác định thủ tục</h5>
                        <p className="text-[9px] text-foreground/50 mt-0.5 font-medium">Đã xác định đúng thủ tục AI gợi ý</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-accent text-white flex items-center justify-center text-[10px] font-bold">2</div>
                      <div>
                        <h5 className="text-xs font-bold text-primary">2. Thông tin cá nhân</h5>
                        <p className="text-[9px] text-foreground/50 mt-0.5 font-medium">Khai báo dữ liệu nhân thân của công dân</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-neutral-bg text-foreground/40 flex items-center justify-center text-[10px] font-bold">3</div>
                      <div>
                        <h5 className="text-xs font-bold text-foreground/45">3. Thông tin cha, mẹ</h5>
                        <p className="text-[9px] text-foreground/50 mt-0.5 font-medium">Khai báo quan hệ gia đình liên quan</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-neutral-bg text-foreground/40 flex items-center justify-center text-[10px] font-bold">4</div>
                      <div>
                        <h5 className="text-xs font-bold text-foreground/45">4. Giấy tờ đính kèm</h5>
                        <p className="text-[9px] text-foreground/50 mt-0.5 font-medium">Tải lên các tài liệu chứng thực hành chính</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-neutral-bg text-foreground/40 flex items-center justify-center text-[10px] font-bold">5</div>
                      <div>
                        <h5 className="text-xs font-bold text-foreground/45">5. Kiểm tra trước khi nộp</h5>
                        <p className="text-[9px] text-foreground/50 mt-0.5 font-medium">Rà soát tính hợp lệ và tiền kiểm lỗi pháp lý</p>
                      </div>
                    </div>
                  </div>

                  {/* Privacy secure notice */}
                  <div className="flex items-center gap-2.5 p-3 bg-neutral-bg/60 border border-border-slate rounded-xl text-[10px] text-foreground/60 font-semibold shadow-inner">
                    <span>🛡️</span>
                    <span>Dữ liệu được mã hóa và bảo vệ theo tiêu chuẩn của Chính phủ.</span>
                  </div>
                </div>

                {/* Intake Form & Side panels (7/12 width) */}
                <div className="lg:col-span-7 space-y-6">
                  {/* Form intake sheet */}
                  <div className="bg-card-bg border border-border-slate rounded-xl p-5 shadow-sm space-y-4">
                    <div className="border-b border-border-slate pb-3 mb-3 flex justify-between items-center text-left">
                      <div>
                        <span className="text-[8px] font-bold text-accent tracking-wider uppercase block">TỜ KHAI ĐIỆN TỬ SƠ BỘ</span>
                        <h3 className="text-sm font-bold text-primary">{checklist.procedure_name}</h3>
                      </div>
                      <button
                        onClick={handlePreCheck}
                        disabled={isValidating}
                        className="px-4 py-2 bg-accent text-white text-xs font-bold rounded-lg hover:bg-accent-hover transition-all shadow-sm flex items-center gap-1.5"
                      >
                        {isValidating ? "Đang quét..." : "🔍 Tiền kiểm"}
                      </button>
                    </div>

                    {/* Dynamic form inputs list */}
                    <div className="space-y-3.5 max-h-[280px] overflow-y-auto pr-1">
                      {checklist.form_schema && checklist.form_schema.properties &&
                        Object.entries(checklist.form_schema.properties).map(([key, prop]) => {
                          const isRequired = checklist.form_schema.required?.includes(key);
                          const hasError = validationResponse?.findings.some(f => f.field === key && f.level === "error");
                          const errorMsg = validationResponse?.findings.find(f => f.field === key && f.level === "error")?.message;

                          return (
                            <div key={key} className="flex flex-col text-left">
                              <label htmlFor={`input-${key}`} className="text-[11px] font-bold text-primary mb-1">
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
                                className={`px-3 py-2 border rounded-lg text-xs transition-all focus:outline-none focus:border-accent ${
                                  hasError ? "border-error bg-error-bg/10" : "border-border-slate bg-card-bg text-foreground"
                                }`}
                              />
                              {hasError && <span className="text-[10px] font-bold text-error mt-0.5">⚠️ {errorMsg}</span>}
                            </div>
                          );
                        })}
                    </div>
                  </div>

                  {/* AI Recommendations ("KẾT QUẢ AI GỢI Ý") */}
                  <div className="bg-card-bg border border-border-slate rounded-xl p-5 shadow-sm space-y-4 text-left">
                    <div className="flex items-center gap-2 border-b border-border-slate pb-2">
                      <span className="text-base">✨</span>
                      <h4 className="text-xs font-bold text-primary uppercase tracking-wider">Kết quả AI gợi ý</h4>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-[10px]">
                      <div className="space-y-1">
                        <span className="text-foreground/50 block font-semibold">Thủ tục:</span>
                        <span className="font-bold text-primary">{checklist.procedure_name}</span>
                      </div>
                      <div className="space-y-1">
                        <span className="text-foreground/50 block font-semibold">Cơ quan tiếp nhận:</span>
                        <span className="font-bold text-primary">UBND cấp xã / phường</span>
                      </div>
                      <div className="space-y-1">
                        <span className="text-foreground/50 block font-semibold">Thời gian giải quyết:</span>
                        <span className="font-bold text-primary">Trong ngày làm việc</span>
                      </div>
                      <div className="space-y-1">
                        <span className="text-foreground/50 block font-semibold">Lệ phí hành chính:</span>
                        <span className="font-bold text-primary">Miễn phí hoàn toàn</span>
                      </div>
                    </div>
                  </div>

                  {/* Collected info ("THÔNG TIN ĐÃ XÁC ĐỊNH") */}
                  <div className="bg-card-bg border border-border-slate rounded-xl p-5 shadow-sm space-y-3 text-left">
                    <div className="flex items-center justify-between border-b border-border-slate pb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-base">📋</span>
                        <h4 className="text-xs font-bold text-primary uppercase tracking-wider">Thông tin đã xác định</h4>
                      </div>
                      <span className="px-2 py-0.5 bg-accent/10 text-accent font-bold text-[9px] rounded-full">
                        {Object.values(formData).filter(Boolean).length} mục
                      </span>
                    </div>
                    <div className="space-y-2 text-[10px] max-h-[140px] overflow-y-auto">
                      {Object.entries(formData).map(([key, value]) => {
                        const prop = checklist.form_schema.properties[key];
                        return (
                          <div key={key} className="flex justify-between items-center py-1 border-b border-border-slate/30 last:border-0 font-medium">
                            <span className="text-foreground/50">{prop?.title}:</span>
                            <span className={value ? "font-bold text-primary" : "italic text-foreground/30"}>
                              {value || "Chưa xác định"}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Pre-check Results details */}
                  {validationResponse && (
                    <div className={`border rounded-xl p-4 shadow-sm text-left ${
                      validationResponse.is_valid ? "bg-emerald-50 dark:bg-emerald-950/15 border-emerald-200 text-emerald-600" : "bg-red-50 dark:bg-red-950/15 border-red-200 text-red-600"
                    }`}>
                      <h5 className="text-xs font-bold flex items-center gap-2">
                        {validationResponse.is_valid ? "✅ HỒ SƠ ĐỦ ĐIỀU KIỆN SƠ BỘ" : "⚠️ PHÁT HIỆN LỖI KÊ KHAI"}
                      </h5>
                      <p className="text-[10px] mt-1.5 leading-relaxed font-semibold">{validationResponse.summary}</p>
                    </div>
                  )}

                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 md:p-12 bg-card-bg border border-border-slate rounded-2xl max-w-2xl mx-auto w-full shadow-md my-auto relative overflow-hidden transition-all duration-300 hover:shadow-lg">
              {/* Decorative Background Elements */}
              <TrongDongPattern className="absolute w-[280px] h-[280px] -top-10 -right-10 text-accent/5 dark:text-accent/5 pointer-events-none" />
              <LotusFlowerPattern className="absolute w-[180px] h-[180px] -bottom-10 -left-10 text-accent/5 dark:text-accent/5 pointer-events-none" />

              {/* Emblem / Logo Icon */}
              <div className="relative flex items-center justify-center w-20 h-20 rounded-full bg-orange-50 dark:bg-zinc-800 text-accent mb-6 shadow-inner border border-border-slate">
                <TrongDongPattern className="absolute inset-0 w-full h-full text-accent/10 dark:text-accent/20 animate-[spin_120s_linear_infinite]" />
                <span className="text-4xl relative z-10">🏛️</span>
              </div>

              {/* Title & Subtitle */}
              <h2 className="text-2xl font-serif font-bold text-primary tracking-tight text-center relative z-10">
                Trợ Lý Tiền Kiểm & Hướng Dẫn Kê Khai
              </h2>
              <p className="text-xs text-zinc-500 mt-3 max-w-md text-center leading-relaxed font-sans relative z-10 font-medium">
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
