"use client";

import { useState } from "react";
import { AlertCircle, FileCheck, CheckSquare, Square } from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";

interface ConsentModalProps {
  isOpen: boolean;
  onConfirm: (ageGroup: string, sex: string) => Promise<void>;
}

export function ConsentModal({ isOpen, onConfirm }: ConsentModalProps) {
  const { t } = useLanguage();
  const [ageGroup, setAgeGroup] = useState("ADULT");
  const [sex, setSex] = useState("UNSPECIFIED");
  const [disclaimerChecked, setDisclaimerChecked] = useState(false);
  const [consentChecked, setConsentChecked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!disclaimerChecked || !consentChecked) {
      setError(t.consentRequiredError);
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await onConfirm(ageGroup, sex);
    } catch (err: any) {
      setError(err.message || "Failed to initiate clinical session.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-lg w-full border border-slate-300 shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="bg-clinical-navy px-6 py-4 flex items-center justify-between text-white border-b border-slate-700">
          <div className="flex items-center space-x-2">
            <FileCheck className="w-5 h-5 text-clinical-teal" />
            <h2 className="text-base font-bold tracking-tight">{t.consentTitle}</h2>
          </div>
          <span className="text-[11px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">
            {t.consentProtocol}
          </span>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5 text-sm text-slate-700">
          <div className="bg-slate-50 p-3.5 rounded border border-slate-200 text-xs leading-relaxed text-slate-600">
            <p className="font-semibold text-slate-800 mb-1">{t.cdssNoticeTitle}</p>
            {t.cdssNoticeText}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {t.ageBracketLabel}
              </label>
              <select
                value={ageGroup}
                onChange={(e) => setAgeGroup(e.target.value)}
                className="w-full border border-slate-300 rounded px-3 py-2 text-xs bg-white text-slate-900 focus:outline-none focus:ring-1 focus:ring-clinical-teal focus:border-clinical-teal"
              >
                <option value="PEDIATRIC">{t.agePediatric}</option>
                <option value="ADULT">{t.ageAdult}</option>
                <option value="GERIATRIC">{t.ageGeriatric}</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {t.biologicalSexLabel}
              </label>
              <select
                value={sex}
                onChange={(e) => setSex(e.target.value)}
                className="w-full border border-slate-300 rounded px-3 py-2 text-xs bg-white text-slate-900 focus:outline-none focus:ring-1 focus:ring-clinical-teal focus:border-clinical-teal"
              >
                <option value="UNSPECIFIED">{t.sexUnspecified}</option>
                <option value="FEMALE">{t.sexFemale}</option>
                <option value="MALE">{t.sexMale}</option>
              </select>
            </div>
          </div>

          <div className="space-y-3 pt-2">
            <div
              onClick={() => setDisclaimerChecked(!disclaimerChecked)}
              className="flex items-start space-x-2.5 cursor-pointer select-none"
            >
              {disclaimerChecked ? (
                <CheckSquare className="w-4 h-4 text-clinical-teal shrink-0 mt-0.5" />
              ) : (
                <Square className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
              )}
              <span className="text-xs text-slate-700 leading-snug">
                {t.disclaimerCheckbox}
              </span>
            </div>

            <div
              onClick={() => setConsentChecked(!consentChecked)}
              className="flex items-start space-x-2.5 cursor-pointer select-none"
            >
              {consentChecked ? (
                <CheckSquare className="w-4 h-4 text-clinical-teal shrink-0 mt-0.5" />
              ) : (
                <Square className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
              )}
              <span className="text-xs text-slate-700 leading-snug">
                {t.consentCheckbox}
              </span>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="pt-3 border-t border-slate-200 flex justify-end">
            <button
              type="submit"
              disabled={loading || !disclaimerChecked || !consentChecked}
              className={`px-5 py-2.5 rounded font-semibold text-xs tracking-wide uppercase transition-colors shadow-xs ${
                loading || !disclaimerChecked || !consentChecked
                  ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                  : "bg-clinical-teal hover:bg-clinical-teal-hover text-white"
              }`}
            >
              {loading ? t.initializingButton : t.acceptButton}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
