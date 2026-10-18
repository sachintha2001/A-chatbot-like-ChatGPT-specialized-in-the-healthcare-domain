"use client";

import { useState, useEffect, useRef } from "react";
import {
  UploadCloud,
  FileText,
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowUpRight,
  Sparkles,
  PhoneCall,
  RotateCcw,
  Stethoscope,
  Info,
  Layers,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { ReportAnalysisResult, SampleReportItem, ReportBiomarkerParam } from "@/lib/types";
import { uploadMedicalReportFile, analyzeReportText, fetchSampleReports } from "@/lib/api";
import { useLanguage } from "@/lib/LanguageContext";

export function MedicalReportAnalyzer() {
  const { language } = useLanguage();
  const [inputMode, setInputMode] = useState<"UPLOAD" | "TEXT">("UPLOAD");
  const [file, setFile] = useState<File | null>(null);
  const [reportText, setReportText] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<ReportAnalysisResult | null>(null);
  const [samples, setSamples] = useState<SampleReportItem[]>([]);
  const [expandedBiomarker, setExpandedBiomarker] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchSampleReports()
      .then((data) => setSamples(data.samples || []))
      .catch(() => {});
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setErrorMessage(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setErrorMessage(null);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      if (inputMode === "UPLOAD") {
        if (!file) {
          throw new Error("Please select a medical report file (PDF, TXT, or CSV) to upload.");
        }
        const res = await uploadMedicalReportFile(file, { language });
        setAnalysisResult(res);
      } else {
        if (!reportText.trim()) {
          throw new Error("Please paste or type the laboratory report text.");
        }
        const res = await analyzeReportText(reportText, { language });
        setAnalysisResult(res);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to process medical report.");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = (sample: SampleReportItem) => {
    setInputMode("TEXT");
    setReportText(sample.sample_text);
    setErrorMessage(null);
  };

  const resetAnalysis = () => {
    setAnalysisResult(null);
    setFile(null);
    setReportText("");
    setErrorMessage(null);
  };

  const isSi = language === "si";

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 rounded-xl border border-slate-800 shadow-2xl overflow-hidden">
      {/* Top Header */}
      <div className="px-6 py-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-bold text-slate-100 flex items-center gap-2">
              {isSi ? "සායනික රසායනාගාර වාර්තා විශ්ලේෂණය" : "Clinical Laboratory Report Diagnostic Engine"}
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800 font-bold">
                WHO / IFCC Standardized
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              {isSi
                ? "රසායනාගාර වාර්තා (FBC, Lipid, Glycemic, Serology) ඇතුළත් කර අගයන් වැඩිද/අඩුද සහ රෝග විනිශ්චය පරීක්ෂා කරන්න"
                : "Automated Biomarker Parsing, Reference Interval Matching, and Clinical Positive/Negative Triaging"}
            </p>
          </div>
        </div>

        {analysisResult && (
          <button
            onClick={resetAnalysis}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{isSi ? "නව වාර්තාවක්" : "New Report"}</span>
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {!analysisResult ? (
          /* INPUT & UPLOAD VIEW */
          <div className="max-w-3xl mx-auto space-y-6">
            {/* Input Mode Selector */}
            <div className="flex items-center gap-2 p-1 bg-slate-900 border border-slate-800 rounded-lg max-w-md">
              <button
                onClick={() => setInputMode("UPLOAD")}
                className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all flex items-center justify-center gap-1.5 ${
                  inputMode === "UPLOAD"
                    ? "bg-teal-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <UploadCloud className="w-3.5 h-3.5" />
                <span>{isSi ? "ගොනුවක් උඩුගත කරන්න (PDF / Doc)" : "Upload Report File (PDF / TXT)"}</span>
              </button>
              <button
                onClick={() => setInputMode("TEXT")}
                className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all flex items-center justify-center gap-1.5 ${
                  inputMode === "TEXT"
                    ? "bg-teal-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>{isSi ? "වාර්තාවේ විස්තර ටයිප් කරන්න" : "Paste Text / Sample Vignettes"}</span>
              </button>
            </div>

            {/* Upload Box */}
            {inputMode === "UPLOAD" ? (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-800 hover:border-teal-500/60 bg-slate-900/50 hover:bg-slate-900 rounded-2xl p-10 text-center cursor-pointer transition-all space-y-3"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt,.csv"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <div className="w-14 h-14 mx-auto rounded-full bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
                  <UploadCloud className="w-7 h-7" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-100">
                    {file ? file.name : isSi ? "ඔබගේ වෛද්‍ය වාර්තාව මෙතැනට Drag & Drop කරන්න" : "Drag and drop your laboratory report here"}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    {file
                      ? `${(file.size / 1024).toFixed(1)} KB - Ready for diagnostic parsing`
                      : isSi
                      ? "PDF, TXT, හෝ CSV ගොනු සහාය දක්වයි (FBC, Lipid, Glycemic, Serology)"
                      : "Supports PDF, TXT, or CSV formats (Full Blood Count, Lipid Profile, LFT, RFT, Dengue Serology)"}
                  </p>
                </div>
                <button
                  type="button"
                  className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 inline-block"
                >
                  {isSi ? "ගොනුව තෝරන්න" : "Browse Files"}
                </button>
              </div>
            ) : (
              /* Text Input Box */
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-300 block">
                  {isSi ? "රසායනාගාර වාර්තාවේ අගයන් ඇතුළත් කරන්න (Paste Report Text):" : "Paste or type clinical laboratory test results:"}
                </label>
                <textarea
                  value={reportText}
                  onChange={(e) => setReportText(e.target.value)}
                  rows={8}
                  placeholder={`Example:\nHemoglobin: 16.5 g/dL\nPlatelet Count: 45000 /uL\nTotal WBC: 3200 /uL\nDengue NS1 Antigen: POSITIVE`}
                  className="w-full bg-slate-900 border border-slate-800 focus:border-teal-500 rounded-xl p-4 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none leading-relaxed"
                />
              </div>
            )}

            {/* Quick Sample Vignettes */}
            <div className="space-y-2 pt-2">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-teal-400" />
                <span>{isSi ? "ක්ෂණික සායනික නිදසුන් පරීක්ෂා කරන්න (Quick Clinical Presets):" : "Instant Clinical Presets for Real Verification:"}</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {samples.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => handleLoadSample(s)}
                    className="p-3 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-teal-500 rounded-xl text-left transition-all group"
                  >
                    <div className="font-semibold text-slate-200 group-hover:text-teal-300 flex items-center justify-between">
                      <span>{isSi ? s.title_si : s.title_en}</span>
                      <ArrowUpRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-teal-400 shrink-0" />
                    </div>
                    <div className="text-[11px] text-slate-500 font-mono mt-1 truncate">
                      {s.sample_text.split("\n")[1] || s.sample_text.slice(0, 40)}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {errorMessage && (
              <div className="p-3.5 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-xl text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Submit Button */}
            <div className="text-center pt-2">
              <button
                onClick={handleAnalyze}
                disabled={loading || (inputMode === "UPLOAD" && !file) || (inputMode === "TEXT" && !reportText.trim())}
                className="px-8 py-3 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-lg transition-all cursor-pointer disabled:cursor-not-allowed inline-flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin" />
                    <span>{isSi ? "සායනික දත්ත විශ්ලේෂණය වෙමින් පවතී..." : "Parsing Biomarkers & Clinical Intervals..."}</span>
                  </>
                ) : (
                  <>
                    <Activity className="w-4 h-4" />
                    <span>{isSi ? "වාර්තාව සම්පූර්ණයෙන් විශ්ලේෂණය කරන්න" : "Execute Full Diagnostic Analysis"}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* ANALYSIS REPORT RESULT VIEW */
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Overall Status Banner */}
            <div
              className={`p-5 rounded-2xl border shadow-xl ${
                analysisResult.is_emergency
                  ? "bg-rose-950/80 border-rose-600 text-rose-100"
                  : analysisResult.overall_status === "ABNORMAL_ELEVATED_RISK"
                  ? "bg-amber-950/80 border-amber-600 text-amber-100"
                  : "bg-teal-950/80 border-teal-500 text-teal-100"
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  {analysisResult.is_emergency ? (
                    <ShieldAlert className="w-7 h-7 text-rose-400 shrink-0 animate-pulse mt-0.5" />
                  ) : analysisResult.overall_status === "ABNORMAL_ELEVATED_RISK" ? (
                    <AlertTriangle className="w-7 h-7 text-amber-400 shrink-0 mt-0.5" />
                  ) : (
                    <CheckCircle2 className="w-7 h-7 text-teal-400 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <div className="text-xs font-mono font-bold tracking-wider uppercase opacity-80">
                      {isSi ? "සායනික තක්සේරු තත්ත්වය" : "Overall Diagnostic Classification"}
                    </div>
                    <h2 className="text-base sm:text-lg font-bold mt-1">
                      {isSi ? analysisResult.overall_status_si : analysisResult.overall_status_en}
                    </h2>
                    {analysisResult.qualitative_verdict !== "NOT_APPLICABLE" && (
                      <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-bold text-xs uppercase bg-black/40 border border-current">
                        <span>
                          {isSi
                            ? `ප්‍රතිඵලය: ${analysisResult.qualitative_verdict === "POSITIVE" ? "ධනාත්මකයි (POSITIVE)" : "සෘණාත්මකයි (NEGATIVE)"}`
                            : `Qualitative Result: ${analysisResult.qualitative_verdict}`}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {analysisResult.is_emergency && (
                  <a
                    href="tel:1990"
                    className="inline-flex items-center gap-2 px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold shadow-lg transition-colors shrink-0"
                  >
                    <PhoneCall className="w-4 h-4" />
                    <span>{isSi ? "1990 සුවසැරිය / 911 අමතන්න" : "Emergency Direct Dial"}</span>
                  </a>
                )}
              </div>
            </div>

            {/* Quick Summary Grid: Elevated (Wedi) vs Decreased (Adu) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Elevated (Wedi) */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                    <TrendingUp className="w-4 h-4 text-rose-400" />
                    <span>{isSi ? "වැඩි වී ඇති අගයන් (Elevated / High)" : "Elevated Biomarkers (High)"}</span>
                  </span>
                  <span className="font-mono text-xs font-bold text-rose-400 bg-rose-950/60 px-2 py-0.5 rounded border border-rose-800">
                    {analysisResult.elevated_count}
                  </span>
                </div>
                {analysisResult.elevated_count === 0 ? (
                  <p className="text-xs text-slate-500 italic">
                    {isSi ? "සාමාන්‍ය සීමාව ඉක්මවා වැඩි වූ අගයන් නොමැත." : "No biomarkers exceeded the upper reference threshold."}
                  </p>
                ) : (
                  <ul className="space-y-1 text-xs text-rose-300">
                    {(isSi ? analysisResult.elevated_parameters_si : analysisResult.elevated_parameters_en).map((item, i) => (
                      <li key={i} className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0" />
                        <span className="font-medium">{item}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Decreased (Adu) */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                    <TrendingDown className="w-4 h-4 text-amber-400" />
                    <span>{isSi ? "අඩු වී ඇති අගයන් (Decreased / Low)" : "Decreased Biomarkers (Low)"}</span>
                  </span>
                  <span className="font-mono text-xs font-bold text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800">
                    {analysisResult.decreased_count}
                  </span>
                </div>
                {analysisResult.decreased_count === 0 ? (
                  <p className="text-xs text-slate-500 italic">
                    {isSi ? "සාමාන්‍ය සීමාවට වඩා අඩු වූ අගයන් නොමැත." : "No biomarkers fell below the lower reference threshold."}
                  </p>
                ) : (
                  <ul className="space-y-1 text-xs text-amber-300">
                    {(isSi ? analysisResult.decreased_parameters_si : analysisResult.decreased_parameters_en).map((item, i) => (
                      <li key={i} className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
                        <span className="font-medium">{item}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            {/* Correlated Clinical Syndromes & ICD-11 */}
            {analysisResult.correlated_conditions.length > 0 && (
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <div className="text-xs font-bold text-teal-400 uppercase tracking-wider flex items-center gap-2">
                  <Layers className="w-4 h-4" />
                  <span>{isSi ? "හඳුනාගත් සායනික රෝග ලක්ෂණ සහ ICD-11 සබඳතා" : "Correlated Clinical Syndromes & ICD-11 Mapping"}</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {analysisResult.correlated_conditions.map((c, i) => (
                    <div
                      key={i}
                      className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl space-y-1 text-xs"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="font-bold text-slate-100">{isSi ? c.condition_si : c.condition}</div>
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800 font-bold shrink-0">
                          ICD-11: {c.icd11}
                        </span>
                      </div>
                      <div className="text-slate-400 text-[11px] leading-relaxed">
                        {isSi ? c.evidence_si : c.evidence}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed Biomarker Breakdown Cards */}
            <div className="space-y-3">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                <span>{isSi ? "පරීක්ෂා කළ සියලුම ජෛව රසායනික අගයන් (All Tested Parameters)" : "Tested Clinical Biomarkers Breakdown"}</span>
                <span className="text-[11px] text-slate-500 font-mono">
                  {analysisResult.total_parameters_tested} Parameters Evaluated
                </span>
              </div>

              <div className="space-y-2">
                {analysisResult.parameters.map((p) => {
                  const isElevated = p.status === "ELEVATED" || p.status === "CRITICAL_HIGH";
                  const isDecreased = p.status === "DECREASED" || p.status === "CRITICAL_LOW";
                  const isPos = p.status === "POSITIVE";
                  const isExpanded = expandedBiomarker === p.canonical_id;

                  const badgeClass = p.is_critical
                    ? "bg-rose-950 text-rose-300 border-rose-700 font-bold"
                    : isElevated
                    ? "bg-rose-950/60 text-rose-300 border-rose-800"
                    : isDecreased
                    ? "bg-amber-950/60 text-amber-300 border-amber-800"
                    : isPos
                    ? "bg-rose-950 text-rose-300 border-rose-700"
                    : "bg-teal-950/60 text-teal-300 border-teal-800";

                  return (
                    <div
                      key={p.canonical_id}
                      className="p-4 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl transition-all"
                    >
                      <div
                        onClick={() => setExpandedBiomarker(isExpanded ? null : p.canonical_id)}
                        className="flex items-center justify-between cursor-pointer"
                      >
                        <div className="flex items-center gap-3">
                          <div className="font-semibold text-xs text-slate-200">
                            {isSi ? p.display_name_si : p.display_name_en}
                          </div>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${badgeClass}`}>
                            {isSi ? p.status_si : p.status}
                          </span>
                        </div>

                        <div className="flex items-center gap-4 text-xs">
                          <div className="text-right">
                            <span className="font-mono font-bold text-slate-100">
                              {p.raw_value}
                            </span>
                            <span className="text-slate-400 text-[11px] ml-1">{p.unit}</span>
                          </div>
                          {p.ref_interval && (
                            <div className="hidden sm:block text-[11px] text-slate-500 font-mono">
                              Ref: {p.ref_interval}
                            </div>
                          )}
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-slate-500" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-slate-500" />
                          )}
                        </div>
                      </div>

                      {/* Expanded Medical Research Interpretation */}
                      {isExpanded && (
                        <div className="mt-3 pt-3 border-t border-slate-800 text-xs text-slate-400 leading-relaxed space-y-2">
                          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80">
                            <span className="font-semibold text-teal-400 block mb-1">
                              {isSi ? "සායනික අර්ථකථනය (Clinical Significance):" : "Evidence-Based Clinical Interpretation:"}
                            </span>
                            <span>{isSi ? p.interpretation_si : p.interpretation_en}</span>
                          </div>
                          <div className="text-[11px] text-slate-500 flex items-center justify-between">
                            <span>Category: {p.category}</span>
                            {p.related_icd11.length > 0 && (
                              <span>Related ICD-11: {p.related_icd11.join(", ")}</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Specialist Referrals */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Stethoscope className="w-4 h-4 text-teal-400" />
                <span>{isSi ? "නිර්දේශිත විශේෂඥ වෛද්‍ය හමුවීම් (Recommended Specialists)" : "Recommended Specialist Referrals"}</span>
              </div>
              <div className="flex flex-wrap gap-2 pt-1">
                {analysisResult.recommended_specialists.map((spec, i) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-slate-300 text-xs font-medium"
                  >
                    {spec}
                  </span>
                ))}
              </div>
            </div>

            {/* Clinical Directives & Next Steps */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Info className="w-4 h-4 text-teal-400" />
                <span>{isSi ? "ක්ෂණික සායනික උපදෙස් සහ ආරක්ෂණ ක්‍රියාමාර්ග" : "Clinical Action Directives & Safety Netting"}</span>
              </div>
              <ul className="space-y-1.5 text-slate-300 pt-1">
                {(isSi ? analysisResult.clinical_directives_si : analysisResult.clinical_directives_en).map((dir, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-teal-400 font-bold">•</span>
                    <span className="leading-relaxed">{dir}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
