import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pathology import Pathology, MedicalSpecialty, TriageAcuityLevel
from app.knowledge.seed_corpus import CLINICAL_PATHOLOGY_CORPUS
from app.ingestion.vector_store import ClinicalVectorStore, vector_store

logger = logging.getLogger("medguard.knowledge.loader")


def create_pathology_vector_chunks(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Constructs high-density semantic vector chunks from a structured pathology record.
    Segments knowledge into:
    1. Clinical Presentation & Red Flag Triage
    2. Diagnostic Workup & Evidence-Based Clinical Management
    """
    icd11 = record["icd11_code"]
    name = record["clinical_name"]
    aliases = record.get("common_aliases", [])
    specialty = record["medical_specialty"]
    specialty_str = specialty.value if isinstance(specialty, MedicalSpecialty) else str(specialty)
    acuity = record["baseline_acuity"]
    acuity_str = acuity.value if isinstance(acuity, TriageAcuityLevel) else str(acuity)

    symptoms = record.get("cardinal_symptoms", {})
    primary_syms = [s["symptom"] if isinstance(s, dict) else str(s) for s in symptoms.get("primary", [])]
    secondary_syms = [s["symptom"] if isinstance(s, dict) else str(s) for s in symptoms.get("secondary", [])]
    red_flags = record.get("red_flag_criteria", [])

    workup = record.get("diagnostic_workup", {})
    mgmt = record.get("evidence_based_management", {})
    source = record.get("source_metadata", {})

    # Chunk 1: Clinical Presentation, Symptomatology & Emergency Red Flags
    presentation_text = (
        f"Pathology: {name} (ICD-11: {icd11}, ICD-10: {record.get('icd10_code', 'N/A')}). "
        f"Medical Specialty: {specialty_str}. Baseline Acuity: {acuity_str}. "
        f"Pathophysiology: {record.get('pathophysiology_overview', '')} "
        f"Primary Cardinal Symptoms: {'; '.join(primary_syms)}. "
        f"Secondary Symptoms: {'; '.join(secondary_syms)}. "
        f"Deterministic Red Flag Criteria: {'; '.join(red_flags)}. "
        f"Common Aliases & Synonyms: {', '.join(aliases)}."
    )

    presentation_keywords = [
        name.lower(),
        icd11.lower(),
        specialty_str.lower(),
        acuity_str.lower(),
    ] + [a.lower() for a in aliases] + [s.lower() for s in primary_syms]

    chunk_1 = {
        "chunk_id": f"pathology_{icd11}_presentation",
        "clinical_domain": specialty_str,
        "section_header": f"ICD-11 {icd11}: {name} - Clinical Presentation & Red Flags",
        "text_content": presentation_text,
        "keywords": presentation_keywords[:15],
        "metadata": {
            "source": f"WHO ICD-11 / {source.get('issuing_authority', 'Clinical Protocol')}",
            "icd11_code": icd11,
            "icd10_code": record.get("icd10_code"),
            "clinical_name": name,
            "medical_specialty": specialty_str,
            "baseline_acuity": acuity_str,
            "red_flag_criteria": red_flags,
            "chunk_type": "clinical_presentation"
        }
    }

    # Chunk 2: Diagnostic Workup, Pharmacotherapy & Management Protocols
    workup_labs = workup.get("initial_labs", [])
    workup_imaging = workup.get("imaging_ecg", [])
    workup_confirmatory = workup.get("confirmatory_tests", [])
    mgmt_lifestyle = mgmt.get("first_line_lifestyle", [])
    mgmt_pharma = mgmt.get("pharmacotherapy", [])
    mgmt_contra = mgmt.get("contraindications", [])

    management_text = (
        f"Pathology: {name} (ICD-11: {icd11}). "
        f"Diagnostic Workup - Initial Labs: {'; '.join(workup_labs)}. "
        f"Imaging & ECG: {'; '.join(workup_imaging)}. "
        f"Confirmatory Tests: {'; '.join(workup_confirmatory)}. "
        f"Management - Non-Pharmacological / Lifestyle: {'; '.join(mgmt_lifestyle)}. "
        f"Pharmacotherapy & Interventions: {'; '.join(mgmt_pharma)}. "
        f"Strict Contraindications: {'; '.join(mgmt_contra)}. "
        f"Clinical Guideline Source: {source.get('issuing_authority', '')} - {source.get('guideline_title', '')} ({source.get('publication_year', '')})."
    )

    management_keywords = [
        name.lower(),
        icd11.lower(),
        "workup",
        "investigations",
        "treatment",
        "management",
    ] + [lab.lower() for lab in workup_labs[:4]] + [rx.lower() for rx in mgmt_pharma[:3]]

    chunk_2 = {
        "chunk_id": f"pathology_{icd11}_management",
        "clinical_domain": specialty_str,
        "section_header": f"ICD-11 {icd11}: {name} - Diagnostic Workup & Management",
        "text_content": management_text,
        "keywords": management_keywords[:15],
        "metadata": {
            "source": f"{source.get('issuing_authority', 'Clinical Guideline')} ({source.get('publication_year', '')})",
            "icd11_code": icd11,
            "clinical_name": name,
            "medical_specialty": specialty_str,
            "guideline_url": source.get("source_url"),
            "chunk_type": "diagnostic_and_management"
        }
    }

    return [chunk_1, chunk_2]


async def ingest_pathology_corpus(
    session: AsyncSession,
    vector_index: Optional[ClinicalVectorStore] = None
) -> Dict[str, Any]:
    """
    Ingests the authoritative 40+ multi-specialty clinical pathology corpus into PostgreSQL
    and indexes rich semantic feature vectors in the dense ClinicalVectorStore.
    Performs idempotent upsert based on unique ICD-11 codes.
    """
    v_store = vector_index or vector_store
    inserted_count = 0
    updated_count = 0
    all_chunks_to_index: List[Dict[str, Any]] = []

    # Identify existing chunk IDs in vector store to avoid duplicates
    existing_chunk_ids = {c.get("chunk_id") for c in v_store.chunks}

    for record in CLINICAL_PATHOLOGY_CORPUS:
        icd11 = record["icd11_code"]
        stmt = select(Pathology).where(Pathology.icd11_code == icd11)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        specialty = record["medical_specialty"]
        if not isinstance(specialty, MedicalSpecialty):
            specialty = MedicalSpecialty(specialty)

        acuity = record["baseline_acuity"]
        if not isinstance(acuity, TriageAcuityLevel):
            acuity = TriageAcuityLevel(acuity)

        if existing:
            existing.icd10_code = record.get("icd10_code")
            existing.clinical_name = record["clinical_name"]
            existing.common_aliases = record.get("common_aliases", [])
            existing.medical_specialty = specialty
            existing.baseline_acuity = acuity
            existing.pathophysiology_overview = record["pathophysiology_overview"]
            existing.cardinal_symptoms = record.get("cardinal_symptoms", {})
            existing.red_flag_criteria = record.get("red_flag_criteria", [])
            existing.differential_diagnoses = record.get("differential_diagnoses", [])
            existing.diagnostic_workup = record.get("diagnostic_workup", {})
            existing.evidence_based_management = record.get("evidence_based_management", {})
            existing.source_metadata = record.get("source_metadata", {})
            updated_count += 1
        else:
            pathology_obj = Pathology(
                icd11_code=icd11,
                icd10_code=record.get("icd10_code"),
                clinical_name=record["clinical_name"],
                common_aliases=record.get("common_aliases", []),
                medical_specialty=specialty,
                baseline_acuity=acuity,
                pathophysiology_overview=record["pathophysiology_overview"],
                cardinal_symptoms=record.get("cardinal_symptoms", {}),
                red_flag_criteria=record.get("red_flag_criteria", []),
                differential_diagnoses=record.get("differential_diagnoses", []),
                diagnostic_workup=record.get("diagnostic_workup", {}),
                evidence_based_management=record.get("evidence_based_management", {}),
                source_metadata=record.get("source_metadata", {})
            )
            session.add(pathology_obj)
            inserted_count += 1

        # Generate vector chunks for this pathology
        record_chunks = create_pathology_vector_chunks(record)
        for chunk in record_chunks:
            if chunk["chunk_id"] not in existing_chunk_ids:
                all_chunks_to_index.append(chunk)
                existing_chunk_ids.add(chunk["chunk_id"])

    await session.commit()

    # Index new pathology chunks in the vector store
    new_vectors_added = 0
    if all_chunks_to_index:
        new_vectors_added = v_store.add_chunks(all_chunks_to_index)
        logger.info("Indexed %d pathology knowledge chunks into vector store", new_vectors_added)

    stats = {
        "inserted": inserted_count,
        "updated": updated_count,
        "total_corpus": len(CLINICAL_PATHOLOGY_CORPUS),
        "new_vector_chunks": new_vectors_added,
        "vector_store_total": v_store.total_count()
    }
    logger.info("Pathology corpus ingestion complete: %s", stats)
    return stats
