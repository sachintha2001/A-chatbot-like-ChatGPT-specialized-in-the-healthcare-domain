"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  HeartPulse,
  ShieldCheck,
  Sparkles,
  FileText,
  CalendarCheck,
  Activity,
  Lock,
  Globe,
  CheckCircle2,
  ArrowRight,
  Download,
  Stethoscope,
  Layers,
  Database,
  Mic,
  Clock,
  Users,
  FileSpreadsheet,
  PhoneCall,
  Award,
  Zap
} from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";

interface CoverLandingPageProps {
  onEnterSystem: () => void;
}

export function CoverLandingPage({ onEnterSystem }: CoverLandingPageProps) {
  const { language, setLanguage } = useLanguage();
  const isSi = language === "si";
  const [isTransitioning, setIsTransitioning] = useState(false);

  const handleLaunchClick = () => {
    setIsTransitioning(true);
    setTimeout(() => {
      onEnterSystem();
    }, 550);
  };

  const customerBenefits = [
    {
      icon: Clock,
      badgeEn: "24/7 Instant Triage",
      badgeSi: "පැය 24 පුරා ක්ෂණික සේවාව",
      titleEn: "Immediate Clinical Guidance & Emergency Detection",
      titleSi: "ක්ෂණික වෛද්‍ය උපදෙස් සහ හදිසි රෝග තත්ත්ව හඳුනාගැනීම",
      descEn:
        "No waiting rooms for initial clinical clarity. Instantly screens for life-threatening emergencies (Heart Attack, Stroke, Severe Dengue, Anaphylaxis) with direct 1990 Suwa Seriya dispatch integration.",
      descSi:
        "රෝග ලක්ෂණ ඇති වූ වහාම නිවැරදි වෛද්‍ය මඟපෙන්වීමක් ලබාගන්න. හෘදයාබාධ, ආඝාතය (Stroke), දරුණු ඩෙංගු වැනි ජීවිත අවදානම් තත්ත්වයන් තත්පර කිහිපයකින් හඳුනාගෙන 1990 සුව සැරිය හදිසි සේවාව හා සම්බන්ධ කරයි."
    },
    {
      icon: FileSpreadsheet,
      badgeEn: "50+ Lab Biomarkers",
      badgeSi: "රසායනාගාර පරීක්ෂණ 50+",
      titleEn: "Plain-Language Lab Report Interpretation",
      titleSi: "රසායනාගාර වාර්තා සරල බසින් පැහැදිලි කිරීම",
      descEn:
        "Upload multi-page PDF health checkup booklets or camera photos (FBC, Lipid Profile, HbA1c, Renal/Liver panels, Dengue NS1). Understand every high/low value in clear English & Sinhala.",
      descSi:
        "රුධිර පරීක්ෂණ, කොලෙස්ටරෝල්, දියවැඩියා (HbA1c), වකුගඩු හා අක්මා වාර්තා හෝ පිටු ගණනාවක PDF වාර්තා උඩුගත කර, එහි ඇති සංකීර්ණ අගයන් සරල සිංහලෙන් සහ ඉංග්‍රීසියෙන් තේරුම් ගන්න."
    },
    {
      icon: CalendarCheck,
      badgeEn: "SLMC Specialists",
      badgeSi: "විශේෂඥ වෛද්‍ය හමුවීම්",
      titleEn: "Seamless Doctor Channeling & Clinical Handoff",
      titleSi: "ක්ෂණික විශේෂඥ වෛද්‍යවරුන් වෙන්කරවා ගැනීම (Telemedicine)",
      descEn:
        "Automatically recommends the right specialist department (Cardiologist, Hematologist, Endocrinologist) and connects with eChannelling, Doc990, and leading hospitals with your AI triage summary attached.",
      descSi:
        "ඔබේ රෝග ලක්ෂණ හෝ වාර්තාවට අදාළ විශේෂඥ වෛද්‍ය අංශය ස්වයංක්‍රීයව තෝරා දී, eChannelling හෝ Doc990 හරහා ක්ෂණිකව වෛද්‍ය හමුවක් වෙන්කරවා ගැනීමේ පහසුකම සලසයි."
    },
    {
      icon: Lock,
      badgeEn: "Zero-Trust DLP & HIPAA",
      badgeSi: "100% දත්ත ආරක්ෂාව",
      titleEn: "Zero Data Leaks & Anti-Malware Security Shield",
      titleSi: "දත්ත පිටතට යාම වළක්වන ඉහළම Zero-Trust ආරක්ෂාව",
      descEn:
        "Automatic HIPAA 18-identifier & Sri Lankan NIC/Phone scrubbing before any AI inference, backed by multi-layer anti-malware file inspection and a SHA-256 tamper-evident audit chain.",
      descSi:
        "ඔබේ නම, හැඳුනුම්පත් අංක (NIC), දුරකථන අංක ඇතුළු පෞද්ගලික තොරතුරු ස්වයංක්‍රීයව ඉවත් කරන (PHI Scrubbing) අතර, වෛරස් හා අනවසර ඇතුළුවීම් වළක්වන Zero-Trust ආරක්ෂණ පද්ධතියකින් සමන්විතයි."
    },
    {
      icon: Download,
      badgeEn: "Official A4 PDF",
      badgeSi: "නිල වෛද්‍ය PDF වාර්තාව",
      titleEn: "Downloadable Official Medical Assessment PDF",
      titleSi: "වෛද්‍යවරයා වෙත ගෙන යා හැකි නිල PDF සාරාංශ වාර්තාව",
      descEn:
        "Generate a verifiable, cryptographically stamped Medical Assessment PDF containing all analyzed biomarkers, ICD-11 codes, and clinical guidance to bring to your doctor or share via WhatsApp.",
      descSi:
        "පරීක්ෂා කළ සියලුම රසායනාගාර අගයන්, ICD-11 කේත සහ වෛද්‍ය නිර්දේශ ඇතුළත් නිල මුද්‍රාවක් සහිත PDF වාර්තාවක් බාගත කර වෛද්‍යවරයාට පෙන්වීමට හෝ WhatsApp මඟින් යැවීමට හැකිය."
    },
    {
      icon: Mic,
      badgeEn: "Sinhala / Singlish / Voice",
      badgeSi: "සිංහල, Singlish සහ හඬ",
      titleEn: "Natural Bilingual & Voice-Enabled Accessibility",
      titleSi: "සිංහල, Singlish සහ කටහඬ මඟින් පහසුවෙන් භාවිතා කිරීම",
      descEn:
        "Type or speak naturally in Sinhala, Singlish, or English—even with informal phrasing or spelling mistakes. Our Hybrid Cloud LLM + Clinical Rules Engine understands your exact clinical context.",
      descSi:
        "සිංහලෙන්, Singlish වලින් හෝ ඉංග්‍රීසියෙන් කතා කරමින් හෝ ටයිප් කරමින් ඕනෑම අයෙකුට ඉතා පහසුවෙන් භාවිතා කළ හැකි පරිදි නිර්මාණය කර ඇත."
    }
  ];

  const systemCapabilities = [
    {
      icon: Activity,
      titleEn: "1. AI Clinical Symptom Triage & Hybrid Cloud LLM",
      titleSi: "1. බුද්ධිමත් රෝග ලක්ෂණ පරීක්ෂාව සහ Hybrid Cloud LLM සංවාදය",
      featuresEn: [
        "Real-time streaming clinical conversation with deterministic red-flag guardrails",
        "Understands complex, ungrammatical Sinhala, Singlish & English patient descriptions",
        "Interactive clinical follow-up questions & citation-backed medical reasoning",
        "Hands-free Voice Dictation (STT) and Clinical Read-Aloud (TTS)"
      ],
      featuresSi: [
        "රෝග ලක්ෂණ පියවරෙන් පියවර විමසමින් සිදුකරන සජීවී වෛද්‍ය සංවාදය",
        "සංකීර්ණ හෝ ව්‍යාකරණ වැරදි සහිත සිංහල/Singlish ප්‍රකාශ නිවැරදිව තේරුම් ගැනීම",
        "හදිසි රෝග අවදානම් (Red-Flags) ක්ෂණිකව හඳුනාගැනීම සහ වෛද්‍ය මූලාශ්‍ර පෙන්වීම",
        "කටහඬින් රෝග ලක්ෂණ පැවසීම සහ පිළිතුරු වලට සවන් දීමේ හැකියාව"
      ],
      href: "/",
      isMainWorkspace: true,
      ctaEn: "Open AI Triage Chat",
      ctaSi: "රෝග පරීක්ෂණ සංවාදය අරඹන්න"
    },
    {
      icon: FileText,
      titleEn: "2. Multi-Page PDF & Camera Lab Report OCR Analyzer",
      titleSi: "2. බහු-පිටු PDF සහ රසායනාගාර වාර්තා ස්වයංක්‍රීය පරීක්ෂාව (OCR)",
      featuresEn: [
        "Batch Asynchronous OCR for 1-to-10 page scanned hospital checkup PDF booklets",
        "Direct camera snapshot & image upload (PNG/JPG/WebP) with magic-byte malware check",
        "Evaluates 50+ clinical biomarkers against age/sex reference intervals",
        "One-click 'Download Medical Assessment PDF' with official verification stamp"
      ],
      featuresSi: [
        "පිටු 10ක් දක්වා වූ සම්පූර්ණ Medical Checkup PDF වාර්තා තත්පර කිහිපයකින් කියවීම",
        "දුරකථන කැමරාවෙන් ගත් ඡායාරූප හෝ රූප ගොනු මඟින් වාර්තා පරීක්ෂා කිරීම",
        "රුධිර, කොලෙස්ටරෝල්, දියවැඩියා, වකුගඩු, අක්මා හා ඩෙංගු ඇතුළු පරීක්ෂණ 50+ විශ්ලේෂණය",
        "නිල මුද්‍රාවක් සහිත සම්පූර්ණ වෛද්‍ය සාරාංශ PDF වාර්තාවක් බාගත කිරීමේ පහසුකම"
      ],
      href: "/reports",
      isMainWorkspace: false,
      ctaEn: "Analyze Lab Reports",
      ctaSi: "රසායනාගාර වාර්තා පරීක්ෂා කරන්න"
    },
    {
      icon: Stethoscope,
      titleEn: "3. Telemedicine & SLMC Specialist Appointment Booking",
      titleSi: "3. විශේෂඥ වෛද්‍යවරුන් හමුවීම සහ වෙන්කරවා ගැනීම (Telemedicine)",
      featuresEn: [
        "Automated specialty matching (Cardiologist, Hematologist, Endocrinologist, General Physician)",
        "Browse verified SLMC-registered consultants across leading Sri Lankan hospitals",
        "Filter by Video Telemedicine or In-Person OPD visits via eChannelling & Doc990",
        "Attaches encrypted clinical triage & biomarker handoff directly to your booking"
      ],
      featuresSi: [
        "රෝග තත්ත්වයට අදාළ විශේෂඥ වෛද්‍ය අංශය ස්වයංක්‍රීයව නිර්දේශ කිරීම",
        "SLMC ලියාපදිංචි විශේෂඥ වෛද්‍යවරුන් සහ ප්‍රමුඛ රෝහල් පහසුවෙන් තෝරාගැනීම",
        "eChannelling සහ Doc990 හරහා Video හෝ රෝහල් හමුවීම් ක්ෂණිකව වෙන්කිරීම",
        "ඔබේ AI වෛද්‍ය සාරාංශය වෛද්‍යවරයා වෙත ස්වයංක්‍රීයව යොමු කිරීම"
      ],
      href: "/telemedicine",
      isMainWorkspace: false,
      ctaEn: "Book a Doctor Now",
      ctaSi: "වෛද්‍ය හමුවක් වෙන්කරන්න"
    },
    {
      icon: Users,
      titleEn: "4. Longitudinal Family Health Records (EHR) & Trends",
      titleSi: "4. පවුලේ සෞඛ්‍ය ඉතිහාසය සහ ප්‍රවණතා නිරීක්ෂණය (EHR)",
      featuresEn: [
        "Manage individual health profiles for yourself, parents, spouse, and children",
        "Interactive SVG sparklines tracking biomarker trajectories (Improving / Deteriorating)",
        "Track Dengue platelet recovery, HbA1c diabetes control & renal creatinine over time",
        "Document known drug allergies, blood group, and chronic conditions safely"
      ],
      featuresSi: [
        "ඔබගේ සහ පවුලේ සාමාජිකයන්ගේ සෞඛ්‍ය තොරතුරු වෙන වෙනම ආරක්ෂිතව පවත්වාගෙන යාම",
        "කාලයත් සමඟ රුධිර සීනි, කොලෙස්ටරෝල් හෝ ඩෙංගු පට්ටිකා වෙනස්වන ආකාරය ප්‍රස්තාර මඟින් බැලීම",
        "රෝග තත්ත්වය සුව අතට හැරේද නැතහොත් අවදානම්ද යන්න ගණිතමය ලෙස විශ්ලේෂණය කිරීම",
        "ඖෂධ ආසාත්මිකතා (Allergies) සහ නිදන්ගත රෝග පිළිබඳ අඛණ්ඩ වාර්තා තබාගැනීම"
      ],
      href: "/records",
      isMainWorkspace: false,
      ctaEn: "View Health Records",
      ctaSi: "සෞඛ්‍ය ඉතිහාසය බලන්න"
    },
    {
      icon: Layers,
      titleEn: "5. ICD-11 & SNOMED-CT Medical Ontology Explorer",
      titleSi: "5. ජාත්‍යන්තර වෛද්‍ය දැනුම් පද්ධතිය (ICD-11 & SNOMED-CT)",
      featuresEn: [
        "Search WHO ICD-11 disease classifications and SNOMED-CT clinical concepts",
        "Review evidence-based clinical triage protocols and differential criteria",
        "Inspect medication contraindications and clinical red-flag thresholds",
        "100% transparent, citation-grounded medical knowledge base"
      ],
      featuresSi: [
        "ලෝක සෞඛ්‍ය සංවිධානයේ (WHO) ICD-11 රෝග වර්ගීකරණ සහ සායනික නිර්ණායක පරීක්ෂාව",
        "සෑම රෝග තත්ත්වයකටම අදාළ වෛද්‍ය මාර්ගෝපදේශ සහ අවදානම් ලක්ෂණ බැලීම",
        "ඖෂධ අන්තර්ක්‍රියා සහ සායනික මූලාශ්‍ර විනිවිදභාවයෙන් යුතුව පරීක්ෂා කිරීම",
        "වෛද්‍ය සිසුන්ට, වෛද්‍යවරුන්ට සහ රෝගීන්ට විශ්වාසවන්ත මූලාශ්‍ර පද්ධතිය"
      ],
      href: "/knowledge",
      isMainWorkspace: false,
      ctaEn: "Explore Medical Knowledge",
      ctaSi: "වෛද්‍ය දැනුම ගවේෂණය කරන්න"
    },
    {
      icon: Database,
      titleEn: "6. HL7 FHIR R4 Interoperability & Clinical Safety Suite",
      titleSi: "6. HL7 FHIR R4 රෝහල් දත්ත හුවමාරුව සහ ආරක්ෂණ පද්ධතිය",
      featuresEn: [
        "Export standardized HL7 FHIR R4 JSON bundles compatible with hospital EHRs",
        "Clinician RLHF Review Queue for human-in-the-loop quality governance",
        "Adversarial Red-Team Safety Benchmarking & Real-Time Epidemiological Analytics",
        "Live Zero-Trust Security Center with 6-vector self-test verification"
      ],
      featuresSi: [
        "ජාත්‍යන්තර රෝහල් පද්ධති සමඟ ගැලපෙන HL7 FHIR R4 සම්මතයට දත්ත ලබාගැනීම",
        "වෛද්‍යවරුන් විසින් AI තීරණ අධීක්ෂණය කරන RLHF තත්ත්ව පාලන පද්ධතිය",
        "පද්ධතියේ ආරක්ෂාව තහවුරු කරන සජීවී Zero-Trust Security ස්වයං-පරීක්ෂාව",
        "සායනික දත්ත විශ්ලේෂණය සහ ආරක්ෂිත Audit Trail ලොග් සටහන්"
      ],
      href: "/fhir",
      isMainWorkspace: false,
      ctaEn: "Open FHIR & Governance",
      ctaSi: "FHIR සහ ආරක්ෂණ පද්ධතිය"
    }
  ];

  return (
    <div
      className={`min-h-screen bg-gradient-to-b from-[#EBF5F8] via-[#F4FAFC] to-white text-[#0A2540] transition-all duration-500 ${
        isTransitioning ? "opacity-0 scale-[0.985] blur-[2px]" : "opacity-100 scale-100"
      }`}
    >
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-[#CBE2EA] bg-gradient-to-br from-[#071A2E] via-[#0A2540] to-[#0D4A6B] text-white">
        {/* Ambient Clinical Grid & Glow */}
        <div
          className="absolute inset-0 opacity-15 pointer-events-none"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 25%, rgba(20, 184, 166, 0.45) 0%, transparent 45%), radial-gradient(circle at 80% 70%, rgba(14, 165, 233, 0.4) 0%, transparent 50%)"
          }}
        />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
          {/* Top Bar inside Cover Hero */}
          <div className="flex flex-wrap items-center justify-between gap-4 mb-10 pb-5 border-b border-white/10">
            <div className="flex items-center space-x-3">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-[#0D9488] via-[#0891B2] to-[#0284C7] flex items-center justify-center shadow-lg border border-teal-300/30">
                <HeartPulse className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-lg sm:text-xl font-extrabold tracking-tight text-white">
                    MedGuard Clinical AI
                  </span>
                </div>
                <p className="text-xs text-cyan-200/80">
                  {isSi
                    ? "ශ්‍රී ලංකාවේ විශේෂිත වෛද්‍ය AI රෝග විනිශ්චය, රසායනාගාර වාර්තා සහ Telemedicine පද්ධතිය"
                    : "Specialized Healthcare Clinical Decision Support, Lab OCR & Telemedicine Platform"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Language Switcher on Cover Page */}
              <div className="flex items-center bg-white/10 rounded-full border border-teal-400/30 p-1 text-xs">
                <Globe className="w-3.5 h-3.5 text-teal-300 ml-2 mr-1.5" />
                <button
                  type="button"
                  onClick={() => setLanguage("en")}
                  className={`px-3 py-1 rounded-full font-bold transition-all cursor-pointer ${
                    language === "en"
                      ? "bg-gradient-to-r from-teal-500 to-cyan-500 text-white shadow-xs"
                      : "text-slate-200 hover:text-white"
                  }`}
                >
                  English
                </button>
                <button
                  type="button"
                  onClick={() => setLanguage("si")}
                  className={`px-3 py-1 rounded-full font-bold transition-all cursor-pointer ${
                    language === "si"
                      ? "bg-gradient-to-r from-teal-500 to-cyan-500 text-white shadow-xs"
                      : "text-slate-200 hover:text-white"
                  }`}
                >
                  සිංහල
                </button>
              </div>

              <button
                type="button"
                onClick={handleLaunchClick}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-extrabold bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-md transition-all cursor-pointer"
              >
                <span>{isSi ? "පද්ධතියට පිවිසෙන්න" : "Enter System"}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Main Hero Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex flex-wrap items-center gap-2 px-3.5 py-1.5 rounded-full bg-teal-500/15 border border-teal-400/30 text-teal-200 text-xs font-semibold">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>
                  {isSi
                    ? "100% ආරක්ෂිත වෛද්‍ය AI පද්ධතිය • HIPAA සහ Zero-Trust ආරක්ෂාව සහිතයි"
                    : "Zero-Trust Medical AI • HIPAA Safe-Harbor & SLMC Telemedicine Ready"}
                </span>
              </div>

              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight leading-[1.15] text-white">
                {isSi ? (
                  <>
                    ඔබේත් පවුලේත් සෞඛ්‍ය ආරක්ෂාව සඳහා නිර්මාණය කළ{" "}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-300 via-cyan-300 to-emerald-300">
                      බුද්ධිමත් වෛද්‍ය AI සහායකයා
                    </span>
                  </>
                ) : (
                  <>
                    Intelligent Clinical Triage, Lab Report OCR &{" "}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-300 via-cyan-300 to-emerald-300">
                      Specialist Telemedicine
                    </span>
                  </>
                )}
              </h1>

              <p className="text-sm sm:text-base text-cyan-100/90 leading-relaxed max-w-2xl">
                {isSi
                  ? "රෝග ලක්ෂණ පරීක්ෂා කර ගැනීමට, පිටු ගණනාවක රසායනාගාර වාර්තා (Lab Reports) සරල සිංහලෙන් තේරුම් ගැනීමට, නිල වෛද්‍ය සාරාංශ PDF වාර්තාවක් ලබා ගැනීමට සහ අදාළ විශේෂඥ වෛද්‍යවරයා ක්ෂණිකව වෙන්කරවා ගැනීමට (eChannelling / Doc990) එක් ස්ථානයකින් පහසුකම් සලසයි."
                  : "Experience hospital-grade clinical symptom triage, instant multi-page PDF lab report analysis across 50+ biomarkers, official downloadable medical assessment reports, and direct SLMC specialist appointment booking in one unified platform."}
              </p>

              {/* Primary CTA Button Group */}
              <div className="pt-2 flex flex-wrap items-center gap-4">
                <button
                  type="button"
                  onClick={handleLaunchClick}
                  className="group relative inline-flex items-center gap-3 px-7 py-4 rounded-2xl text-sm sm:text-base font-extrabold text-white bg-gradient-to-r from-[#0D9488] via-[#0891B2] to-[#0284C7] hover:from-[#14B8A6] hover:to-[#0284C7] shadow-xl shadow-teal-950/50 border border-teal-300/40 transition-all duration-300 hover:scale-[1.02] active:scale-[0.99] cursor-pointer"
                >
                  <Sparkles className="w-5 h-5 text-emerald-300 animate-pulse" />
                  <span>
                    {isSi
                      ? "වෛද්‍ය AI පද්ධතිය ආරම්භ කරන්න (Launch Clinical System)"
                      : "Launch Clinical AI System"}
                  </span>
                  <span className="w-7 h-7 rounded-xl bg-white/20 flex items-center justify-center group-hover:translate-x-1 transition-transform">
                    <ArrowRight className="w-4 h-4 text-white" />
                  </span>
                </button>

                <Link
                  href="/reports"
                  className="inline-flex items-center gap-2 px-5 py-4 rounded-2xl text-xs sm:text-sm font-bold text-cyan-100 bg-white/10 hover:bg-white/20 border border-white/20 transition-all"
                >
                  <FileText className="w-4 h-4 text-teal-300" />
                  <span>{isSi ? "රසායනාගාර වාර්තා පරීක්ෂාව (Lab OCR)" : "Analyze Lab Report PDF"}</span>
                </Link>

                <Link
                  href="/telemedicine"
                  className="inline-flex items-center gap-2 px-5 py-4 rounded-2xl text-xs sm:text-sm font-bold text-cyan-100 bg-white/10 hover:bg-white/20 border border-white/20 transition-all"
                >
                  <CalendarCheck className="w-4 h-4 text-emerald-300" />
                  <span>{isSi ? "වෛද්‍ය හමුවක් වෙන්කරන්න" : "Book SLMC Doctor"}</span>
                </Link>
              </div>

              {/* Trust Metrics Strip */}
              <div className="pt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-white/10 backdrop-blur-xs border border-white/15 rounded-xl p-3">
                  <div className="text-lg sm:text-xl font-extrabold text-teal-300 font-mono">50+</div>
                  <div className="text-[11px] text-cyan-100/80 font-medium">
                    {isSi ? "රසායනාගාර දර්ශක (Biomarkers)" : "Verified Lab Biomarkers"}
                  </div>
                </div>
                <div className="bg-white/10 backdrop-blur-xs border border-white/15 rounded-xl p-3">
                  <div className="text-lg sm:text-xl font-extrabold text-emerald-300 font-mono">100%</div>
                  <div className="text-[11px] text-cyan-100/80 font-medium">
                    {isSi ? "PHI දත්ත රහස්‍යභාවය" : "PHI Scrubbed & Encrypted"}
                  </div>
                </div>
                <div className="bg-white/10 backdrop-blur-xs border border-white/15 rounded-xl p-3">
                  <div className="text-lg sm:text-xl font-extrabold text-cyan-300 font-mono">ICD-11</div>
                  <div className="text-[11px] text-cyan-100/80 font-medium">
                    {isSi ? "ලෝක සෞඛ්‍ය සංවිධාන ප්‍රමිතිය" : "WHO & SNOMED-CT Grounded"}
                  </div>
                </div>
                <div className="bg-white/10 backdrop-blur-xs border border-white/15 rounded-xl p-3">
                  <div className="text-lg sm:text-xl font-extrabold text-amber-300 font-mono">24/7</div>
                  <div className="text-[11px] text-cyan-100/80 font-medium">
                    {isSi ? "සිංහල සහ English සහාය" : "Bilingual Sinhala & English"}
                  </div>
                </div>
              </div>
            </div>

            {/* Right Interactive Preview Card */}
            <div className="lg:col-span-5">
              <div className="bg-white/95 text-[#0A2540] rounded-3xl p-6 shadow-2xl border border-teal-300/40 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-200 pb-3.5">
                  <div className="flex items-center gap-2.5">
                    <span className="w-9 h-9 rounded-xl bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center">
                      <Activity className="w-5 h-5" />
                    </span>
                    <div>
                      <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#0A2540]">
                        {isSi ? "සජීවී සායනික හැකියාවන්" : "Live Clinical Capabilities"}
                      </h3>
                      <p className="text-[11px] text-slate-500">
                        {isSi ? "එක් ක්ලික් කිරීමකින් ක්‍රියාත්මක වේ" : "All-in-one Healthcare Intelligence"}
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                    ONLINE
                  </span>
                </div>

                {/* Biometric ECG Waveform SVG */}
                <div className="bg-[#0A2540] rounded-2xl p-3.5 text-white border border-teal-500/30">
                  <div className="flex items-center justify-between text-[11px] text-teal-300 font-mono mb-1">
                    <span>CDSS BIOMETRIC MONITOR</span>
                    <span>ZERO-TRUST SHIELD ACTIVE</span>
                  </div>
                  <svg viewBox="0 0 400 56" className="w-full h-12 overflow-visible">
                    <path
                      d="M 0 28 L 70 28 L 85 18 L 100 36 L 118 6 L 135 50 L 152 22 L 170 28 L 250 28 L 265 18 L 280 36 L 298 6 L 315 50 L 332 22 L 350 28 L 400 28"
                      fill="none"
                      stroke="#2DD4BF"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>

                {/* Quick Checklist of What Customers Get */}
                <div className="space-y-2.5 text-xs">
                  <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-[#F4FAFC] border border-[#CBE2EA]">
                    <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-[#0A2540] block">
                        {isSi
                          ? "රෝග ලක්ෂණ අනුව ක්ෂණික වෛද්‍ය මඟපෙන්වීම"
                          : "AI Symptom Triage & Emergency Guardrails"}
                      </span>
                      <span className="text-slate-600 text-[11px]">
                        {isSi
                          ? "සිංහල, Singlish හෝ ඉංග්‍රීසි බසින් ඔබේ රෝග ලක්ෂණ පවසා නිවැරදි උපදෙස් ලබාගන්න."
                          : "Describe symptoms in English, Sinhala, or Singlish for citation-backed guidance."}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-[#F4FAFC] border border-[#CBE2EA]">
                    <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-[#0A2540] block">
                        {isSi
                          ? "පිටු 10ක් දක්වා PDF රසායනාගාර වාර්තා කියවීම"
                          : "Multi-Page PDF Lab Booklet OCR & Official PDF Report"}
                      </span>
                      <span className="text-slate-600 text-[11px]">
                        {isSi
                          ? "සම්පූර්ණ වාර්තා පොත් එකවර ස්කෑන් කර නිල PDF සාරාංශ වාර්තාවක් බාගත කරගන්න."
                          : "Batch-scan full checkup PDFs and download a stamped Medical Assessment PDF."}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-start gap-2.5 p-2.5 rounded-xl bg-[#F4FAFC] border border-[#CBE2EA]">
                    <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-[#0A2540] block">
                        {isSi
                          ? "විශේෂඥ වෛද්‍යවරුන් ක්ෂණිකව වෙන්කරවා ගැනීම"
                          : "Direct SLMC Specialist Booking (eChannelling / Doc990)"}
                      </span>
                      <span className="text-slate-600 text-[11px]">
                        {isSi
                          ? "නිර්දේශිත විශේෂඥ වෛද්‍යවරයා තෝරා එසැනින් වේලාවක් වෙන්කරවා ගන්න."
                          : "Auto-matched specialist routing with one-click appointment confirmation."}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleLaunchClick}
                  className="w-full py-3.5 px-5 rounded-xl font-extrabold text-xs sm:text-sm text-white bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0D9488] hover:from-[#0D9488] hover:to-[#0284C7] shadow-md flex items-center justify-center gap-2 transition-all cursor-pointer"
                >
                  <span>
                    {isSi
                      ? "දැන්ම පද්ධතියට පිවිසෙන්න (Enter Clinical Workspace)"
                      : "Enter Clinical Workspace Now"}
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 1: Customer & Patient Benefits */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="text-center max-w-3xl mx-auto mb-10">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider bg-teal-50 text-teal-700 border border-teal-200">
            <Award className="w-3.5 h-3.5" />
            {isSi ? "පාරිභෝගිකයන්ට ලැබෙන ප්‍රතිලාභ" : "Customer & Patient Benefits"}
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-[#0A2540] mt-3">
            {isSi
              ? "මෙම පද්ධතිය මඟින් ඔබට සහ රෝගීන්ට ලැබෙන සුවිශේෂී ප්‍රතිලාභ"
              : "Why Patients, Families & Clinics Choose MedGuard AI"}
          </h2>
          <p className="text-xs sm:text-sm text-[#486581] mt-2 leading-relaxed">
            {isSi
              ? "සාමාන්‍ය Chatbot එකකින් ඔබ්බට ගිය, සායනික නීතිරීති (Clinical Rules), ලෝක සෞඛ්‍ය සංවිධානයේ ICD-11 ප්‍රමිතීන් සහ ඉහළම දත්ත ආරක්ෂාව සහිත පූර්ණ වෛද්‍ය සහායක පද්ධතියකි."
              : "Designed specifically for healthcare accuracy, patient empowerment, and zero-trust medical privacy."}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {customerBenefits.map((benefit, idx) => {
            const IconComponent = benefit.icon;
            return (
              <div
                key={idx}
                className="bg-white border border-[#CBE2EA] rounded-2xl p-6 shadow-clinical-card hover:shadow-lg hover:border-teal-400 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-4">
                    <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-teal-50 to-cyan-50 border border-teal-200 text-[#0D9488] flex items-center justify-center">
                      <IconComponent className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-[#F0F9FF] text-[#0284C7] border border-sky-200">
                      {isSi ? benefit.badgeSi : benefit.badgeEn}
                    </span>
                  </div>
                  <h3 className="text-base font-extrabold text-[#0A2540] mb-2">
                    {isSi ? benefit.titleSi : benefit.titleEn}
                  </h3>
                  <p className="text-xs text-[#486581] leading-relaxed">
                    {isSi ? benefit.descSi : benefit.descEn}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Section 2: Complete System Capabilities (What You Can Do) */}
      <section className="bg-[#EBF5F8]/70 border-y border-[#CBE2EA] py-14">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider bg-cyan-50 text-cyan-800 border border-cyan-200">
              <Zap className="w-3.5 h-3.5 text-teal-600" />
              {isSi ? "පද්ධතියෙන් කළ හැකි දේවල්" : "Complete System Capabilities"}
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#0A2540] mt-3">
              {isSi
                ? "මෙම වෛද්‍ය පද්ධතිය හරහා ඔබට සිදුකරගත හැකි සේවාවන්"
                : "Everything You Can Do Inside MedGuard Clinical AI"}
            </h2>
            <p className="text-xs sm:text-sm text-[#486581] mt-2">
              {isSi
                ? "ඕනෑම සේවාවක් මත ක්ලික් කර සෘජුවම එම අංශයට පිවිසිය හැකිය."
                : "Explore our 6 integrated clinical modules built for patients and healthcare professionals."}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {systemCapabilities.map((cap, idx) => {
              const IconComponent = cap.icon;
              const features = isSi ? cap.featuresSi : cap.featuresEn;
              return (
                <div
                  key={idx}
                  className="bg-white border border-[#CBE2EA] rounded-2xl p-6 shadow-clinical-card hover:border-teal-500 transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start gap-3.5 mb-4">
                      <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-[#0A2540] to-[#0D9488] text-white flex items-center justify-center shrink-0 shadow-xs">
                        <IconComponent className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="text-base font-extrabold text-[#0A2540]">
                          {isSi ? cap.titleSi : cap.titleEn}
                        </h3>
                      </div>
                    </div>

                    <ul className="space-y-2 mb-5">
                      {features.map((feat, fIdx) => (
                        <li key={fIdx} className="flex items-start gap-2 text-xs text-[#334E68]">
                          <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
                          <span>{feat}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-end">
                    {cap.isMainWorkspace ? (
                      <button
                        type="button"
                        onClick={handleLaunchClick}
                        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-extrabold text-white bg-gradient-to-r from-[#0D9488] to-[#0284C7] hover:from-[#0F766E] hover:to-[#0369A1] shadow-xs transition-all cursor-pointer"
                      >
                        <span>{isSi ? cap.ctaSi : cap.ctaEn}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    ) : (
                      <Link
                        href={cap.href}
                        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-extrabold text-[#0A2540] bg-[#F0F9FF] hover:bg-teal-600 hover:text-white border border-sky-200 transition-all"
                      >
                        <span>{isSi ? cap.ctaSi : cap.ctaEn}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Section 3: 3-Step Workflow & Final Launch CTA Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 space-y-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-[#CBE2EA] rounded-2xl p-5 text-center shadow-xs">
            <div className="w-10 h-10 mx-auto rounded-full bg-teal-600 text-white font-extrabold text-sm flex items-center justify-center mb-3">
              1
            </div>
            <h3 className="text-sm font-extrabold text-[#0A2540]">
              {isSi
                ? "රෝග ලක්ෂණ පවසන්න හෝ වාර්තාව Upload කරන්න"
                : "Describe Symptoms or Upload Lab PDF"}
            </h3>
            <p className="text-xs text-[#486581] mt-1.5">
              {isSi
                ? "සිංහල/ඉංග්‍රීසි බසින් රෝග ලක්ෂණ ඇතුළත් කරන්න නැතහොත් ඔබේ රසායනාගාර වාර්තාව (PDF/Photo) උඩුගත කරන්න."
                : "Chat in English, Sinhala, or Singlish, or upload a 1-to-10 page lab report PDF/photo."}
            </p>
          </div>

          <div className="bg-white border border-[#CBE2EA] rounded-2xl p-5 text-center shadow-xs">
            <div className="w-10 h-10 mx-auto rounded-full bg-cyan-600 text-white font-extrabold text-sm flex items-center justify-center mb-3">
              2
            </div>
            <h3 className="text-sm font-extrabold text-[#0A2540]">
              {isSi
                ? "AI වෛද්‍ය විශ්ලේෂණය සහ නිල PDF වාර්තාව ලබාගන්න"
                : "Receive AI Clinical Analysis & Official PDF"}
            </h3>
            <p className="text-xs text-[#486581] mt-1.5">
              {isSi
                ? "අසාමාන්‍ය අගයන්, ICD-11 කේත සහ වෛද්‍ය උපදෙස් සහිත නිල PDF වාර්තාව ක්ෂණිකව බාගත කරගන්න."
                : "Review biomarker status, triage severity, and download your stamped Medical Assessment PDF."}
            </p>
          </div>

          <div className="bg-white border border-[#CBE2EA] rounded-2xl p-5 text-center shadow-xs">
            <div className="w-10 h-10 mx-auto rounded-full bg-emerald-600 text-white font-extrabold text-sm flex items-center justify-center mb-3">
              3
            </div>
            <h3 className="text-sm font-extrabold text-[#0A2540]">
              {isSi
                ? "නිර්දේශිත විශේෂඥ වෛද්‍යවරයා වෙන්කරවා ගන්න"
                : "Book the Recommended SLMC Specialist"}
            </h3>
            <p className="text-xs text-[#486581] mt-1.5">
              {isSi
                ? "එකම ක්ලික් කිරීමකින් eChannelling / Doc990 හරහා අදාළ විශේෂඥ වෛද්‍යවරයා වෙන්කරවා ගන්න."
                : "Connect directly with SLMC specialists via eChannelling or Doc990 with your clinical summary."}
            </p>
          </div>
        </div>

        {/* Bottom CTA Banner */}
        <div className="rounded-3xl bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0D9488] p-8 sm:p-10 text-white shadow-xl flex flex-col lg:flex-row items-center justify-between gap-6">
          <div className="space-y-2 text-center lg:text-left max-w-2xl">
            <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-teal-300">
              <HeartPulse className="w-4 h-4" />
              {isSi ? "දැන්ම ආරම්භ කරන්න" : "Ready for Clinical Consultation"}
            </span>
            <h3 className="text-xl sm:text-2xl font-extrabold">
              {isSi
                ? "ඔබේ සෞඛ්‍ය පරීක්ෂාව ආරක්ෂිතව ආරම්භ කිරීමට සූදානම්ද?"
                : "Ready to Start Your Clinical AI Consultation?"}
            </h3>
            <p className="text-xs sm:text-sm text-cyan-100/90">
              {isSi
                ? "පහත බොත්තම ක්ලික් කර ප්‍රධාන වෛද්‍ය AI පද්ධතියට (Clinical Triage System) පිවිසෙන්න."
                : "Click the button to smoothly transition into the interactive Clinical AI Triage & Diagnostic Workspace."}
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 shrink-0">
            <button
              type="button"
              onClick={handleLaunchClick}
              className="inline-flex items-center gap-2.5 px-7 py-4 rounded-2xl text-sm sm:text-base font-extrabold bg-white text-[#0A2540] hover:bg-teal-50 shadow-lg transition-all hover:scale-105 cursor-pointer"
            >
              <span>
                {isSi ? "වෛද්‍ය පද්ධතියට පිවිසෙන්න (Enter System)" : "Enter Clinical AI System"}
              </span>
              <ArrowRight className="w-4 h-4 text-teal-700" />
            </button>
            <a
              href="tel:1990"
              className="inline-flex items-center gap-2 px-4 py-4 rounded-2xl text-xs font-bold bg-rose-600/90 hover:bg-rose-500 text-white transition-colors"
            >
              <PhoneCall className="w-4 h-4" />
              <span>1990 Suwa Seriya</span>
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
