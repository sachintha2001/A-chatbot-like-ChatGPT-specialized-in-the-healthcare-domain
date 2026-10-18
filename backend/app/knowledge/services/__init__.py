"""
Federated Medical Knowledge Services for MedGuard AI.
Integrates live connectors to NIH MedlinePlus, NCBI PubMed, and OpenFDA.
"""

from app.knowledge.services.medical_connectors import (
    NIHMedlinePlusConnector,
    NCBIPubMedConnector,
    OpenFDAConnector,
    FederatedMedicalKnowledgeService,
    federated_knowledge_service
)

__all__ = [
    "NIHMedlinePlusConnector",
    "NCBIPubMedConnector",
    "OpenFDAConnector",
    "FederatedMedicalKnowledgeService",
    "federated_knowledge_service"
]
