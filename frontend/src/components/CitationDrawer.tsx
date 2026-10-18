"use client";

import { X, BookOpen, ExternalLink, ShieldCheck } from "lucide-react";
import { ClinicalCitation } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

interface CitationDrawerProps {
  citation: ClinicalCitation | null;
  onClose: () => void;
}

export function CitationDrawer({ citation, onClose }: CitationDrawerProps) {
  const { t } = useLanguage();
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-md bg-white h-full shadow-2xl border-l border-slate-300 flex flex-col animate-in slide-in-from-right duration-200">
        <div className="bg-clinical-navy text-white px-5 py-4 flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-clinical-teal" />
            <div>
              <h2 className="text-sm font-bold tracking-tight">{t.citationDrawerTitle}</h2>
              <span className="text-[11px] text-slate-300 font-mono">
                {citation.citation_id} • {citation.guideline_id}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 overflow-y-auto space-y-4 flex-1 text-xs text-slate-700">
          <div>
            <span className="text-[11px] font-semibold text-clinical-muted uppercase tracking-wider block mb-1">
              {t.guidelineTitleLabel}
            </span>
            <p className="text-sm font-bold text-clinical-navy leading-snug">
              {citation.source_title}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded border border-slate-200">
            <div>
              <span className="text-[11px] text-slate-500 font-semibold block">{t.clinicalDomainLabel}</span>
              <span className="font-semibold text-slate-800">{citation.clinical_domain}</span>
            </div>
            <div>
              <span className="text-[11px] text-slate-500 font-semibold block">{t.publicationYearLabel}</span>
              <span className="font-semibold text-slate-800">{citation.publication_year}</span>
            </div>
            <div className="col-span-2">
              <span className="text-[11px] text-slate-500 font-semibold block">{t.evidenceHierarchyLabel}</span>
              <span className="inline-flex items-center text-teal-700 font-medium bg-teal-50 px-2 py-0.5 rounded border border-teal-200 mt-0.5">
                <ShieldCheck className="w-3.5 h-3.5 mr-1 text-teal-600" />
                {citation.evidence_level}
              </span>
            </div>
          </div>

          <div>
            <span className="text-[11px] font-semibold text-clinical-muted uppercase tracking-wider block mb-1">
              {t.guidelineSectionLabel}
            </span>
            <p className="font-semibold text-slate-900 bg-slate-100 p-2 rounded border border-slate-200">
              {citation.section_header}
            </p>
          </div>

          <div>
            <span className="text-[11px] font-semibold text-clinical-muted uppercase tracking-wider block mb-1">
              {t.retrievedSnippetLabel}
            </span>
            <div className="p-3 bg-slate-50 rounded border border-slate-200 font-mono text-[11px] text-slate-800 leading-relaxed whitespace-pre-wrap">
              {citation.matched_snippet}
            </div>
          </div>

          <div>
            <span className="text-[11px] font-semibold text-clinical-muted uppercase tracking-wider block mb-1">
              {t.vectorSimilarityLabel}
            </span>
            <div className="w-full bg-slate-200 rounded-full h-2 mt-1">
              <div
                className="bg-clinical-teal h-2 rounded-full"
                style={{ width: `${Math.round(citation.relevance_score * 100)}%` }}
              />
            </div>
            <span className="text-[10px] text-slate-500 mt-1 block">
              {t.cosineScoreLabel}: <strong>{citation.relevance_score}</strong>
            </span>
          </div>

          {citation.source_url && (
            <div className="pt-3 border-t border-slate-200">
              <a
                href={citation.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-clinical-teal hover:underline font-semibold"
              >
                {t.viewSourceDocument}
                <ExternalLink className="w-3.5 h-3.5 ml-1" />
              </a>
            </div>
          )}
        </div>

        <div className="p-4 bg-slate-100 border-t border-slate-200 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded text-xs font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
