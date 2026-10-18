import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Float, Integer, JSON
from app.database import Base, utc_now


class MetricCategory(str, enum.Enum):
    CONFIDENCE_DRIFT = "CONFIDENCE_DRIFT"
    RETRIEVAL_SIMILARITY = "RETRIEVAL_SIMILARITY"
    LATENCY_SPIKE = "LATENCY_SPIKE"
    HALLUCINATION_ALERT = "HALLUCINATION_ALERT"
    SAFETY_FILTER_TRIGGER = "SAFETY_FILTER_TRIGGER"


class MetricSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class MonitoringMetric(Base):
    __tablename__ = "monitoring_metrics"

    metric_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)
    metric_category = Column(Enum(MetricCategory), nullable=False, index=True)
    severity_level = Column(Enum(MetricSeverity), default=MetricSeverity.INFO, nullable=False, index=True)

    metric_value = Column(Float, nullable=False)
    diagnostic_context = Column(JSON, default=dict, nullable=False)


class ClinicalGuidelineCatalog(Base):
    __tablename__ = "clinical_guidelines_catalog"

    guideline_id = Column(String(128), primary_key=True)
    source_title = Column(String(512), nullable=False)
    issuing_authority = Column(String(255), nullable=False)
    clinical_domain = Column(String(255), nullable=False, index=True)
    evidence_level = Column(String(255), nullable=False)
    publication_year = Column(Integer, nullable=False)
    source_url = Column(String(512), nullable=False)
    icd10_codes = Column(JSON, default=list, nullable=False)

    chunk_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_reviewed_at = Column(DateTime, default=utc_now, nullable=False)
