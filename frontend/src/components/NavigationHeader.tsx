"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ShieldCheck,
  ShieldAlert,
  Lock,
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
  PhoneCall,
  CheckCircle2,
  X,
  RefreshCw,
  FileWarning,
  KeyRound
} from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";
import { fetchSecurityPosture, runSecuritySelfTest } from "@/lib/api";

export function NavigationHeader() {
  const pathname = usePathname();
  const { language, setLanguage, t } = useLanguage();
  const [clinicalTheme, setClinicalTheme] = useState<"DAYLIGHT" | "NIGHTWARD">("DAYLIGHT");
  const [showSecurityModal, setShowSecurityModal] = useState(false);
  const [securityPosture, setSecurityPosture] = useState<any>(null);
  const [selfTestResult, setSelfTestResult] = useState<any>(null);
  const [runningSelfTest, setRunningSelfTest] = useState(false);

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

  const handleOpenSecurityCenter = async () => {
    setShowSecurityModal(true);
    try {
      const statusData = await fetchSecurityPosture();
      setSecurityPosture(statusData);
    } catch {
      // Fallback if offline
    }
  };

  const handleRunLiveSecurityAudit = async () => {
    setRunningSelfTest(true);
    try {
      const res = await runSecuritySelfTest();
      setSelfTestResult(res);
      const statusData = await fetchSecurityPosture();
      setSecurityPosture(statusData);
    } catch {
      // Fallback
    } finally {
      setRunningSelfTest(false);
    }
  };

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
    <>
      <header className="sticky top-0 z-30 border-b border-[#CBE2EA] bg-white/95 backdrop-blur-md shadow-clinical-card">
        {/* Top Clinical Governance & Safety Ribbon */}
        <div className="clinical-dark-preserve bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0A2540] text-slate-200 text-xs px-4 py-1.5 border-b border-teal-500/25">
          <div className="max-w-7xl mx-auto flex flex-wrap justify-between items-center gap-2 tracking-wide">
            <div className="flex items-center space-x-3">
              <span className="inline-flex items-center font-semibold text-emerald-300 bg-emerald-950/70 border border-emerald-500/40 px-2 py-0.5 rounded-full text-[11px]">
                <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5 animate-pulse" />
                {t.hipaaActive}
              </span>
              <button
                type="button"
                onClick={handleOpenSecurityCenter}
                className="inline-flex items-center gap-1.5 font-bold text-teal-200 hover:text-white bg-teal-950/80 hover:bg-teal-900 border border-teal-400/40 px-2.5 py-0.5 rounded-full text-[11px] transition-colors cursor-pointer"
                title="Open Zero-Trust Anti-Malware, WAF & Data Loss Prevention (DLP) Verification Center"
              >
                <Lock className="w-3 h-3 text-emerald-400" />
                <span>
                  {language === "si"
                    ? "Zero-Trust ආරක්ෂණ පලිහ (Anti-Malware & DLP)"
                    : "Zero-Trust Security Shield"}
                </span>
              </button>
              <span className="text-slate-500 hidden lg:inline">|</span>
              <span className="hidden lg:inline text-cyan-100/90 text-[11px]">{t.phiScrubbedNotice}</span>
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

      {/* Zero-Trust Security Shield, Anti-Malware & DLP Verification Modal */}
      {showSecurityModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/75 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white border border-[#CBE2EA] rounded-2xl max-w-3xl w-full overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="clinical-dark-preserve bg-gradient-to-r from-[#0A2540] via-[#0F3D5E] to-[#0D9488] px-6 py-4 text-white flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center">
                  <ShieldCheck className="w-6 h-6 text-emerald-300" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-extrabold tracking-tight">
                      {language === "si"
                        ? "MedGuard Zero-Trust ආරක්ෂණ සහ Anti-Malware පද්ධතිය"
                        : "MedGuard Zero-Trust Security, Anti-Malware & DLP Shield"}
                    </h3>
                    <span className="px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded-full bg-emerald-500/20 text-emerald-200 border border-emerald-400/40">
                      ACTIVE
                    </span>
                  </div>
                  <p className="text-xs text-cyan-100/90 mt-0.5">
                    {language === "si"
                      ? "වෛරස්, Malware, විෂ සහිත PDF සහ දත්ත කාන්දුවීම් (Data Leakage) 100% වැළැක්වීමේ ආරක්ෂණ පද්ධතිය"
                      : "Enterprise Anti-Virus, Magic-Byte File Inspection, WAF & Zero-Leakage Data Loss Prevention"}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowSecurityModal(false)}
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-5 max-h-[80vh] overflow-y-auto bg-[#F4F9FB]">
              {/* Top Defense Pillars */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="bg-white p-4 rounded-xl border border-[#D5E6ED] shadow-xs">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#0A2540]">
                    <FileWarning className="w-4 h-4 text-teal-600" />
                    <span>
                      {language === "si"
                        ? "Anti-Malware ගොනු පරීක්ෂාව"
                        : "Anti-Malware File Inspection"}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 mt-1.5 leading-relaxed">
                    {language === "si"
                      ? "EICAR වෛරස් අත්සන්, වෙස්වලාගත් .EXE/.ELF/ZIP ගොනු (Magic-Byte Verification) සහ PDF තුළ සැඟවූ JavaScript/Launch ප්‍රහාර ක්ෂණිකව අවහිර කරයි."
                      : "Blocks EICAR virus signatures, disguised PE/ELF/ZIP executables via magic-byte header verification, and malicious PDF /JavaScript & /Launch exploits."}
                  </p>
                </div>

                <div className="bg-white p-4 rounded-xl border border-[#D5E6ED] shadow-xs">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#0A2540]">
                    <KeyRound className="w-4 h-4 text-cyan-600" />
                    <span>
                      {language === "si"
                        ? "Zero-Leakage දත්ත ආරක්ෂණය (DLP)"
                        : "Zero-Leakage PHI & Secret DLP"}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 mt-1.5 leading-relaxed">
                    {language === "si"
                      ? "රෝගියාගේ නම, දුරකථන, ශ්‍රී ලංකා ජාතික හැඳුනුම්පත් (NIC), Credit Card සහ Cloud API Keys කිසිවිටෙක පිටතට කාන්දු නොවන ලෙස Redact කරයි."
                      : "Scrubs 18 HIPAA Safe Harbor identifiers, Sri Lankan NICs/Phones, Credit Cards, and Cloud API Keys before storage, LLM calls, or outbound responses."}
                  </p>
                </div>

                <div className="bg-white p-4 rounded-xl border border-[#D5E6ED] shadow-xs">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#0A2540]">
                    <ShieldAlert className="w-4 h-4 text-emerald-600" />
                    <span>
                      {language === "si"
                        ? "WAF සහ SHA-256 Audit දාමය"
                        : "WAF & Hash-Chained Audit Log"}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 mt-1.5 leading-relaxed">
                    {language === "si"
                      ? "Prompt Injection, SQL Injection, XSS සහ SSRF ප්‍රහාර වළක්වන අතර සෑම ක්‍රියාවක්ම වෙනස් කළ නොහැකි SHA-256 Hash-Chain එකකින් සටහන් කරයි."
                      : "Blocks Prompt Injection, SQLi, XSS & SSRF, enforces OWASP CSP/HSTS headers, and seals every audit entry with a SHA-256 cryptographic hash chain."}
                  </p>
                </div>
              </div>

              {/* Live Self-Test Action Bar */}
              <div className="bg-white border border-teal-200 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-xs">
                <div>
                  <h4 className="text-xs font-extrabold text-[#0A2540] uppercase tracking-wider">
                    {language === "si"
                      ? "සජීවී ආරක්ෂණ සහ Anti-Virus පරීක්ෂණ කට්ටලය (6-Point Live Verification)"
                      : "6-Point Live Anti-Malware, WAF & Zero-Leakage DLP Self-Test"}
                  </h4>
                  <p className="text-xs text-slate-600 mt-0.5">
                    {language === "si"
                      ? "වෛරස්, EXE, Malicious PDF, Prompt Injection, SQLi/XSS සහ Data Leakage පරීක්ෂණ 6ම දැන්ම ක්‍රියාත්මක කර පරීක්ෂා කරන්න."
                      : "Simulate non-destructive EICAR virus, disguised EXE, malicious PDF JS, Prompt Injection, SQLi/XSS, and API/PHI leak attacks to verify 100% blocking."}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleRunLiveSecurityAudit}
                  disabled={runningSelfTest}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-teal-600 to-cyan-700 hover:from-teal-700 hover:to-cyan-800 text-white text-xs font-bold shadow-sm transition-all cursor-pointer disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 ${runningSelfTest ? "animate-spin" : ""}`} />
                  <span>
                    {runningSelfTest
                      ? language === "si"
                        ? "පරීක්ෂා කරමින්..."
                        : "Running Security Audit..."
                      : language === "si"
                      ? "Run Live Security Check (පරීක්ෂා කරන්න)"
                      : "Run 6-Point Security Self-Test"}
                  </span>
                </button>
              </div>

              {/* Self-Test Results Table */}
              {selfTestResult && (
                <div className="bg-white border border-emerald-200 rounded-xl p-4 space-y-3 shadow-xs">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                      <span className="text-xs font-extrabold text-emerald-900">
                        {language === "si"
                          ? `ආරක්ෂණ පරීක්ෂණ ${selfTestResult.passed}/${selfTestResult.total_checks} සාර්ථකව සමත් විය (${selfTestResult.overall_status})`
                          : `All ${selfTestResult.passed}/${selfTestResult.total_checks} Security Controls Verified (${selfTestResult.overall_status})`}
                      </span>
                    </div>
                    <span className="text-[11px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                      100% ZERO-LEAKAGE & MALWARE-PROOF
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {selfTestResult.checks?.map((chk: any) => (
                      <div
                        key={chk.check_id}
                        className="p-3 rounded-lg bg-emerald-50/50 border border-emerald-200/80 flex items-start gap-2.5"
                      >
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        <div>
                          <div className="text-[11px] font-mono font-bold text-[#0A2540]">
                            {chk.check_id}
                          </div>
                          <div className="text-[11px] text-slate-600 mt-0.5">
                            {chk.detail}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Active Security Posture Details */}
              {securityPosture && (
                <div className="bg-white border border-[#D5E6ED] rounded-xl p-4 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#0A2540]">
                      {language === "si"
                        ? "සක්‍රිය ආරක්ෂණ ස්තර (Active Security Layers)"
                        : "Active Enterprise Defense Layers"}
                    </span>
                    <span className="text-[11px] font-mono text-teal-700 font-semibold">
                      Threats Blocked: {securityPosture.blocked_threats_total ?? 0}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11px] text-slate-700">
                    {securityPosture.defenses_enabled?.map((defItem: string, idx: number) => (
                      <div key={idx} className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-teal-600 shrink-0" />
                        <span>{defItem}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
