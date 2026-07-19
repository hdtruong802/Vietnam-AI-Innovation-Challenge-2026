"use client";

import { useState } from "react";
import Image from "next/image";
import vngovSymbol from "@/image/VNGov_symbol.svg";
import portalLogo from "@/image/logo-cong-dich-vu-cong-quoc-gia.png";
import { useProcedureCase } from "./useProcedureCase";
import {
  selectAvailabilityBanner,
  selectCanConfirmU2,
  selectCanRenderForm,
  selectVisibleFindings,
  selectCanRenderPrecheck,
  selectCanRunPrecheck,
  selectProgressStage,
  selectRightPaneMode,
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
import DemoModeBanner from "./trust/DemoModeBanner";
import { AlertCircleIcon, ChecklistIcon, DocIcon, ShieldIcon } from "./icons";
import { FORM_TEMPLATES } from "./procedureCase.constants";
import type { ProcedureCaseState } from "./procedureCase.types";
import type { AuthUser } from "@/features/auth/types";

const PROGRESS_STAGES: { id: number; label: string }[] = [
  { id: 1, label: "Nhu cầu" },
  { id: 2, label: "Điều kiện" },
  { id: 3, label: "Giấy tờ" },
  { id: 4, label: "Tờ khai" },
  { id: 5, label: "Kiểm tra" },
  { id: 6, label: "Hoàn tất" },
];

interface ProcedureWorkspaceProps {
  onGoLanding: () => void;
  initialMessage?: string;
  initialProcedureId?: string;
  /** Preview-only: seeds state from a fixture and makes the workspace
   * read-only (no network/session-storage activity). Undefined in the real
   * app — production behavior is unchanged. */
  fixtureState?: ProcedureCaseState;
  /** Preview-only: disables the avatar button when there's no logout host
   * on the current route, instead of silently no-op-ing it. */
  avatarDisabled?: boolean;
  user?: AuthUser;
  onLogout?: () => void;
}

export default function ProcedureWorkspace({
  onGoLanding,
  initialMessage,
  initialProcedureId,
  fixtureState,
  avatarDisabled = false,
  user,
  onLogout,
}: ProcedureWorkspaceProps) {
  const { state, actions } = useProcedureCase(initialMessage, initialProcedureId, fixtureState);
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

  const stage = selectProgressStage(state);
  const paneView = selectRightPaneMode(state);
  const canRenderForm = selectCanRenderForm(state);
  const visibleFindings = selectVisibleFindings(state);
  const fieldLabels: Record<string, string> = Object.fromEntries(
    Object.entries(state.checklist?.form_schema?.properties ?? {}).map(([key, prop]) => [key, prop.title]),
  );
  const canRenderPrecheck = selectCanRenderPrecheck(state);
  const canConfirmU2 = selectCanConfirmU2(state);
  const canRunPrecheck = selectCanRunPrecheck(state);
  const availabilityBanner = selectAvailabilityBanner(state);
  const showQuickPicks = state.transcript.length <= 1;
  const demoMode = Boolean(state.trustMetadata?.demo_mode || state.checklist?.demo_mode);

  const officialReviewMessage =
    state.lastValidationResponse?.summary_message ??
    state.checklist?.message_plain ??
    state.lastIntakeResponse?.message_plain ??
    "Yêu cầu này cần cơ quan có thẩm quyền xem xét trực tiếp.";

  return (
    <div className="copilot-workspace flex flex-col h-screen bg-[var(--vg-canvas)] text-[var(--vg-text)] font-sans antialiased pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)] pb-[env(safe-area-inset-bottom)]">
      {/* Header */}
      <header className="flex items-center justify-between gap-4 px-6 pr-[max(1.5rem,env(safe-area-inset-right))] pl-[max(1.5rem,env(safe-area-inset-left))] py-3 min-h-[72px] bg-[var(--vg-surface)] border-b border-[var(--vg-border)] shrink-0 relative z-20">
        <div className="flex items-center gap-3 min-w-0">
          <Image src={vngovSymbol} alt="Biểu tượng VNGov" className="w-9 h-9 shrink-0 object-contain" priority unoptimized />
          <Image src={portalLogo} alt="Cổng dịch vụ công Quốc gia" className="h-7 w-auto hidden sm:block" priority />
          <span className="text-[var(--vg-border-strong)] font-light text-lg hidden sm:inline">|</span>
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-base font-bold tracking-tight text-[var(--vg-text)] truncate">
              VNGov Copilot
            </span>
            <span className="text-[10px] font-semibold text-[var(--vg-text-muted)] hidden md:inline">
              Trợ lý AI cho dịch vụ công
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={onGoLanding}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-[var(--vg-border)] bg-[var(--vg-surface)] hover:bg-[var(--vg-surface-subtle)] text-xs font-bold text-[var(--vg-accent)] transition-all"
          >
            ← Quay lại Trang chủ
          </button>

          <button
            onClick={actions.resetSession}
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-[var(--vg-border)] bg-[var(--vg-surface)] hover:bg-[var(--vg-surface-subtle)] text-xs font-semibold text-[var(--vg-text-secondary)] transition-all"
          >
            Xóa dữ liệu phiên
          </button>

          <div
            role="status"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[10px] font-bold ${
              state.availability.backendReachable
                ? "bg-[var(--vg-success-soft)] border-[var(--vg-success)]/30 text-[var(--vg-success)]"
                : "bg-[var(--vg-error-soft)] border-[var(--vg-error)]/30 text-[var(--vg-error)]"
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${state.availability.backendReachable ? "bg-[var(--vg-success)] animate-pulse" : "bg-[var(--vg-error)]"}`}
            />
            {state.availability.backendReachable ? "Hệ thống kết nối" : "Mất kết nối"}
          </div>

          <div className="hidden text-right sm:block">
            <p className="text-xs font-bold text-[var(--vg-accent)]">{user?.display_name ?? "Người dùng"}</p>
            <button
              type="button"
              onClick={onLogout}
              disabled={avatarDisabled}
              className="text-[10px] font-semibold text-[var(--vg-text-muted)] hover:text-[var(--vg-error)] disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Đăng xuất
            </button>
          </div>

          <button
            type="button"
            onClick={onLogout}
            disabled={avatarDisabled}
            aria-label="Đăng xuất"
            title={avatarDisabled ? "Không khả dụng trong chế độ xem trước" : undefined}
            className="w-8 h-8 rounded-full bg-[var(--vg-surface-subtle)] border border-[var(--vg-border)] flex items-center justify-center font-bold text-xs text-[var(--vg-accent)] hover:bg-[var(--vg-gold-soft)] transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-[var(--vg-surface-subtle)]"
          >
            {(user?.display_name ?? "ND").slice(0, 2).toUpperCase()}
          </button>
        </div>
      </header>

      {/* Availability banner */}
      {availabilityBanner.visible && (
        <div
          role="status"
          aria-live="polite"
          className={`flex flex-col sm:flex-row sm:items-center gap-2 px-4 py-2.5 text-xs shrink-0 border-b ${
            availabilityBanner.severity === "blocking"
              ? "bg-[var(--vg-error-soft)] text-[var(--vg-error)] border-[var(--vg-error)]/30"
              : "bg-[var(--vg-warning-soft)] text-[var(--vg-warning)] border-[var(--vg-warning)]/30"
          }`}
        >
          <div className="flex items-center gap-2 flex-1">
            <AlertCircleIcon className="w-4 h-4 shrink-0" />
            <span className="font-semibold">{availabilityBanner.message}</span>
          </div>
          <button
            type="button"
            onClick={actions.retryHealthCheck}
            className="self-start sm:self-auto shrink-0 font-bold underline underline-offset-2 hover:no-underline"
          >
            Thử kết nối lại
          </button>
        </div>
      )}

      {demoMode && <DemoModeBanner />}

      {/* Mobile tabs */}
      <div className="flex md:hidden border-b border-[var(--vg-border)] bg-[var(--vg-surface)] shrink-0" role="tablist" aria-label="Chuyển đổi khung nhìn">
        <button
          role="tab"
          aria-selected={activeMobileTab === "chat"}
          onClick={() => setActiveMobileTab("chat")}
          className={`flex-1 py-3 text-sm font-semibold border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none ${
            activeMobileTab === "chat" ? "border-[var(--vg-accent)] text-[var(--vg-accent)]" : "border-transparent text-[var(--vg-text-muted)]"
          }`}
        >
          Trợ lý & Checklist
        </button>
        <button
          role="tab"
          aria-selected={activeMobileTab === "form"}
          onClick={() => setActiveMobileTab("form")}
          className={`flex-1 py-3 text-sm font-semibold border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none ${
            activeMobileTab === "form" ? "border-[var(--vg-accent)] text-[var(--vg-accent)]" : "border-transparent text-[var(--vg-text-muted)]"
          }`}
        >
          Tờ khai & Tiền kiểm
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left column */}
        <aside
          className={`${activeMobileTab === "chat" ? "flex" : "hidden"} md:flex flex-col w-full md:w-[38%] bg-[var(--vg-surface)] border-r border-[var(--vg-border)] overflow-hidden`}
        >
          <div className="flex border-b border-[var(--vg-border)] bg-[var(--vg-surface)]" role="tablist" aria-label="Trợ lý và checklist">
            <button
              role="tab"
              aria-selected={activeLeftTab === "chat"}
              onClick={() => setActiveLeftTab("chat")}
              className={`flex-1 py-3 text-sm font-semibold border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none ${
                activeLeftTab === "chat" ? "border-[var(--vg-accent)] text-[var(--vg-accent)]" : "border-transparent text-[var(--vg-text-muted)] hover:text-[var(--vg-text)]"
              }`}
            >
              Trợ lý hướng dẫn
            </button>
            <button
              role="tab"
              aria-selected={activeLeftTab === "checklist"}
              onClick={() => setActiveLeftTab("checklist")}
              disabled={!state.checklist}
              className={`flex-1 py-3 text-sm font-semibold border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none ${
                !state.checklist
                  ? "opacity-40 cursor-not-allowed text-[var(--vg-text-muted)]"
                  : activeLeftTab === "checklist"
                    ? "border-[var(--vg-accent)] text-[var(--vg-accent)]"
                    : "border-transparent text-[var(--vg-text-muted)] hover:text-[var(--vg-text)]"
              }`}
            >
              Checklist hồ sơ
            </button>
          </div>

          <div className={`${activeLeftTab === "chat" ? "flex" : "hidden"} flex-col flex-1 overflow-hidden bg-[var(--vg-surface)]`}>
            <ChatTranscript messages={state.transcript} />

            {paneView.mode === "procedure_review" && state.lastIntakeResponse?.procedure && (
              <ProcedureRecommendationCard
                candidate={state.lastIntakeResponse.procedure}
                trustMetadata={state.trustMetadata}
                onConfirm={actions.confirmU1}
                onReject={actions.rejectU1}
              />
            )}

            {paneView.mode === "clarifying" && (
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

          <div className={`${activeLeftTab === "checklist" ? "flex" : "hidden"} flex-col flex-1 overflow-y-auto bg-[var(--vg-surface)]`}>
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
              <div className="flex-1 flex flex-col items-center justify-center p-6 text-center text-[var(--vg-text-muted)]">
                <ChecklistIcon className="w-8 h-8 text-[var(--vg-border-strong)]" />
                <h3 className="text-sm font-semibold mt-3 text-[var(--vg-text)]">Chưa có dữ liệu thủ tục</h3>
                <p className="text-xs mt-1 max-w-xs">
                  Vui lòng trò chuyện với trợ lý hoặc chọn nhanh dịch vụ để tải checklist hồ sơ.
                </p>
              </div>
            )}
          </div>
        </aside>

        {/* Right column */}
        <main className={`${activeMobileTab === "form" ? "flex" : "hidden"} md:flex flex-col flex-1 bg-[var(--vg-canvas)] overflow-y-auto p-6`}>
          {paneView.mode === "official_review" ? (
            <div className="m-auto w-full">
              <OfficialReviewCard message={officialReviewMessage} trustMetadata={state.trustMetadata} />
            </div>
          ) : canRenderForm && state.checklist ? (
            <div className="max-w-4xl mx-auto w-full">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                <div className="lg:col-span-5 space-y-6 text-left">
                  <div className="p-4 bg-[var(--vg-surface)] border border-[var(--vg-border)] rounded-xl space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-[var(--vg-text-muted)] uppercase tracking-wider">
                        Bước {stage.id} / {stage.total}
                      </span>
                      {paneView.degraded && (
                        <span className="text-[10px] font-bold text-[var(--vg-error)]">Đang gián đoạn kết nối</span>
                      )}
                    </div>
                    <div className="flex items-center">
                      {PROGRESS_STAGES.map((s, i) => (
                        <div key={s.id} className="flex items-center flex-1 last:flex-none">
                          <div className="flex flex-col items-center gap-1">
                            <div
                              className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 ${
                                s.id < stage.id
                                  ? "bg-[var(--vg-success)] border-[var(--vg-success)] text-white"
                                  : s.id === stage.id
                                    ? "border-[var(--vg-accent)] text-[var(--vg-accent)] bg-[var(--vg-accent-soft)]"
                                    : "border-[var(--vg-border)] text-[var(--vg-text-muted)]"
                              }`}
                            >
                              {s.id < stage.id ? "✓" : s.id}
                            </div>
                            <span
                              className={`text-[9px] font-semibold whitespace-nowrap ${
                                s.id === stage.id ? "text-[var(--vg-accent)]" : "text-[var(--vg-text-muted)]"
                              }`}
                            >
                              {s.label}
                            </span>
                          </div>
                          {i < PROGRESS_STAGES.length - 1 && (
                            <div className={`flex-1 h-px mx-1 mb-4 ${s.id < stage.id ? "bg-[var(--vg-success)]" : "bg-[var(--vg-border)]"}`} />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-2.5 p-3 bg-[var(--vg-surface-subtle)] border border-[var(--vg-border)] rounded-xl text-[10px] text-[var(--vg-text-muted)] font-semibold">
                    <ShieldIcon className="w-4 h-4 shrink-0 text-[var(--vg-gold)]" />
                    <span>Dữ liệu của bản thử nghiệm được lưu tạm trong phiên trình duyệt.</span>
                  </div>
                </div>

                <div className="lg:col-span-7 space-y-6">
                  <div className="bg-[var(--vg-surface)] border border-[var(--vg-border)] rounded-xl p-5 space-y-4">
                    <div className="border-b border-[var(--vg-border)] pb-3 mb-3 text-left">
                      <span className="text-[10px] font-bold text-[var(--vg-accent)] tracking-wider uppercase block">
                        {state.checklist.fixture_mode || state.checklist.demo_mode
                          ? "Biểu mẫu demo MVP"
                          : "Tờ khai"}
                      </span>
                      <h3 className="text-sm font-bold text-[var(--vg-text)]">{state.checklist.procedure_name}</h3>
                      {FORM_TEMPLATES[state.checklist.procedure_id] && (
                        <a
                          href={FORM_TEMPLATES[state.checklist.procedure_id].href}
                          download
                          className="inline-flex items-center gap-1.5 mt-2 text-[11px] font-bold text-[var(--vg-accent)] hover:underline focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] outline-none rounded"
                        >
                          <DocIcon className="w-3.5 h-3.5" />
                          Tải biểu mẫu chính thức: {FORM_TEMPLATES[state.checklist.procedure_id].label}
                        </a>
                      )}
                    </div>
                    <DynamicFormRenderer
                      checklist={state.checklist}
                      formDraft={state.formDraft}
                      findings={visibleFindings}
                      onChange={actions.updateFormField}
                      onFocusField={setActiveField}
                      onBlurField={() => setActiveField(null)}
                    />
                  </div>

                  {canRenderPrecheck && (
                    <PrecheckPanel
                      flow={state.flow}
                      isBusy={state.isBusy}
                      canRunPrecheck={canRunPrecheck}
                      lastValidationResponse={state.lastValidationResponse}
                      visibleFindings={visibleFindings}
                      fieldLabels={fieldLabels}
                      trustMetadata={state.trustMetadata}
                      onRunPrecheck={actions.runPrecheck}
                      onConfirmU3={actions.confirmU3}
                      onFeedback={(vote, reason, note) => actions.recordFeedback("precheck", vote, reason, note)}
                    />
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="m-auto w-full max-w-md space-y-4">
              <div className="flex flex-col items-center text-center p-8 bg-[var(--vg-surface)] border border-[var(--vg-border)] rounded-2xl">
                <div className="w-16 h-16 rounded-full bg-[var(--vg-gold-soft)] flex items-center justify-center text-[var(--vg-gold)] mb-4">
                  <DocIcon />
                </div>
                <h2 className="text-lg font-bold text-[var(--vg-text)]">Tờ khai</h2>
                <p className="text-sm font-semibold text-[var(--vg-text)] mt-3">Tờ khai chưa được mở</p>
                <p className="text-xs text-[var(--vg-text-muted)] mt-2 leading-relaxed">
                  Hãy chọn hoặc mô tả thủ tục cần thực hiện. Sau khi bạn xác nhận checklist, tờ khai phù hợp sẽ xuất hiện tại đây.
                </p>
              </div>

              <div className="flex items-start gap-3 p-4 bg-[var(--vg-surface-subtle)] border border-[var(--vg-border)] rounded-xl text-left">
                <span className="shrink-0 w-8 h-8 rounded-lg bg-[var(--vg-surface)] border border-[var(--vg-border)] flex items-center justify-center text-[var(--vg-text-muted)]">
                  <ChecklistIcon className="w-4 h-4" />
                </span>
                <div>
                  <h3 className="text-xs font-bold text-[var(--vg-text)]">Kiểm tra sơ bộ</h3>
                  <p className="text-[11px] text-[var(--vg-text-muted)] mt-0.5">
                    Chức năng sẽ khả dụng sau khi hoàn tất tờ khai.
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
