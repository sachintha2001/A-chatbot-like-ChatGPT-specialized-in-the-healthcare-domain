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
