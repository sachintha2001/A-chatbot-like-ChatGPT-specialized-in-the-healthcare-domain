"use client";

import { AlertTriangle, PhoneCall } from "lucide-react";
import { EmergencyEscalationInfo } from "@/lib/types";
import { useLanguage } from "@/lib/LanguageContext";

interface EmergencyBannerProps {
  emergencyInfo: EmergencyEscalationInfo;
}

export function EmergencyBanner({ emergencyInfo }: EmergencyBannerProps) {
  const { t } = useLanguage();
  const { matched_red_flags, escalation_directive, hotline_numbers } = emergencyInfo;

  return (
    <div className="bg-red-50 border-l-4 border-red-600 p-4 rounded-r-md shadow-xs mb-4">
      <div className="flex items-start">
        <div className="shrink-0">
          <AlertTriangle className="h-6 w-6 text-red-600 mt-0.5" />
        </div>
        <div className="ml-3 flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-red-800 tracking-wide uppercase">
              {t.emergencyAlertTitle}
            </h3>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-bold bg-red-600 text-white animate-pulse">
              {t.emergencyBadge}
            </span>
          </div>

          <div className="mt-2 text-xs text-red-900 leading-relaxed font-medium">
            <p className="mb-2">
              <strong>{t.emergencyIndicatorsLabel}:</strong> {matched_red_flags.join(", ")}
            </p>
            <p className="bg-white/80 p-2.5 rounded border border-red-200 text-red-950 font-semibold mb-3">
              {escalation_directive}
            </p>
          </div>

          <div className="pt-2 border-t border-red-200 flex flex-wrap items-center gap-2 text-xs">
            <span className="font-bold text-red-900 flex items-center">
              <PhoneCall className="w-3.5 h-3.5 mr-1" /> {t.emergencyDispatchLabel}:
            </span>
            <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded font-mono font-bold">
              ශ්‍රී ලංකාව: {hotline_numbers.Sri_Lanka_Suwa_Seriya || "1990 (සුවසැරිය)"}
            </span>
            <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded font-mono font-bold">
              UK: {hotline_numbers.UK_Emergency || "999"}
            </span>
            <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded font-mono font-bold">
              US/Canada: {hotline_numbers.US_Canada_Emergency || "911"}
            </span>
            <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded font-mono font-bold">
              EU: {hotline_numbers.EU_Emergency || "112"}
            </span>
            <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded font-mono font-bold">
              Mental Health: {hotline_numbers.Sri_Lanka_Mental_Health || "1926"} / {hotline_numbers.Suicide_Crisis_Lifeline || "988"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
