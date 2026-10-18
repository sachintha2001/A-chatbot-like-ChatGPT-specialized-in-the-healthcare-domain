import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.triage import TriageSession, TriageMessage, MessageSenderRole


class FHIRResourceGenerator:
    """
    HL7 FHIR R4 (Fast Healthcare Interoperability Resources) Integration Adapter.
    Exports structured Clinical Triage Encounters as standard FHIR R4 Document Bundles
    for ingestion into Electronic Health Record (EHR) systems (Epic Systems, Cerner, NHS Spine).
    """

    def generate_patient_summary_bundle(
        self,
        triage_session: TriageSession,
        messages: list[TriageMessage]
    ) -> Dict[str, Any]:
        bundle_id = f"bundle-triage-{triage_session.session_id}"
        patient_ref_id = f"patient-anon-{uuid.uuid5(uuid.NAMESPACE_DNS, triage_session.session_id).hex[:12]}"
        composition_id = f"comp-{triage_session.session_id[:8]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Find presenting symptoms and last assistant guidance
        presenting_problem = "Acute clinical evaluation"
        for m in messages:
            if m.sender_role == MessageSenderRole.PATIENT:
                presenting_problem = m.redacted_content[:120]
                break

        last_assistant_guidance = "Triage completed."
        citations = []
        for m in reversed(messages):
            if m.sender_role == MessageSenderRole.CLINICIAN_ASSISTANT:
                last_assistant_guidance = m.redacted_content
                citations = m.clinical_citations or []
                break

        entries = []

        # 1. Composition (FHIR Document Header)
        entries.append({
            "fullUrl": f"urn:uuid:{composition_id}",
            "resource": {
                "resourceType": "Composition",
                "id": composition_id,
                "status": "final",
                "type": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "60591-5",
                            "display": "Patient summary Document"
                        }
                    ],
                    "text": "MedGuard AI Clinical Decision Support Triage Summary"
                },
                "subject": {
                    "reference": f"urn:uuid:{patient_ref_id}",
                    "display": f"Anonymized Patient ({triage_session.patient_age_group})"
                },
                "date": now_iso,
                "author": [
                    {
                        "display": "MedGuard AI Clinical Decision Support Engine v1.0"
                    }
                ],
                "title": f"Clinical Triage Encounter Summary - {triage_session.triage_severity.value}",
                "section": [
                    {
                        "title": "Reason for Triage Contact",
                        "code": {
                            "coding": [{"system": "http://loinc.org", "code": "29299-5", "display": "Reason for visit"}]
                        },
                        "text": {
                            "status": "generated",
                            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p>{presenting_problem}</p></div>"
                        }
                    },
                    {
                        "title": "Clinical Guidance & Citations",
                        "code": {
                            "coding": [{"system": "http://loinc.org", "code": "55752-0", "display": "Clinical Information"}]
                        },
                        "text": {
                            "status": "generated",
                            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p>{last_assistant_guidance}</p></div>"
                        }
                    }
                ]
            }
        })

        # 2. Patient Resource (Anonymized)
        gender_map = {"MALE": "male", "FEMALE": "female", "UNSPECIFIED": "unknown"}
        entries.append({
            "fullUrl": f"urn:uuid:{patient_ref_id}",
            "resource": {
                "resourceType": "Patient",
                "id": patient_ref_id,
                "active": True,
                "gender": gender_map.get(triage_session.biological_sex.upper(), "unknown"),
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/patient-ageGroup",
                        "valueString": triage_session.patient_age_group
                    }
                ]
            }
        })

        # 3. Observation (Triage Acuity Severity Level)
        severity_code_map = {
            "ROUTINE": ("routine", "Routine non-urgent triage"),
            "URGENT": ("urgent", "Urgent clinical attention required"),
            "EMERGENCY": ("emergency", "Emergency immediate escalation required")
        }
        code_info = severity_code_map.get(triage_session.triage_severity.value, ("routine", "Routine"))

        entries.append({
            "fullUrl": f"urn:uuid:obs-{triage_session.session_id[:8]}",
            "resource": {
                "resourceType": "Observation",
                "id": f"obs-{triage_session.session_id[:8]}",
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                "code": "exam",
                                "display": "Exam"
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "225399009",
                            "display": "Triage assessment"
                        }
                    ],
                    "text": "Triage Acuity Assessment"
                },
                "subject": {
                    "reference": f"urn:uuid:{patient_ref_id}"
                },
                "effectiveDateTime": now_iso,
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                            "code": code_info[0].upper(),
                            "display": code_info[1]
                        }
                    ],
                    "text": triage_session.triage_severity.value
                }
            }
        })

        return {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": "document",
            "timestamp": now_iso,
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/documentbundle"]
            },
            "entry": entries
        }


fhir_generator = FHIRResourceGenerator()
