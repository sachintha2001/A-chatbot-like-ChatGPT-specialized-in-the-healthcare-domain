import {
  TriageSession,
  TriageMessage,
  RLHFPendingItem,
  RLHFReviewItem,
  AnalyticsOverview,
  EvaluationRunResult,
  ClinicalEvalMetric,
  MonitoringStatus,
  StreamBadgeData,
  StreamCitation,
  StreamStatusData
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

export async function fetchPathologies(params?: {
  specialty?: string;
  acuity?: string;
  search?: string;
  limit?: number;
}): Promise<any[]> {
  const query = new URLSearchParams();
  if (params?.specialty) query.append("specialty", params.specialty);
  if (params?.acuity) query.append("acuity", params.acuity);
  if (params?.search) query.append("search", params.search);
  if (params?.limit) query.append("limit", params.limit.toString());

  const res = await fetch(`${API_BASE}/knowledge/pathologies?${query.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch clinical pathologies");
  return res.json();
}

export async function fetchPathologyByIcd11(icd11Code: string): Promise<any> {
  const res = await fetch(`${API_BASE}/knowledge/pathologies/${encodeURIComponent(icd11Code)}`);
  if (!res.ok) throw new Error(`Pathology with ICD-11 '${icd11Code}' not found`);
  return res.json();
}

export async function fetchSpecialties(): Promise<{ total_pathologies: number; specialties: Record<string, number> }> {
  const res = await fetch(`${API_BASE}/knowledge/specialties`);
  if (!res.ok) throw new Error("Failed to fetch specialty breakdown");
  return res.json();
}

export async function fetchFederatedCondition(query: string, icd10?: string): Promise<any> {
  const params = new URLSearchParams({ q: query });
  if (icd10) params.append("icd10", icd10);
  const res = await fetch(`${API_BASE}/knowledge/federated/condition?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to query federated medical sources");
  return res.json();
}

export async function fetchFederatedMedication(drugName: string): Promise<any> {
  const params = new URLSearchParams({ name: drugName });
  const res = await fetch(`${API_BASE}/knowledge/federated/medication?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to query OpenFDA drug label");
  return res.json();
}

export async function streamClinicalChat(
  params: {
    message: string;
    conversationHistory?: { role: string; content: string }[];
    preferredLanguage?: string;
  },
  callbacks: {
    onStatus?: (data: StreamStatusData) => void;
    onBadge?: (data: StreamBadgeData) => void;
    onToken?: (token: string) => void;
    onCitations?: (citations: StreamCitation[]) => void;
    onFollowUpChips?: (chips: string[]) => void;
    onDone?: (data: any) => void;
    onError?: (err: Error) => void;
  }
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream"
      },
      body: JSON.stringify({
        message: params.message,
        conversation_history: params.conversationHistory || [],
        preferred_language: params.preferredLanguage
      })
    });

    if (!res.ok || !res.body) {
      throw new Error(`Server returned HTTP ${res.status}: Streaming triage failed`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split("\n\n");
      buffer = blocks.pop() || "";

      for (const block of blocks) {
        if (!block.trim()) continue;

        let eventType = "message";
        let rawData = "";

        for (const line of block.split("\n")) {
          if (line.startsWith("event: ")) {
            eventType = line.replace("event: ", "").trim();
          } else if (line.startsWith("data: ")) {
            rawData = line.replace("data: ", "").trim();
          }
        }

        if (!rawData) continue;

        try {
          const parsed = JSON.parse(rawData);
          if (eventType === "status") {
            callbacks.onStatus?.(parsed);
          } else if (eventType === "triage_badge") {
            callbacks.onBadge?.(parsed);
          } else if (eventType === "token") {
            callbacks.onToken?.(parsed.token || "");
          } else if (eventType === "citations") {
            callbacks.onCitations?.(parsed.citations || []);
          } else if (eventType === "follow_up_chips") {
            callbacks.onFollowUpChips?.(parsed.chips || []);
          } else if (eventType === "done") {
            callbacks.onDone?.(parsed);
          }
        } catch (e) {
          // If non-JSON data
          if (eventType === "token") {
            callbacks.onToken?.(rawData);
          }
        }
      }
    }
  } catch (err: any) {
    callbacks.onError?.(err);
  }
}

export async function uploadMedicalReportFile(
  file: File,
  params?: {
    patientAgeGroup?: string;
    biologicalSex?: string;
    language?: string;
  }
): Promise<any> {
  const formData = new FormData();
  formData.append("file", file);
  if (params?.patientAgeGroup) formData.append("patient_age_group", params.patientAgeGroup);
  if (params?.biologicalSex) formData.append("biological_sex", params.biologicalSex);
  if (params?.language) formData.append("language", params.language);

  const res = await fetch(`${API_BASE}/reports/upload`, {
    method: "POST",
    body: formData
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "File upload analysis failed" }));
    throw new Error(errorData.detail || "Medical report analysis failed");
  }
  return res.json();
}

export async function analyzeReportText(
  text: string,
  params?: {
    patientAgeGroup?: string;
    biologicalSex?: string;
    language?: string;
  }
): Promise<any> {
  const res = await fetch(`${API_BASE}/reports/analyze-text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      report_text: text,
      patient_age_group: params?.patientAgeGroup || "ADULT",
      biological_sex: params?.biologicalSex || "UNSPECIFIED",
      language: params?.language || "en"
    })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Text analysis failed" }));
    throw new Error(errorData.detail || "Failed to analyze report text");
  }
  return res.json();
}

export async function captureMedicalReportImage(
  imageBase64: string,
  params?: {
    patientAgeGroup?: string;
    biologicalSex?: string;
    language?: string;
  }
): Promise<any> {
  const res = await fetch(`${API_BASE}/reports/capture-image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      image_base64: imageBase64,
      filename: "camera_capture.jpg",
      patient_age_group: params?.patientAgeGroup || "ADULT",
      biological_sex: params?.biologicalSex || "UNSPECIFIED",
      language: params?.language || "en"
    })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Camera capture analysis failed" }));
    throw new Error(errorData.detail || "Medical report camera analysis failed");
  }
  return res.json();
}

export async function fetchSampleReports(): Promise<{ samples: any[] }> {
  const res = await fetch(`${API_BASE}/reports/samples`);
  if (!res.ok) throw new Error("Failed to fetch sample clinical reports");
  return res.json();
}


