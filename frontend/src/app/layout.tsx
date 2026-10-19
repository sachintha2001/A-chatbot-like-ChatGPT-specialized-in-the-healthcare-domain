import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/lib/LanguageContext";
import { UIProvider } from "@/lib/UIContext";
import { ClientAppLayout } from "@/components/ClientAppLayout";

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
          <UIProvider>
            <ClientAppLayout>{children}</ClientAppLayout>
          </UIProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}

