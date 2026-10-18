"""
Clinical Knowledge and Disease Ontology Subsystem.
Provides multi-specialty clinical pathology schemas, WHO ICD-11 ontology models,
automated ingestion loaders, and federated medical knowledge connectors.
"""

from app.knowledge.seed_corpus import CLINICAL_PATHOLOGY_CORPUS

__all__ = ["CLINICAL_PATHOLOGY_CORPUS"]
