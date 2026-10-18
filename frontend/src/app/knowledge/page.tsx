"use client";

import { useState, useEffect } from "react";
import {
  Layers,
  Search,
  Filter,
  FileText,
  Activity,
  AlertTriangle,
  ExternalLink,
  BookOpen,
  Globe,
  Pill,
  Sparkles
} from "lucide-react";
import { PathologySummaryItem, PathologyDetailItem } from "@/lib/types";
import {
  fetchPathologies,
  fetchPathologyByIcd11,
  fetchSpecialties,
  fetchFederatedCondition,
  fetchFederatedMedication
} from "@/lib/api";
import { useLanguage } from "@/lib/LanguageContext";

export default function KnowledgeOntologyPage() {
  const { language } = useLanguage();
  const [activeTab, setActiveTab] = useState<"LOCAL_ONTOLOGY" | "FEDERATED_SEARCH">("LOCAL_ONTOLOGY");

  // Local Ontology State
  const [pathologies, setPathologies] = useState<PathologySummaryItem[]>([]);
  const [specialties, setSpecialties] = useState<Record<string, number>>({});
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedPathology, setSelectedPathology] = useState<PathologyDetailItem | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Federated Live Connectors State
  const [fedQuery, setFedQuery] = useState("");
  const [fedType, setFedType] = useState<"CONDITION" | "MEDICATION">("CONDITION");
  const [fedLoading, setFedLoading] = useState(false);
  const [fedResult, setFedResult] = useState<any>(null);

  useEffect(() => {
    const loadInitial = async () => {
      setLoading(true);
      try {
        const [specData, listData] = await Promise.all([
          fetchSpecialties(),
          fetchPathologies({ limit: 60 })
        ]);
        setSpecialties(specData.specialties || {});
        setPathologies(listData);
        if (listData.length > 0) {
          const firstDetail = await fetchPathologyByIcd11(listData[0].icd11_code);
          setSelectedPathology(firstDetail);
        }
      } catch (e) {
        //
      } finally {
        setLoading(false);
      }
    };
    loadInitial();
  }, []);

  const handleFilter = async (queryText: string, specFilter?: string) => {
    setSearchQuery(queryText);
    const spec = specFilter !== undefined ? specFilter : selectedSpecialty;
    setLoading(true);
    try {
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

  const handleFederatedQuery = async () => {
    if (!fedQuery.trim() || fedLoading) return;
    setFedLoading(true);
    setFedResult(null);
    try {
      if (fedType === "CONDITION") {
        const res = await fetchFederatedCondition(fedQuery.trim());
        setFedResult(res);
      } else {
        const res = await fetchFederatedMedication(fedQuery.trim());
        setFedResult(res);
      }
    } catch (e: any) {
      setFedResult({ error: e.message || "Failed to query live federated source" });
    } finally {
      setFedLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-h-[920px] bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-2xl text-slate-100">
      {/* Header bar */}
      <div className="px-6 py-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-100 flex items-center gap-2">
              Clinical Knowledge & Disease Ontology Pipeline
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800">
                WHO ICD-11 Certified
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Relational Pathology Models, Cardinal Symptom Signatures, and Federated Medical Connectors
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab("LOCAL_ONTOLOGY")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
              activeTab === "LOCAL_ONTOLOGY"
                ? "bg-teal-600 text-white"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Local Ontology ({pathologies.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("FEDERATED_SEARCH")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
              activeTab === "FEDERATED_SEARCH"
                ? "bg-teal-600 text-white"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Federated Live Connectors</span>
          </button>
        </div>
      </div>

      {/* Main Body */}
      {activeTab === "LOCAL_ONTOLOGY" ? (
        <div className="flex-1 flex flex-col min-h-0">
          {/* Filter Bar */}
          <div className="p-4 bg-slate-900 border-b border-slate-800 flex flex-wrap gap-3 items-center shrink-0">
            <div className="relative flex-1 min-w-[240px]">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleFilter(e.target.value)}
                placeholder="Search across 44+ pathologies by name, ICD-11 code, or symptoms..."
                className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 focus:border-teal-500 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none"
              />
            </div>

            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={selectedSpecialty}
                onChange={(e) => {
                  setSelectedSpecialty(e.target.value);
                  handleFilter(searchQuery, e.target.value);
                }}
                className="bg-slate-950 border border-slate-800 focus:border-teal-500 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none"
              >
                <option value="">All Specialties (14 Categories)</option>
                {Object.keys(specialties).map((spec) => (
                  <option key={spec} value={spec}>
                    {spec} ({specialties[spec]})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Split Pane: Pathology List + Pathology Detail */}
          <div className="flex-1 flex min-h-0 overflow-hidden">
            {/* List */}
            <div className="w-2/5 border-r border-slate-800 overflow-y-auto p-4 space-y-2">
              {loading ? (
                <div className="text-center py-10 text-xs text-slate-500">
                  Loading clinical ontology...
                </div>
              ) : pathologies.length === 0 ? (
                <div className="text-center py-10 text-xs text-slate-500">
                  No pathologies found matching the search criteria.
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
                          ? "bg-teal-950/50 border-teal-500 shadow-sm"
                          : "bg-slate-900/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-800/50"
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
                        <span className="text-rose-400">{item.red_flag_count} Red Flags</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Detail */}
            <div className="w-3/5 overflow-y-auto p-6 bg-slate-950/40">
              {loadingDetail ? (
                <div className="text-center py-20 text-xs text-slate-400">
                  Loading clinical dossier...
                </div>
              ) : selectedPathology ? (
                <div className="space-y-6 text-xs text-slate-300">
                  {/* Title & Codes */}
                  <div className="border-b border-slate-800 pb-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-lg font-bold text-slate-100">
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
                        <span className="font-semibold text-slate-500">Aliases / Synonyms:</span>
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
                      Cardinal Symptoms (Weighted Clinical Presentation)
                    </h4>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                        <div className="text-[10px] font-bold text-teal-400 uppercase">
                          Primary Cardinal Symptoms
                        </div>
                        <ul className="space-y-1.5 text-slate-300 text-[11px]">
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

                      <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                        <div className="text-[10px] font-bold text-slate-400 uppercase">
                          Secondary Presentations
                        </div>
                        <ul className="space-y-1.5 text-slate-400 text-[11px]">
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
                    <ul className="p-3.5 rounded-lg bg-rose-950/20 border border-rose-900/50 space-y-1.5 text-rose-300">
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
                        <span className="font-semibold text-teal-400 text-[11px]">First-Line Non-Pharmacological: </span>
                        <span className="text-slate-300">
                          {selectedPathology.evidence_based_management?.first_line_lifestyle?.join("; ")}
                        </span>
                      </div>
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
                      Authority: {selectedPathology.source_metadata?.issuing_authority} (
                      {selectedPathology.source_metadata?.publication_year}) -{" "}
                      {selectedPathology.source_metadata?.guideline_title}
                    </div>
                    {selectedPathology.source_metadata?.source_url && (
                      <a
                        href={selectedPathology.source_metadata.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-teal-400 hover:text-teal-300 inline-flex items-center gap-1 font-medium"
                      >
                        <span>Verified Guideline</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      ) : (
        /* FEDERATED CONNECTORS LIVE SEARCH TAB */
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="max-w-2xl mx-auto space-y-4">
            <div>
              <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Globe className="w-4 h-4 text-teal-400" />
                Live Federated Medical Knowledge Acquisition
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Query NIH MedlinePlus, NCBI PubMed, and OpenFDA in real-time. Live results are normalized,
                indexed into the local vector store, and cached so the ontology grows autonomously.
              </p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setFedType("CONDITION")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  fedType === "CONDITION"
                    ? "bg-teal-600 text-white"
                    : "bg-slate-900 text-slate-400 border border-slate-800"
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                NIH MedlinePlus + NCBI PubMed
              </button>
              <button
                onClick={() => setFedType("MEDICATION")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  fedType === "MEDICATION"
                    ? "bg-teal-600 text-white"
                    : "bg-slate-900 text-slate-400 border border-slate-800"
                }`}
              >
                <Pill className="w-3.5 h-3.5" />
                OpenFDA Drug Label Service
              </button>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={fedQuery}
                onChange={(e) => setFedQuery(e.target.value)}
                placeholder={
                  fedType === "CONDITION"
                    ? "Enter disease or symptom (e.g., Kawasaki disease, Guillain-Barre, Celiac)..."
                    : "Enter active substance or drug (e.g., Metformin, Lisinopril, Warfarin)..."
                }
                className="flex-1 bg-slate-900 border border-slate-800 focus:border-teal-500 rounded-lg px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none"
              />
              <button
                onClick={handleFederatedQuery}
                disabled={!fedQuery.trim() || fedLoading}
                className="px-5 py-2.5 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 text-white rounded-lg text-xs font-bold transition-colors cursor-pointer"
              >
                {fedLoading ? "Connecting..." : "Fetch Live"}
              </button>
            </div>

            {/* Federated Results Card */}
            {fedResult && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <span className="font-bold text-sm text-slate-100">
                    Federated Result: {fedResult.query}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800">
                    Vector Indexed Locally
                  </span>
                </div>

                {fedResult.medlineplus && (
                  <div className="space-y-1.5">
                    <div className="text-[11px] font-bold text-teal-400 uppercase">
                      NIH MedlinePlus Clinical Summary
                    </div>
                    <div className="text-xs text-slate-300 font-semibold">
                      {fedResult.medlineplus.title}
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800">
                      {fedResult.medlineplus.summary}
                    </p>
                  </div>
                )}

                {fedResult.pubmed_citations && fedResult.pubmed_citations.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <div className="text-[11px] font-bold text-teal-400 uppercase">
                      NCBI PubMed Clinical Systematic Reviews
                    </div>
                    <div className="space-y-2">
                      {fedResult.pubmed_citations.map((p: any, idx: number) => (
                        <div
                          key={idx}
                          className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-1"
                        >
                          <div className="font-semibold text-slate-200">{p.title}</div>
                          <div className="text-[11px] text-slate-400">
                            {p.lead_authors} - <span className="text-slate-300">{p.journal}</span> ({p.pub_date})
                          </div>
                          <a
                            href={p.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-teal-400 hover:text-teal-300 inline-flex items-center gap-1 text-[11px] font-medium"
                          >
                            <span>View PubMed Article (PMID: {p.pmid})</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {fedResult.fda_label && (
                  <div className="space-y-3">
                    <div className="text-xs text-slate-200 font-bold">
                      {fedResult.fda_label.generic_name} ({fedResult.fda_label.source})
                    </div>
                    {fedResult.fda_label.boxed_warning && (
                      <div className="p-3 bg-rose-950/40 border border-rose-800 rounded-lg text-rose-300 text-xs leading-relaxed">
                        <strong className="block text-rose-400 uppercase tracking-wider mb-1">
                          Boxed Warning (FDA Black Box)
                        </strong>
                        {fedResult.fda_label.boxed_warning}
                      </div>
                    )}
                    <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-1.5 text-slate-300">
                      <div>
                        <strong className="text-teal-400">Contraindications: </strong>
                        {fedResult.fda_label.contraindications}
                      </div>
                      <div>
                        <strong className="text-teal-400">Drug Interactions: </strong>
                        {fedResult.fda_label.drug_interactions}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
