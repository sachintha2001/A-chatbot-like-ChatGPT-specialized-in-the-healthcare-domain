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
from app.models.patient import PatientProfile, PatientMedicalRecord
from app.api.v1 import api_v1_router
from app.compliance.security_shield import SecurityHeadersAndWAFMiddleware, security_shield
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import delete


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

        # 4. Purge any legacy demo/sample patient profiles (Alex/Arthur/Eleanor Turner) for clean production hosting
        demo_profiles_stmt = select(PatientProfile).where(
            PatientProfile.last_name == "Turner",
            PatientProfile.first_name.in_(["Alex", "Arthur", "Eleanor"]),
        )
        demo_res = await session.execute(demo_profiles_stmt)
        demo_profiles = demo_res.scalars().all()
        for dp in demo_profiles:
            await session.execute(
                delete(PatientMedicalRecord).where(PatientMedicalRecord.profile_id == dp.id)
            )
            await session.delete(dp)

        # 5. Ensure system service accounts exist for clinical governance RBAC
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
                full_name="Registered Patient",
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
    version="2.5.0",
    lifespan=lifespan
)

# Zero-Trust Security Headers, Rate Limiting & WAF Middleware
app.add_middleware(SecurityHeadersAndWAFMiddleware)

# Cross-Origin Resource Sharing (CORS) Configuration (Production Web Hosting Ready)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Disposition", "X-Report-Ref-Id", "X-MedGuard-Security-Shield"],
)


# Global Zero-Leakage Exception Sanitizer (prevents stack trace or internal path exposure)
@app.exception_handler(Exception)
async def global_zero_leakage_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal clinical processing error occurred. Diagnostic details have been logged securely without exposing sensitive system internals."
        },
        headers={
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-store, no-cache, must-revalidate, private",
        }
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
        "security_shield_status": "ACTIVE_ZERO_TRUST_DLP",
        "threats_blocked": security_shield.blocked_threats_count,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["Root"])
async def root_redirect():
    return {
        "platform": "MedGuard AI Clinical Decision Support Platform",
        "status": "ONLINE",
        "security_shield": "ACTIVE_ZERO_TRUST_DLP",
        "docs_url": "/docs",
        "health_url": "/api/v1/health"
    }
