"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ShieldCheck,
  Activity,
  Brain,
  BarChart3,
  Database,
  Globe,
  Layers,
  FileText,
  ClipboardList,
  CalendarCheck,
  HeartPulse,
  Sun,
  Moon,
  PhoneCall
} from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";

export function NavigationHeader() {
  const pathname = usePathname();
  const { language, setLanguage, t } = useLanguage();
  const [clinicalTheme, setClinicalTheme] = useState<"DAYLIGHT" | "NIGHTWARD">("DAYLIGHT");

  useEffect(() => {
    const body = document.body;
    if (clinicalTheme === "DAYLIGHT") {
      body.classList.add("medical-daylight-theme");
      body.classList.remove("medical-nightward-theme");
    } else {
      body.classList.add("medical-nightward-theme");
      body.classList.remove("medical-daylight-theme");
    }
  }, [clinicalTheme]);

  const navLinks = [
    { href: "/", label: t.navTriage, icon: Activity, badge: "AI" },
    { href: "/reports", label: t.navReports, icon: FileText, badge: "OCR+PDF" },
    { href: "/telemedicine", label: t.navTelemedicine, icon: CalendarCheck, badge: "SLMC" },
    { href: "/records", label: t.navRecords, icon: ClipboardList },
    { href: "/knowledge", label: t.navOntology, icon: Layers },
    { href: "/rlhf", label: t.navRLHF, icon: Brain },
    { href: "/analytics", label: t.navAnalytics, icon: BarChart3 },
    { href: "/evaluation", label: t.navEvaluation, icon: ShieldCheck },
    { href: "/fhir", label: t.navFHIR, icon: Database },
  ];

  return (
    <header className="sticky top-0 z-30 border-b border-[#CBE2EA] bg-white/95 backdrop-blur-md shadow-clinical-card">
      {/* Top Clinical Governance & Safety Ribbon */}
      <div className="clinical-dark-preserve bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0A2540] text-slate-200 text-xs px-4 py-1.5 border-b border-teal-500/25">
        <div className="max-w-7xl mx-auto flex flex-wrap justify-between items-center gap-2 tracking-wide">
          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center font-semibold text-emerald-300 bg-emerald-950/70 border border-emerald-500/40 px-2 py-0.5 rounded-full text-[11px]">
              <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5 animate-pulse" />
              {t.hipaaActive}
            </span>
            <span className="text-slate-500 hidden md:inline">|</span>
            <span className="hidden md:inline text-cyan-100/90 text-[11px]">{t.phiScrubbedNotice}</span>
            <span className="text-slate-500 hidden lg:inline">|</span>
            <span className="hidden lg:inline text-teal-200/90 text-[11px]">{t.redFlagFilterStatus}</span>
          </div>

          <div className="flex items-center space-x-2.5">
            {/* Emergency Hotline Quick Pill */}
            <a
              href="tel:1990"
              className="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-rose-600/90 hover:bg-rose-500 text-white text-[11px] font-bold shadow-xs transition-colors"
              title="Sri Lanka Suwa Seriya Emergency Ambulance Service (1990)"
            >
              <PhoneCall className="w-3 h-3" />
              <span>1990 Suwa Seriya</span>
            </a>

            <span className="bg-[#10375C] text-cyan-100 px-2.5 py-0.5 rounded-full text-[11px] font-mono border border-cyan-500/30 hidden xl:inline">
              {t.clinicianBadge}
            </span>

            {/* Clinical Daylight / Ward Night Theme Switcher */}
            <button
              type="button"
              onClick={() => setClinicalTheme((prev) => (prev === "DAYLIGHT" ? "NIGHTWARD" : "DAYLIGHT"))}
              className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#10375C] hover:bg-[#164875] text-teal-200 border border-teal-400/30 text-[11px] font-semibold transition-colors cursor-pointer"
              title="Switch between Clinical Daylight Palette and Night Ward Mode"
            >
              {clinicalTheme === "DAYLIGHT" ? (
                <>
                  <Sun className="w-3 h-3 text-amber-300" />
                  <span className="hidden sm:inline">Clinical Light</span>
                </>
              ) : (
                <>
                  <Moon className="w-3 h-3 text-cyan-300" />
                  <span className="hidden sm:inline">Ward Dark</span>
                </>
              )}
            </button>

            {/* Language Switcher */}
            <div className="flex items-center bg-[#071A2E] rounded-full border border-cyan-500/30 p-0.5 text-[11px]">
              <Globe className="w-3 h-3 text-teal-300 ml-1.5 mr-1" />
              <button
                onClick={() => setLanguage("en")}
                className={`px-2 py-0.5 rounded-full font-bold transition-all cursor-pointer ${
                  language === "en"
                    ? "bg-gradient-to-r from-teal-600 to-cyan-600 text-white shadow-xs"
                    : "text-slate-300 hover:text-white"
                }`}
              >
                EN
              </button>
              <button
                onClick={() => setLanguage("si")}
                className={`px-2 py-0.5 rounded-full font-bold transition-all cursor-pointer ${
                  language === "si"
                    ? "bg-gradient-to-r from-teal-600 to-cyan-600 text-white shadow-xs"
                    : "text-slate-300 hover:text-white"
                }`}
              >
                සිංහල
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Clinical Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-2.5 gap-4">
          {/* Brand Emblem */}
          <Link href="/" className="flex items-center space-x-3 shrink-0 group">
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-[#0D9488] via-[#0891B2] to-[#0284C7] flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform">
              <HeartPulse className="w-5 h-5 text-white" />
              <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-white flex items-center justify-center text-[8px] font-extrabold text-white">
                +
              </span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-base sm:text-lg font-extrabold tracking-tight text-[#0A2540] leading-tight">
                  {t.appTitle}
                </span>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-teal-50 text-teal-700 border border-teal-200">
                  CDSS v2.5
                </span>
              </div>
              <span className="text-[10px] text-[#486581] uppercase tracking-wider font-semibold block">
                {t.appSubtitle}
              </span>
            </div>
          </Link>

          {/* Navigation Links (Responsive Horizontal Scrollable Pill Bar) */}
          <nav className="flex items-center space-x-1 overflow-x-auto py-1 no-scrollbar">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`inline-flex items-center px-3 py-2 text-xs rounded-xl transition-all shrink-0 ${
                    isActive
                      ? "bg-gradient-to-r from-teal-600 to-cyan-700 text-white font-bold shadow-sm"
                      : "text-[#243B53] hover:text-[#0A2540] hover:bg-[#EBF5F8] font-medium"
                  }`}
                >
                  <Icon className={`w-4 h-4 mr-1.5 ${isActive ? "text-teal-100" : "text-teal-600"}`} />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span
                      className={`ml-1.5 text-[9px] font-mono px-1.5 py-0.2 rounded-full font-bold ${
                        isActive
                          ? "bg-white/20 text-white"
                          : "bg-teal-50 text-teal-700 border border-teal-200"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}

