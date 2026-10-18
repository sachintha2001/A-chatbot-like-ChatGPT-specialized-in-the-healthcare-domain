"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send,
  AlertTriangle,
  ShieldAlert,
  Activity,
  FileText,
  ExternalLink,
  RotateCcw,
  Sparkles,
  Stethoscope,
  ChevronRight,
  PhoneCall,
  Info
} from "lucide-react";
import {
  StreamCitation,
  StreamBadgeData,
  StreamStatusData,
  TriageAcuityLevel,
  TriageWorkflowState
} from "@/lib/types";
import { streamClinicalChat } from "@/lib/api";
import { useLanguage } from "@/lib/LanguageContext";

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

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamedText, activeStatus]);

  const handleSend = async (messageToSend?: string) => {
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

          const assistantMsg: ChatMessage = {
            id: `assistant-${Date.now()}`,
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
      <div className={`p-3.5 rounded-lg border mb-3.5 ${badgeBg} shadow-md`}>
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
          {isEmerg && (
            <a
              href="tel:911"
              className="inline-flex items-center gap-1.5 px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-bold shrink-0 transition-colors shadow-sm"
            >
              <PhoneCall className="w-3.5 h-3.5" />
              Call 911 / 1990
            </a>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 rounded-xl border border-slate-800 shadow-2xl overflow-hidden">
      {/* Top Header */}
      <div className="px-5 py-3.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
            <Stethoscope className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              SOCRATES Clinical Triage Engine
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800">
                ICD-11 Real-Time SSE
              </span>
            </div>
            <div className="text-xs text-slate-400">
              Protocolized Symptom Assessment & Federated Ontology Integration
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onOpenOntology && (
            <button
              onClick={onOpenOntology}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 flex items-center gap-1.5 transition-colors"
            >
              <FileText className="w-3.5 h-3.5 text-teal-400" />
              ICD-11 Ontology (44 Diseases)
            </button>
          )}
          <button
            onClick={resetChat}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
            title="Reset Conversation"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {messages.length === 0 && !isStreaming && (
          <div className="max-w-xl mx-auto my-10 text-center space-y-4">
            <div className="w-12 h-12 mx-auto rounded-full bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
              <Sparkles className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-slate-100">
              Clinical Conversational Triage
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              Describe your symptoms naturally in English or Sinhala. The triage engine will screen for
              life-threatening red flags, ask targeted SOCRATES clarifying questions, and deliver evidence-grounded
              assessments mapped to official WHO ICD-11 codes.
            </p>
            <div className="pt-2 flex flex-wrap justify-center gap-2">
              <button
                onClick={() => handleSend("I have a persistent headache")}
                className="text-xs px-3 py-1.5 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
              >
                Intake: "I have a persistent headache"
              </button>
              <button
                onClick={() => handleSend("Sharp left-sided chest pain worse when breathing")}
                className="text-xs px-3 py-1.5 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
              >
                Respiratory: "Sharp chest pain worse on breathing"
              </button>
              <button
                onClick={() => handleSend("Crushing central chest pain radiating to left arm and jaw")}
                className="text-xs px-3 py-1.5 rounded-full bg-rose-950/60 hover:bg-rose-900/60 border border-rose-800 text-rose-300 transition-colors"
              >
                Red Flag: "Crushing chest pain radiating to left arm"
              </button>
              <button
                onClick={() => handleSend("මට දින 3ක සිට තද උණ සහ ඇඟපත වේදනාව තියෙනවා")}
                className="text-xs px-3 py-1.5 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors font-sans"
              >
                Sinhala: "මට දින 3ක සිට තද උණ සහ ඇඟපත වේදනාව"
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
            <div className="flex items-center gap-2 mb-1 text-[11px] text-slate-400">
              <span>{msg.sender === "PATIENT" ? "Patient Narrative" : "Clinical Assessment"}</span>
              <span>{msg.timestamp}</span>
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
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isStreaming}
            placeholder="Type clinical symptoms, onset, character, or questions in English or Sinhala..."
            className="flex-1 bg-slate-950 border border-slate-700 focus:border-teal-500 rounded-lg px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none transition-colors disabled:opacity-50"
          />
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
    </div>
  );
}
