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
      <body className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
        <LanguageProvider>
          <NavigationHeader />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
          <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
            <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
              <span>MedGuard AI Platform • Clinical Decision Support System (CDSS)</span>
              <span className="font-mono text-[11px] text-slate-400">
                HIPAA Safe Harbor 45 CFR § 164.514(b) • ISO 27799 Clinical Governance
              </span>
            </div>
          </footer>
        </LanguageProvider>
      </body>
    </html>
  );
}
