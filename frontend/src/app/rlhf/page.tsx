"use client";

import { useState, useEffect } from "react";
import {
  Brain,
  CheckCircle,
  AlertTriangle,
  Download,
  Star,
  FileEdit,
  RefreshCw,
  Search,
  Filter
} from "lucide-react";
import { RLHFPendingItem, RLHFReviewItem } from "@/lib/types";
import {
  fetchRLHFQueue,
  submitRLHFReview,
  fetchRLHFReviews,
  exportFineTuningDataset
} from "@/lib/api";

export default function ClinicianRLHFPage() {
  const [activeTab, setActiveTab] = useState<"queue" | "history" | "export">("queue");
  const [queue, setQueue] = useState<RLHFPendingItem[]>([]);
  const [history, setHistory] = useState<RLHFReviewItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<RLHFPendingItem | null>(null);

  // Form State
  const [rating, setRating] = useState<number>(5);
  const [hallucination, setHallucination] = useState(false);
  const [safetyViolation, setSafetyViolation] = useState(false);
  const [redFlagOmission, setRedFlagOmission] = useState(false);
  const [revisedText, setRevisedText] = useState("");
  const [clinicianNotes, setClinicianNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // Export State
  const [exportFormat, setExportFormat] = useState<"openai_chat" | "llama_alpaca">("openai_chat");
  const [exportedData, setExportedData] = useState<any[] | null>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [queueData, historyData] = await Promise.all([
        fetchRLHFQueue(),
        fetchRLHFReviews()
      ]);
      setQueue(queueData);
      setHistory(historyData);
      if (queueData.length > 0 && !selectedItem) {
        setSelectedItem(queueData[0]);
      }
    } catch (e: any) {
      setStatusMessage(e.message || "Failed to load RLHF dataset queue.");
    }
  };

  const handleSelectQueueItem = (item: RLHFPendingItem) => {
    setSelectedItem(item);
    setRating(5);
    setHallucination(false);
    setSafetyViolation(false);
    setRedFlagOmission(false);
    setRevisedText("");
    setClinicianNotes("");
    setStatusMessage(null);
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem) return;

    setSubmitting(true);
    setStatusMessage(null);

    try {
      await submitRLHFReview({
        message_id: selectedItem.message_id,
        clinical_accuracy_rating: rating,
        hallucination_flag: hallucination,
        safety_guideline_violation: safetyViolation,
        omission_of_red_flag_symptom: redFlagOmission,
        revised_completion_text: revisedText.trim() ? revisedText.trim() : null,
        clinician_notes: clinicianNotes.trim() ? clinicianNotes.trim() : null
      });

      setStatusMessage("Clinician review registered successfully in alignment catalog.");
      // Refresh data
      await loadData();
      if (queue.length > 1) {
        setSelectedItem(queue[1]);
      } else {
        setSelectedItem(null);
      }
    } catch (err: any) {
      setStatusMessage(err.message || "Failed to submit review.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await exportFineTuningDataset(exportFormat);
      setExportedData(res.data);
    } catch (err: any) {
      setStatusMessage(err.message || "Export failed.");
    } finally {
      setExporting(false);
    }
  };

  const downloadJsonl = () => {
    if (!exportedData || exportedData.length === 0) return;
    const jsonlLines = exportedData.map((d) => JSON.stringify(d)).join("\n");
    const blob = new Blob([jsonlLines], { type: "application/x-jsonlines;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `medguard_finetune_${exportFormat}_${Date.now()}.jsonl`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-5">
      {/* Page Header */}
      <div className="clinical-dark-preserve bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0D7490] border border-teal-500/30 rounded-2xl p-5 flex flex-wrap items-center justify-between shadow-clinical-elevated text-white">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 border border-teal-300/30 flex items-center justify-center text-teal-300 shrink-0">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold text-white">
              Clinician RLHF Review Portal & Alignment Engine
            </h1>
            <p className="text-xs text-cyan-100/80 mt-0.5 max-w-3xl">
              Verified Healthcare Provider workspace for evaluating model accuracy (1–5 Likert), flagging clinical
              hallucinations, providing expert rewrites, and curating supervised fine-tuning datasets.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 mt-3 sm:mt-0">
          <button
            onClick={loadData}
            className="inline-flex items-center px-3.5 py-2 text-xs font-bold text-white bg-white/15 hover:bg-white/25 rounded-xl border border-white/25 transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            Refresh Queue
          </button>
        </div>
      </div>


      {/* Tabs */}
      <div className="border-b border-slate-200 flex space-x-4 text-xs font-semibold">
        <button
          onClick={() => setActiveTab("queue")}
          className={`pb-2.5 px-2 border-b-2 transition-colors ${
            activeTab === "queue"
              ? "border-clinical-teal text-clinical-teal font-bold"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          Pending Review Queue ({queue.length})
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`pb-2.5 px-2 border-b-2 transition-colors ${
            activeTab === "history"
              ? "border-clinical-teal text-clinical-teal font-bold"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          Historical Review Registry ({history.length})
        </button>
        <button
          onClick={() => setActiveTab("export")}
          className={`pb-2.5 px-2 border-b-2 transition-colors ${
            activeTab === "export"
              ? "border-clinical-teal text-clinical-teal font-bold"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          Dataset Export (.jsonl)
        </button>
      </div>

      {/* Tab 1: Queue Review Workspace */}
      {activeTab === "queue" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Queue Sidebar */}
          <div className="lg:col-span-5 bg-white border border-slate-200 rounded-lg overflow-hidden shadow-xs flex flex-col h-[700px]">
            <div className="bg-slate-100 px-4 py-3 border-b border-slate-200 text-xs font-bold text-slate-700 flex justify-between items-center">
              <span>Unreviewed Encounters</span>
              <span className="font-mono text-[11px] text-slate-500">{queue.length} Pending</span>
            </div>

            <div className="overflow-y-auto divide-y divide-slate-200 flex-1">
              {queue.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">
                  No interactions currently pending clinician review.
                </div>
              ) : (
                queue.map((item) => {
                  const isSelected = selectedItem?.message_id === item.message_id;
                  return (
                    <div
                      key={item.message_id}
                      onClick={() => handleSelectQueueItem(item)}
                      className={`p-3.5 cursor-pointer text-xs transition-colors ${
                        isSelected
                          ? "bg-teal-50/70 border-l-4 border-clinical-teal"
                          : "hover:bg-slate-50"
                      }`}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-mono text-[11px] font-bold text-slate-600">
                          {item.message_id.slice(0, 8)}
                        </span>
                        <span className="text-[10px] text-slate-400">
                          {new Date(item.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </span>
                      </div>
                      <p className="font-medium text-slate-800 line-clamp-2 mb-1.5">
                        {item.patient_query_redacted}
                      </p>
                      <div className="flex items-center space-x-2 text-[10px] text-slate-500 font-mono">
                        <span>Groundedness: {Math.round(item.groundedness_score * 100)}%</span>
                        <span>•</span>
                        <span>Citations: {item.clinical_citations.length}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Clinician Evaluation Form */}
          <div className="lg:col-span-7 bg-white border border-slate-200 rounded-lg p-5 shadow-xs overflow-y-auto max-h-[700px]">
            {selectedItem ? (
              <form onSubmit={handleSubmitReview} className="space-y-4">
                <div className="border-b border-slate-200 pb-3">
                  <h2 className="text-sm font-bold text-clinical-navy">Interaction Review & Calibration</h2>
                  <span className="text-xs text-slate-500 font-mono">
                    Encounter Message ID: {selectedItem.message_id}
                  </span>
                </div>

                {/* Patient Query Prompt */}
                <div>
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                    De-Identified Patient Narrative (Prompt)
                  </span>
                  <div className="p-3 bg-slate-50 border border-slate-200 rounded text-xs text-slate-800 font-medium">
                    {selectedItem.patient_query_redacted}
                  </div>
                </div>

                {/* Model Output */}
                <div>
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                    Model Generated Guidance (Completion)
                  </span>
                  <div className="p-3 bg-slate-50 border border-slate-200 rounded text-xs text-slate-800 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                    {selectedItem.assistant_response}
                  </div>
                </div>

                {/* Clinical Rating 1-5 */}
                <div className="pt-2 border-t border-slate-200">
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">
                    Clinical Accuracy Rating (Likert 1–5 Scale)
                  </label>
                  <div className="flex items-center space-x-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setRating(star)}
                        className={`flex items-center px-3 py-1.5 rounded border text-xs font-bold transition-colors ${
                          rating >= star
                            ? "bg-teal-50 border-teal-500 text-teal-800"
                            : "bg-white border-slate-200 text-slate-400"
                        }`}
                      >
                        <Star className="w-3.5 h-3.5 mr-1 fill-current" />
                        {star}
                      </button>
                    ))}
                    <span className="text-xs text-slate-500 ml-2 font-medium">
                      {rating === 5 && "Full Evidence Alignment (Publication Grade)"}
                      {rating === 4 && "Clinically Accurate with Minor Style Deviation"}
                      {rating === 3 && "Partially Accurate but Suboptimal Context"}
                      {rating === 2 && "Clinically Deficient or Missing Red Flags"}
                      {rating === 1 && "Dangerous / Factually Contradictory"}
                    </span>
                  </div>
                </div>

                {/* Error Typology Flags */}
                <div className="space-y-2 pt-2 border-t border-slate-200 text-xs">
                  <span className="font-bold text-slate-700 block">Alignment Deficit Typology:</span>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <label className="flex items-center space-x-2 bg-slate-50 p-2 rounded border border-slate-200 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={hallucination}
                        onChange={(e) => setHallucination(e.target.checked)}
                        className="rounded text-clinical-teal"
                      />
                      <span className="font-medium text-slate-700">Hallucination Flag</span>
                    </label>

                    <label className="flex items-center space-x-2 bg-slate-50 p-2 rounded border border-slate-200 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={safetyViolation}
                        onChange={(e) => setSafetyViolation(e.target.checked)}
                        className="rounded text-clinical-teal"
                      />
                      <span className="font-medium text-slate-700">Safety Violation</span>
                    </label>

                    <label className="flex items-center space-x-2 bg-slate-50 p-2 rounded border border-slate-200 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={redFlagOmission}
                        onChange={(e) => setRedFlagOmission(e.target.checked)}
                        className="rounded text-clinical-teal"
                      />
                      <span className="font-medium text-slate-700">Red Flag Omission</span>
                    </label>
                  </div>
                </div>

                {/* Ground Truth Clinician Rewritten Completion */}
                <div className="pt-2 border-t border-slate-200">
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Clinician Rewritten Ground Truth Completion (For Fine-Tuning Calibration)
                  </label>
                  <textarea
                    rows={4}
                    value={revisedText}
                    onChange={(e) => setRevisedText(e.target.value)}
                    placeholder="Provide optimal evidence-grounded response text if model output was suboptimal..."
                    className="w-full border border-slate-300 rounded p-2.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-clinical-teal"
                  />
                  <span className="text-[10px] text-slate-400 mt-0.5 block">
                    Rewritten completions replace model completions when exporting fine-tuning training datasets.
                  </span>
                </div>

                {/* Clinician Notes */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Governance & Protocol Notes
                  </label>
                  <input
                    type="text"
                    value={clinicianNotes}
                    onChange={(e) => setClinicianNotes(e.target.value)}
                    placeholder="Optional notes for institutional audit review..."
                    className="w-full border border-slate-300 rounded px-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-clinical-teal"
                  />
                </div>

                {statusMessage && (
                  <div className="p-2.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded text-xs">
                    {statusMessage}
                  </div>
                )}

                <div className="pt-3 border-t border-slate-200 flex justify-end">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-5 py-2 bg-clinical-teal hover:bg-clinical-teal-hover text-white rounded font-bold text-xs uppercase tracking-wide transition-colors shadow-xs"
                  >
                    {submitting ? "Registering..." : "Submit Clinical Alignment Review"}
                  </button>
                </div>
              </form>
            ) : (
              <div className="h-full flex items-center justify-center text-center text-xs text-slate-400">
                Select an interaction from the queue to start clinician review.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Historical Review Registry */}
      {activeTab === "history" && (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left clinical-table">
              <thead>
                <tr>
                  <th>Encounter ID</th>
                  <th>Reviewing Clinician</th>
                  <th>Likert Rating</th>
                  <th>Typology Flags</th>
                  <th>Rewritten</th>
                  <th>Export Status</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {history.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-8 text-slate-400">
                      No clinician reviews have been registered yet.
                    </td>
                  </tr>
                ) : (
                  history.map((h) => (
                    <tr key={h.feedback_id} className="hover:bg-slate-50">
                      <td className="font-mono text-xs font-semibold">{h.message_id.slice(0, 8)}</td>
                      <td className="font-medium text-xs text-slate-800">{h.clinician_name}</td>
                      <td>
                        <span className="inline-flex items-center font-bold text-xs text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                          {h.clinical_accuracy_rating} / 5
                        </span>
                      </td>
                      <td className="space-x-1">
                        {h.hallucination_flag && (
                          <span className="px-1.5 py-0.5 bg-red-100 text-red-800 rounded text-[10px] font-bold">
                            Hallucination
                          </span>
                        )}
                        {h.safety_guideline_violation && (
                          <span className="px-1.5 py-0.5 bg-red-100 text-red-800 rounded text-[10px] font-bold">
                            Safety
                          </span>
                        )}
                        {!h.hallucination_flag && !h.safety_guideline_violation && (
                          <span className="text-slate-400 text-xs">None</span>
                        )}
                      </td>
                      <td>
                        {h.revised_completion_text ? (
                          <span className="text-emerald-700 font-semibold text-xs">Yes (Ground Truth)</span>
                        ) : (
                          <span className="text-slate-400 text-xs">No</span>
                        )}
                      </td>
                      <td>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">
                          {h.export_status}
                        </span>
                      </td>
                      <td className="text-xs text-slate-500 font-mono">
                        {new Date(h.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Dataset Exporter */}
      {activeTab === "export" && (
        <div className="bg-white border border-slate-200 rounded-lg p-6 space-y-5 shadow-xs">
          <div className="border-b border-slate-200 pb-3">
            <h2 className="text-sm font-bold text-clinical-navy">Supervised Fine-Tuning (SFT) Dataset Exporter</h2>
            <p className="text-xs text-slate-500 mt-1">
              Extracts clinician-aligned pairs (Rating &gt;= 4, incorporating clinician ground-truth rewrites) formatted
              for instruction fine-tuning.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-4 bg-slate-50 p-4 rounded border border-slate-200 text-xs">
            <div>
              <label className="block font-bold text-slate-700 mb-1">Format Specification</label>
              <select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value as any)}
                className="border border-slate-300 rounded px-3 py-1.5 bg-white text-slate-900"
              >
                <option value="openai_chat">OpenAI ChatML JSONL</option>
                <option value="llama_alpaca">Llama / Alpaca Instruction JSONL</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={handleExport}
                disabled={exporting}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded font-bold transition-colors"
              >
                {exporting ? "Generating..." : "Generate Export Bundle"}
              </button>
            </div>

            {exportedData && exportedData.length > 0 && (
              <div className="flex items-end ml-auto">
                <button
                  onClick={downloadJsonl}
                  className="px-4 py-2 bg-clinical-teal hover:bg-clinical-teal-hover text-white rounded font-bold flex items-center space-x-1.5 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download .jsonl ({exportedData.length} pairs)</span>
                </button>
              </div>
            )}
          </div>

          {exportedData && (
            <div>
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                JSONL Output Preview ({exportedData.length} records generated)
              </span>
              <pre className="p-4 bg-slate-900 text-emerald-400 rounded text-xs font-mono overflow-x-auto max-h-96">
                {exportedData.slice(0, 3).map((d) => JSON.stringify(d, null, 2)).join("\n\n")}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
