"use client";

import { useState } from "react";
import { Database, Download, FileCode, CheckCircle, Search, Server } from "lucide-react";
import { fetchFHIRPatientSummary } from "@/lib/api";

export default function FHIRExportPage() {
  const [sessionId, setSessionId] = useState("");
  const [bundle, setBundle] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFetchBundle = async (idToFetch?: string) => {
    const targetId = idToFetch || sessionId;
    if (!targetId.trim()) {
      setError("Please specify a valid clinical triage session ID.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await fetchFHIRPatientSummary(targetId.trim());
      setBundle(data);
    } catch (e: any) {
      setError(e.message || "Failed to generate FHIR Document Bundle. Ensure session exists.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!bundle) return;
    const jsonStr = JSON.stringify(bundle, null, 2);
    const blob = new Blob([jsonStr], { type: "application/fhir+json;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.setAttribute("download", `fhir_bundle_${bundle.id || "export"}.json`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="clinical-dark-preserve bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0D7490] border border-teal-500/30 rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-clinical-elevated text-white">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 border border-teal-300/30 flex items-center justify-center text-teal-300 shrink-0">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold text-white">
              EHR Interoperability & HL7 FHIR R4 Bundle Exporter
            </h1>
            <p className="text-xs text-cyan-100/80 mt-0.5 max-w-3xl">
              Standardized Fast Healthcare Interoperability Resources (FHIR R4) Document Bundle export supporting
              direct ingestion into hospital Electronic Health Record (EHR) systems (Epic Systems, Cerner, NHS Spine).
            </p>
          </div>
        </div>
        <span className="text-xs font-mono bg-white/10 text-teal-200 px-3 py-1.5 rounded-xl border border-teal-300/30">
          Standard: HL7 FHIR Release 4
        </span>
      </div>


      {/* Query Bar */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
        <label className="block text-xs font-bold text-slate-700 mb-1.5">
          Triage Session Identifier
        </label>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="Enter active or past session UUID (e.g. 869dc0cd-91f9-4c2a-a4aa-7b66b017aa32)..."
            className="flex-1 border border-slate-300 rounded px-3.5 py-2 text-xs font-mono text-slate-900 focus:outline-none focus:ring-1 focus:ring-clinical-teal"
          />
          <button
            onClick={() => handleFetchBundle()}
            disabled={loading}
            className="px-5 py-2 bg-clinical-teal hover:bg-clinical-teal-hover text-white rounded font-bold text-xs uppercase tracking-wide flex items-center justify-center space-x-1.5 transition-colors shadow-xs"
          >
            <Search className="w-3.5 h-3.5" />
            <span>{loading ? "Exporting..." : "Generate FHIR R4 Bundle"}</span>
          </button>
        </div>

        {error && (
          <div className="mt-2.5 p-2.5 bg-red-50 border border-red-200 text-red-700 rounded text-xs">
            {error}
          </div>
        )}
      </div>

      {/* Bundle Display */}
      {bundle && (
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs space-y-4">
          <div className="flex flex-wrap items-center justify-between border-b border-slate-200 pb-3">
            <div>
              <h2 className="text-sm font-bold text-clinical-navy flex items-center">
                <FileCode className="w-4 h-4 mr-1.5 text-clinical-teal" />
                FHIR Document Bundle Generated: {bundle.id}
              </h2>
              <span className="text-xs text-slate-500 font-mono">
                MIME Type: application/fhir+json • Resources: {bundle.entry?.length || 0}
              </span>
            </div>

            <button
              onClick={handleDownload}
              className="mt-2 sm:mt-0 px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded text-xs font-bold flex items-center space-x-1.5 transition-colors shadow-xs"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download FHIR JSON</span>
            </button>
          </div>

          {/* Bundled Resources Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {bundle.entry?.map((entry: any, idx: number) => {
              const resType = entry.resource?.resourceType;
              const resId = entry.resource?.id;
              return (
                <div key={idx} className="bg-slate-50 border border-slate-200 rounded p-3 text-xs">
                  <div className="flex items-center justify-between font-bold text-slate-800 mb-1">
                    <span>{resType}</span>
                    <span className="text-[10px] bg-slate-200 text-slate-600 px-1.5 py-0.5 rounded font-mono">
                      {resId}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 truncate">
                    {resType === "Composition" && entry.resource.title}
                    {resType === "Patient" && `Gender: ${entry.resource.gender}`}
                    {resType === "Observation" && `Acuity: ${entry.resource.valueCodeableConcept?.text}`}
                  </p>
                </div>
              );
            })}
          </div>

          {/* JSON Tree Preview */}
          <div>
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Raw FHIR R4 JSON Structure
            </span>
            <pre className="p-4 bg-slate-900 text-emerald-400 rounded text-xs font-mono overflow-x-auto max-h-[500px] leading-relaxed">
              {JSON.stringify(bundle, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* EHR Integration Architecture Box */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 text-xs text-slate-600 space-y-2">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide flex items-center">
          <Server className="w-4 h-4 mr-1.5 text-slate-600" />
          Hospital EHR Integration Specifications
        </h3>
        <p className="leading-relaxed">
          The <code>/api/v1/fhir/PatientSummary</code> endpoint complies with LOINC <code>60591-5</code> (Patient Summary Document)
          and SNOMED CT <code>225399009</code> (Triage Assessment). In production deployments, this endpoint serves as an authorized
          SMART-on-FHIR provider for integration into Epic MyChart or Cerner Millennium clinical queues.
        </p>
      </div>
    </div>
  );
}
