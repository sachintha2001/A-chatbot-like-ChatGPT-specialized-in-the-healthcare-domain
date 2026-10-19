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

export type TriageWorkflowState = "RED_FLAG_EMERGENCY" | "CLINICAL_INTAKE_REQUIRED" | "STRUCTURED_ASSESSMENT";
export type TriageAcuityLevel = "EMERGENCY" | "URGENT_CONSULT" | "ROUTINE_CLINIC" | "SELF_CARE_MONITORING";

export interface StreamCitation {
  badge: string;
  authority: string;
  title: string;
  excerpt: string;
  url: string;
}

export interface StreamBadgeData {
  state: TriageWorkflowState;
  acuity: TriageAcuityLevel;
  headline: string;
  is_emergency: boolean;
  llm_provider?: string;
  llm_model?: string;
  cloud_synthesized?: boolean;
  scrubbed_entities?: string[];
}

export interface HybridLLMStatus {
  configured_mode: string;
  active_provider: string;
  active_model: string;
  cloud_llm_enabled: boolean;
  phi_scrubber_enforced_pre_cloud: boolean;
  deterministic_red_flag_gate_active: boolean;
  providers_configured: {
    gemini: boolean;
    anthropic: boolean;
    openai: boolean;
    local_fallback: boolean;
  };
  models: {
    gemini: string;
    anthropic: string;
    openai: string;
  };
}

export interface StreamStatusData {
  stage: string;
  message: string;
}

export interface PathologySummaryItem {
  id: number;
  icd11_code: string;
  clinical_name: string;
  medical_specialty: string;
  baseline_acuity: TriageAcuityLevel;
  primary_symptoms: string[];
  red_flag_count: number;
}

export interface PathologyDetailItem {
  id: number;
  icd11_code: string;
  icd10_code?: string;
  clinical_name: string;
  common_aliases: string[];
  medical_specialty: string;
  baseline_acuity: TriageAcuityLevel;
  pathophysiology_overview: string;
  cardinal_symptoms: {
    primary: { symptom: string; weight: number }[];
    secondary: { symptom: string; weight: number }[];
  };
  red_flag_criteria: string[];
  differential_diagnoses: { condition: string; icd11: string; distinction: string }[];
  diagnostic_workup: {
    initial_labs: string[];
    imaging_ecg: string[];
    confirmatory_tests: string[];
  };
  evidence_based_management: {
    first_line_lifestyle: string[];
    pharmacotherapy: string[];
    contraindications: string[];
  };
  source_metadata: {
    issuing_authority: string;
    guideline_title: string;
    publication_year: number;
    source_url?: string;
  };
}

export type BiomarkerStatus = "NORMAL" | "ELEVATED" | "DECREASED" | "CRITICAL_HIGH" | "CRITICAL_LOW" | "POSITIVE" | "NEGATIVE";

export interface ReportBiomarkerParam {
  canonical_id: string;
  display_name_en: string;
  display_name_si: string;
  category: string;
  raw_value: string;
  numeric_value: number | null;
  unit: string;
  ref_interval?: string;
  status: BiomarkerStatus;
  status_si: string;
  is_qualitative: boolean;
  is_abnormal: boolean;
  is_critical: boolean;
  interpretation_en: string;
  interpretation_si: string;
  related_icd11: string[];
}

export interface CorrelatedConditionItem {
  condition: string;
  condition_si: string;
  icd11: string;
  evidence: string;
  evidence_si: string;
  urgency: string;
}

export interface ReportAnalysisResult {
  success: boolean;
  overall_status: "ALL_NORMAL" | "ABNORMAL_ELEVATED_RISK" | "CRITICAL_EMERGENCY";
  overall_status_en: string;
  overall_status_si: string;
  qualitative_verdict: "POSITIVE" | "NEGATIVE" | "NOT_APPLICABLE";
  is_emergency: boolean;
  total_parameters_tested: number;
  abnormal_count: number;
  elevated_count: number;
  decreased_count: number;
  elevated_parameters_en: string[];
  elevated_parameters_si: string[];
  decreased_parameters_en: string[];
  decreased_parameters_si: string[];
  critical_parameters: string[];
  parameters: ReportBiomarkerParam[];
  correlated_conditions: CorrelatedConditionItem[];
  recommended_specialists: string[];
  clinical_directives_en: string[];
  clinical_directives_si: string[];
  filename?: string;
  extracted_text_preview?: string;
  message_en?: string;
  message_si?: string;
}

export interface SampleReportItem {
  id: string;
  title_en: string;
  title_si: string;
  sample_text: string;
}

export type PatientRelationship = "SELF" | "FATHER" | "MOTHER" | "SPOUSE" | "CHILD" | "SIBLING" | "OTHER";
export type BiologicalSex = "MALE" | "FEMALE" | "UNSPECIFIED";
export type MedicalRecordType = "LAB_REPORT" | "TRIAGE_SESSION" | "PHYSICAL_EXAM" | "DISCHARGE_SUMMARY";

export interface PatientProfileItem {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  relationship: PatientRelationship;
  date_of_birth?: string | null;
  biological_sex: BiologicalSex;
  blood_group: string;
  allergies: string[];
  chronic_conditions: string[];
  emergency_contact_phone?: string | null;
  notes?: string | null;
  total_records: number;
  latest_record_date?: string | null;
  created_at?: string | null;
}

export interface PatientMedicalRecordItem {
  id: string;
  profile_id: string;
  record_type: MedicalRecordType;
  record_date: string;
  title: string;
  overall_status: string;
  qualitative_verdict: string;
  extracted_biomarkers: any[];
  correlated_icd11: any[];
  notes?: string | null;
  source_filename?: string | null;
  created_at?: string | null;
}

export interface BiomarkerDataPoint {
  record_id: string;
  record_title: string;
  date: string;
  value: number;
  unit: string;
  status: string;
  status_si: string;
  is_abnormal: boolean;
  is_critical: boolean;
  display_name_en: string;
  display_name_si: string;
  ref_interval: string;
}

export interface BiomarkerTrendItem {
  canonical_id: string;
  display_name_en: string;
  display_name_si: string;
  category: string;
  unit: string;
  ref_interval: string;
  data_points: BiomarkerDataPoint[];
  point_count: number;
  baseline_value: number;
  previous_value: number;
  latest_value: number;
  delta_value: number;
  delta_percentage: number;
  trajectory: "IMPROVING" | "DETERIORATING" | "STABLE" | "CRITICAL_ATTENTION";
  trajectory_label_en: string;
  trajectory_label_si: string;
  clinical_insight_en: string;
  clinical_insight_si: string;
  is_abnormal: boolean;
  is_critical: boolean;
}

export interface PatientTrendsResponse {
  profile_id: string;
  patient_name: string;
  total_records_analyzed: number;
  tracked_biomarkers_count: number;
  trends: BiomarkerTrendItem[];
  overall_trajectory: "IMPROVING" | "DETERIORATING" | "STABLE" | "CRITICAL_ATTENTION";
  longitudinal_summary_en: string;
  longitudinal_summary_si: string;
}

export interface SpecialistDoctor {
  doctor_id: string;
  full_name_en: string;
  full_name_si: string;
  qualifications: string;
  slmc_reg_no: string;
  specialty_code: string;
  specialty_en: string;
  specialty_si: string;
  primary_hospital_en: string;
  primary_hospital_si: string;
  visiting_hospitals: string[];
  supported_modes: string[];
  supported_gateways: string[];
  consultation_fee_lkr: number;
  next_available_slots: string[];
  languages_spoken: string[];
  rating: number;
  echannelling_url: string;
  doc990_url: string;
  odoc_url: string;
}

export interface PartnerGatewayItem {
  gateway_id: string;
  name_en: string;
  name_si: string;
  description_en: string;
  description_si: string;
  portal_url: string;
  hotline: string;
}

export interface SpecialistRecommendationResponse {
  matched_specialty_code: string;
  matched_specialty_en: string;
  matched_specialty_si: string;
  triage_acuity: string;
  emergency_warning_active: boolean;
  emergency_directive_en?: string | null;
  emergency_directive_si?: string | null;
  recommended_consultation_mode: string;
  specialists: SpecialistDoctor[];
  partner_gateways: PartnerGatewayItem[];
}

export interface AppointmentBookingRequestPayload {
  doctor_id: string;
  patient_name: string;
  patient_phone: string;
  patient_age?: number;
  preferred_slot: string;
  consultation_mode: string;
  booking_gateway: string;
  hospital_name?: string;
  clinical_context_summary?: string;
  recommended_specialty?: string;
  triage_acuity?: string;
  correlated_icd11_codes?: string[];
  language?: string;
}

export interface AppointmentBookingResponse {
  booking_id: string;
  booking_reference: string;
  status: string;
  queue_token_number: number;
  doctor: SpecialistDoctor;
  patient_display_name: string;
  patient_phone_masked: string;
  scheduled_slot: string;
  consultation_mode: string;
  booking_gateway: string;
  hospital_or_platform: string;
  estimated_fee_lkr: number;
  telemedicine_meeting_url?: string | null;
  external_gateway_redirect_url: string;
  sbar_clinical_handover_en: string;
  sbar_clinical_handover_si: string;
  created_at: string;
}
