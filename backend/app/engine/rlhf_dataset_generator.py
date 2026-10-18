import json
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.rlhf import RLHFFeedbackRecord, FeedbackExportStatus
from app.models.triage import TriageMessage, MessageSenderRole


class RLHFDatasetExportEngine:
    """
    Clinician Alignment & Supervised Fine-Tuning (SFT) Dataset Exporter.
    Filters high-accuracy, clinician-verified or rewritten dialogue turns
    and transforms them into standard instruction-tuning JSONL formats.
    """

    SYSTEM_PROMPT = (
        "You are MedGuard AI, an evidence-grounded Clinical Decision Support Assistant. "
        "Adhere strictly to verified clinical protocols, state clinical citations with [Ref X] badges, "
        "and enforce patient safety netting."
    )

    async def export_dataset(
        self,
        session: AsyncSession,
        format_type: str = "openai_chat",
        minimum_rating: int = 4,
        include_system_guardrails: bool = True
    ) -> List[Dict[str, Any]]:
        # Retrieve approved feedback records that meet the minimum clinician Likert rating
        stmt = (
            select(RLHFFeedbackRecord)
            .options(selectinload(RLHFFeedbackRecord.message).selectinload(TriageMessage.session))
            .where(
                RLHFFeedbackRecord.clinical_accuracy_rating >= minimum_rating,
                RLHFFeedbackRecord.export_status.in_([
                    FeedbackExportStatus.PENDING,
                    FeedbackExportStatus.APPROVED_FOR_FINETUNE,
                    FeedbackExportStatus.EXPORTED
                ])
            )
        )
        result = await session.execute(stmt)
        records = result.scalars().all()

        dataset_entries: List[Dict[str, Any]] = []

        for r in records:
            msg = r.message
            if not msg:
                continue

            # Prioritize the clinician's rewritten completion over the original model output
            effective_completion = r.revised_completion_text or msg.redacted_content

            # Query patient prompt directly for this session
            patient_prompt = "Patient clinical presentation"
            if msg.session_id:
                p_stmt = (
                    select(TriageMessage.redacted_content)
                    .where(
                        TriageMessage.session_id == msg.session_id,
                        TriageMessage.sender_role == MessageSenderRole.PATIENT,
                        TriageMessage.created_at <= msg.created_at
                    )
                    .order_by(TriageMessage.created_at.desc())
                    .limit(1)
                )
                p_res = await session.execute(p_stmt)
                prompt_match = p_res.scalar_one_or_none()
                if prompt_match:
                    patient_prompt = prompt_match

            if format_type == "llama_alpaca":
                entry = {
                    "instruction": "Evaluate the following patient clinical presentation, apply institutional triage guidelines, cite evidence with [Ref X], and provide safety netting.",
                    "input": patient_prompt,
                    "output": effective_completion,
                    "metadata": {
                        "feedback_id": r.feedback_id,
                        "clinician_rating": r.clinical_accuracy_rating,
                        "hallucination_flag": r.hallucination_flag,
                        "rewritten_by_clinician": bool(r.revised_completion_text)
                    }
                }
            else:
                # Default: OpenAI ChatML format
                messages = []
                if include_system_guardrails:
                    messages.append({"role": "system", "content": self.SYSTEM_PROMPT})
                messages.append({"role": "user", "content": patient_prompt})
                messages.append({"role": "assistant", "content": effective_completion})

                entry = {
                    "messages": messages,
                    "metadata": {
                        "feedback_id": r.feedback_id,
                        "clinician_rating": r.clinical_accuracy_rating,
                        "rewritten_by_clinician": bool(r.revised_completion_text)
                    }
                }

            dataset_entries.append(entry)

            # Mark export status as EXPORTED
            r.export_status = FeedbackExportStatus.EXPORTED

        await session.commit()
        return dataset_entries


rlhf_export_engine = RLHFDatasetExportEngine()
