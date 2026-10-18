import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal, get_db_session
from app.models.user import User, UserRole
from app.auth.security import hash_password
from app.ingestion.seed_loader import seed_clinical_guidelines
from app.ingestion.vector_store import vector_store
from app.knowledge.clinical_corpus_loader import ingest_pathology_corpus
from app.api.v1 import api_v1_router


async def bootstrap_initial_state():
    # 1. Create database tables if not existing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Ingest clinical guidelines into vector index and database catalog
    async with AsyncSessionLocal() as session:
        guideline_dir = "./data/guidelines" if os.path.exists("./data/guidelines") else "backend/data/guidelines"
        await seed_clinical_guidelines(session, guidelines_dir=guideline_dir)

        # 3. Ingest multi-specialty clinical pathology ontology into PostgreSQL and vector store
        await ingest_pathology_corpus(session, vector_store)

        # 3. Seed verified clinician, auditor, and patient test accounts
        clinician_stmt = select(User).where(User.email == "dr.evans@hospital.nhs.uk")
        res = await session.execute(clinician_stmt)
        if not res.scalar_one_or_none():
            clinician = User(
                email="dr.evans@hospital.nhs.uk",
                hashed_password=hash_password("Clinical2026!"),
                full_name="Dr. Sarah Evans, MBChB MRCP",
                role=UserRole.CLINICIAN,
                license_credential_id="GMC-7890123",
                is_active=True
            )
            session.add(clinician)

        auditor_stmt = select(User).where(User.email == "compliance@medguard.org")
        res = await session.execute(auditor_stmt)
        if not res.scalar_one_or_none():
            auditor = User(
                email="compliance@medguard.org",
                hashed_password=hash_password("Auditor2026!"),
                full_name="Marcus Vance, HIPAA Compliance Officer",
                role=UserRole.AUDITOR,
                license_credential_id="HCCA-CHPC-491",
                is_active=True
            )
            session.add(auditor)

        patient_stmt = select(User).where(User.email == "patient@healthcare.org")
        res = await session.execute(patient_stmt)
        if not res.scalar_one_or_none():
            patient = User(
                email="patient@healthcare.org",
                hashed_password=hash_password("Patient2026!"),
                full_name="Alex Turner",
                role=UserRole.PATIENT,
                is_active=True
            )
            session.add(patient)

        await session.commit()


import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    await bootstrap_initial_state()
    yield
    # Graceful shutdown sequence
    await engine.dispose()


app = FastAPI(
    title="MedGuard AI - Clinical Decision Support Platform",
    description="HIPAA/GDPR-aligned conversational clinical decision support and patient triage API.",
    version="1.0.0",
    lifespan=lifespan
)

# Cross-Origin Resource Sharing (CORS) Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API version 1 routers
app.include_router(api_v1_router)


@app.get("/api/v1/health", tags=["Operational Health"])
async def health_check():
    return {
        "status": "OPERATIONAL",
        "service": "MedGuard AI Clinical Backend",
        "version": "1.0.0",
        "vector_chunks_indexed": vector_store.total_count(),
        "phi_scrubbing_enabled": settings.ENABLE_PHI_SCRUBBING,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["Root"])
async def root_redirect():
    return {
        "platform": "MedGuard AI Clinical Decision Support Platform",
        "status": "ONLINE",
        "docs_url": "/docs",
        "health_url": "/api/v1/health"
    }
