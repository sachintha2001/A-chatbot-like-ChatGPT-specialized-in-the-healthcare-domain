import type { Metadata } from "next";
import "./globals.css";
import { NavigationHeader } from "@/components/NavigationHeader";
import { LanguageProvider } from "@/lib/LanguageContext";

export const metadata: Metadata = {
  title: "MedGuard AI - Clinical Decision Support & Patient Triage Platform",
  description: "HIPAA/GDPR-aligned evidence-grounded clinical decision support and patient triage system.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="medical-daylight-theme min-h-screen text-clinical-navy flex flex-col font-sans selection:bg-teal-100 selection:text-teal-900">
        <LanguageProvider>
          <NavigationHeader />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-5">
            {children}
          </main>
          <footer className="border-t border-[#CBE2EA] bg-white/90 backdrop-blur-md py-4 text-xs text-clinical-muted mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-3">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="inline-flex items-center gap-1.5 font-bold text-clinical-navy">
                  <span className="w-2 h-2 rounded-full bg-teal-600" />
                  MedGuard AI Clinical Platform
                </span>
                <span className="text-slate-300">•</span>
                <span className="text-[11px] text-clinical-slate">
                  Evidence-Grounded Clinical Decision Support & Diagnostic Triage
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-2 text-[11px]">
                <a
                  href="tel:1990"
                  className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 font-bold hover:bg-rose-100 transition-colors"
                >
                  <span>🚑 Suwa Seriya Emergency: 1990</span>
                </a>
                <span className="px-2.5 py-0.5 rounded-full bg-teal-50 text-teal-800 border border-teal-200 font-mono">
                  WHO ICD-11 • HL7 FHIR R4
                </span>
                <span className="font-mono text-clinical-muted hidden sm:inline">
                  HIPAA 45 CFR § 164.514(b) • ISO 27799
                </span>
              </div>
            </div>
          </footer>
        </LanguageProvider>
      </body>
    </html>
  );
}

