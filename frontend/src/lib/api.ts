import {
  TriageSession,
  TriageMessage,
  RLHFPendingItem,
  RLHFReviewItem,
  AnalyticsOverview,
  EvaluationRunResult,
  ClinicalEvalMetric,
  MonitoringStatus
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function loginDemoClinician(): Promise<string> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "dr.evans@hospital.nhs.uk",
      password: "Clinical2026!"
    })
  });
  if (!res.ok) throw new Error("Clinician authentication failed");
  const data = await res.json();
  if (typeof window !== "undefined") {
    localStorage.setItem("medguard_auth_token", data.access_token);
  }
  return data.access_token;
}

export function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("medguard_auth_token");
  }
  return null;
}

export async function initializeTriageSession(params: {
  patient_age_group: string;
  biological_sex: string;
  consent_acknowledged: boolean;
  disclaimer_acknowledged: boolean;
}): Promise<TriageSession> {
  const token = getAuthToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/triage/session`, {
    method: "POST",
    headers,
    body: JSON.stringify(params)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Session creation failed" }));
    throw new Error(err.detail || "Failed to initialize triage session");
  }
  return res.json();
}

export async function submitTriagePrompt(params: {
  session_id: string;
  prompt_text: string;
  language?: string;
}): Promise<TriageMessage> {
  const token = getAuthToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/triage/prompt`, {
    method: "POST",
    headers,
    body: JSON.stringify(params)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Prompt submission failed" }));
    throw new Error(err.detail || "Failed to process clinical prompt");
  }
  return res.json();
}

export async function fetchTriageHistory(sessionId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/triage/session/${sessionId}`);
  if (!res.ok) throw new Error("Failed to load session history");
  return res.json();
}

export async function fetchRLHFQueue(): Promise<RLHFPendingItem[]> {
  let token = getAuthToken();
  if (!token) token = await loginDemoClinician();

  const res = await fetch(`${API_BASE}/rlhf/queue`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Failed to load RLHF pending queue");
  return res.json();
}

export async function submitRLHFReview(payload: {
  message_id: string;
  clinical_accuracy_rating: number;
  hallucination_flag: boolean;
  safety_guideline_violation: boolean;
  omission_of_red_flag_symptom: boolean;
  revised_completion_text?: string | null;
  clinician_notes?: string | null;
}): Promise<any> {
  let token = getAuthToken();
  if (!token) token = await loginDemoClinician();

  const res = await fetch(`${API_BASE}/rlhf/review`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Review submission failed" }));
    throw new Error(err.detail || "Review submission failed");
  }
  return res.json();
}

export async function fetchRLHFReviews(): Promise<RLHFReviewItem[]> {
  let token = getAuthToken();
  if (!token) token = await loginDemoClinician();

  const res = await fetch(`${API_BASE}/rlhf/reviews`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Failed to load historical RLHF reviews");
  return res.json();
}

export async function exportFineTuningDataset(format: "openai_chat" | "llama_alpaca" = "openai_chat"): Promise<any> {
  let token = getAuthToken();
  if (!token) token = await loginDemoClinician();

  const res = await fetch(`${API_BASE}/rlhf/export`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ format_type: format, minimum_rating: 4 })
  });
  if (!res.ok) throw new Error("Dataset export failed");
  return res.json();
}

export async function fetchAnalyticsOverview(): Promise<AnalyticsOverview> {
  let token = getAuthToken();
  if (!token) token = await loginDemoClinician();

  const res = await fetch(`${API_BASE}/analytics/overview`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Failed to load analytics overview");
  return res.json();
}

export async function triggerEvaluationRun(sampleSize: number = 8): Promise<EvaluationRunResult> {
  let token = getAuthToken();
  if (!token) token = await loginDemoClinician();

  const res = await fetch(`${API_BASE}/evaluation/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ sample_size: sampleSize })
  });
  if (!res.ok) throw new Error("Evaluation benchmark run failed");
  return res.json();
}

export async function fetchEvaluationHistory(): Promise<any[]> {
  let token = getAuthToken();
  if (!token) token = await loginDemoClinician();

  const res = await fetch(`${API_BASE}/evaluation/history`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Failed to load evaluation history");
  return res.json();
}

export async function fetchMonitoringStatus(): Promise<MonitoringStatus> {
  let token = getAuthToken();
  if (!token) token = await loginDemoClinician();

  const res = await fetch(`${API_BASE}/monitoring/status`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Failed to fetch monitoring status");
  return res.json();
}

export async function fetchFHIRPatientSummary(sessionId: string): Promise<any> {
  let token = getAuthToken();
  if (!token) token = await loginDemoClinician();

  const res = await fetch(`${API_BASE}/fhir/PatientSummary/${sessionId}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Failed to export FHIR Patient Summary");
  return res.json();
}
