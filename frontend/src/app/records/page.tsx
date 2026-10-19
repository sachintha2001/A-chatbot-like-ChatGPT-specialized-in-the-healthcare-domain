"use client";

import { PatientHistoryDashboard } from "@/components/records/PatientHistoryDashboard";

export default function PatientRecordsPage() {
  return (
    <div className="min-h-[calc(100vh-8.5rem)] pb-12">
      <PatientHistoryDashboard />
    </div>
  );
}
