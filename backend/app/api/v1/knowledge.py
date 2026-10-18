from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.database import get_db_session
from app.models.pathology import Pathology, MedicalSpecialty, TriageAcuityLevel
from app.schemas.pathology import PathologyRead, PathologySummary
from app.knowledge.clinical_corpus_loader import ingest_pathology_corpus
from app.ingestion.vector_store import vector_store

router = APIRouter(prefix="/knowledge", tags=["Medical Knowledge & Disease Ontology"])


@router.get("/pathologies", response_model=List[PathologySummary])
async def list_pathologies(
    specialty: Optional[MedicalSpecialty] = None,
    acuity: Optional[TriageAcuityLevel] = None,
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """
    List structured clinical pathologies from the authoritative ontology.
    Supports filtering by medical specialty, triage acuity level, and keyword search.
    """
    stmt = select(Pathology)

    if specialty:
        stmt = stmt.where(Pathology.medical_specialty == specialty)
    if acuity:
        stmt = stmt.where(Pathology.baseline_acuity == acuity)
    if search:
        search_pattern = f"%{search.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Pathology.clinical_name).like(search_pattern),
                func.lower(Pathology.icd11_code).like(search_pattern),
                func.lower(Pathology.pathophysiology_overview).like(search_pattern)
            )
        )

    stmt = stmt.order_by(Pathology.clinical_name).offset(offset).limit(limit)
    result = await session.execute(stmt)
    records = result.scalars().all()

    summaries = []
    for p in records:
        primary_symptoms = []
        if isinstance(p.cardinal_symptoms, dict):
            for s in p.cardinal_symptoms.get("primary", []):
                if isinstance(s, dict):
                    primary_symptoms.append(s.get("symptom", ""))
                else:
                    primary_symptoms.append(str(s))

        summaries.append(
            PathologySummary(
                id=p.id,
                icd11_code=p.icd11_code,
                clinical_name=p.clinical_name,
                medical_specialty=p.medical_specialty,
                baseline_acuity=p.baseline_acuity,
                primary_symptoms=primary_symptoms[:4],
                red_flag_count=len(p.red_flag_criteria) if isinstance(p.red_flag_criteria, list) else 0
            )
        )

    return summaries


@router.get("/pathologies/{icd11_code}", response_model=PathologyRead)
async def get_pathology_by_icd11(
    icd11_code: str,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Retrieve full clinical pathology record by WHO ICD-11 code.
    Includes pathophysiology, weighted cardinal symptoms, red flags, workup, and management.
    """
    stmt = select(Pathology).where(
        func.lower(Pathology.icd11_code) == icd11_code.lower()
    )
    result = await session.execute(stmt)
    pathology = result.scalar_one_or_none()

    if not pathology:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pathology with ICD-11 code '{icd11_code}' not found in local ontology cache"
        )

    return PathologyRead(
        id=pathology.id,
        icd11_code=pathology.icd11_code,
        icd10_code=pathology.icd10_code,
        clinical_name=pathology.clinical_name,
        common_aliases=pathology.common_aliases or [],
        medical_specialty=pathology.medical_specialty,
        baseline_acuity=pathology.baseline_acuity,
        pathophysiology_overview=pathology.pathophysiology_overview,
        cardinal_symptoms=pathology.cardinal_symptoms or {},
        red_flag_criteria=pathology.red_flag_criteria or [],
        differential_diagnoses=pathology.differential_diagnoses or [],
        diagnostic_workup=pathology.diagnostic_workup or {},
        evidence_based_management=pathology.evidence_based_management or {},
        source_metadata=pathology.source_metadata or {},
        created_at=pathology.created_at.isoformat() if pathology.created_at else "",
        updated_at=pathology.updated_at.isoformat() if pathology.updated_at else ""
    )


@router.get("/specialties")
async def get_specialty_breakdown(session: AsyncSession = Depends(get_db_session)):
    """
    Returns breakdown of registered pathologies grouped by medical specialty.
    """
    stmt = select(
        Pathology.medical_specialty,
        func.count(Pathology.id)
    ).group_by(Pathology.medical_specialty)

    result = await session.execute(stmt)
    counts = {row[0].value if hasattr(row[0], "value") else str(row[0]): row[1] for row in result.all()}
    return {
        "total_pathologies": sum(counts.values()),
        "specialties": counts
    }


@router.get("/search")
async def semantic_search_knowledge(
    q: str = Query(..., min_length=2, max_length=200),
    top_k: int = Query(5, ge=1, le=10),
    domain: Optional[str] = Query(None)
):
    """
    Performs cosine semantic vector search across indexed clinical guidelines and pathology profiles.
    """
    raw_results = vector_store.search(
        query=q,
        top_k=top_k,
        clinical_domain=domain
    )

    formatted = []
    for chunk, score in raw_results:
        formatted.append({
            "chunk_id": chunk.get("chunk_id"),
            "section_header": chunk.get("section_header"),
            "clinical_domain": chunk.get("clinical_domain"),
            "similarity_score": round(float(score), 4),
            "text_excerpt": chunk.get("text_content", "")[:350],
            "metadata": chunk.get("metadata", {})
        })

    return {
        "query": q,
        "results_count": len(formatted),
        "results": formatted
    }


@router.post("/bootstrap")
async def bootstrap_pathology_corpus(session: AsyncSession = Depends(get_db_session)):
    """
    Manually triggers ingestion of the authoritative multi-specialty clinical pathology corpus.
    """
    stats = await ingest_pathology_corpus(session, vector_store)
    return {
        "status": "success",
        "message": "Clinical pathology ontology ingested and vector index updated",
        "statistics": stats
    }


@router.get("/federated/condition")
async def federated_condition_lookup(
    q: str = Query(..., min_length=2, max_length=150),
    icd10: Optional[str] = Query(None)
):
    """
    Live federated query to NIH MedlinePlus and NCBI PubMed.
    Normalizes clinical findings and caches embeddings in local vector store.
    """
    from app.knowledge.services.medical_connectors import federated_knowledge_service
    record = await federated_knowledge_service.enrich_condition(query=q, icd10_code=icd10)
    return record


@router.get("/federated/medication")
async def federated_medication_lookup(
    name: str = Query(..., min_length=2, max_length=150)
):
    """
    Live federated query to OpenFDA Drug Product Labeling.
    Retrieves verified boxed warnings, indications, contraindications, and drug interactions.
    """
    from app.knowledge.services.medical_connectors import federated_knowledge_service
    record = await federated_knowledge_service.enrich_medication(drug_name=name)
    return record

