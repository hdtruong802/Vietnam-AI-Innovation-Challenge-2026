"use client";

import React, { useState } from "react";
import ProcedureWorkspace from "../features/procedure-case/ProcedureWorkspace";
import LandingHeader from "./components/landing/LandingHeader";
import LandingHero from "./components/landing/LandingHero";
import ServiceQuickGrid from "./components/landing/ServiceQuickGrid";
import FeaturedServicesAndNews from "./components/landing/FeaturedServicesAndNews";
import BenefitsSection from "./components/landing/BenefitsSection";
import LandingFooter from "./components/landing/LandingFooter";
import ComingSoonModal from "./components/landing/ComingSoonModal";

export default function Home() {
  const [view, setView] = useState<"landing" | "copilot">("landing");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalText, setModalText] = useState<string>("");

  const [handoffMessage, setHandoffMessage] = useState<string | undefined>(undefined);
  const [handoffProcedureId, setHandoffProcedureId] = useState<string | undefined>(undefined);

  const handleOpenComingSoon = (text: string) => {
    setModalText(text);
    setShowModal(true);
  };

  const handleGoLanding = () => {
    setHandoffMessage(undefined);
    setHandoffProcedureId(undefined);
    setView("landing");
  };

  const handleGoCopilot = () => {
    setHandoffMessage(undefined);
    setHandoffProcedureId(undefined);
    setView("copilot");
  };

  const handleSelectProcedure = (procedureId: string) => {
    setHandoffMessage(undefined);
    setHandoffProcedureId(procedureId);
    setView("copilot");
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (!query) return;

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

  return (
    <>
      {view === "landing" ? (
        <div className="portal-home min-h-screen bg-[var(--portal-page)] text-foreground font-sans antialiased flex flex-col relative overflow-x-hidden">
          <LandingHeader
            onGoCopilot={handleGoCopilot}
            onComingSoon={handleOpenComingSoon}
            onLogin={() => handleOpenComingSoon("Chức năng đăng nhập thông qua VNeID / Cổng Quốc gia đang được kết nối.")}
          />

          <LandingHero
            searchQuery={searchQuery}
            onSearchQueryChange={setSearchQuery}
            onSearchSubmit={handleSearchSubmit}
          />

          <ServiceQuickGrid onGoCopilot={handleGoCopilot} onComingSoon={handleOpenComingSoon} />

          <FeaturedServicesAndNews
            onSelectProcedure={handleSelectProcedure}
            onGoCopilot={handleGoCopilot}
            onComingSoon={handleOpenComingSoon}
          />

          <BenefitsSection />

          <LandingFooter onComingSoon={handleOpenComingSoon} />
        </div>
      ) : (
        <ProcedureWorkspace
          onGoLanding={handleGoLanding}
          onOpenComingSoon={handleOpenComingSoon}
          initialMessage={handoffMessage}
          initialProcedureId={handoffProcedureId}
        />
      )}
      <ComingSoonModal show={showModal} text={modalText} onClose={() => setShowModal(false)} />
    </>
  );
}
