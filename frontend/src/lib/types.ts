export type TriageSeverity = "ROUTINE" | "URGENT" | "EMERGENCY";
export type MessageSenderRole = "PATIENT" | "CLINICIAN_ASSISTANT" | "SYSTEM";
export type UserRole = "PATIENT" | "CLINICIAN" | "AUDITOR";

export interface ClinicalCitation {
  citation_id: string;
  guideline_id: string;
  source_title: string;
  clinical_domain: string;
  evidence_level: string;
  section_header: string;
  source_url: string;
  publication_year: number;
  matched_snippet: string;
  relevance_score: number;
}

export interface EmergencyEscalationInfo {
  is_emergency: boolean;
  matched_red_flags: string[];
  escalation_directive: string;
  hotline_numbers: {
    US_Canada_Emergency?: string;
    UK_Emergency?: string;
    EU_Emergency?: string;
    Suicide_Crisis_Lifeline?: string;
    [key: string]: string | undefined;
  };
}

export interface TriageMessage {
  message_id: string;
  session_id: string;
  sender_role: MessageSenderRole;
  redacted_content: string;
  clinical_citations: ClinicalCitation[];
  retrieval_similarity_score: number;
  groundedness_score: number;
  latency_ms: number;
  safety_check_passed: boolean;
  emergency_info?: EmergencyEscalationInfo | null;
  triage_severity: TriageSeverity;
  created_at: string;
}

export interface TriageSession {
  session_id: string;
  patient_age_group: string;
  biological_sex: string;
  consent_acknowledged: boolean;
  disclaimer_acknowledged: boolean;
  emergency_escalated: boolean;
  escalation_reason?: string | null;
  triage_severity: TriageSeverity;
  created_at: string;
  messages?: TriageMessage[];
}

export interface RLHFPendingItem {
  message_id: string;
  session_id: string;
  patient_query_redacted: string;
  assistant_response: string;
  clinical_citations: ClinicalCitation[];
  groundedness_score: number;
  retrieval_similarity_score: number;
  created_at: string;
}

export interface RLHFReviewItem {
  feedback_id: string;
  message_id: string;
  clinician_id: string;
  clinician_name?: string;
  clinical_accuracy_rating: number;
  hallucination_flag: boolean;
  safety_guideline_violation: boolean;
  omission_of_red_flag_symptom: boolean;
  revised_completion_text?: string | null;
  clinician_notes?: string | null;
  export_status: string;
  prompt_text: string;
  original_model_output: string;
  citations: ClinicalCitation[];
  created_at: string;
}

export interface SymptomDistributionItem {
  symptom_category: string;
  frequency_count: number;
  triage_urgency_ratio: { [key: string]: number };
}

export interface ClinicalDomainQueryStats {
  clinical_domain: string;
  query_count: number;
  mean_similarity_score: number;
  groundedness_index: number;
}

export interface IntentDistributionItem {
  intent_label: string;
  percentage: number;
  count: number;
}

export interface TokenDistributionBin {
  token_range: string;
  frequency: number;
}

export interface AnalyticsOverview {
  total_triage_sessions: number;
  total_messages_processed: number;
  emergency_escalations_count: number;
  emergency_escalation_rate_pct: number;
  symptom_frequencies: SymptomDistributionItem[];
  domain_breakdown: ClinicalDomainQueryStats[];
  intent_distributions: IntentDistributionItem[];
  query_length_distribution: TokenDistributionBin[];
}

export interface ClinicalEvalMetric {
  benchmark_name: string;
  groundedness_score: number;
  clinical_relevance_score: number;
  safety_pass_rate: number;
  hallucination_rate: number;
  citation_precision: number;
  sample_size: number;
  timestamp: string;
}

export interface EvaluationRunResult {
  evaluation_run_id: string;
  aggregate_metrics: ClinicalEvalMetric;
  detailed_case_evaluations: Array<{
    case_id: string;
    clinical_domain: string;
    expected_acuity: string;
    emergency_detected: boolean;
    groundedness_score: number;
    clinical_relevance_score: number;
    safety_passed: boolean;
    hallucination_flagged: boolean;
    citations_count: number;
  }>;
  passed_regulatory_threshold: boolean;
}

export interface DriftAlertItem {
  alert_id: string;
  timestamp: string;
  category: string;
  severity: "INFO" | "WARNING" | "CRITICAL";
  description: string;
  metric_value: number;
  threshold: number;
  recommended_action: string;
}

export interface GuidelineCatalogItem {
  guideline_id: string;
  source_title: string;
  issuing_authority: string;
  clinical_domain: string;
  evidence_level: string;
  publication_year: number;
  source_url: string;
  icd10_codes: string[];
  chunk_count: number;
  is_active: boolean;
  last_reviewed_at: string;
}

export interface MonitoringStatus {
  system_health: string;
  active_alerts: DriftAlertItem[];
  retrieval_similarity_moving_avg: number;
  low_confidence_query_rate: number;
  hallucination_flag_rate: number;
  p95_latency_ms: number;
  total_guidelines_indexed: number;
  guidelines_catalog: GuidelineCatalogItem[];
}
