export type Language = "en" | "si";

export interface Translations {
  // Navigation & Header
  appTitle: string;
  appSubtitle: string;
  navTriage: string;
  navReports: string;
  navRecords: string;
  navOntology: string;
  navRLHF: string;
  navAnalytics: string;
  navEvaluation: string;
  navFHIR: string;
  hipaaActive: string;
  phiScrubbedNotice: string;
  redFlagFilterStatus: string;
  clinicianBadge: string;
  vectorIndexLabel: string;
  buildVersion: string;

  // Consent Modal
  consentTitle: string;
  consentProtocol: string;
  cdssNoticeTitle: string;
  cdssNoticeText: string;
  ageBracketLabel: string;
  agePediatric: string;
  ageAdult: string;
  ageGeriatric: string;
  biologicalSexLabel: string;
  sexUnspecified: string;
  sexFemale: string;
  sexMale: string;
  disclaimerCheckbox: string;
  consentCheckbox: string;
  acceptButton: string;
  initializingButton: string;
  consentRequiredError: string;

  // Triage Page
  triageThreadTitle: string;
  sessionLabel: string;
  cohortLabel: string;
  sexLabel: string;
  severityLabel: string;
  resetButton: string;
  intakeReadyTitle: string;
  intakeReadyDescription: string;
  vignettesTitle: string;
  vignetteAcsTitle: string;
  vignetteAcsDesc: string;
  vignetteHypoTitle: string;
  vignetteHypoDesc: string;
  vignetteStrokeTitle: string;
  vignetteStrokeDesc: string;
  vignettePediatricTitle: string;
  vignettePediatricDesc: string;
  patientNarrativeHeader: string;
  assistantHeader: string;
  inputPlaceholderReady: string;
  inputPlaceholderConsent: string;
  triageButton: string;
  footerNotice: string;
  scrubbingNotice: string;
  groundednessLabel: string;
  similarityLabel: string;
  latencyLabel: string;
  guidelinesCitedLabel: string;

  // Severities
  severityRoutine: string;
  severityUrgent: string;
  severityEmergency: string;

  // Emergency Banner
  emergencyAlertTitle: string;
  emergencyBadge: string;
  emergencyIndicatorsLabel: string;
  emergencyDispatchLabel: string;

  // Citation Drawer
  citationDrawerTitle: string;
  guidelineTitleLabel: string;
  clinicalDomainLabel: string;
  publicationYearLabel: string;
  evidenceHierarchyLabel: string;
  guidelineSectionLabel: string;
  retrievedSnippetLabel: string;
  vectorSimilarityLabel: string;
  cosineScoreLabel: string;
  viewSourceDocument: string;

  // Voice STT & TTS
  voiceInputTooltip: string;
  voiceListening: string;
  voiceStop: string;
  voicePlay: string;
  voiceStopAudio: string;
  voiceAutoRead: string;
  voicePermissionError: string;
  voiceNotSupported: string;
}

export const translations: Record<Language, Translations> = {
  en: {
    appTitle: "MedGuard AI",
    appSubtitle: "Clinical Decision Support & Patient Triage",
    navTriage: "Clinical Triage",
    navReports: "Lab Reports",
    navRecords: "Health Records (EHR)",
    navOntology: "ICD-11 Ontology",
    navRLHF: "Clinician RLHF Queue",
    navAnalytics: "Epidemiological Analytics",
    navEvaluation: "Evaluation & Benchmarks",
    navFHIR: "EHR / FHIR R4",
    hipaaActive: "HIPAA Safe Harbor Active",
    phiScrubbedNotice: "18 Identifier Classes Scrubbed Prior to Ingestion",
    redFlagFilterStatus: "Deterministic Red-Flag Safety Filter: ENABLED",
    clinicianBadge: "Authenticated Clinician: Dr. Sarah Evans (GMC-7890123)",
    vectorIndexLabel: "Vector Index: 16 Guidelines",
    buildVersion: "Build 1.0.0-PROD",

    consentTitle: "Clinical Intake & Statutory Consent",
    consentProtocol: "Protocol NHS/HIPAA-2026",
    cdssNoticeTitle: "Notice of Clinical Decision Support (CDSS):",
    cdssNoticeText:
      "MedGuard AI provides evidence-grounded clinical decision support based on validated medical consensus guidelines (NICE, AHA/ACC, ADA, WHO). It does not provide definitive medical diagnoses or prescribe medications.",
    ageBracketLabel: "Patient Age Bracket",
    agePediatric: "Pediatric (<16 years)",
    ageAdult: "Adult (16–64 years)",
    ageGeriatric: "Geriatric (65+ years)",
    biologicalSexLabel: "Biological Sex (Clinical)",
    sexUnspecified: "Not Specified",
    sexFemale: "Female",
    sexMale: "Male",
    disclaimerCheckbox:
      "I acknowledge that this system is an assistive clinical decision aid, not a substitute for professional clinical evaluation or emergency medical services.",
    consentCheckbox:
      "I consent to automated pre-inference PHI de-identification (HIPAA Safe Harbor) and triage analysis against institutional clinical guidelines.",
    acceptButton: "Accept & Begin Triage Intake",
    initializingButton: "Initializing...",
    consentRequiredError:
      "Statutory consent and clinical disclaimer acknowledgment are mandatory before clinical intake.",

    triageThreadTitle: "Clinical Intake & Triage Thread",
    sessionLabel: "Session",
    cohortLabel: "Cohort",
    sexLabel: "Sex",
    severityLabel: "Severity",
    resetButton: "Reset Intake",
    intakeReadyTitle: "Clinical Triage Intake Ready",
    intakeReadyDescription:
      "Describe patient clinical symptoms below. The system automatically scrubs PHI identifiers, evaluates emergency red flags deterministically, and cross-references verified institutional medical protocols.",
    vignettesTitle: "Demonstration Clinical Vignettes (Click to evaluate):",
    vignetteAcsTitle: "Acute Coronary Syndrome (ACS)",
    vignetteAcsDesc: "Crushing chest pain radiating to left arm + diaphoresis + PHI tokens.",
    vignetteHypoTitle: "Endocrine / Hypoglycemia",
    vignetteHypoDesc: "Blood sugar 58 mg/dL with autonomic signs (ADA Rule of 15).",
    vignetteStrokeTitle: "Neurology / Stroke FAST",
    vignetteStrokeDesc: "Facial drooping, arm drift, slurred speech (FAST criteria).",
    vignettePediatricTitle: "Pediatric Fever / NICE NG143",
    vignettePediatricDesc: "Infant fever, grunting, non-blanching petechial spots.",
    patientNarrativeHeader: "Patient Intake Narrative",
    assistantHeader: "MedGuard Clinical Decision Support",
    inputPlaceholderReady:
      "Enter patient symptoms or clinical observations (e.g., chest pain, fever, hypoglycemia)...",
    inputPlaceholderConsent: "Complete clinical consent intake first...",
    triageButton: "Triage",
    footerNotice:
      "Deterministic pre-inference red flag detector intercepts acute emergencies. In non-emergencies, guidance is strictly evidence-grounded.",
    scrubbingNotice: "Scrubbing PHI tokens & executing clinical guideline retrieval...",
    groundednessLabel: "Groundedness",
    similarityLabel: "Cosine Similarity",
    latencyLabel: "Latency",
    guidelinesCitedLabel: "Guidelines Cited",

    severityRoutine: "ROUTINE",
    severityUrgent: "URGENT",
    severityEmergency: "EMERGENCY",

    emergencyAlertTitle: "Deterministic High-Acuity Triage Alert",
    emergencyBadge: "IMMEDIATE ESCALATION REQUIRED",
    emergencyIndicatorsLabel: "Emergency Indicators Detected",
    emergencyDispatchLabel: "Emergency Dispatch",

    citationDrawerTitle: "Clinical Evidence Provenance",
    guidelineTitleLabel: "Institutional Guideline Title",
    clinicalDomainLabel: "Clinical Domain",
    publicationYearLabel: "Publication Year",
    evidenceHierarchyLabel: "Evidence Hierarchy",
    guidelineSectionLabel: "Guideline Section",
    retrievedSnippetLabel: "Retrieved Context Snippet",
    vectorSimilarityLabel: "Semantic Vector Similarity",
    cosineScoreLabel: "Cosine Similarity Score",
    viewSourceDocument: "View Source Clinical Protocol",

    // Voice STT & TTS
    voiceInputTooltip: "Speak symptoms (Sinhala or English)",
    voiceListening: "Listening... Speak clearly into your microphone",
    voiceStop: "Stop listening",
    voicePlay: "Read clinical response aloud",
    voiceStopAudio: "Stop audio playback",
    voiceAutoRead: "Auto Read Aloud",
    voicePermissionError: "Microphone permission denied. Please allow microphone access in your browser.",
    voiceNotSupported: "Speech recognition is not supported in this browser.",
  },
  si: {
    appTitle: "MedGuard AI",
    appSubtitle: "සායනික තීරණ සහායක සහ රෝගී Triage පද්ධතිය",
    navTriage: "සායනික Triage",
    navReports: "වෛද්‍ය වාර්තා",
    navRecords: "සෞඛ්‍ය ඉතිහාසය (EHR)",
    navOntology: "ICD-11 නාමාවලිය",
    navRLHF: "වෛද්‍ය RLHF සමාලෝචනය",
    navAnalytics: "වසංගතවේදී විශ්ලේෂණ",
    navEvaluation: "ඇගයීම් සහ මිණුම්දඬු",
    navFHIR: "EHR / FHIR R4 දත්ත",
    hipaaActive: "HIPAA Safe Harbor සක්‍රියයි",
    phiScrubbedNotice: "තොරතුරු කාණ්ඩ 18ක් ආරක්ෂිතව පෙරහන් කෙරේ",
    redFlagFilterStatus: "හදිසි රතු අනතුරු පෙරහන: සක්‍රියයි",
    clinicianBadge: "සත්‍යාපිත වෛද්‍යවරයා: Dr. Sarah Evans (GMC-7890123)",
    vectorIndexLabel: "දර්ශකය: මාර්ගෝපදේශ 16ක්",
    buildVersion: "නිර්මාණය 1.0.0-PROD",

    consentTitle: "සායනික බඳවාගැනීම සහ නීතිමය එකඟතාවය",
    consentProtocol: "ප්‍රොටෝකෝලය NHS/HIPAA-2026",
    cdssNoticeTitle: "සායනික තීරණ සහායක පද්ධති (CDSS) නිවේදනය:",
    cdssNoticeText:
      "MedGuard AI යනු ජාත්‍යන්තරව පිළිගත් සත්‍යාපිත වෛද්‍ය මාර්ගෝපදේශ (NICE, AHA/ACC, ADA, WHO) මත පදනම් වූ සායනික තීරණ ආධාරකයකි. මෙය ස්ථිර වෛද්‍ය රෝග විනිශ්චයක් හෝ බෙහෙත් නිර්දේශ කිරීමක් සිදු නොකරයි.",
    ageBracketLabel: "රෝගියාගේ වයස් කාණ්ඩය",
    agePediatric: "ළමා (වයස අවුරුදු 16ට අඩු)",
    ageAdult: "වැඩිහිටි (වයස අවුරුදු 16–64)",
    ageGeriatric: "වියපත් (වයස අවුරුදු 65+)",
    biologicalSexLabel: "ජීව විද්‍යාත්මක ලිංගභේදය",
    sexUnspecified: "නිශ්චිතව සඳහන් කර නැත",
    sexFemale: "ස්ත්‍රී",
    sexMale: "පුරුෂ",
    disclaimerCheckbox:
      "මෙම පද්ධතිය සායනික තීරණ ආධාරකයක් පමණක් බවත්, වෘත්තීය වෛද්‍ය පරීක්ෂණයක් හෝ හදිසි ගිලන්රථ සේවාවක් සඳහා ආදේශකයක් නොවන බවත් මම පිළිගනිමි.",
    consentCheckbox:
      "ස්වයංක්‍රීයව පෞද්ගලික තොරතුරු (PHI) ඉවත් කිරීමට සහ ආයතනික සායනික මාර්ගෝපදේශ සමඟ සංසන්දනය කිරීමට මම එකඟ වෙමි.",
    acceptButton: "එකඟ වී සායනික Triage ආරම්භ කරන්න",
    initializingButton: "ආරම්භ වෙමින් පවතී...",
    consentRequiredError:
      "සායනික බඳවාගැනීමට පෙර නීතිමය එකඟතාවය සහ වගකීම් ප්‍රකාශය තහවුරු කිරීම අනිවාර්ය වේ.",

    triageThreadTitle: "සායනික බඳවාගැනීම සහ Triage සංවාදය",
    sessionLabel: "සැසිය",
    cohortLabel: "කාණ්ඩය",
    sexLabel: "ලිංගය",
    severityLabel: "බරපතලකම",
    resetButton: "නැවුම් ආරම්භය",
    intakeReadyTitle: "සායනික Triage සූදානම්",
    intakeReadyDescription:
      "රෝගියාගේ රෝග ලක්ෂණ පහතින් සඳහන් කරන්න. පද්ධතිය මඟින් ස්වයංක්‍රීයව පෞද්ගලික තොරතුරු මකාදැමීම, ක්ෂණික හදිසි අනතුරු පරීක්ෂාව සහ සත්‍යාපිත වෛද්‍ය මාර්ගෝපදේශ සංසන්දනය සිදු කෙරේ.",
    vignettesTitle: "සායනික ආදර්ශ ගැටලු (පරීක්ෂා කිරීමට click කරන්න):",
    vignetteAcsTitle: "හෘදයාබාධ තත්ත්වය (ACS)",
    vignetteAcsDesc: "වම් අතට විහිදෙන පපුවේ තද කැක්කුම + සීතල දහඩිය + පුද්ගලික තොරතුරු.",
    vignetteHypoTitle: "දියවැඩියාව / සීනි අඩුවීම",
    vignetteHypoDesc: "රුධිර සීනි මට්ටම 58 mg/dL දක්වා අඩුවීම සහ වෙව්ලීම (ADA 15 නීතිය).",
    vignetteStrokeTitle: "ස්නායු ආබාධ / අංශභාගය (Stroke FAST)",
    vignetteStrokeDesc: "මුහුණ ඇදවීම, අත පණ නැතිවීම, වචන පැටලීම (FAST නිර්ණායක).",
    vignettePediatricTitle: "ළදරු උණ සහ ආසාදන (NICE NG143)",
    vignettePediatricDesc: "ළදරුවන්ට අධික උණ 38.9 C, අසාමාන්‍ය හැඬීම, සමෙහි ලප.",
    patientNarrativeHeader: "රෝගියාගේ සායනික සටහන",
    assistantHeader: "MedGuard සායනික තීරණ සහාය",
    inputPlaceholderReady:
      "රෝග ලක්ෂණ මෙහි සටහන් කරන්න... (උදා: පපුවේ වේදනාව, දියවැඩියාව, උණ, හුස්ම ගැනීමේ අපහසුව)...",
    inputPlaceholderConsent: "පළමුව සායනික එකඟතාවය සම්පූර්ණ කරන්න...",
    triageButton: "Triage කරන්න",
    footerNotice:
      "ක්ෂණික පෙරහන මඟින් ජීවිත අනතුරු හඳුනා ගැනේ. සාමාන්‍ය අවස්ථාවලදී උපදෙස් නිල මාර්ගෝපදේශ මත පදනම් වේ.",
    scrubbingNotice: "පෞද්ගලික තොරතුරු ඉවත් කර සායනික මාර්ගෝපදේශ සොයමින් පවතී...",
    groundednessLabel: "විශ්වාසනීයතාව",
    similarityLabel: "සමානතා දර්ශකය",
    latencyLabel: "ප්‍රතිචාර කාලය",
    guidelinesCitedLabel: "උපුටාගත් මාර්ගෝපදේශ",

    severityRoutine: "සාමාන්‍ය (ROUTINE)",
    severityUrgent: "හදිසි (URGENT)",
    severityEmergency: "අධි-හදිසි (EMERGENCY)",

    emergencyAlertTitle: "තීරණාත්මක සායනික අනතුරු ඇඟවීමයි",
    emergencyBadge: "වහාම වෛද්‍ය ප්‍රතිකාර අවශ්‍යයි",
    emergencyIndicatorsLabel: "හඳුනාගත් හදිසි රෝග ලක්ෂණ",
    emergencyDispatchLabel: "හදිසි ගිලන්රථ සේවාව",

    citationDrawerTitle: "සායනික සාක්ෂි සහ මුලාශ්‍ර පිරික්සුම",
    guidelineTitleLabel: "ආයතනික මාර්ගෝපදේශ නාමය",
    clinicalDomainLabel: "සායනික ක්ෂේත්‍රය",
    publicationYearLabel: "ප්‍රකාශිත වර්ෂය",
    evidenceHierarchyLabel: "සාක්ෂි මට්ටම",
    guidelineSectionLabel: "මාර්ගෝපදේශ අංශය",
    retrievedSnippetLabel: "උපුටාගත් සන්දර්භය",
    vectorSimilarityLabel: "දෛශික සමානතාවය",
    cosineScoreLabel: "සමානතා ලකුණු",
    viewSourceDocument: "මුල් සායනික ලේඛනය බලන්න",

    // Voice STT & TTS
    voiceInputTooltip: "කටහඬින් රෝග ලක්ෂණ කියන්න (සිංහල හෝ ඉංග්‍රීසි)",
    voiceListening: "සවන් දෙමින් පවතී... මයික්‍රෆෝනයට පැහැදිලිව කතා කරන්න",
    voiceStop: "හඬ පටිගත කිරීම නවත්වන්න",
    voicePlay: "සායනික ප්‍රතිචාරය හඬින් අසන්න",
    voiceStopAudio: "ශ්‍රව්‍ය ධාවනය නවත්වන්න",
    voiceAutoRead: "ස්වයංක්‍රීයව හඬින් කියවීම",
    voicePermissionError: "මයික්‍රෆෝනය භාවිතයට අවසර නැත. කරුණාකර ඔබගේ බ්‍රව්සරයෙන් අවසර ලබා දෙන්න.",
    voiceNotSupported: "මෙම බ්‍රව්සරය මඟින් හඬ හඳුනාගැනීම සඳහා සහය නොදක්වයි.",
  },
};
