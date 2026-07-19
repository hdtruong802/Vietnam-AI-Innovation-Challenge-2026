"use client";

import React, { useState } from "react";
import LoginDialog from "@/features/auth/LoginDialog";
import { clearDemoSession, readDemoSession, startDemoSession } from "@/features/auth/session";
import type { StoredDemoSession } from "@/features/auth/types";
import ProcedureWorkspace from "../features/procedure-case/ProcedureWorkspace";
import BenefitsSection from "./components/landing/BenefitsSection";
import ComingSoonModal from "./components/landing/ComingSoonModal";
import FeaturedServicesAndNews from "./components/landing/FeaturedServicesAndNews";
import LandingFooter from "./components/landing/LandingFooter";
import LandingHeader from "./components/landing/LandingHeader";
import LandingHero from "./components/landing/LandingHero";
import ServiceQuickGrid from "./components/landing/ServiceQuickGrid";

export default function Home() {
  const [view, setView] = useState<"landing" | "copilot">("landing");
  const [searchQuery, setSearchQuery] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [modalText, setModalText] = useState("");
  const [authSession, setAuthSession] = useState<StoredDemoSession | null>(() => readDemoSession());
  const [showLogin, setShowLogin] = useState(false);
  const [handoffMessage, setHandoffMessage] = useState<string | undefined>();
  const [handoffProcedureId, setHandoffProcedureId] = useState<string | undefined>();

  const handleOpenComingSoon = (text: string) => {
    setModalText(text);
    setShowModal(true);
  };

  const handleGoLanding = () => {
    setHandoffMessage(undefined);
    setHandoffProcedureId(undefined);
    setView("landing");
  };

  const openCopilot = () => {
    setHandoffMessage(undefined);
    setHandoffProcedureId(undefined);
    setView("copilot");
  };

  const requireLogin = () => {
    if (authSession) return false;
    setShowLogin(true);
    return true;
  };

  const handleGoCopilot = () => {
    if (requireLogin()) return;
    openCopilot();
  };

  const handleSelectProcedure = (procedureId: string) => {
    if (requireLogin()) return;
    setHandoffMessage(undefined);
    setHandoffProcedureId(procedureId);
    setView("copilot");
  };

  const handleSearchSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const query = searchQuery.trim();
    if (!query || requireLogin()) return;
    const lower = query.toLowerCase();
    if (lower.includes("sinh") || lower.includes("birth")) {
      handleSelectProcedure("dang-ky-khai-sinh");
    } else if (lower.includes("trú") || lower.includes("residence")) {
      handleSelectProcedure("dang-ky-thuong-tru");
    } else if (lower.includes("doanh") || lower.includes("business")) {
      handleSelectProcedure("dang-ky-ho-kinh-doanh");
    } else {
      setHandoffProcedureId(undefined);
      setHandoffMessage(query);
      setView("copilot");
    }
    setSearchQuery("");
  };

  const handleDemoLogin = () => {
    setAuthSession(startDemoSession());
    setShowLogin(false);
    openCopilot();
  };

  const handleLogout = () => {
    clearDemoSession();
    setAuthSession(null);
    handleGoLanding();
  };

  return (
    <>
      {view === "landing" ? (
        <div className="portal-home relative flex min-h-screen flex-col overflow-x-hidden bg-background font-sans text-foreground antialiased">
          <LandingHeader
            onGoCopilot={handleGoCopilot}
            onComingSoon={handleOpenComingSoon}
            onLogin={() => setShowLogin(true)}
            isAuthenticated={Boolean(authSession)}
            onLogout={handleLogout}
          />
          <LandingHero searchQuery={searchQuery} onSearchQueryChange={setSearchQuery} onSearchSubmit={handleSearchSubmit} />
          <ServiceQuickGrid onGoCopilot={handleGoCopilot} onComingSoon={handleOpenComingSoon} />
          <FeaturedServicesAndNews onSelectProcedure={handleSelectProcedure} onGoCopilot={handleGoCopilot} onComingSoon={handleOpenComingSoon} />
          <BenefitsSection />
          <LandingFooter onComingSoon={handleOpenComingSoon} />
        </div>
      ) : (
        <ProcedureWorkspace
          onGoLanding={handleGoLanding}
          initialMessage={handoffMessage}
          initialProcedureId={handoffProcedureId}
          user={authSession?.user}
          onLogout={handleLogout}
        />
      )}
      <ComingSoonModal show={showModal} text={modalText} onClose={() => setShowModal(false)} />
      <LoginDialog
          key={showLogin ? "login-open" : "login-closed"}
          isOpen={showLogin}
          onClose={() => {
            setShowLogin(false);
          }}
          onDemoLogin={handleDemoLogin}
      />
    </>
  );
}
