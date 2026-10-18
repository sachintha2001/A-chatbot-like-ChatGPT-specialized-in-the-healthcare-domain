"use client";

import { useState, useEffect } from "react";
import {
  X,
  Search,
  BookOpen,
  AlertTriangle,
  FileText,
  Activity,
  Layers,
  CheckCircle,
  ExternalLink,
  Filter
} from "lucide-react";
import { PathologySummaryItem, PathologyDetailItem } from "@/lib/types";
import { fetchPathologies, fetchPathologyByIcd11, fetchSpecialties } from "@/lib/api";

interface OntologyBrowserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectCondition?: (name: string) => void;
}

export function OntologyBrowserModal({
  isOpen,
  onClose,
  onSelectCondition
}: OntologyBrowserModalProps) {
  const [pathologies, setPathologies] = useState<PathologySummaryItem[]>([]);
  const [specialties, setSpecialties] = useState<Record<string, number>>({});
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedPathology, setSelectedPathology] = useState<PathologyDetailItem | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    const loadData = async () => {
      setLoading(true);
      try {
        const [specData, listData] = await Promise.all([
          fetchSpecialties(),
          fetchPathologies({ limit: 60 })
        ]);
        setSpecialties(specData.specialties || {});
        setPathologies(listData);
      } catch (e) {
        // Fallback gracefully
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isOpen]);

  const handleSearch = async (queryText: string, specialtyFilter?: string) => {
    setSearchQuery(queryText);
    const spec = specialtyFilter !== undefined ? specialtyFilter : selectedSpecialty;
    try {
      setLoading(true);
      const data = await fetchPathologies({
        search: queryText || undefined,
        specialty: spec || undefined,
        limit: 60
      });
      setPathologies(data);
    } catch (e) {
      //
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPathology = async (icd11Code: string) => {
    setLoadingDetail(true);
    try {
      const detail = await fetchPathologyByIcd11(icd11Code);
      setSelectedPathology(detail);
    } catch (e) {
      //
    } finally {
      setLoadingDetail(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl h-[85vh] flex flex-col shadow-2xl overflow-hidden text-slate-100">
        {/* Modal Header */}
        <div className="px-6 py-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-slate-100 flex items-center gap-2">
                WHO ICD-11 Multi-Specialty Clinical Knowledge Ontology
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800">
                  {pathologies.length} Verified Pathologies
                </span>
              </div>
              <div className="text-xs text-slate-400">
                Authoritative Relational Disease Registry & Cardinal Clinical Signatures
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search & Filter Bar */}
        <div className="p-4 bg-slate-900 border-b border-slate-800 flex flex-wrap gap-3 items-center shrink-0">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search by disease name, ICD-11 code, or symptoms..."
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 focus:border-teal-500 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={selectedSpecialty}
              onChange={(e) => {
                setSelectedSpecialty(e.target.value);
                handleSearch(searchQuery, e.target.value);
              }}
              className="bg-slate-950 border border-slate-800 focus:border-teal-500 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none"
            >
              <option value="">All Clinical Specialties (14)</option>
              {Object.keys(specialties).map((spec) => (
                <option key={spec} value={spec}>
                  {spec} ({specialties[spec]})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Content Split Pane */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left: Disease List */}
          <div className="w-2/5 border-r border-slate-800 overflow-y-auto p-4 space-y-2">
            {loading ? (
              <div className="text-center py-10 text-xs text-slate-500">
                Loading clinical ontology records...
              </div>
            ) : pathologies.length === 0 ? (
              <div className="text-center py-10 text-xs text-slate-500">
                No pathologies match your search criteria.
              </div>
            ) : (
              pathologies.map((item) => {
                const isSelected = selectedPathology?.icd11_code === item.icd11_code;
                const isEmergency = item.baseline_acuity === "EMERGENCY";

                return (
                  <div
                    key={item.id}
                    onClick={() => handleSelectPathology(item.icd11_code)}
                    className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                      isSelected
                        ? "bg-teal-950/40 border-teal-500 shadow-sm"
                        : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-800/40"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="font-semibold text-slate-200">{item.clinical_name}</div>
                      <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-teal-400 border border-slate-700 shrink-0 font-bold">
                        {item.icd11_code}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-400 mt-1">{item.medical_specialty}</div>

                    <div className="mt-2 flex items-center justify-between text-[10px]">
                      <span
                        className={`px-1.5 py-0.5 rounded font-bold uppercase ${
                          isEmergency
                            ? "bg-rose-950 text-rose-400 border border-rose-800"
                            : "bg-slate-800 text-slate-400"
                        }`}
                      >
                        {item.baseline_acuity}
                      </span>
                      <span className="text-rose-400">
                        {item.red_flag_count} Red Flags
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Right: Disease Detail View */}
          <div className="w-3/5 overflow-y-auto p-6 bg-slate-950/40">
            {loadingDetail ? (
              <div className="text-center py-20 text-xs text-slate-400">
                Loading clinical dossier...
              </div>
            ) : selectedPathology ? (
              <div className="space-y-6 text-xs text-slate-300">
                {/* Header Title */}
                <div className="border-b border-slate-800 pb-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-base font-bold text-slate-100">
                        {selectedPathology.clinical_name}
                      </h3>
                      <div className="text-xs text-teal-400 mt-0.5">
                        {selectedPathology.medical_specialty}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono text-xs font-bold text-teal-400 bg-teal-950/80 px-2.5 py-1 rounded border border-teal-800">
                        ICD-11: {selectedPathology.icd11_code}
                      </div>
                      {selectedPathology.icd10_code && (
                        <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                          ICD-10: {selectedPathology.icd10_code}
                        </div>
                      )}
                    </div>
                  </div>

                  {selectedPathology.common_aliases && selectedPathology.common_aliases.length > 0 && (
                    <div className="mt-2 text-[11px] text-slate-400 flex flex-wrap gap-1">
                      <span className="font-semibold text-slate-500">Aliases:</span>
                      {selectedPathology.common_aliases.join(", ")}
                    </div>
                  )}
                </div>

                {/* Pathophysiology */}
                <div>
                  <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-teal-400" />
                    Pathophysiological Mechanism
                  </h4>
                  <p className="leading-relaxed bg-slate-900 p-3.5 rounded-lg border border-slate-800 text-slate-300">
                    {selectedPathology.pathophysiology_overview}
                  </p>
                </div>

                {/* Cardinal Symptoms */}
                <div>
                  <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Cardinal Symptoms (Weighted Presentation)
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1.5">
                      <div className="text-[10px] font-bold text-teal-400 uppercase">
                        Primary Cardinal Symptoms
                      </div>
                      <ul className="space-y-1 text-slate-300 text-[11px]">
                        {selectedPathology.cardinal_symptoms?.primary?.map((s, idx) => (
                          <li key={idx} className="flex items-center justify-between gap-1">
                            <span>- {s.symptom}</span>
                            <span className="text-[10px] font-mono text-teal-400 font-bold shrink-0">
                              {(s.weight * 100).toFixed(0)}%
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1.5">
                      <div className="text-[10px] font-bold text-slate-400 uppercase">
                        Secondary Presentations
                      </div>
                      <ul className="space-y-1 text-slate-400 text-[11px]">
                        {selectedPathology.cardinal_symptoms?.secondary?.map((s, idx) => (
                          <li key={idx} className="flex items-center justify-between gap-1">
                            <span>- {s.symptom}</span>
                            <span className="text-[10px] font-mono text-slate-500 shrink-0">
                              {(s.weight * 100).toFixed(0)}%
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Red Flags */}
                <div>
                  <h4 className="text-[11px] font-bold text-rose-400 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                    Deterministic Red-Flag Triggers (Emergency Escalation)
                  </h4>
                  <ul className="p-3.5 rounded-lg bg-rose-950/20 border border-rose-900/50 space-y-1 text-rose-300">
                    {selectedPathology.red_flag_criteria?.map((rf, idx) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-rose-500 font-bold">-</span>
                        <span>{rf}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Diagnostic Workup */}
                <div>
                  <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                    Standard Diagnostic Workup
                  </h4>
                  <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                    <div>
                      <span className="font-semibold text-teal-400 text-[11px]">Initial Labs: </span>
                      <span className="text-slate-300">
                        {selectedPathology.diagnostic_workup?.initial_labs?.join("; ")}
                      </span>
                    </div>
                    {selectedPathology.diagnostic_workup?.imaging_ecg?.length > 0 && (
                      <div>
                        <span className="font-semibold text-teal-400 text-[11px]">Imaging & ECG: </span>
                        <span className="text-slate-300">
                          {selectedPathology.diagnostic_workup?.imaging_ecg?.join("; ")}
                        </span>
                      </div>
                    )}
                    {selectedPathology.diagnostic_workup?.confirmatory_tests?.length > 0 && (
                      <div>
                        <span className="font-semibold text-teal-400 text-[11px]">Confirmatory Tests: </span>
                        <span className="text-slate-300">
                          {selectedPathology.diagnostic_workup?.confirmatory_tests?.join("; ")}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Evidence-Based Management */}
                <div>
                  <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                    Evidence-Based Clinical Management
                  </h4>
                  <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                    <div>
                      <span className="font-semibold text-teal-400 text-[11px]">Pharmacotherapy & Protocols: </span>
                      <span className="text-slate-300">
                        {selectedPathology.evidence_based_management?.pharmacotherapy?.join("; ")}
                      </span>
                    </div>
                    <div>
                      <span className="font-semibold text-rose-400 text-[11px]">Strict Contraindications: </span>
                      <span className="text-rose-300">
                        {selectedPathology.evidence_based_management?.contraindications?.join("; ")}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Source Metadata */}
                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
                  <div>
                    Source: {selectedPathology.source_metadata?.issuing_authority} (
                    {selectedPathology.source_metadata?.publication_year})
                  </div>
                  {selectedPathology.source_metadata?.source_url && (
                    <a
                      href={selectedPathology.source_metadata.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-teal-400 hover:text-teal-300 inline-flex items-center gap-1 font-medium"
                    >
                      <span>Clinical Guideline</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-24 text-slate-500 space-y-2">
                <BookOpen className="w-10 h-10 mx-auto text-slate-600" />
                <p className="text-xs">Select any pathology from the left panel to inspect full clinical details.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
