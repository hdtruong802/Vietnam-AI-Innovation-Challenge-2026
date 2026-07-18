"use client";

import { useState } from "react";
import { useProcedureCase } from "./useProcedureCase";
import {
  selectAvailabilityBanner,
  selectCanConfirmU2,
  selectCanRunPrecheck,
  selectStepperProgress,
} from "./procedureCase.selectors";
import type { FlowState } from "./procedureCase.types";
import ChatTranscript from "./intake/ChatTranscript";
import MessageComposer from "./intake/MessageComposer";
import ProcedureRecommendationCard from "./intake/ProcedureRecommendationCard";
import ClarificationQuestionCard from "./intake/ClarificationQuestionCard";
import ChecklistPanel from "./checklist/ChecklistPanel";
import DynamicFormRenderer from "./form/DynamicFormRenderer";
import PrecheckPanel from "./validation/PrecheckPanel";
import OfficialReviewCard from "./trust/OfficialReviewCard";
import type { AuthUser } from "@/features/auth/types";

const VNGovLogo = ({ className = "w-8 h-8" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M50 85 C25 80, 20 55, 18 45 C35 48, 45 65, 50 78 C55 65, 65 48, 82 45 C80 55, 75 80, 50 85 Z" fill="#0D1B3D" />
    <path d="M48 70 C40 50, 22 35, 15 32 C28 25, 45 35, 48 55 Z" fill="#F97316" />
    <path d="M52 70 C60 50, 78 35, 85 32 C72 25, 55 35, 52 55 Z" fill="#F97316" />
    <path d="M50 15 L52 23 L60 25 L52 27 L50 35 L48 27 L40 25 L48 23 Z" fill="#FDBA40" />
  </svg>
);

interface ProcedureWorkspaceProps {
  onGoLanding: () => void;
  initialMessage?: string;
  initialProcedureId?: string;
  user?: AuthUser;
  onLogout: () => void;
}

export default function ProcedureWorkspace({
  onGoLanding,
  initialMessage,
  initialProcedureId,
  user,
  onLogout,
}: ProcedureWorkspaceProps) {
  const { state, actions } = useProcedureCase(initialMessage, initialProcedureId);
  const [activeLeftTab, setActiveLeftTab] = useState<"chat" | "checklist">("chat");
  const [activeMobileTab, setActiveMobileTab] = useState<"chat" | "form">("chat");
  const [activeField, setActiveField] = useState<string | null>(null);

  // Auto-switch tabs to follow the flow once, on the render where it
  // changes, without a separate effect (React's "adjust state during
  // render" pattern — avoids the extra commit an effect would cause).
  const [lastSyncedFlow, setLastSyncedFlow] = useState<FlowState | null>(null);
  if (state.flow !== lastSyncedFlow) {
    setLastSyncedFlow(state.flow);
    if (state.flow === "checklist_review") setActiveLeftTab("checklist");
    if (state.flow === "form_editing") setActiveMobileTab("form");
  }

  const stepper = selectStepperProgress(state);
  const canConfirmU2 = selectCanConfirmU2(state);
  const canRunPrecheck = selectCanRunPrecheck(state);
  const availabilityBanner = selectAvailabilityBanner(state);
  const showQuickPicks = state.transcript.length <= 1;

  const officialReviewMessage =
    state.lastValidationResponse?.summary_message ??
    state.checklist?.message_plain ??
    state.lastIntakeResponse?.message_plain ??
    "Yêu cầu này cần cơ quan có thẩm quyền xem xét trực tiếp.";

  return (
    <div className="flex flex-col h-screen bg-background text-foreground font-sans antialiased pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)] pb-[env(safe-area-inset-bottom)]">
      {/* Navbar */}
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
            onClick={onGoLanding}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-border-slate bg-neutral-bg hover:bg-neutral-bg/85 text-xs font-bold text-primary transition-all duration-200"
          >
            ← Quay lại Trang chủ
          </button>

          <button
            onClick={actions.resetSession}
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border-slate bg-card-bg hover:bg-neutral-bg text-xs font-bold text-foreground/80 transition-all"
          >
            Xóa dữ liệu phiên
          </button>

          <div
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[10px] font-bold ${
              state.availability.backendReachable
                ? "bg-emerald-50 dark:bg-emerald-950/20 border-emerald-200/40 text-emerald-600 dark:text-emerald-400"
                : "bg-error-bg border-error-border text-error"
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${state.availability.backendReachable ? "bg-emerald-500 animate-pulse" : "bg-error"}`}
            />
            {state.availability.backendReachable ? "Hệ thống kết nối" : "Mất kết nối"}
          </div>

          <div className="hidden text-right sm:block">
            <p className="text-xs font-bold text-primary">{user?.display_name ?? "Người dùng"}</p>
            <button type="button" onClick={onLogout} className="text-[10px] font-semibold text-foreground/60 hover:text-gov-red">
              Đăng xuất
            </button>
          </div>
          <button type="button" onClick={onLogout} className="h-8 w-8 rounded-full border border-border-slate bg-neutral-bg text-xs font-bold text-primary shadow-sm transition-all hover:bg-zinc-100" aria-label="Đăng xuất">
            {(user?.display_name ?? "ND").slice(0, 2).toUpperCase()}
          </button>
        </div>
      </header>

      {/* Availability banner */}
      {availabilityBanner.visible && (
        <div
          role="status"
          className={`px-4 py-2 text-[11px] font-bold text-center shrink-0 ${
            availabilityBanner.severity === "blocking"
              ? "bg-error-bg text-error border-b border-error-border"
              : "bg-warning-bg text-warning border-b border-warning-border"
          }`}
        >
          {availabilityBanner.message}
        </div>
      )}

      {/* Mobile tabs */}
      <div className="flex md:hidden border-b border-border-slate bg-card-bg shrink-0" role="tablist" aria-label="Chuyển đổi khung nhìn">
        <button
          role="tab"
          aria-selected={activeMobileTab === "chat"}
          onClick={() => setActiveMobileTab("chat")}
          className={`flex-1 py-3 text-sm font-semibold border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-accent outline-none ${
            activeMobileTab === "chat" ? "border-accent text-accent" : "border-transparent text-zinc-500"
          }`}
        >
          Trợ lý Chat & Checklist
        </button>
        <button
          role="tab"
          aria-selected={activeMobileTab === "form"}
          onClick={() => setActiveMobileTab("form")}
          className={`flex-1 py-3 text-sm font-semibold border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-accent outline-none ${
            activeMobileTab === "form" ? "border-accent text-accent" : "border-transparent text-zinc-500"
          }`}
        >
          Tờ khai & Tiền kiểm
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left column */}
        <aside
          className={`${activeMobileTab === "chat" ? "flex" : "hidden"} md:flex flex-col w-full md:w-[40%] bg-card-bg border-r border-border-slate overflow-hidden`}
        >
          <div className="flex border-b border-border-slate bg-neutral-bg shrink-0" role="tablist" aria-label="Trợ lý và checklist">
            <button
              role="tab"
              aria-selected={activeLeftTab === "chat"}
              onClick={() => setActiveLeftTab("chat")}
              className={`flex-1 py-3 text-xs uppercase tracking-wider font-bold border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-accent outline-none ${
                activeLeftTab === "chat" ? "border-primary text-primary bg-card-bg" : "border-transparent text-zinc-500 hover:text-zinc-800"
              }`}
            >
              Trợ lý Hướng dẫn
            </button>
            <button
              role="tab"
              aria-selected={activeLeftTab === "checklist"}
              onClick={() => setActiveLeftTab("checklist")}
              disabled={!state.checklist}
              className={`flex-1 py-3 text-xs uppercase tracking-wider font-bold border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-accent outline-none ${
                !state.checklist
                  ? "opacity-40 cursor-not-allowed text-zinc-400"
                  : activeLeftTab === "checklist"
                    ? "border-primary text-primary bg-card-bg"
                    : "border-transparent text-zinc-500 hover:text-zinc-800"
              }`}
            >
              Checklist Hồ sơ
            </button>
          </div>

          <div className={`${activeLeftTab === "chat" ? "flex" : "hidden"} flex-col flex-1 overflow-hidden bg-card-bg`}>
            <ChatTranscript messages={state.transcript} />

            {state.flow === "procedure_review" && state.lastIntakeResponse?.procedure && (
              <ProcedureRecommendationCard
                candidate={state.lastIntakeResponse.procedure}
                trustMetadata={state.trustMetadata}
                onConfirm={actions.confirmU1}
                onReject={actions.rejectU1}
              />
            )}

            {state.flow === "clarifying" && (
              <ClarificationQuestionCard
                questions={state.activeClarifyingQuestions}
                currentIndex={state.currentQuestionIndex}
                answeredQuestions={state.answeredQuestions}
                onSubmit={actions.answerClarification}
                onEdit={actions.editClarificationAnswer}
              />
            )}

            <MessageComposer
              isBusy={state.isBusy}
              showQuickPicks={showQuickPicks}
              onSend={actions.sendMessage}
              onSelectStaticProcedure={actions.selectStaticProcedure}
              onCancel={actions.cancelRequest}
            />
          </div>

          <div className={`${activeLeftTab === "checklist" ? "flex" : "hidden"} flex-col flex-1 overflow-y-auto bg-card-bg`}>
            {state.checklist ? (
              <ChecklistPanel
                state={state}
                checklist={state.checklist}
                activeField={activeField}
                canConfirmU2={canConfirmU2}
                onConfirmU2={actions.confirmU2}
                onFeedback={(vote, reason, note) => actions.recordFeedback("checklist", vote, reason, note)}
              />
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-6 text-center bg-card-bg text-zinc-500">
                <span className="text-3xl">📋</span>
                <h3 className="text-sm font-semibold mt-3 text-primary">Chưa có dữ liệu thủ tục</h3>
                <p className="text-xs mt-1 max-w-xs">
                  Vui lòng trò chuyện với trợ lý hoặc chọn nhanh dịch vụ để tải checklist hồ sơ.
                </p>
              </div>
            )}
          </div>
        </aside>

        {/* Right column */}
        <main className={`${activeMobileTab === "form" ? "flex" : "hidden"} md:flex flex-col flex-1 bg-neutral-bg overflow-y-auto p-6`}>
          {state.flow === "official_review_required" ? (
            <div className="m-auto w-full">
              <OfficialReviewCard message={officialReviewMessage} trustMetadata={state.trustMetadata} />
            </div>
          ) : state.checklist ? (
            <div className="max-w-4xl mx-auto w-full">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                <div className="lg:col-span-5 space-y-6 text-left">
                  <div className="flex items-center gap-4 p-4 bg-card-bg border border-border-slate rounded-xl shadow-sm">
                    <div className="relative w-12 h-12 flex items-center justify-center rounded-full border-2 border-accent text-accent font-bold text-xs bg-accent/5">
                      {stepper.current}/{stepper.total}
                    </div>
                    <div>
                      <h4 className="text-xs font-extrabold text-primary">{stepper.label}</h4>
                      <p className="text-[10px] text-foreground/60 font-semibold mt-0.5">
                        Bước {stepper.current} / {stepper.total}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2.5 p-3 bg-neutral-bg/60 border border-border-slate rounded-xl text-[10px] text-foreground/60 font-semibold shadow-inner">
                    <span>🛡️</span>
                    <span>Dữ liệu được lưu tạm trong phiên trình duyệt, không lưu trữ lâu dài.</span>
                  </div>
                </div>

                <div className="lg:col-span-7 space-y-6">
                  <div className="bg-card-bg border border-border-slate rounded-xl p-5 shadow-sm space-y-4">
                    <div className="border-b border-border-slate pb-3 mb-3 text-left">
                      <span className="text-[8px] font-bold text-accent tracking-wider uppercase block">TỜ KHAI ĐIỆN TỬ SƠ BỘ</span>
                      <h3 className="text-sm font-bold text-primary">{state.checklist.procedure_name}</h3>
                    </div>
                    <DynamicFormRenderer
                      checklist={state.checklist}
                      formDraft={state.formDraft}
                      findings={state.lastValidationResponse?.findings ?? []}
                      onChange={actions.updateFormField}
                      onFocusField={setActiveField}
                      onBlurField={() => setActiveField(null)}
                    />
                  </div>

                  <PrecheckPanel
                    flow={state.flow}
                    isBusy={state.isBusy}
                    canRunPrecheck={canRunPrecheck}
                    lastValidationResponse={state.lastValidationResponse}
                    trustMetadata={state.trustMetadata}
                    onRunPrecheck={actions.runPrecheck}
                    onConfirmU3={actions.confirmU3}
                    onFeedback={(vote, reason, note) => actions.recordFeedback("precheck", vote, reason, note)}
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 md:p-12 bg-card-bg border border-border-slate rounded-2xl max-w-2xl mx-auto w-full shadow-md my-auto">
              <div className="relative flex items-center justify-center w-20 h-20 rounded-full bg-orange-50 dark:bg-zinc-800 text-accent mb-6 shadow-inner border border-border-slate">
                <span className="text-4xl relative z-10">🏛️</span>
              </div>
              <h2 className="text-2xl font-serif font-bold text-primary tracking-tight text-center">
                Trợ Lý Tiền Kiểm & Hướng Dẫn Kê Khai
              </h2>
              <p className="text-xs text-zinc-500 mt-3 max-w-md text-center leading-relaxed font-sans font-medium">
                Hệ thống hỗ trợ công dân chuẩn bị hồ sơ hành chính công trực tuyến theo đúng quy định pháp lý, tự động rà soát sai sót trước khi nộp chính thức.
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
