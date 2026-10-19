import os
import json
import glob
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.monitoring import ClinicalGuidelineCatalog
from app.ingestion.chunker import ClinicalSemanticChunker
from app.ingestion.vector_store import vector_store


async def seed_clinical_guidelines(session: AsyncSession, guidelines_dir: str = "./data/guidelines") -> Dict[str, Any]:
    """
    Ingests curated clinical guidelines into the local vector index and database catalog.
    Maintains provenance and evidence levels across all searchable chunks.
    """
    chunker = ClinicalSemanticChunker(max_token_window=200, token_overlap=30)
    all_chunks: List[Dict[str, Any]] = []
    catalog_entries: List[Dict[str, Any]] = []

    pattern = os.path.join(guidelines_dir, "*.json")
    files = glob.glob(pattern)

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                doc = json.load(f)

            guideline_id = doc.get("guideline_id")
            if not guideline_id:
                continue

            chunks = chunker.chunk_structured_guideline(doc)
            chunk_dicts = [c.to_dict() for c in chunks]
            all_chunks.extend(chunk_dicts)

            catalog_entries.append({
                "guideline_id": guideline_id,
                "source_title": doc.get("source_title", "Clinical Protocol"),
                "issuing_authority": doc.get("issuing_authority", "Health Authority"),
                "clinical_domain": doc.get("clinical_domain", "General Medicine"),
                "evidence_level": doc.get("evidence_level", "Level I"),
                "publication_year": doc.get("publication_year", 2024),
                "source_url": doc.get("source_url", ""),
                "icd10_codes": doc.get("icd10_codes", []),
                "chunk_count": len(chunks)
            })
        except Exception as e:
            # Skip invalid json formatting in ingestion pipeline
            continue

    # Upsert to vector store
    # Clear existing memory if re-seeding
    vector_store.chunks = []
    import numpy as np
    vector_store.embeddings = np.empty((0, vector_store.DIMENSIONS), dtype=np.float32)
    indexed_count = vector_store.add_chunks(all_chunks)

    # Sync with relational database catalog
    for entry in catalog_entries:
        stmt = select(ClinicalGuidelineCatalog).where(ClinicalGuidelineCatalog.guideline_id == entry["guideline_id"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.source_title = entry["source_title"]
            existing.issuing_authority = entry["issuing_authority"]
            existing.clinical_domain = entry["clinical_domain"]
            existing.evidence_level = entry["evidence_level"]
            existing.publication_year = entry["publication_year"]
            existing.source_url = entry["source_url"]
            existing.icd10_codes = entry["icd10_codes"]
            existing.chunk_count = entry["chunk_count"]
            existing.is_active = True
        else:
            new_cat = ClinicalGuidelineCatalog(
                guideline_id=entry["guideline_id"],
                source_title=entry["source_title"],
                issuing_authority=entry["issuing_authority"],
                clinical_domain=entry["clinical_domain"],
                evidence_level=entry["evidence_level"],
                publication_year=entry["publication_year"],
                source_url=entry["source_url"],
                icd10_codes=entry["icd10_codes"],
                chunk_count=entry["chunk_count"],
                is_active=True
            )
            session.add(new_cat)

    await session.commit()

    return {
        "status": "SUCCESS",
        "guidelines_processed": len(catalog_entries),
        "chunks_indexed": indexed_count
    }


async def seed_patient_profiles(session: AsyncSession) -> Dict[str, Any]:
    """
    Seeds verified realistic patient profiles with longitudinal medical records
    including acute dengue fever thrombocytopenia recovery and chronic diabetes/lipid tracking.
    """
    from datetime import datetime, timedelta, timezone
    from app.models.patient import (
        PatientProfile,
        PatientMedicalRecord,
        RelationshipType,
        BiologicalSex,
        MedicalRecordType,
    )

    # Check if profiles are already seeded
    existing_stmt = select(PatientProfile)
    existing_res = await session.execute(existing_stmt)
    if existing_res.scalars().first():
        return {"status": "ALREADY_SEEDED", "profiles_seeded": 0}

    from app.database import utc_now
    now = utc_now()

    # 1. Self: Alex Turner (34M) - Acute Dengue Fever 5-day Platelet Progression
    alex = PatientProfile(
        first_name="Alex",
        last_name="Turner",
        relationship=RelationshipType.SELF,
        date_of_birth="1992-06-15",
        biological_sex=BiologicalSex.MALE,
        blood_group="O+",
        allergies=["Penicillin (Mild Urticaria)"],
        chronic_conditions=[],
        emergency_contact_phone="+94 77 123 4567",
        notes="Previous acute dengue fever episode successfully managed with supportive fluid therapy."
    )
    session.add(alex)
    await session.flush()

    # Day 1: 4 days ago
    alex_d1 = PatientMedicalRecord(
        profile_id=alex.id,
        record_type=MedicalRecordType.LAB_REPORT,
        record_date=now - timedelta(days=4),
        title="Full Blood Count (FBC) - Day 1 Acute Febrile Onset",
        overall_status="ABNORMAL_ELEVATED_RISK",
        qualitative_verdict="POSITIVE",
        extracted_biomarkers=[
            {
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "display_name_si": "පට්ටිකා ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "95000",
                "numeric_value": 95000.0,
                "unit": "/uL",
                "ref_interval": "150000 - 450000",
                "status": "DECREASED",
                "status_si": "අඩු වී ඇත (Decreased)",
                "is_abnormal": True,
                "is_critical": False,
                "interpretation_en": "Thrombocytopenia detected. Initial dengue monitoring indicated.",
                "interpretation_si": "පට්ටිකා අඩුවීමක් හඳුනාගෙන ඇත. ඩෙංගු නිරීක්ෂණය අත්‍යවශ්‍යයි."
            },
            {
                "canonical_id": "wbc",
                "display_name_en": "Total White Blood Cells (WBC)",
                "display_name_si": "සුදු රුධිරාණු ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "3800",
                "numeric_value": 3800.0,
                "unit": "/uL",
                "ref_interval": "4000 - 11000",
                "status": "DECREASED",
                "status_si": "අඩු වී ඇත (Decreased)",
                "is_abnormal": True,
                "is_critical": False,
                "interpretation_en": "Leukopenia consistent with early viral infection phase.",
                "interpretation_si": "වෛරස් ආසාදන ආරම්භක අවස්ථාවට අනුකූලව සුදු රුධිරාණු අඩුවී ඇත."
            },
            {
                "canonical_id": "hemoglobin",
                "display_name_en": "Hemoglobin (Hb)",
                "display_name_si": "හීමොග්ලොබින්",
                "category": "Hematology",
                "raw_value": "14.5",
                "numeric_value": 14.5,
                "unit": "g/dL",
                "ref_interval": "12.0 - 16.5",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False,
                "interpretation_en": "Normal hemoglobin level.",
                "interpretation_si": "සාමාන්‍ය නිරෝගී මට්ටම."
            },
            {
                "canonical_id": "pcv",
                "display_name_en": "Packed Cell Volume (PCV)",
                "display_name_si": "PCV රුධිර සාන්ද්‍රණය",
                "category": "Hematology",
                "raw_value": "43.0",
                "numeric_value": 43.0,
                "unit": "%",
                "ref_interval": "36.0 - 48.0",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False,
                "interpretation_en": "Baseline hematocrit within standard limits.",
                "interpretation_si": "ආරම්භක රුධිර සාන්ද්‍රණය සාමාන්‍යයි."
            },
            {
                "canonical_id": "dengue_ns1",
                "display_name_en": "Dengue NS1 Antigen",
                "display_name_si": "ඩෙංගු NS1 ඇන්ටිජන් පරීක්ෂාව",
                "category": "Infectious Disease Serology",
                "raw_value": "POSITIVE",
                "numeric_value": None,
                "unit": "",
                "status": "POSITIVE",
                "status_si": "ධනාත්මකයි (Positive)",
                "is_abnormal": True,
                "is_critical": False,
                "interpretation_en": "Dengue virus non-structural protein 1 confirmed.",
                "interpretation_si": "ඩෙංගු වෛරස් ප්‍රතිදේහජනක තහවුරු විය."
            }
        ],
        correlated_icd11=[{"condition": "Dengue Fever", "icd11": "1D20", "urgency": "URGENT"}],
        notes="Day 1 acute high fever, retro-orbital headache, body aches."
    )
    session.add(alex_d1)

    # Day 2: 3 days ago
    alex_d2 = PatientMedicalRecord(
        profile_id=alex.id,
        record_type=MedicalRecordType.LAB_REPORT,
        record_date=now - timedelta(days=3),
        title="Full Blood Count (FBC) - Day 2 Fever Monitoring",
        overall_status="ABNORMAL_ELEVATED_RISK",
        qualitative_verdict="POSITIVE",
        extracted_biomarkers=[
            {
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "display_name_si": "පට්ටිකා ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "58000",
                "numeric_value": 58000.0,
                "unit": "/uL",
                "ref_interval": "150000 - 450000",
                "status": "DECREASED",
                "status_si": "අඩු වී ඇත (Decreased)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "wbc",
                "display_name_en": "Total White Blood Cells (WBC)",
                "display_name_si": "සුදු රුධිරාණු ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "3100",
                "numeric_value": 3100.0,
                "unit": "/uL",
                "ref_interval": "4000 - 11000",
                "status": "DECREASED",
                "status_si": "අඩු වී ඇත (Decreased)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "hemoglobin",
                "display_name_en": "Hemoglobin (Hb)",
                "display_name_si": "හීමොග්ලොබින්",
                "category": "Hematology",
                "raw_value": "15.2",
                "numeric_value": 15.2,
                "unit": "g/dL",
                "ref_interval": "12.0 - 16.5",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            },
            {
                "canonical_id": "pcv",
                "display_name_en": "Packed Cell Volume (PCV)",
                "display_name_si": "PCV රුධිර සාන්ද්‍රණය",
                "category": "Hematology",
                "raw_value": "46.5",
                "numeric_value": 46.5,
                "unit": "%",
                "ref_interval": "36.0 - 48.0",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            }
        ],
        notes="Progressive decline in platelet counts. Fluid management initiated."
    )
    session.add(alex_d2)

    # Day 3: 2 days ago (Critical Phase Nadir)
    alex_d3 = PatientMedicalRecord(
        profile_id=alex.id,
        record_type=MedicalRecordType.LAB_REPORT,
        record_date=now - timedelta(days=2),
        title="Full Blood Count (FBC) - Day 3 Critical Phase Evaluation",
        overall_status="CRITICAL_EMERGENCY",
        qualitative_verdict="POSITIVE",
        extracted_biomarkers=[
            {
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "display_name_si": "පට්ටිකා ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "42000",
                "numeric_value": 42000.0,
                "unit": "/uL",
                "ref_interval": "150000 - 450000",
                "status": "CRITICAL_LOW",
                "status_si": "තීරණාත්මක ලෙස අඩුයි (Critical Low)",
                "is_abnormal": True,
                "is_critical": True,
                "interpretation_en": "Critical thrombocytopenia (<50,000 /uL). High hemorrhage risk.",
                "interpretation_si": "පට්ටිකා 50,000ට වඩා අඩුයි. රුධිර වහනය වැළැක්වීමට නේවාසික ප්‍රතිකාර අවශ්‍යයි."
            },
            {
                "canonical_id": "wbc",
                "display_name_en": "Total White Blood Cells (WBC)",
                "display_name_si": "සුදු රුධිරාණු ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "3200",
                "numeric_value": 3200.0,
                "unit": "/uL",
                "ref_interval": "4000 - 11000",
                "status": "DECREASED",
                "status_si": "අඩු වී ඇත (Decreased)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "pcv",
                "display_name_en": "Packed Cell Volume (PCV)",
                "display_name_si": "PCV රුධිර සාන්ද්‍රණය",
                "category": "Hematology",
                "raw_value": "49.5",
                "numeric_value": 49.5,
                "unit": "%",
                "ref_interval": "36.0 - 48.0",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (Elevated)",
                "is_abnormal": True,
                "is_critical": False,
                "interpretation_en": "Hematocrit elevated >20% above baseline indicating plasma leakage.",
                "interpretation_si": "ප්ලාස්මා කාන්දු වීම නිසා රුධිර සාන්ද්‍රණය 20% කට වඩා වැඩි වී ඇත."
            }
        ],
        correlated_icd11=[{"condition": "Dengue with Warning Signs", "icd11": "1D20.1", "urgency": "EMERGENCY"}],
        notes="Critical phase nadir. Strict bed rest and iv/oral fluid balance monitoring."
    )
    session.add(alex_d3)

    # Day 4: 1 day ago (Early Recovery)
    alex_d4 = PatientMedicalRecord(
        profile_id=alex.id,
        record_type=MedicalRecordType.LAB_REPORT,
        record_date=now - timedelta(days=1),
        title="Full Blood Count (FBC) - Day 4 Early Recovery Phase",
        overall_status="ABNORMAL_ELEVATED_RISK",
        qualitative_verdict="NOT_APPLICABLE",
        extracted_biomarkers=[
            {
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "display_name_si": "පට්ටිකා ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "78000",
                "numeric_value": 78000.0,
                "unit": "/uL",
                "ref_interval": "150000 - 450000",
                "status": "DECREASED",
                "status_si": "අඩු වී ඇත (Decreased)",
                "is_abnormal": True,
                "is_critical": False,
                "interpretation_en": "Platelets recovering from critical nadir (+36,000 /uL).",
                "interpretation_si": "පට්ටිකා නැවත ඉහළ යමින් පවතී (+36,000 /uL)."
            },
            {
                "canonical_id": "wbc",
                "display_name_en": "Total White Blood Cells (WBC)",
                "display_name_si": "සුදු රුධිරාණු ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "4500",
                "numeric_value": 4500.0,
                "unit": "/uL",
                "ref_interval": "4000 - 11000",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            },
            {
                "canonical_id": "pcv",
                "display_name_en": "Packed Cell Volume (PCV)",
                "display_name_si": "PCV රුධිර සාන්ද්‍රණය",
                "category": "Hematology",
                "raw_value": "44.0",
                "numeric_value": 44.0,
                "unit": "%",
                "ref_interval": "36.0 - 48.0",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            }
        ],
        notes="Fever subsided, appetite returning, early marrow recovery signs."
    )
    session.add(alex_d4)

    # Day 5: Today (Marked Platelet Recovery)
    alex_d5 = PatientMedicalRecord(
        profile_id=alex.id,
        record_type=MedicalRecordType.LAB_REPORT,
        record_date=now - timedelta(hours=2),
        title="Full Blood Count (FBC) - Day 5 Convalescent Discharge Evaluation",
        overall_status="ABNORMAL_ELEVATED_RISK",
        qualitative_verdict="NOT_APPLICABLE",
        extracted_biomarkers=[
            {
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "display_name_si": "පට්ටිකා ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "148000",
                "numeric_value": 148000.0,
                "unit": "/uL",
                "ref_interval": "150000 - 450000",
                "status": "DECREASED",
                "status_si": "අඩු වී ඇත (නමුත් සාමාන්‍ය සීමාවට ආසන්නයි)",
                "is_abnormal": True,
                "is_critical": False,
                "interpretation_en": "Platelet count near normal threshold (+70,000 /uL recovery).",
                "interpretation_si": "පට්ටිකා අගය සාමාන්‍ය මට්ටමට ඉතා ආසන්න වී ඇත (+70,000 /uL ප්‍රකෘතිමත් වීම)."
            },
            {
                "canonical_id": "wbc",
                "display_name_en": "Total White Blood Cells (WBC)",
                "display_name_si": "සුදු රුධිරාණු ප්‍රමාණය",
                "category": "Hematology",
                "raw_value": "5800",
                "numeric_value": 5800.0,
                "unit": "/uL",
                "ref_interval": "4000 - 11000",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            },
            {
                "canonical_id": "hemoglobin",
                "display_name_en": "Hemoglobin (Hb)",
                "display_name_si": "හීමොග්ලොබින්",
                "category": "Hematology",
                "raw_value": "14.1",
                "numeric_value": 14.1,
                "unit": "g/dL",
                "ref_interval": "12.0 - 16.5",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            },
            {
                "canonical_id": "pcv",
                "display_name_en": "Packed Cell Volume (PCV)",
                "display_name_si": "PCV රුධිර සාන්ද්‍රණය",
                "category": "Hematology",
                "raw_value": "41.0",
                "numeric_value": 41.0,
                "unit": "%",
                "ref_interval": "36.0 - 48.0",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            }
        ],
        notes="Clinical recovery complete. Discharged from acute monitoring."
    )
    session.add(alex_d5)

    # 2. Father: Arthur Turner (68M) - Longitudinal Type 2 Diabetes & Lipid Panel Monitoring
    arthur = PatientProfile(
        first_name="Arthur",
        last_name="Turner",
        relationship=RelationshipType.FATHER,
        date_of_birth="1958-03-22",
        biological_sex=BiologicalSex.MALE,
        blood_group="B+",
        allergies=["Aspirin (Bronchospasm)"],
        chronic_conditions=["Type 2 Diabetes Mellitus", "Essential Hypertension", "Dyslipidemia"],
        emergency_contact_phone="+94 71 987 6543",
        notes="Long-standing diabetes under Metformin and Atorvastatin pharmacotherapy."
    )
    session.add(arthur)
    await session.flush()

    # Arthur record 1: 6 months ago (High risk, uncontrolled)
    arthur_r1 = PatientMedicalRecord(
        profile_id=arthur.id,
        record_type=MedicalRecordType.LAB_REPORT,
        record_date=now - timedelta(days=180),
        title="Comprehensive Metabolic & Fasting Lipid Panel - Baseline",
        overall_status="ABNORMAL_ELEVATED_RISK",
        qualitative_verdict="NOT_APPLICABLE",
        extracted_biomarkers=[
            {
                "canonical_id": "fbs",
                "display_name_en": "Fasting Blood Sugar (FBS)",
                "display_name_si": "නිරාහාර රුධිර සීනි මට්ටම",
                "category": "Glycemic Metabolism",
                "raw_value": "210",
                "numeric_value": 210.0,
                "unit": "mg/dL",
                "ref_interval": "70 - 99",
                "status": "CRITICAL_HIGH",
                "status_si": "තීරණාත්මක ලෙස ඉහළයි (Critical High)",
                "is_abnormal": True,
                "is_critical": True
            },
            {
                "canonical_id": "hba1c",
                "display_name_en": "Glycated Hemoglobin (HbA1c)",
                "display_name_si": "HbA1c ත්‍රෛමාසික සීනි සාමාන්‍යය",
                "category": "Glycemic Metabolism",
                "raw_value": "9.4",
                "numeric_value": 9.4,
                "unit": "%",
                "ref_interval": "4.0 - 5.6",
                "status": "CRITICAL_HIGH",
                "status_si": "තීරණාත්මක ලෙස ඉහළයි (Critical High)",
                "is_abnormal": True,
                "is_critical": True
            },
            {
                "canonical_id": "cholesterol_total",
                "display_name_en": "Total Cholesterol",
                "display_name_si": "මුළු කොලෙස්ටරෝල් මට්ටම",
                "category": "Lipid Profile",
                "raw_value": "268",
                "numeric_value": 268.0,
                "unit": "mg/dL",
                "ref_interval": "125 - 200",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (Elevated)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "ldl_cholesterol",
                "display_name_en": "LDL Cholesterol",
                "display_name_si": "LDL අහිතකර කොලෙස්ටරෝල්",
                "category": "Lipid Profile",
                "raw_value": "178",
                "numeric_value": 178.0,
                "unit": "mg/dL",
                "ref_interval": "50 - 100",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (Elevated)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "serum_creatinine",
                "display_name_en": "Serum Creatinine",
                "display_name_si": "ක්‍රියේටිනින් (වකුගඩු ක්‍රියාකාරීත්වය)",
                "category": "Renal Function",
                "raw_value": "1.4",
                "numeric_value": 1.4,
                "unit": "mg/dL",
                "ref_interval": "0.7 - 1.2",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (Elevated)",
                "is_abnormal": True,
                "is_critical": False
            }
        ],
        correlated_icd11=[
            {"condition": "Type 2 Diabetes Mellitus", "icd11": "5A11"},
            {"condition": "Pure Hypercholesterolaemia", "icd11": "5C80.0"}
        ],
        notes="Uncontrolled hyperglycemia and hyperlipidemia. Dose of Metformin increased, Atorvastatin added."
    )
    session.add(arthur_r1)

    # Arthur record 2: 3 months ago (Intermediate improvement)
    arthur_r2 = PatientMedicalRecord(
        profile_id=arthur.id,
        record_type=MedicalRecordType.LAB_REPORT,
        record_date=now - timedelta(days=90),
        title="Quarterly Glycemic & Statin Response Follow-up",
        overall_status="ABNORMAL_ELEVATED_RISK",
        qualitative_verdict="NOT_APPLICABLE",
        extracted_biomarkers=[
            {
                "canonical_id": "fbs",
                "display_name_en": "Fasting Blood Sugar (FBS)",
                "display_name_si": "නිරාහාර රුධිර සීනි මට්ටම",
                "category": "Glycemic Metabolism",
                "raw_value": "162",
                "numeric_value": 162.0,
                "unit": "mg/dL",
                "ref_interval": "70 - 99",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (Elevated)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "hba1c",
                "display_name_en": "Glycated Hemoglobin (HbA1c)",
                "display_name_si": "HbA1c ත්‍රෛමාසික සීනි සාමාන්‍යය",
                "category": "Glycemic Metabolism",
                "raw_value": "8.1",
                "numeric_value": 8.1,
                "unit": "%",
                "ref_interval": "4.0 - 5.6",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (Elevated)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "cholesterol_total",
                "display_name_en": "Total Cholesterol",
                "display_name_si": "මුළු කොලෙස්ටරෝල් මට්ටම",
                "category": "Lipid Profile",
                "raw_value": "224",
                "numeric_value": 224.0,
                "unit": "mg/dL",
                "ref_interval": "125 - 200",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (Elevated)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "ldl_cholesterol",
                "display_name_en": "LDL Cholesterol",
                "display_name_si": "LDL අහිතකර කොලෙස්ටරෝල්",
                "category": "Lipid Profile",
                "raw_value": "138",
                "numeric_value": 138.0,
                "unit": "mg/dL",
                "ref_interval": "50 - 100",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (Elevated)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "serum_creatinine",
                "display_name_en": "Serum Creatinine",
                "display_name_si": "ක්‍රියේටිනින් (වකුගඩු ක්‍රියාකාරීත්වය)",
                "category": "Renal Function",
                "raw_value": "1.2",
                "numeric_value": 1.2,
                "unit": "mg/dL",
                "ref_interval": "0.7 - 1.2",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            }
        ],
        notes="Progressive decline in glucose and lipid markers under enhanced therapy."
    )
    session.add(arthur_r2)

    # Arthur record 3: 2 weeks ago (Marked improvement)
    arthur_r3 = PatientMedicalRecord(
        profile_id=arthur.id,
        record_type=MedicalRecordType.LAB_REPORT,
        record_date=now - timedelta(days=14),
        title="Latest Glycemic & Renal Health Panel",
        overall_status="ABNORMAL_ELEVATED_RISK",
        qualitative_verdict="NOT_APPLICABLE",
        extracted_biomarkers=[
            {
                "canonical_id": "fbs",
                "display_name_en": "Fasting Blood Sugar (FBS)",
                "display_name_si": "නිරාහාර රුධිර සීනි මට්ටම",
                "category": "Glycemic Metabolism",
                "raw_value": "122",
                "numeric_value": 122.0,
                "unit": "mg/dL",
                "ref_interval": "70 - 99",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (නමුත් සැලකිය යුතු ලෙස අඩු වී ඇත)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "hba1c",
                "display_name_en": "Glycated Hemoglobin (HbA1c)",
                "display_name_si": "HbA1c ත්‍රෛමාසික සීනි සාමාන්‍යය",
                "category": "Glycemic Metabolism",
                "raw_value": "6.8",
                "numeric_value": 6.8,
                "unit": "%",
                "ref_interval": "4.0 - 5.6",
                "status": "ELEVATED",
                "status_si": "ඉහළ ගොස් ඇත (ADA ඉලක්කයට ආසන්නයි)",
                "is_abnormal": True,
                "is_critical": False
            },
            {
                "canonical_id": "cholesterol_total",
                "display_name_en": "Total Cholesterol",
                "display_name_si": "මුළු කොලෙස්ටරෝල් මට්ටම",
                "category": "Lipid Profile",
                "raw_value": "184",
                "numeric_value": 184.0,
                "unit": "mg/dL",
                "ref_interval": "125 - 200",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            },
            {
                "canonical_id": "ldl_cholesterol",
                "display_name_en": "LDL Cholesterol",
                "display_name_si": "LDL අහිතකර කොලෙස්ටරෝල්",
                "category": "Lipid Profile",
                "raw_value": "98",
                "numeric_value": 98.0,
                "unit": "mg/dL",
                "ref_interval": "50 - 100",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            },
            {
                "canonical_id": "serum_creatinine",
                "display_name_en": "Serum Creatinine",
                "display_name_si": "ක්‍රියේටිනින් (වකුගඩු ක්‍රියාකාරීත්වය)",
                "category": "Renal Function",
                "raw_value": "0.95",
                "numeric_value": 0.95,
                "unit": "mg/dL",
                "ref_interval": "0.7 - 1.2",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            }
        ],
        notes="Excellent compliance. HbA1c reduced from 9.4% to 6.8%. Lipid levels fully normalized."
    )
    session.add(arthur_r3)

    # 3. Mother: Eleanor Turner (65F) - Routine Annual Health Check
    eleanor = PatientProfile(
        first_name="Eleanor",
        last_name="Turner",
        relationship=RelationshipType.MOTHER,
        date_of_birth="1961-09-10",
        biological_sex=BiologicalSex.FEMALE,
        blood_group="A+",
        allergies=["Sulfa drugs (Skin Exanthema)"],
        chronic_conditions=["Osteoarthritis (Knee)"],
        emergency_contact_phone="+94 77 123 4567",
        notes="Active lifestyle with regular physiotherapy for knee osteoarthritis."
    )
    session.add(eleanor)
    await session.flush()

    eleanor_r1 = PatientMedicalRecord(
        profile_id=eleanor.id,
        record_type=MedicalRecordType.LAB_REPORT,
        record_date=now - timedelta(days=45),
        title="Annual Preventive Geriatric Health Screening",
        overall_status="ALL_NORMAL",
        qualitative_verdict="NOT_APPLICABLE",
        extracted_biomarkers=[
            {
                "canonical_id": "hemoglobin",
                "display_name_en": "Hemoglobin (Hb)",
                "display_name_si": "හීමොග්ලොබින්",
                "category": "Hematology",
                "raw_value": "13.8",
                "numeric_value": 13.8,
                "unit": "g/dL",
                "ref_interval": "12.0 - 15.5",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            },
            {
                "canonical_id": "fbs",
                "display_name_en": "Fasting Blood Sugar (FBS)",
                "display_name_si": "නිරාහාර රුධිර සීනි මට්ටම",
                "category": "Glycemic Metabolism",
                "raw_value": "89",
                "numeric_value": 89.0,
                "unit": "mg/dL",
                "ref_interval": "70 - 99",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            },
            {
                "canonical_id": "cholesterol_total",
                "display_name_en": "Total Cholesterol",
                "display_name_si": "මුළු කොලෙස්ටරෝල් මට්ටම",
                "category": "Lipid Profile",
                "raw_value": "182",
                "numeric_value": 182.0,
                "unit": "mg/dL",
                "ref_interval": "125 - 200",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            },
            {
                "canonical_id": "serum_creatinine",
                "display_name_en": "Serum Creatinine",
                "display_name_si": "ක්‍රියේටිනින් (වකුගඩු ක්‍රියාකාරීත්වය)",
                "category": "Renal Function",
                "raw_value": "0.82",
                "numeric_value": 0.82,
                "unit": "mg/dL",
                "ref_interval": "0.6 - 1.1",
                "status": "NORMAL",
                "status_si": "සාමාන්‍ය (Normal)",
                "is_abnormal": False,
                "is_critical": False
            }
        ],
        notes="All parameters within normal reference limits. Scheduled for annual routine checkup."
    )
    session.add(eleanor_r1)

    await session.commit()
    return {"status": "SUCCESS", "profiles_seeded": 3}

