"use client";

import { useState, useEffect, useRef } from "react";
import {
  Send,
  ShieldCheck,
  AlertCircle,
  RotateCcw,
  BookOpen,
  HeartPulse,
  Activity,
  Layers,
  Sparkles,
  Zap,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Radio
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
import { StreamingChatView } from "@/components/chat/StreamingChatView";
import { OntologyBrowserModal } from "@/components/chat/OntologyBrowserModal";
import { CoverLandingPage } from "@/components/CoverLandingPage";
import { useLanguage } from "@/lib/LanguageContext";
import {
  clinicalVoicePlayer,
  ClinicalSpeechRecognizer,
  isSpeechRecognitionSupported
} from "@/lib/voice";

export default function ClinicalTriagePage() {
  const { language, t } = useLanguage();
  const [showCoverPage, setShowCoverPage] = useState<boolean>(true);
  const [activeMode, setActiveMode] = useState<"STREAMING" | "LEGACY">("STREAMING");
  const [isOntologyOpen, setIsOntologyOpen] = useState(false);

  // Legacy Session Mode State
  const [session, setSession] = useState<TriageSession | null>(null);
  const [messages, setMessages] = useState<TriageMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [isConsentOpen, setIsConsentOpen] = useState(false);
  const [activeCitation, setActiveCitation] = useState<ClinicalCitation | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Legacy Voice Engine States
  const [activePlayingId, setActivePlayingId] = useState<string | null>(null);
  const [isListening, setIsListening] = useState<boolean>(false);
  const [voiceNotice, setVoiceNotice] = useState<string | null>(null);
  const recognizerRef = useRef<ClinicalSpeechRecognizer | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    return () => {
      recognizerRef.current?.stop();
      clinicalVoicePlayer.stop();
    };
  }, []);

  const toggleVoiceInput = () => {
    if (isListening) {
      recognizerRef.current?.stop();
      setIsListening(false);
      setVoiceNotice(null);
      return;
    }

    if (!isSpeechRecognitionSupported()) {
      setVoiceNotice(t.voiceNotSupported);
      setTimeout(() => setVoiceNotice(null), 4000);
      return;
    }

    setVoiceNotice(t.voiceListening);
    const recognizer = new ClinicalSpeechRecognizer({
      language,
      onResult: (transcript, isFinal) => {
        if (isFinal) {
          setInputText((prev) => (prev ? `${prev.trim()} ${transcript}` : transcript));
        } else {
          setVoiceNotice(`${t.voiceListening}: "${transcript}"`);
        }
      },
      onError: (err) => {
        setIsListening(false);
        setVoiceNotice(t.voicePermissionError);
        setTimeout(() => setVoiceNotice(null), 5000);
      },
      onEnd: () => {
        setIsListening(false);
        setTimeout(() => setVoiceNotice(null), 1500);
      }
    });

    const started = recognizer.start();
    if (started) {
      recognizerRef.current = recognizer;
      setIsListening(true);
    }
  };

  const handleToggleSpeak = (msgId: string, content: string) => {
    if (activePlayingId === msgId) {
      clinicalVoicePlayer.stop();
      setActivePlayingId(null);
    } else {
      setActivePlayingId(msgId);
      clinicalVoicePlayer.speak(msgId, content, language, {
        onStart: () => setActivePlayingId(msgId),
        onEnd: () => setActivePlayingId(null),
        onError: () => setActivePlayingId(null)
      });
    }
  };

  useEffect(() => {
    if (activeMode === "LEGACY" && !session) {
      setIsConsentOpen(true);
    }
  }, [activeMode, session]);

  useEffect(() => {
    if (activeMode === "LEGACY") {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading, activeMode]);

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

  const handleEnterClinicalSystem = () => {
    setShowCoverPage(false);
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  if (showCoverPage) {
    return <CoverLandingPage onEnterSystem={handleEnterClinicalSystem} />;
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-h-[920px] space-y-2.5 animate-in fade-in slide-in-from-bottom-3 duration-500">
      {/* Top Clinical Mode Selector & Quick Diagnostic Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 bg-white border border-[#CBE2EA] rounded-2xl px-4 py-2.5 shrink-0 text-xs shadow-clinical-card">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowCoverPage(true)}
            className="px-3 py-1.5 rounded-xl font-bold flex items-center gap-1.5 bg-[#F0F9FF] hover:bg-teal-50 text-[#0A2540] border border-[#CBE2EA] transition-all cursor-pointer"
            title="Return to Cover & Benefits Page"
          >
            <Sparkles className="w-3.5 h-3.5 text-teal-600" />
            <span>{language === "si" ? "මුල් පිටුව (Cover Page)" : "Cover Page"}</span>
          </button>
          <span className="text-[#486581] font-semibold hidden sm:flex items-center gap-1.5 ml-1">
            <HeartPulse className="w-4 h-4 text-teal-600" />
            <span>Clinical Triage Engine:</span>
          </span>
          <button
            onClick={() => setActiveMode("STREAMING")}
            className={`px-3.5 py-1.5 rounded-xl font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
              activeMode === "STREAMING"
                ? "bg-gradient-to-r from-teal-600 to-cyan-700 text-white shadow-sm"
                : "bg-[#EBF5F8] text-[#243B53] hover:bg-[#DCEEF4]"
            }`}
          >
            <Zap className={`w-3.5 h-3.5 ${activeMode === "STREAMING" ? "text-amber-300" : "text-teal-600"}`} />
            <span>SOCRATES Real-Time Clinical Stream</span>
          </button>
          <button
            onClick={() => setActiveMode("LEGACY")}
            className={`px-3.5 py-1.5 rounded-xl font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
              activeMode === "LEGACY"
                ? "bg-gradient-to-r from-teal-600 to-cyan-700 text-white shadow-sm"
                : "bg-[#EBF5F8] text-[#243B53] hover:bg-[#DCEEF4]"
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Standard Session Mode</span>
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-semibold">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>PHI Scrubber + Red-Flag Screen Active</span>
          </span>
          <button
            onClick={() => setIsOntologyOpen(true)}
            className="px-3.5 py-1.5 rounded-xl bg-sky-50 hover:bg-sky-100 border border-sky-200 text-sky-800 text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer shadow-2xs"
          >
            <Layers className="w-3.5 h-3.5 text-sky-600" />
            <span>Browse 44+ WHO ICD-11 Pathologies</span>
          </button>
        </div>
      </div>

      {/* Main Chat Interface */}

      {activeMode === "STREAMING" ? (
        <div className="flex-1 min-h-0">
          <StreamingChatView onOpenOntology={() => setIsOntologyOpen(true)} />
        </div>
      ) : (
        <div className="flex-1 flex flex-col min-h-0 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
          <ConsentModal isOpen={isConsentOpen} onConfirm={handleConsentConfirm} />
          <CitationDrawer citation={activeCitation} onClose={() => setActiveCitation(null)} />

          {/* Triage Session Status Bar */}
          <div className="bg-slate-50 border-b border-slate-200 p-3.5 flex flex-wrap items-center justify-between shrink-0">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-teal-600" />
                <h1 className="text-sm font-bold text-slate-900">{t.triageThreadTitle}</h1>
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
                className="inline-flex items-center px-2.5 py-1 text-xs font-medium text-slate-600 bg-white hover:bg-slate-100 rounded border border-slate-300 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5 mr-1" />
                {t.resetButton}
              </button>
            </div>
          </div>

          {/* Conversational Message Thread */}
          <div className="flex-1 bg-white overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500 space-y-4">
                <div className="w-12 h-12 rounded-full bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-600">
                  <HeartPulse className="w-6 h-6" />
                </div>
                <div className="max-w-md">
                  <h2 className="text-base font-bold text-slate-800">{t.intakeReadyTitle}</h2>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                    {t.intakeReadyDescription}
                  </p>
                </div>
              </div>
            )}

            {messages.map((msg) => {
              const isPatient = msg.sender_role === "PATIENT";
              const isEmergency = msg.triage_severity === "EMERGENCY" && !isPatient;

              return (
                <div
                  key={msg.message_id}
                  className={`flex flex-col ${isPatient ? "items-end" : "items-start"}`}
                >
                  <div className="flex items-center justify-between w-full max-w-[85%] mb-1 text-[11px] text-slate-500">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">
                        {isPatient ? t.patientNarrativeHeader : t.assistantHeader}
                      </span>
                      <span>•</span>
                      <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                    </div>
                    {!isPatient && (
                      <button
                        onClick={() => handleToggleSpeak(msg.message_id, msg.redacted_content)}
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium transition-colors ${
                          activePlayingId === msg.message_id
                            ? "bg-teal-100 text-teal-800 border border-teal-300 animate-pulse"
                            : "hover:bg-slate-200 text-slate-600"
                        }`}
                        title={activePlayingId === msg.message_id ? t.voiceStopAudio : t.voicePlay}
                      >
                        {activePlayingId === msg.message_id ? (
                          <>
                            <VolumeX className="w-3 h-3 text-rose-600" />
                            <span>{t.voiceStopAudio}</span>
                          </>
                        ) : (
                          <>
                            <Volume2 className="w-3 h-3 text-teal-600" />
                            <span>{t.voicePlay}</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  <div
                    className={`max-w-[85%] rounded-lg p-3.5 text-xs sm:text-sm leading-relaxed ${
                      isPatient
                        ? "bg-teal-600 text-white rounded-br-none shadow-xs"
                        : isEmergency
                        ? "bg-red-50 text-red-950 border border-red-300 rounded-bl-none shadow-xs"
                        : "bg-slate-50 text-slate-900 border border-slate-200 rounded-bl-none shadow-xs"
                    }`}
                  >
                    {!isPatient && msg.emergency_info?.is_emergency && (
                      <EmergencyBanner emergencyInfo={msg.emergency_info} />
                    )}

                    <div className="whitespace-pre-wrap">
                      {isPatient
                        ? msg.redacted_content
                        : renderContentWithCitationBadges(
                            msg.redacted_content,
                            msg.clinical_citations
                          )}
                    </div>

                    {!isPatient && (
                      <div className="mt-3 pt-2.5 border-t border-slate-200/80 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500">
                        <div className="flex items-center space-x-3">
                          <span>
                            {t.groundednessLabel}:{" "}
                            <strong className="text-slate-700">
                              {(msg.groundedness_score * 100).toFixed(0)}%
                            </strong>
                          </span>
                          <span>•</span>
                          <span>
                            {t.latencyLabel}:{" "}
                            <strong className="text-slate-700">{msg.latency_ms}ms</strong>
                          </span>
                        </div>
                        {msg.clinical_citations.length > 0 && (
                          <span className="text-teal-700 font-semibold">
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
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 text-xs text-slate-500 flex items-center space-x-3 shadow-xs">
                  <div className="w-2.5 h-2.5 rounded-full bg-teal-600 animate-ping" />
                  <span>{t.scrubbingNotice}</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Controls */}
          <div className="bg-slate-50 border-t border-slate-200 p-3.5 shrink-0">
            {voiceNotice && (
              <div className="mb-2.5 px-3 py-1.5 rounded bg-teal-50 border border-teal-200 text-teal-800 text-xs flex items-center gap-2">
                <Radio className="w-3.5 h-3.5 animate-pulse text-teal-600 shrink-0" />
                <span className="truncate">{voiceNotice}</span>
              </div>
            )}

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
              <div className="relative flex-1">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  disabled={loading || !session}
                  placeholder={
                    isListening
                      ? t.voiceListening
                      : session
                      ? t.inputPlaceholderReady
                      : t.inputPlaceholderConsent
                  }
                  className={`w-full bg-white border rounded px-3.5 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500 shadow-2xs transition-all ${
                    isListening ? "border-rose-500 ring-1 ring-rose-400 pr-20" : "border-slate-300"
                  }`}
                />
                {isListening && (
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1 text-[10px] text-rose-600 font-mono bg-rose-50 px-1.5 py-0.5 rounded border border-rose-200 animate-pulse">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-600"></span>
                    REC
                  </span>
                )}
              </div>

              <button
                type="button"
                onClick={toggleVoiceInput}
                disabled={loading || !session}
                className={`px-3 py-2 rounded text-xs font-semibold flex items-center justify-center transition-all cursor-pointer disabled:cursor-not-allowed shrink-0 border ${
                  isListening
                    ? "bg-rose-600 hover:bg-rose-500 text-white border-rose-600 animate-pulse"
                    : "bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-300"
                }`}
                title={isListening ? t.voiceStop : t.voiceInputTooltip}
              >
                {isListening ? (
                  <MicOff className="w-3.5 h-3.5 text-white" />
                ) : (
                  <Mic className="w-3.5 h-3.5 text-teal-600" />
                )}
              </button>

              <button
                type="submit"
                disabled={loading || !session || !inputText.trim()}
                className="px-5 py-2 rounded font-bold text-xs tracking-wide uppercase flex items-center space-x-1.5 transition-colors bg-teal-600 hover:bg-teal-500 text-white disabled:bg-slate-300 disabled:text-slate-500 disabled:cursor-not-allowed cursor-pointer"
              >
                <span>{t.triageButton}</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Ontology Browser Modal */}
      <OntologyBrowserModal
        isOpen={isOntologyOpen}
        onClose={() => setIsOntologyOpen(false)}
      />
    </div>
  );
}
