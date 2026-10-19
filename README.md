# MedGuard AI

Production-Grade, HIPAA/GDPR-Aligned Clinical Decision Support & Patient Triage Platform

---

## Architectural Overview

MedGuard AI is an evidence-grounded Clinical Decision Support System (CDSS) and patient triage conversational engine. The architecture adheres to clinical software engineering standards inspired by NHS Digital and Epic Systems, implementing the complete AI Project Cycle as working software modules.

```mermaid
flowchart TD
    Patient([Patient Intake]) --> ConsentCheck[Statutory Consent & Disclaimer]
    ConsentCheck --> PHIScrubber[HIPAA Safe Harbor PHI Scrubber]
    PHIScrubber --> PreInference[Deterministic Red-Flag Filter]
    
    PreInference -- Acute Red Flag Triggered --> EmergencyBanner[Emergency Dispatch & Hotline Banner]
    EmergencyBanner --> AuditLogger[HIPAA Audit Log]
    
    PreInference -- Nominal / Non-Emergency --> RAGRetriever[Clinical Vector Store Search]
    RAGRetriever --> CitationBinder[Evidence Binder & [Ref X] Attributions]
    CitationBinder --> ResponseGenerator[Evidence-Grounded CDS Synthesis]
    ResponseGenerator --> TelemetryAudit[Groundedness & Telemetry Logging]
    
    ResponseGenerator --> RLHFQueue[Clinician RLHF Review Portal]
    RLHFQueue --> LikertRating[1-5 Likert Accuracy & Error Typologies]
    LikertRating --> ClinicianRewrite[Ground Truth Supervised Rewrites]
    ClinicianRewrite --> SFTExporter[OpenAI / Llama JSONL Dataset Export]
    
    ResponseGenerator --> EHRExporter[HL7 FHIR R4 PatientSummary Bundle]
    EHRExporter --> HospitalEHR[(Epic / Cerner EHR Systems)]
```

---

## AI Project Cycle Implementation

### 1. Problem Scoping & Ethical Guardrails (`backend/app/compliance/`)
- **Deterministic Pre-Inference Triage Filter** (`red_flag_detector.py`): Microsecond bilingual (English + Sinhala) regex pattern scanner detecting high-acuity life threats (Acute Coronary Syndrome, Acute Ischemic Stroke FAST, Sepsis qSOFA criteria, Severe Dyspnea, Anaphylaxis, Level 3 Neuroglycopenia, and Suicidal Crisis) BEFORE any model inference. Returns emergency escalation directives and dispatch numbers: Sri Lanka (`1990` Suwa Seriya, `1926` Mental Health), UK (`999`), US/Canada (`911`), EU (`112`).
- **HIPAA Safe Harbor PHI Scrubber** (`phi_scrubber.py`): Redacts 18 HIPAA identifier classes (names, SSNs, NHS/NIC IDs, phone numbers, email addresses, MRNs, dates of birth, street addresses) with native English and Sinhala pattern recognition prior to persistence.
- **Bilingual Internationalization (i18n)**: Global instant language switching (`[ EN | සිංහල ]`) across navigation, statutory consent, clinical intake, emergency escalation banners, and evidence provenance drawers.
- **Tamper-Evident Audit Trail** (`audit_logger.py`): Immutable logging dual-written to disk JSONL archives and database records with salted SHA-256 IP anonymization.

### 2. Medical Data Acquisition & Ingestion (`backend/app/ingestion/`)
- **Clinical Semantic Chunker** (`chunker.py`): Decomposes clinical guidelines preserving evidence levels, issuing authorities, clinical domains, and section headers.
- **Deterministic Dense Vector Store** (`vector_store.py`): 384-dimensional dense semantic feature index with cosine similarity ranking, clinical keyword boosting, and disk persistence.
- **Curated Guideline Catalog** (`seed_loader.py` & `backend/data/guidelines/`): 7 verified protocols from NICE, AHA/ACC, Surviving Sepsis Campaign, ADA, and WHO indexed into 16 semantically tagged chunks with ICD-10 and MeSH classification.

### 3. Data Exploration & Analytics (`backend/app/analytics/`, `frontend/src/app/analytics/`)
- Aggregated symptom frequency distributions, clinical sub-specialty query breakdowns, intent categorizations, and query token histograms derived from anonymized interaction logs.
- Interactive Recharts visual dashboard for clinical governance surveillance.

### 4. Modeling: RAG + RLHF Alignment (`backend/app/engine/`, `frontend/src/app/rlhf/`)
- **Evidence-Grounded RAG Pipeline** (`rag_pipeline.py`): Enforces inline citation badges (`[Ref 1]`, `[Ref 2]`), calculates factual claim groundedness scores, and appends mandatory safety-netting instructions.
- **Clinician RLHF Portal** (`rlhf_dataset_generator.py`): Verified Healthcare Providers review model responses, submit 1–5 Likert accuracy ratings, tag error typologies (`hallucination_flag`, `safety_guideline_violation`, `omission_of_red_flag_symptom`), write ground-truth completions, and export fine-tuning `.jsonl` datasets (OpenAI ChatML and Llama/Alpaca formats).

### 5. Evaluation Suite (`backend/app/evaluation/`, `frontend/src/app/evaluation/`)
- Standardized multi-case clinical vignettes assessing Groundedness (claim overlap with institutional guidelines), Clinical Relevance, Safety Pass Rate (zero unauthorized diagnostic prescribing claims), and Hallucination Frequency.
- Automated benchmark runner with historical metric trend tracking.

### 6. Deployment & EHR Interoperability (`backend/app/integrations/`, `frontend/src/app/fhir/`)
- Multi-container Docker Compose orchestration with isolated internal network boundaries.
- Standardized **HL7 FHIR Release 4 Document Bundle** (`/api/v1/fhir/PatientSummary/{session_id}`) exporting Composition, Patient, Observation (Acuity Level with SNOMED CT `225399009`), and Guideline Citations.

### 7. Maintenance, Drift & Misinformation Monitoring (`backend/app/monitoring/`)
- Real-time monitoring of retrieval similarity moving averages, low-confidence query rates, hallucination flags, p95 latency, and guideline currency audits (alerting when protocols exceed 3 years since publication).

### 8. Patient Profiles & Longitudinal EHR Records (`backend/app/engine/patient_history_engine.py`, `frontend/src/app/records/`, `frontend/src/app/reports/`)
- **Family Health Profiles**: Comprehensive multilingual patient directory managing relationship hierarchies (`SELF`, `FATHER`, `MOTHER`, `SPOUSE`, `CHILD`, etc.), biological sex, blood group, allergies, chronic conditions, emergency contact numbers, and clinical history notes.
- **Biomarker Trajectory Analytics**: Automated mathematical calculation of multi-point longitudinal trajectories (`IMPROVING`, `DETERIORATING`, `STABLE`, `CRITICAL_ATTENTION`) across hematological, metabolic, lipid, and renal markers (such as Platelet counts in Dengue fever, Fasting Blood Sugar, HbA1c, and Total Cholesterol).
- **Direct EHR Diagnostic Ingestion**: One-click integration in the Medical Report Diagnostic Analyzer allowing clinicians and patients to persist parsed laboratory reports directly into longitudinal profiles with real-time trajectory visualization and timeline audits.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14 (App Router, TypeScript), Tailwind CSS (Strict Clinical Theme), Recharts, Lucide |
| **Backend API** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Uvicorn |
| **Database & Vector** | PostgreSQL 16 / SQLite (Async aiosqlite), 384-dimensional dense cosine index |
| **Security** | JWT (HS256), Bcrypt, Regex Safe Harbor Scrubbing, Salted SHA-256 IP Hashing |
| **DevOps** | Docker, Docker Compose, GitHub Actions CI, Pytest |

---

## Clinical Design System

Inspired by **Epic Systems** and **NHS Digital**:
- High-contrast slate typography (`#0F172A`)
- Clinical teal accents (`#0D9488`)
- Warm neutral clinical surfaces (`#F8FAFC`)
- Semantic severity badges:
  - **Routine**: `#15803D` / `#F0FDF4`
  - **Urgent**: `#B45309` / `#FFFBEB`
  - **Emergency Red**: `#B91C1C` / `#FEF2F2`
- High tabular data density with accessible contrast ratios.

---

## Quickstart

### Option A: Docker Compose (Production Multi-Container)

```bash
# Clone and launch all services
docker compose up --build
```

- Frontend Clinical Portal: `http://localhost:3000`
- Backend API & Interactive Docs: `http://localhost:8000/docs`
- Visual Database Explorer (Web GUI): `http://localhost:8081`
- Operational Health Check: `http://localhost:8000/api/v1/health`

### Option B: Local Developer Mode

#### 1. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run Uvicorn server (auto-bootstraps database and guidelines on startup)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## Automated Test Suites

Execute full unit and integration tests across compliance, RAG, and API routers:
```bash
PYTHONPATH=backend pytest -v backend/tests/
```

Execute frontend production build:
```bash
cd frontend
npm run build
```

---

## Pre-Seeded Demonstration Accounts

| Role | Email | Password | Identifier / Credential |
|---|---|---|---|
| **Clinician** | `dr.evans@hospital.nhs.uk` | `Clinical2026!` | GMC-7890123 (UK Medical Council) |
| **Auditor** | `compliance@medguard.org` | `Auditor2026!` | HCCA-CHPC-491 (Compliance Officer) |
| **Patient** | `patient@healthcare.org` | `Patient2026!` | Verified Consent Registered |

---

## Regulatory Compliance Statements
- **HIPAA**: Conforms to 45 CFR § 164.514(b) (Safe Harbor Method of De-Identification) and 45 CFR § 164.312(b) (Audit Controls).
- **GDPR**: Implements Data Minimization (Article 5(1)(c)) and Purpose Limitation.
- **CDSS Classification**: Assistive Decision Support; non-diagnostic device pursuant to FDA Section 520(o)(1)(E) and EU MDR Annex VIII.
