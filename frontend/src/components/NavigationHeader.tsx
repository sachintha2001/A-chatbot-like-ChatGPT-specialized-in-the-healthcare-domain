"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, Activity, Brain, BarChart3, Database, Globe, Layers, FileText, ClipboardList, CalendarCheck } from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";

export function NavigationHeader() {
  const pathname = usePathname();
  const { language, setLanguage, t } = useLanguage();

  const navLinks = [
    { href: "/", label: t.navTriage, icon: Activity },
    { href: "/reports", label: t.navReports, icon: FileText },
    { href: "/telemedicine", label: t.navTelemedicine, icon: CalendarCheck },
    { href: "/records", label: t.navRecords, icon: ClipboardList },
    { href: "/knowledge", label: t.navOntology, icon: Layers },
    { href: "/rlhf", label: t.navRLHF, icon: Brain },
    { href: "/analytics", label: t.navAnalytics, icon: BarChart3 },
    { href: "/evaluation", label: t.navEvaluation, icon: ShieldCheck },
    { href: "/fhir", label: t.navFHIR, icon: Database },
  ];

  return (
    <header className="border-b border-clinical-border bg-white sticky top-0 z-30 shadow-xs">
      {/* Top Clinical Compliance Ribbon */}
      <div className="bg-clinical-navy text-slate-300 text-xs px-4 py-1.5 flex justify-between items-center tracking-wide">
        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center font-semibold text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5 animate-pulse" />
            {t.hipaaActive}
          </span>
          <span className="text-slate-400">|</span>
          <span className="hidden md:inline">{t.phiScrubbedNotice}</span>
          <span className="text-slate-400 hidden md:inline">|</span>
          <span className="hidden sm:inline">{t.redFlagFilterStatus}</span>
        </div>
        <div className="flex items-center space-x-3">
          <span className="bg-slate-800 text-slate-200 px-2 py-0.5 rounded text-[11px] font-mono border border-slate-700 hidden sm:inline">
            {t.clinicianBadge}
          </span>

          {/* Language Switcher */}
          <div className="flex items-center bg-slate-800 rounded border border-slate-700 p-0.5 text-[11px]">
            <Globe className="w-3 h-3 text-slate-400 ml-1.5 mr-1" />
            <button
              onClick={() => setLanguage("en")}
              className={`px-2 py-0.5 rounded font-semibold transition-colors ${
                language === "en"
                  ? "bg-clinical-teal text-white shadow-xs"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage("si")}
              className={`px-2 py-0.5 rounded font-semibold transition-colors ${
                language === "si"
                  ? "bg-clinical-teal text-white shadow-xs"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              සිංහල
            </button>
          </div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded bg-clinical-teal flex items-center justify-center text-white font-bold text-lg shadow-sm">
                MG
              </div>
              <div>
                <span className="text-lg font-bold tracking-tight text-clinical-navy block leading-tight">
                  {t.appTitle}
                </span>
                <span className="text-[11px] text-clinical-muted uppercase tracking-wider font-medium block">
                  {t.appSubtitle}
                </span>
              </div>
            </Link>

            <nav className="hidden md:flex ml-10 space-x-1">
              {navLinks.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`inline-flex items-center px-3.5 py-2 text-xs font-medium rounded-md transition-colors ${
                      isActive
                        ? "bg-clinical-teal-light text-clinical-teal font-semibold border border-clinical-teal-border"
                        : "text-slate-600 hover:text-clinical-navy hover:bg-slate-100"
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-1.5" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <span className="hidden lg:inline text-slate-500 font-mono">
              {t.vectorIndexLabel}
            </span>
            <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded border border-slate-200 font-mono">
              {t.buildVersion}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
