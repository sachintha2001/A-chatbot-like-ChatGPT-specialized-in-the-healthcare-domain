"use client";

import { useState, useEffect, useRef } from "react";
import {
  Send,
  ShieldCheck,
  AlertCircle,
  RotateCcw,
  BookOpen,
  User,
  HeartPulse,
  Activity
} from "lucide-react";
import {
  TriageSession,
  TriageMessage,
  ClinicalCitation,
  TriageSeverity
} from "@/lib/types";
import { initializeTriageSession, submitTriagePrompt } from "@/lib/api";
import { ConsentModal } from "@/components/ConsentModal";
import { EmergencyBanner } from "@/components/EmergencyBanner";
import { CitationDrawer } from "@/components/CitationDrawer";
import { useLanguage } from "@/lib/LanguageContext";

export default function ClinicalTriagePage() {
  const { language, t } = useLanguage();
  const [session, setSession] = useState<TriageSession | null>(null);
  const [messages, setMessages] = useState<TriageMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [isConsentOpen, setIsConsentOpen] = useState(false);
  const [activeCitation, setActiveCitation] = useState<ClinicalCitation | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!session) {
      setIsConsentOpen(true);
    }
  }, [session]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleConsentConfirm = async (ageGroup: string, sex: string) => {
    const newSession = await initializeTriageSession({
      patient_age_group: ageGroup,
      biological_sex: sex,
      consent_acknowledged: true,
      disclaimer_acknowledged: true
    });
    setSession(newSession);
    setIsConsentOpen(false);
    setMessages([]);
  };

  const handleSendMessage = async (customText?: string) => {
    const textToSend = customText || inputText;
    if (!textToSend.trim() || !session || loading) return;

    setInputText("");
    setErrorMessage(null);
    setLoading(true);

    // Optimistically add patient narrative message
    const tempPatientMsg: TriageMessage = {
      message_id: `temp-${Date.now()}`,
      session_id: session.session_id,
      sender_role: "PATIENT",
      redacted_content: textToSend,
      clinical_citations: [],
      retrieval_similarity_score: 1.0,
      groundedness_score: 1.0,
      latency_ms: 0,
      safety_check_passed: true,
      triage_severity: session.triage_severity,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempPatientMsg]);

    try {
      const response = await submitTriagePrompt({
        session_id: session.session_id,
        prompt_text: textToSend,
        language: language
      });

      if (response.triage_severity !== session.triage_severity) {
        setSession((prev) => prev ? { ...prev, triage_severity: response.triage_severity } : null);
      }

      setMessages((prev) => [...prev, response]);
    } catch (err: any) {
      setErrorMessage(err.message || "An unexpected error occurred during clinical evaluation.");
    } finally {
      setLoading(false);
    }
  };

  const resetSession = () => {
    setSession(null);
    setMessages([]);
    setIsConsentOpen(true);
  };

  const renderContentWithCitationBadges = (content: string, citations: ClinicalCitation[]) => {
    const parts = content.split(/(\[Ref\s*\d+\])/g);
    return parts.map((part, idx) => {
      const match = part.match(/\[Ref\s*(\d+)\]/);
      if (match) {
        const refNum = parseInt(match[1]);
        const citation = citations[refNum - 1];
        return (
          <button
            key={idx}
            onClick={() => citation && setActiveCitation(citation)}
            className="inline-flex items-center px-1.5 py-0.5 mx-1 rounded text-[11px] font-bold bg-teal-100 text-teal-800 border border-teal-300 hover:bg-teal-200 transition-colors cursor-pointer align-baseline"
            title={citation?.source_title || "Click to inspect evidence provenance"}
          >
            <BookOpen className="w-3 h-3 mr-0.5" />
            Ref {refNum}
          </button>
        );
      }
      return <span key={idx}>{part}</span>;
    });
  };

  const getSeverityBadgeClass = (severity: TriageSeverity) => {
    switch (severity) {
      case "EMERGENCY":
        return "bg-red-100 text-red-800 border-red-300 font-bold";
      case "URGENT":
        return "bg-amber-100 text-amber-800 border-amber-300 font-bold";
      case "ROUTINE":
      default:
        return "bg-emerald-100 text-emerald-800 border-emerald-300 font-semibold";
    }
  };

  const getSeverityText = (severity: TriageSeverity) => {
    switch (severity) {
      case "EMERGENCY":
        return t.severityEmergency;
      case "URGENT":
        return t.severityUrgent;
      case "ROUTINE":
      default:
        return t.severityRoutine;
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] max-h-[920px]">
      <ConsentModal isOpen={isConsentOpen} onConfirm={handleConsentConfirm} />
      <CitationDrawer citation={activeCitation} onClose={() => setActiveCitation(null)} />

      {/* Triage Session Status Bar */}
      <div className="bg-white border border-slate-200 rounded-t-lg p-3.5 flex flex-wrap items-center justify-between shadow-xs">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-clinical-teal" />
            <h1 className="text-sm font-bold text-clinical-navy">{t.triageThreadTitle}</h1>
          </div>
          {session && (
            <div className="hidden sm:flex items-center space-x-3 text-xs text-slate-500 font-mono">
              <span>{t.sessionLabel}: <strong className="text-slate-800">{session.session_id.slice(0, 8)}</strong></span>
              <span>•</span>
              <span>{t.cohortLabel}: <strong className="text-slate-800">{session.patient_age_group}</strong></span>
              <span>•</span>
              <span>{t.sexLabel}: <strong className="text-slate-800">{session.biological_sex}</strong></span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-3">
          {session && (
            <span
              className={`px-2.5 py-1 text-xs rounded border uppercase tracking-wider ${getSeverityBadgeClass(
                session.triage_severity
              )}`}
            >
              {t.severityLabel}: {getSeverityText(session.triage_severity)}
            </span>
          )}
          <button
            onClick={resetSession}
            className="inline-flex items-center px-2.5 py-1 text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded border border-slate-300 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5 mr-1" />
            {t.resetButton}
          </button>
        </div>
      </div>

      {/* Conversational Message Thread */}
      <div className="flex-1 bg-white border-x border-slate-200 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500 space-y-4">
            <div className="w-12 h-12 rounded-full bg-teal-50 border border-teal-200 flex items-center justify-center text-clinical-teal">
              <HeartPulse className="w-6 h-6" />
            </div>
            <div className="max-w-md">
              <h2 className="text-base font-bold text-slate-800">{t.intakeReadyTitle}</h2>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                {t.intakeReadyDescription}
              </p>
            </div>

            {/* Quick Test Clinical Vignettes (Bilingual) */}
            <div className="w-full max-w-xl text-left bg-slate-50 border border-slate-200 rounded-lg p-3.5 mt-2">
              <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-2">
                {t.vignettesTitle}
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {language === "si" ? (
                  <>
                    <button
                      onClick={() =>
                        handleSendMessage(
                          "මගේ නම කමල් පෙරේරා, ජාතික හැඳුනුම්පත 891234567V. මට වම් අතට සහ බෙල්ලට විහිදෙන තද පපුවේ කැක්කුමක්, හුස්ම ගැනීමේ අපහසුව සහ සීතල දහඩියක් තියෙනවා."
                        )
                      }
                      className="p-2.5 bg-white border border-slate-200 rounded text-left hover:border-red-400 hover:bg-red-50/50 transition-colors"
                    >
                      <span className="font-semibold text-red-700 block">{t.vignetteAcsTitle}</span>
                      <span className="text-[11px] text-slate-500 line-clamp-2">
                        {t.vignetteAcsDesc}
                      </span>
                    </button>

                    <button
                      onClick={() =>
                        handleSendMessage(
                          "මම දියවැඩියා රෝගියෙක් වන අතර වෙව්ලීමක් සහ කරකැවිල්ලක් තියෙනවා. රුධිර සීනි මට්ටම 55 mg/dL දක්වා අඩුවී ඇත. මම කුමක් කළ යුතුද?"
                        )
                      }
                      className="p-2.5 bg-white border border-slate-200 rounded text-left hover:border-teal-400 hover:bg-teal-50/50 transition-colors"
                    >
                      <span className="font-semibold text-teal-800 block">{t.vignetteHypoTitle}</span>
                      <span className="text-[11px] text-slate-500 line-clamp-2">
                        {t.vignetteHypoDesc}
                      </span>
                    </button>

                    <button
                      onClick={() =>
                        handleSendMessage(
                          "මීට විනාඩි 20කට පෙර එක්වරම මුහුණ දකුණු පැත්තට ඇදවුණා, දකුණු අත පණ නැතිවුණා සහ කතා කරන වචන පැටලෙනවා."
                        )
                      }
                      className="p-2.5 bg-white border border-slate-200 rounded text-left hover:border-red-400 hover:bg-red-50/50 transition-colors"
                    >
                      <span className="font-semibold text-red-700 block">{t.vignetteStrokeTitle}</span>
                      <span className="text-[11px] text-slate-500 line-clamp-2">
                        {t.vignetteStrokeDesc}
                      </span>
                    </button>

                    <button
                      onClick={() =>
                        handleSendMessage(
                          "මාස 4ක බිළිඳාට 38.9 C අධික උණ, හුස්ම ගැනීමේදී ශබ්දයක් සහ සමේ දම් පැහැති ලප හටගෙන තිබේ."
                        )
                      }
                      className="p-2.5 bg-white border border-slate-200 rounded text-left hover:border-red-400 hover:bg-red-50/50 transition-colors"
                    >
                      <span className="font-semibold text-red-700 block">{t.vignettePediatricTitle}</span>
                      <span className="text-[11px] text-slate-500 line-clamp-2">
                        {t.vignettePediatricDesc}
                      </span>
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() =>
                        handleSendMessage(
                          "My name is Arthur Morgan, SSN 452-98-1120. I have crushing chest pain radiating to my left arm with cold diaphoresis for 20 minutes."
                        )
                      }
                      className="p-2.5 bg-white border border-slate-200 rounded text-left hover:border-red-400 hover:bg-red-50/50 transition-colors"
                    >
                      <span className="font-semibold text-red-700 block">{t.vignetteAcsTitle}</span>
                      <span className="text-[11px] text-slate-500 line-clamp-2">
                        {t.vignetteAcsDesc}
                      </span>
                    </button>

                    <button
                      onClick={() =>
                        handleSendMessage(
                          "I was diagnosed with type 2 diabetes and feel shaky, trembling, and dizzy. Capillary blood glucose reads 58 mg/dL. What should I do?"
                        )
                      }
                      className="p-2.5 bg-white border border-slate-200 rounded text-left hover:border-teal-400 hover:bg-teal-50/50 transition-colors"
                    >
                      <span className="font-semibold text-teal-800 block">{t.vignetteHypoTitle}</span>
                      <span className="text-[11px] text-slate-500 line-clamp-2">
                        {t.vignetteHypoDesc}
                      </span>
                    </button>

                    <button
                      onClick={() =>
                        handleSendMessage(
                          "Sudden onset right-sided facial drooping and right arm weakness noticed 30 minutes ago. Speech sounds slurred and garbled."
                        )
                      }
                      className="p-2.5 bg-white border border-slate-200 rounded text-left hover:border-red-400 hover:bg-red-50/50 transition-colors"
                    >
                      <span className="font-semibold text-red-700 block">{t.vignetteStrokeTitle}</span>
                      <span className="text-[11px] text-slate-500 line-clamp-2">
                        {t.vignetteStrokeDesc}
                      </span>
                    </button>

                    <button
                      onClick={() =>
                        handleSendMessage(
                          "4-month-old infant with high fever 38.9 C, weak high-pitched cry, grunting breathing, and a non-blanching dark rash on trunk."
                        )
                      }
                      className="p-2.5 bg-white border border-slate-200 rounded text-left hover:border-red-400 hover:bg-red-50/50 transition-colors"
                    >
                      <span className="font-semibold text-red-700 block">{t.vignettePediatricTitle}</span>
                      <span className="text-[11px] text-slate-500 line-clamp-2">
                        {t.vignettePediatricDesc}
                      </span>
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, index) => {
          const isPatient = msg.sender_role === "PATIENT";
          return (
            <div key={msg.message_id || index} className={`flex ${isPatient ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-3xl rounded-lg border text-sm leading-relaxed p-4 shadow-xs ${
                  isPatient
                    ? "bg-slate-100 text-slate-900 border-slate-300 ml-12"
                    : "bg-white text-slate-900 border-slate-200 mr-12"
                }`}
              >
                {/* Sender Header */}
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-200/80 text-xs">
                  <span className="font-bold text-slate-700 flex items-center">
                    {isPatient ? (
                      <>
                        <User className="w-3.5 h-3.5 mr-1 text-slate-500" />
                        {t.patientNarrativeHeader}
                      </>
                    ) : (
                      <>
                        <ShieldCheck className="w-3.5 h-3.5 mr-1 text-clinical-teal" />
                        {t.assistantHeader}
                      </>
                    )}
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">
                    {new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>

                {/* Emergency Red-Flag Banner */}
                {msg.emergency_info && msg.emergency_info.is_emergency && (
                  <EmergencyBanner emergencyInfo={msg.emergency_info} />
                )}

                {/* Formatted Content with Interactive Citations */}
                <div className="whitespace-pre-wrap font-sans text-xs sm:text-sm text-slate-800">
                  {renderContentWithCitationBadges(msg.redacted_content, msg.clinical_citations || [])}
                </div>

                {/* Telemetry Footer */}
                {!isPatient && (
                  <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap items-center justify-between text-[11px] text-slate-500 font-mono">
                    <div className="flex items-center space-x-3">
                      <span>
                        {t.groundednessLabel}: <strong className="text-slate-700">{Math.round(msg.groundedness_score * 100)}%</strong>
                      </span>
                      <span>•</span>
                      <span>
                        {t.similarityLabel}: <strong className="text-slate-700">{msg.retrieval_similarity_score}</strong>
                      </span>
                      <span>•</span>
                      <span>
                        {t.latencyLabel}: <strong className="text-slate-700">{msg.latency_ms}ms</strong>
                      </span>
                    </div>

                    {msg.clinical_citations && msg.clinical_citations.length > 0 && (
                      <span className="text-clinical-teal font-semibold">
                        {msg.clinical_citations.length} {t.guidelinesCitedLabel}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 rounded-lg p-3.5 text-xs text-slate-500 flex items-center space-x-3 shadow-xs">
              <div className="w-2.5 h-2.5 rounded-full bg-clinical-teal animate-ping" />
              <span>{t.scrubbingNotice}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Controls */}
      <div className="bg-slate-100 border border-slate-200 rounded-b-lg p-3.5 shadow-xs">
        {errorMessage && (
          <div className="mb-2 p-2.5 bg-red-50 border border-red-200 text-red-700 rounded text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex space-x-2"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={loading || !session}
            placeholder={
              session
                ? t.inputPlaceholderReady
                : t.inputPlaceholderConsent
            }
            className="flex-1 bg-white border border-slate-300 rounded px-3.5 py-2.5 text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-clinical-teal focus:border-clinical-teal shadow-2xs"
          />
          <button
            type="submit"
            disabled={loading || !session || !inputText.trim()}
            className={`px-5 py-2.5 rounded font-bold text-xs tracking-wide uppercase flex items-center space-x-1.5 transition-colors shadow-xs ${
              loading || !session || !inputText.trim()
                ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                : "bg-clinical-teal hover:bg-clinical-teal-hover text-white"
            }`}
          >
            <span>{t.triageButton}</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
        <span className="text-[10px] text-slate-500 mt-1.5 block text-center sm:text-left">
          {t.footerNotice}
        </span>
      </div>
    </div>
  );
}
