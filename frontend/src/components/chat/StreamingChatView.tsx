"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send,
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  Activity,
  FileText,
  ExternalLink,
  RotateCcw,
  Sparkles,
  Stethoscope,
  ChevronRight,
  PhoneCall,
  Info,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Radio,
  Cpu,
  CalendarCheck
} from "lucide-react";
import {
  StreamCitation,
  StreamBadgeData,
  StreamStatusData,
  TriageAcuityLevel,
  TriageWorkflowState,
  HybridLLMStatus
} from "@/lib/types";
import { streamClinicalChat, fetchHybridLLMStatus, updateHybridLLMConfig } from "@/lib/api";
import { useLanguage } from "@/lib/LanguageContext";
import {
  clinicalVoicePlayer,
  ClinicalSpeechRecognizer,
  isSpeechRecognitionSupported
} from "@/lib/voice";
import { AppointmentBookingModal } from "@/components/telemedicine/AppointmentBookingModal";

interface ChatMessage {
  id: string;
  sender: "PATIENT" | "CLINICIAN_ASSISTANT";
  content: string;
  citations?: StreamCitation[];
  badge?: StreamBadgeData;
  chips?: string[];
  timestamp: string;
}

interface StreamingChatViewProps {
  onOpenOntology?: () => void;
}

export function StreamingChatView({ onOpenOntology }: StreamingChatViewProps) {
  const { language, t } = useLanguage();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [activeStatus, setActiveStatus] = useState<StreamStatusData | null>(null);
  const [currentBadge, setCurrentBadge] = useState<StreamBadgeData | null>(null);
  const [streamedText, setStreamedText] = useState("");
  const [streamedCitations, setStreamedCitations] = useState<StreamCitation[]>([]);
  const [streamedChips, setStreamedChips] = useState<string[]>([]);
  const [activeCitationModal, setActiveCitationModal] = useState<StreamCitation | null>(null);

  // Hybrid Cloud LLM Connector State
  const [llmStatus, setLlmStatus] = useState<HybridLLMStatus | null>(null);
  const [isLlmModalOpen, setIsLlmModalOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState("auto");
  const [geminiKey, setGeminiKey] = useState("");
  const [anthropicKey, setAnthropicKey] = useState("");
  const [openaiKey, setOpenaiKey] = useState("");
  const [savingLlmConfig, setSavingLlmConfig] = useState(false);

  // Telemedicine & Specialist Booking Modal State
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [bookingHeadline, setBookingHeadline] = useState("");
  const [bookingAcuity, setBookingAcuity] = useState("ROUTINE");
  const [bookingSummary, setBookingSummary] = useState("");

  // Voice Engine States
  const [autoReadAloud, setAutoReadAloud] = useState<boolean>(false);
  const [activePlayingId, setActivePlayingId] = useState<string | null>(null);
  const [isListening, setIsListening] = useState<boolean>(false);
  const [voiceNotice, setVoiceNotice] = useState<string | null>(null);
  const recognizerRef = useRef<ClinicalSpeechRecognizer | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Stop voice and audio on unmount, and load Hybrid LLM status
  useEffect(() => {
    fetchHybridLLMStatus()
      .then((data) => {
        setLlmStatus(data);
        setSelectedProvider(data.configured_mode || "auto");
      })
      .catch(() => {});
    return () => {
      recognizerRef.current?.stop();
      clinicalVoicePlayer.stop();
    };
  }, []);

  const handleSaveLlmConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingLlmConfig(true);
    try {
      const updated = await updateHybridLLMConfig({
        provider: selectedProvider,
        gemini_api_key: geminiKey || undefined,
        anthropic_api_key: anthropicKey || undefined,
        openai_api_key: openaiKey || undefined
      });
      setLlmStatus(updated);
      setIsLlmModalOpen(false);
    } catch {
      // ignore
    } finally {
      setSavingLlmConfig(false);
    }
  };

  // Sync speech recognizer language when user switches language
  useEffect(() => {
    if (isListening && recognizerRef.current) {
      recognizerRef.current.stop();
      startVoiceListening();
    }
  }, [language]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamedText, activeStatus]);

  const startVoiceListening = () => {
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
        if (err === "not-allowed" || err === "permission-denied") {
          setVoiceNotice(t.voicePermissionError);
        } else {
          setVoiceNotice(t.voicePermissionError);
        }
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

  const toggleVoiceInput = () => {
    if (isListening) {
      recognizerRef.current?.stop();
      setIsListening(false);
      setVoiceNotice(null);
    } else {
      startVoiceListening();
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

  const handleStopAllAudio = () => {
    clinicalVoicePlayer.stop();
    setActivePlayingId(null);
  };

  const handleSend = async (messageToSend?: string) => {
    // If voice recognition is listening, stop it when sending
    if (isListening) {
      recognizerRef.current?.stop();
      setIsListening(false);
      setVoiceNotice(null);
    }

    const text = messageToSend || inputText;
    if (!text.trim() || isStreaming) return;

    setInputText("");
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "PATIENT",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);
    setActiveStatus({ stage: "screening_red_flags", message: "Screening clinical red flags..." });
    setCurrentBadge(null);
    setStreamedText("");
    setStreamedCitations([]);
    setStreamedChips([]);

    // Construct conversation history
    const historyPayload = messages.map((m) => ({
      role: m.sender === "PATIENT" ? "user" : "assistant",
      content: m.content
    }));

    let accumulatedText = "";
    let finalBadge: StreamBadgeData | null = null;
    let finalCitations: StreamCitation[] = [];
    let finalChips: string[] = [];

    await streamClinicalChat(
      {
        message: text,
        conversationHistory: historyPayload,
        preferredLanguage: language
      },
      {
        onStatus: (status) => {
          setActiveStatus(status);
        },
        onBadge: (badge) => {
          setCurrentBadge(badge);
          finalBadge = badge;
        },
        onToken: (token) => {
          accumulatedText += token;
          setStreamedText(accumulatedText);
        },
        onCitations: (citations) => {
          setStreamedCitations(citations);
          finalCitations = citations;
        },
        onFollowUpChips: (chips) => {
          setStreamedChips(chips);
          finalChips = chips;
        },
        onDone: () => {
          setIsStreaming(false);
          setActiveStatus(null);

          const assistantMsgId = `assistant-${Date.now()}`;
          const assistantMsg: ChatMessage = {
            id: assistantMsgId,
            sender: "CLINICIAN_ASSISTANT",
            content: accumulatedText,
            citations: finalCitations,
            badge: finalBadge || undefined,
            chips: finalChips,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
          };

          setMessages((prev) => [...prev, assistantMsg]);
          setStreamedText("");
          setCurrentBadge(null);
          setStreamedCitations([]);
          setStreamedChips([]);

          // Automatically speak clinical response if Auto Read Aloud is enabled
          if (autoReadAloud && accumulatedText.trim()) {
            setTimeout(() => {
              handleToggleSpeak(assistantMsgId, accumulatedText);
            }, 300);
          }
        },
        onError: (err) => {
          setIsStreaming(false);
          setActiveStatus(null);
          const errorMsg: ChatMessage = {
            id: `err-${Date.now()}`,
            sender: "CLINICIAN_ASSISTANT",
            content: "A temporary clinical pipeline error occurred while connecting to the triage engine. Please retry.",
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
          };
          setMessages((prev) => [...prev, errorMsg]);
          setStreamedText("");
        }
      }
    );
  };

  const handleChipClick = (chipText: string) => {
    if (isStreaming) return;
    handleSend(chipText);
  };

  const resetChat = () => {
    clinicalVoicePlayer.stop();
    recognizerRef.current?.stop();
    setIsListening(false);
    setActivePlayingId(null);
    setVoiceNotice(null);
    setMessages([]);
    setStreamedText("");
    setCurrentBadge(null);
    setStreamedCitations([]);
    setStreamedChips([]);
    setActiveStatus(null);
  };

  const renderBadge = (badge: StreamBadgeData) => {
    const isEmerg = badge.acuity === "EMERGENCY" || badge.is_emergency;
    const isUrgent = badge.acuity === "URGENT_CONSULT";

    const badgeBg = isEmerg
      ? "bg-rose-950/80 border-rose-600 text-rose-200"
      : isUrgent
      ? "bg-amber-950/80 border-amber-500 text-amber-200"
      : "bg-teal-950/80 border-teal-500 text-teal-200";

    const iconColor = isEmerg ? "text-rose-400" : isUrgent ? "text-amber-400" : "text-teal-400";

    return (
      <div className={`p-3.5 rounded-lg border mb-3.5 ${badgeBg} shadow-md space-y-2`}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            {isEmerg ? (
              <ShieldAlert className={`w-5 h-5 ${iconColor} shrink-0 animate-pulse`} />
            ) : isUrgent ? (
              <AlertTriangle className={`w-5 h-5 ${iconColor} shrink-0`} />
            ) : (
              <Activity className={`w-5 h-5 ${iconColor} shrink-0`} />
            )}
            <div>
              <div className="text-xs font-semibold tracking-wider uppercase opacity-80">
                Triage Classification: {badge.acuity}
              </div>
              <div className="text-sm font-bold mt-0.5">{badge.headline}</div>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {isEmerg && (
              <a
                href="tel:1990"
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-bold shrink-0 transition-colors shadow-sm"
              >
                <PhoneCall className="w-3.5 h-3.5" />
                Call 1990 / 911
              </a>
            )}
            <button
              type="button"
              onClick={() => {
                setBookingHeadline(badge.headline || "");
                setBookingAcuity(badge.acuity || "ROUTINE");
                setBookingSummary(`${badge.headline || "Clinical Triage"} (Acuity: ${badge.acuity})`);
                setIsBookingModalOpen(true);
              }}
              className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-bold shrink-0 transition-colors shadow-sm cursor-pointer"
            >
              <CalendarCheck className="w-3.5 h-3.5" />
              <span>{language === "si" ? "වෛද්‍යවරයෙකු වෙන්කරන්න (Book)" : "Book Specialist (eChannelling / Doc990)"}</span>
            </button>
          </div>
        </div>

        {/* Hybrid LLM & Pre-Transmission PHI Scrubber Telemetry Row */}
        {(badge.llm_model || (badge.scrubbed_entities && badge.scrubbed_entities.length > 0)) && (
          <div className="pt-2 border-t border-white/10 flex flex-wrap items-center gap-2 text-[10px]">
            {badge.llm_model && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-950/70 border border-slate-700 text-slate-300 font-mono">
                <Cpu className="w-3 h-3 text-teal-400" />
                <span>Engine: {badge.llm_model}</span>
              </span>
            )}
            {badge.scrubbed_entities && badge.scrubbed_entities.length > 0 && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-700 text-emerald-300 font-mono">
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                <span>PHI Scrubbed Pre-LLM: {badge.scrubbed_entities.join(", ")}</span>
              </span>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 rounded-2xl border border-[#CBE2EA] shadow-clinical-elevated overflow-hidden">
      {/* Top Clinical Consultation Header */}
      <div className="clinical-dark-preserve px-5 py-3.5 bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0D7490] border-b border-teal-500/30 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 border border-teal-300/30 flex items-center justify-center text-teal-300 shadow-inner">
            <Stethoscope className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-white flex items-center gap-2">
              <span>SOCRATES Clinical Triage & Consultation Workstation</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-teal-400/20 text-teal-200 border border-teal-300/40">
                ICD-11 Real-Time SSE
              </span>
            </div>
            <div className="text-xs text-cyan-100/80">
              Protocolized Symptom Assessment • Hybrid Cloud LLM • HIPAA Safe Harbor PHI Scrubber
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Hybrid Cloud LLM Connector Status & Settings Button */}
          <button
            onClick={() => setIsLlmModalOpen(true)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold border flex items-center gap-1.5 transition-colors cursor-pointer ${
              llmStatus?.cloud_llm_enabled
                ? "bg-emerald-500/20 border-emerald-400/50 text-emerald-200 hover:bg-emerald-500/30"
                : "bg-white/10 hover:bg-white/20 border-white/20 text-teal-200"
            }`}
            title="Configure Hybrid Cloud LLM (Google Gemini 1.5 Pro, Claude 3.5 Sonnet, GPT-4o)"
          >
            <Cpu className="w-3.5 h-3.5 text-teal-300" />
            <span className="hidden sm:inline">
              {llmStatus?.cloud_llm_enabled
                ? `Cloud LLM: ${llmStatus.active_model}`
                : "Hybrid LLM: Local + NLU"}
            </span>
          </button>

          {activePlayingId && (
            <button
              onClick={handleStopAllAudio}
              className="px-2.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 border border-rose-400 text-white text-xs font-bold flex items-center gap-1.5 transition-colors animate-pulse"
              title={t.voiceStopAudio}
            >
              <VolumeX className="w-3.5 h-3.5" />
              <span>{t.voiceStopAudio}</span>
            </button>
          )}

          <button
            onClick={() => setAutoReadAloud((prev) => !prev)}
            className={`px-2.5 py-1.5 rounded-xl text-xs font-semibold border flex items-center gap-1.5 transition-colors cursor-pointer ${
              autoReadAloud
                ? "bg-teal-500/30 border-teal-300 text-white"
                : "bg-white/10 hover:bg-white/20 border-white/20 text-cyan-100"
            }`}
            title={t.voiceAutoRead}
          >
            <Volume2 className={`w-3.5 h-3.5 ${autoReadAloud ? "text-teal-200" : "text-cyan-200"}`} />
            <span>{t.voiceAutoRead}</span>
          </button>

          {onOpenOntology && (
            <button
              onClick={onOpenOntology}
              className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-semibold border border-white/20 flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <FileText className="w-3.5 h-3.5 text-teal-300" />
              <span className="hidden md:inline">ICD-11 Ontology (44 Diseases)</span>
            </button>
          )}
          <button
            onClick={resetChat}
            className="p-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-cyan-100 hover:text-white border border-white/15 transition-colors cursor-pointer"
            title="Reset Conversation"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 clinical-ecg-grid">
        {messages.length === 0 && !isStreaming && (
          <div className="max-w-3xl mx-auto my-6 text-center space-y-5">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-teal-50 border border-teal-200 text-teal-800 text-xs font-bold shadow-2xs">
              <Sparkles className="w-3.5 h-3.5 text-teal-600" />
              <span>{language === "si" ? "සායනික රෝග විනිශ්චය සහ Triage සහායක" : "Evidence-Grounded Medical Triage & Decision Support"}</span>
            </div>

            <div className="space-y-2">
              <h2 className="text-lg sm:text-xl font-extrabold text-slate-100">
                {language === "si"
                  ? "ඔබගේ රෝග ලක්ෂණ සිංහලෙන්, Singlish හෝ ඉංග්‍රීසියෙන් විස්තර කරන්න"
                  : "How can MedGuard Clinical AI assist with your symptoms today?"}
              </h2>
              <p className="text-xs text-slate-400 max-w-2xl mx-auto leading-relaxed">
                {language === "si"
                  ? "රෝගියාගේ පෞද්ගලික තොරතුරු (PHI) ස්වයංක්‍රීයව ඉවත් කර (HIPAA Safe Harbor), හදිසි අවදානම් ලක්ෂණ (Red Flags) සහ WHO ICD-11 සායනික මාර්ගෝපදේශ අනුව ක්ෂණිකව පරීක්ෂා කෙරේ."
                  : "Describe your symptoms naturally in English, Sinhala, or Singlish. Patient identifiers (PHI) are scrubbed via HIPAA Safe Harbor prior to Hybrid LLM synthesis, and red-flag emergencies are screened in sub-milliseconds."}
              </p>
            </div>

            {/* Structured Medical Sample Scenario Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left pt-1">
              <button
                onClick={() => handleSend("I have a persistent headache and mild photophobia for 2 days")}
                className="p-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-teal-500 transition-all group cursor-pointer flex items-start gap-3 shadow-2xs"
              >
                <div className="w-8 h-8 rounded-lg bg-teal-500/15 border border-teal-500/30 flex items-center justify-center text-teal-600 shrink-0 mt-0.5">
                  <Activity className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-100 group-hover:text-teal-700">
                    Neurological / Routine Intake
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    &ldquo;I have a persistent headache and mild photophobia for 2 days&rdquo;
                  </div>
                </div>
              </button>

              <button
                onClick={() => handleSend("මට දින 3ක සිට තද උණ, හිසරදය සහ ඇඟපත වේදනාව තියෙනවා")}
                className="p-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-teal-500 transition-all group cursor-pointer flex items-start gap-3 shadow-2xs"
              >
                <div className="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-600 shrink-0 mt-0.5">
                  <Stethoscope className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-100 group-hover:text-sky-700">
                    සිංහල සායනික පරීක්ෂාව (Dengue / Viral Fever)
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    &ldquo;මට දින 3ක සිට තද උණ, හිසරදය සහ ඇඟපත වේදනාව තියෙනවා&rdquo;
                  </div>
                </div>
              </button>

              <button
                onClick={() => handleSend("Crushing central chest pain radiating to left arm and jaw with sweating")}
                className="p-3.5 rounded-xl bg-rose-950/60 hover:bg-rose-900/60 border border-rose-800 hover:border-rose-500 transition-all group cursor-pointer flex items-start gap-3 shadow-2xs"
              >
                <div className="w-8 h-8 rounded-lg bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-600 shrink-0 mt-0.5">
                  <ShieldAlert className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-bold text-rose-300">
                    Cardiac Emergency Red-Flag Protocol (1990)
                  </div>
                  <div className="text-[11px] text-rose-400 mt-0.5">
                    &ldquo;Crushing central chest pain radiating to left arm and jaw&rdquo;
                  </div>
                </div>
              </button>

              <button
                onClick={() =>
                  handleSend(
                    "Mage nama Kamal Perera, phone 077-123-4567. Mata dawas 3k idan thada una saha oluwe kakkuma wamanaya thiyenawa"
                  )
                }
                className="p-3.5 rounded-xl bg-teal-950/60 hover:bg-teal-900/60 border border-teal-800 hover:border-teal-500 transition-all group cursor-pointer flex items-start gap-3 shadow-2xs"
              >
                <div className="w-8 h-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-600 shrink-0 mt-0.5">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-bold text-teal-300">
                    Singlish + Pre-LLM PHI Scrubber Verification
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    &ldquo;Mage nama Kamal... dawas 3k idan thada una saha wamanaya&rdquo;
                  </div>
                </div>
              </button>
            </div>
          </div>
        )}


        {/* Existing Messages */}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === "PATIENT" ? "items-end" : "items-start"}`}
          >
            <div className="flex items-center justify-between w-full max-w-[85%] mb-1 text-[11px] text-slate-400">
              <span>{msg.sender === "PATIENT" ? "Patient Narrative" : "Clinical Assessment"}</span>
              <div className="flex items-center gap-2">
                {msg.sender === "CLINICIAN_ASSISTANT" && (
                  <button
                    onClick={() => handleToggleSpeak(msg.id, msg.content)}
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] transition-colors ${
                      activePlayingId === msg.id
                        ? "bg-teal-950 text-teal-300 border border-teal-700 animate-pulse"
                        : "hover:bg-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                    title={activePlayingId === msg.id ? t.voiceStopAudio : t.voicePlay}
                  >
                    {activePlayingId === msg.id ? (
                      <>
                        <VolumeX className="w-3 h-3 text-teal-400" />
                        <span>{t.voiceStopAudio}</span>
                      </>
                    ) : (
                      <>
                        <Volume2 className="w-3 h-3 text-slate-400" />
                        <span>{t.voicePlay}</span>
                      </>
                    )}
                  </button>
                )}
                <span>{msg.timestamp}</span>
              </div>
            </div>

            <div
              className={`max-w-[85%] rounded-xl p-4 text-xs leading-relaxed whitespace-pre-wrap ${
                msg.sender === "PATIENT"
                  ? "bg-teal-600 text-white rounded-br-none"
                  : "bg-slate-900 text-slate-200 border border-slate-800 rounded-bl-none shadow-sm"
              }`}
            >
              {msg.badge && renderBadge(msg.badge)}

              <div>{msg.content}</div>

              {/* Citations Card Row */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3.5 pt-3 border-t border-slate-800 space-y-1.5">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-teal-400" />
                    Verified Evidence Citations
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {msg.citations.map((c, i) => (
                      <button
                        key={i}
                        onClick={() => setActiveCitationModal(c)}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-950 border border-slate-700 hover:border-teal-500 text-[11px] text-teal-300 transition-colors"
                      >
                        <span className="font-bold">{c.badge}</span>
                        <span className="truncate max-w-[200px] text-slate-300">{c.authority}</span>
                        <ChevronRight className="w-3 h-3 text-slate-500" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Follow-up quick-reply chips */}
              {msg.chips && msg.chips.length > 0 && (
                <div className="mt-3.5 pt-3 border-t border-slate-800">
                  <div className="text-[11px] font-semibold text-slate-400 mb-2">
                    Quick Clinical Clarification:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {msg.chips.map((chip, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleChipClick(chip)}
                        className="px-3 py-1.5 rounded-full bg-slate-800 hover:bg-teal-900/60 border border-slate-700 hover:border-teal-500 text-slate-200 hover:text-teal-200 text-xs transition-all"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Live Streaming Message Box */}
        {isStreaming && (
          <div className="flex flex-col items-start">
            <div className="flex items-center gap-2 mb-1 text-[11px] text-slate-400">
              <span>Clinical Decision Support Engine</span>
              <span className="text-teal-400 animate-pulse">Streaming</span>
            </div>

            <div className="max-w-[85%] rounded-xl p-4 text-xs leading-relaxed bg-slate-900 text-slate-200 border border-slate-800 rounded-bl-none shadow-sm">
              {/* Pipeline Live Status Bar */}
              {activeStatus && (
                <div className="mb-3 px-3 py-1.5 rounded bg-slate-950 border border-slate-800 flex items-center gap-2 text-xs text-teal-400">
                  <Activity className="w-3.5 h-3.5 animate-spin" />
                  <span className="font-mono text-[11px]">{activeStatus.message}</span>
                </div>
              )}

              {/* Immediate Triage Badge before text finishes */}
              {currentBadge && renderBadge(currentBadge)}

              {/* Streamed text tokens */}
              <div className="whitespace-pre-wrap">{streamedText}</div>

              {/* Streamed citations if arrived */}
              {streamedCitations.length > 0 && (
                <div className="mt-3.5 pt-3 border-t border-slate-800 space-y-1.5">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-teal-400" />
                    Verified Evidence Citations
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {streamedCitations.map((c, i) => (
                      <button
                        key={i}
                        onClick={() => setActiveCitationModal(c)}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-950 border border-slate-700 hover:border-teal-500 text-[11px] text-teal-300 transition-colors"
                      >
                        <span className="font-bold">{c.badge}</span>
                        <span className="truncate max-w-[200px] text-slate-300">{c.authority}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Streamed chips if arrived */}
              {streamedChips.length > 0 && (
                <div className="mt-3.5 pt-3 border-t border-slate-800">
                  <div className="text-[11px] font-semibold text-slate-400 mb-2">
                    Quick Clinical Clarification:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {streamedChips.map((chip, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleChipClick(chip)}
                        className="px-3 py-1.5 rounded-full bg-slate-800 hover:bg-teal-900/60 border border-slate-700 text-slate-200 text-xs transition-all"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Bar */}
      <div className="p-4 bg-slate-900 border-t border-slate-800 shrink-0">
        {voiceNotice && (
          <div className="mb-2.5 px-3 py-1.5 rounded bg-teal-950/80 border border-teal-700/60 text-teal-300 text-xs flex items-center gap-2">
            <Radio className="w-3.5 h-3.5 animate-pulse text-teal-400 shrink-0" />
            <span className="truncate">{voiceNotice}</span>
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isStreaming}
              placeholder={
                isListening
                  ? t.voiceListening
                  : "Type clinical symptoms, onset, character, or questions in English or Sinhala..."
              }
              className={`w-full bg-slate-950 border rounded-lg px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none transition-all disabled:opacity-50 ${
                isListening
                  ? "border-rose-500 ring-1 ring-rose-500/50 pr-24"
                  : "border-slate-700 focus:border-teal-500"
              }`}
            />
            {isListening && (
              <span className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5 text-[10px] text-rose-400 font-mono bg-rose-950/90 px-2 py-0.5 rounded border border-rose-800 animate-pulse">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                REC {language === "si" ? "SI" : "EN"}
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={toggleVoiceInput}
            disabled={isStreaming}
            className={`p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center transition-all cursor-pointer disabled:cursor-not-allowed shrink-0 ${
              isListening
                ? "bg-rose-600 hover:bg-rose-500 text-white border-rose-500 shadow-lg shadow-rose-900/40 animate-pulse"
                : "bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700 hover:border-slate-600"
            }`}
            title={isListening ? t.voiceStop : t.voiceInputTooltip}
          >
            {isListening ? (
              <MicOff className="w-4 h-4 text-white" />
            ) : (
              <Mic className="w-4 h-4 text-teal-400" />
            )}
          </button>

          <button
            type="submit"
            disabled={!inputText.trim() || isStreaming}
            className="px-4 py-2.5 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 disabled:text-slate-600 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors shrink-0 cursor-pointer disabled:cursor-not-allowed"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Send</span>
          </button>
        </form>
        <div className="mt-2 text-[10px] text-slate-500 flex items-center justify-between">
          <span>Clinical Decision Support System aligned with WHO ICD-11 & SOCRATES protocol</span>
          <span>Deterministic Red-Flag Escalation Active</span>
        </div>
      </div>

      {/* Citation Detail Modal */}
      {activeCitationModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800 text-xs font-bold font-mono">
                  {activeCitationModal.badge}
                </span>
                <span className="text-xs font-bold text-slate-200">
                  {activeCitationModal.authority}
                </span>
              </div>
              <button
                onClick={() => setActiveCitationModal(null)}
                className="text-slate-400 hover:text-slate-200 text-xs font-bold"
              >
                Close
              </button>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-semibold text-slate-100">
                {activeCitationModal.title}
              </div>
              <p className="text-xs text-slate-400 leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800">
                "{activeCitationModal.excerpt}"
              </p>
            </div>

            <div className="flex items-center justify-between pt-2 text-xs">
              <a
                href={activeCitationModal.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-teal-400 hover:text-teal-300 font-medium"
              >
                <span>View Official Clinical Guideline</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
              <button
                onClick={() => setActiveCitationModal(null)}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-medium"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Hybrid Cloud LLM Configuration Modal */}
      {isLlmModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-5 space-y-4 shadow-2xl text-xs">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-teal-400" />
                <span className="text-sm font-bold text-slate-100">
                  Hybrid Cloud LLM & PHI Scrubber Connector
                </span>
              </div>
              <button
                onClick={() => setIsLlmModalOpen(false)}
                className="text-slate-400 hover:text-slate-200 font-bold"
              >
                Close
              </button>
            </div>

            <div className="p-3 rounded-lg bg-emerald-950/50 border border-emerald-800/70 text-emerald-200 space-y-1">
              <div className="font-bold flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>HIPAA Safe Harbor PHI Scrubber Enforced Pre-Transmission</span>
              </div>
              <p className="text-[11px] text-emerald-300/80 leading-relaxed">
                All patient names, NIC/SSN numbers, phone numbers, emails, and dates of birth (in English, Sinhala, and
                Singlish) are deterministically scrubbed BEFORE any Cloud LLM call. If no cloud API key is set or
                network is offline, the system automatically falls back to the 100% Local Deterministic Clinical Engine.
              </p>
            </div>

            <form onSubmit={handleSaveLlmConfig} className="space-y-3">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">
                  Active Hybrid Inference Mode
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-teal-500"
                >
                  <option value="auto">Auto (Use Configured Cloud LLM or Local Fallback)</option>
                  <option value="gemini">Google Gemini 1.5 Pro (gemini-1.5-pro)</option>
                  <option value="anthropic">Anthropic Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)</option>
                  <option value="openai">OpenAI GPT-4o (gpt-4o)</option>
                  <option value="local">100% Local Deterministic RAG + Singlish NLU Only</option>
                </select>
              </div>

              <div className="space-y-2 pt-1">
                <div>
                  <label className="block text-slate-400 text-[11px] mb-1">
                    Google Gemini API Key {llmStatus?.providers_configured?.gemini && "(Configured ✓)"}
                  </label>
                  <input
                    type="password"
                    value={geminiKey}
                    onChange={(e) => setGeminiKey(e.target.value)}
                    placeholder="AIzaSy... (Leave blank to keep existing)"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 text-[11px] mb-1">
                    Anthropic Claude API Key {llmStatus?.providers_configured?.anthropic && "(Configured ✓)"}
                  </label>
                  <input
                    type="password"
                    value={anthropicKey}
                    onChange={(e) => setAnthropicKey(e.target.value)}
                    placeholder="sk-ant-... (Leave blank to keep existing)"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 text-[11px] mb-1">
                    OpenAI GPT-4o API Key {llmStatus?.providers_configured?.openai && "(Configured ✓)"}
                  </label>
                  <input
                    type="password"
                    value={openaiKey}
                    onChange={(e) => setOpenaiKey(e.target.value)}
                    placeholder="sk-proj-... (Leave blank to keep existing)"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-teal-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-800">
                <span className="text-[11px] text-slate-400 font-mono">
                  Active: {llmStatus?.active_model || "MedGuard-Local-Deterministic-RAG"}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setIsLlmModalOpen(false)}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={savingLlmConfig}
                    className="px-4 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-semibold cursor-pointer"
                  >
                    {savingLlmConfig ? "Applying..." : "Apply Hybrid Config"}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Telemedicine & Specialist Doctor Appointment Booking Modal */}
      <AppointmentBookingModal
        isOpen={isBookingModalOpen}
        onClose={() => setIsBookingModalOpen(false)}
        specialtyHint={bookingHeadline}
        clinicalContext={bookingSummary}
        triageAcuity={bookingAcuity}
      />
    </div>
  );
}
