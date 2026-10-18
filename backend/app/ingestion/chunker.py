import re
from typing import List, Dict, Any


class ClinicalDocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        guideline_id: str,
        source_title: str,
        clinical_domain: str,
        evidence_level: str,
        section_header: str,
        text_content: str,
        keywords: List[str],
        icd10_codes: List[str],
        source_url: str,
        publication_year: int,
        triage_urgency: str = "ROUTINE"
    ):
        self.chunk_id = chunk_id
        self.guideline_id = guideline_id
        self.source_title = source_title
        self.clinical_domain = clinical_domain
        self.evidence_level = evidence_level
        self.section_header = section_header
        self.text_content = text_content
        self.keywords = keywords
        self.icd10_codes = icd10_codes
        self.source_url = source_url
        self.publication_year = publication_year
        self.triage_urgency = triage_urgency

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "guideline_id": self.guideline_id,
            "source_title": self.source_title,
            "clinical_domain": self.clinical_domain,
            "evidence_level": self.evidence_level,
            "section_header": self.section_header,
            "text_content": self.text_content,
            "keywords": self.keywords,
            "icd10_codes": self.icd10_codes,
            "source_url": self.source_url,
            "publication_year": self.publication_year,
            "triage_urgency": self.triage_urgency
        }


class ClinicalSemanticChunker:
    """
    Semantic chunker designed for evidence-based medical guidelines.
    Preserves section context, hierarchical parent headers, and clinical urgency tags.
    """

    def __init__(self, max_token_window: int = 250, token_overlap: int = 35):
        self.max_token_window = max_token_window
        self.token_overlap = token_overlap

    def chunk_structured_guideline(self, guideline_doc: Dict[str, Any]) -> List[ClinicalDocumentChunk]:
        chunks: List[ClinicalDocumentChunk] = []

        guideline_id = guideline_doc["guideline_id"]
        source_title = guideline_doc["source_title"]
        clinical_domain = guideline_doc["clinical_domain"]
        evidence_level = guideline_doc["evidence_level"]
        source_url = guideline_doc.get("source_url", "")
        publication_year = guideline_doc.get("publication_year", 2024)
        icd10_codes = guideline_doc.get("icd10_codes", [])

        for idx, raw_chunk in enumerate(guideline_doc.get("chunks", [])):
            chunk_id = raw_chunk.get("chunk_id", f"{guideline_id}-C{idx+1}")
            section_header = raw_chunk.get("section_header", "Clinical Guidance")
            raw_text = raw_chunk.get("text_content", "").strip()
            keywords = raw_chunk.get("keywords", [])
            urgency = raw_chunk.get("triage_urgency", "ROUTINE")

            words = raw_text.split()
            # If chunk is within reasonable clinical window, keep intact to preserve logical continuity
            if len(words) <= self.max_token_window:
                chunk = ClinicalDocumentChunk(
                    chunk_id=chunk_id,
                    guideline_id=guideline_id,
                    source_title=source_title,
                    clinical_domain=clinical_domain,
                    evidence_level=evidence_level,
                    section_header=section_header,
                    text_content=raw_text,
                    keywords=keywords,
                    icd10_codes=icd10_codes,
                    source_url=source_url,
                    publication_year=publication_year,
                    triage_urgency=urgency
                )
                chunks.append(chunk)
            else:
                # Sliding window chunking with sentence boundary preservation
                sentences = re.split(r'(?<=[.!?]) +', raw_text)
                current_subchunk: List[str] = []
                sub_index = 1

                for sentence in sentences:
                    current_subchunk.append(sentence)
                    subchunk_word_count = sum(len(s.split()) for s in current_subchunk)
                    if subchunk_word_count >= self.max_token_window:
                        joined_text = " ".join(current_subchunk)
                        chunk = ClinicalDocumentChunk(
                            chunk_id=f"{chunk_id}-P{sub_index}",
                            guideline_id=guideline_id,
                            source_title=source_title,
                            clinical_domain=clinical_domain,
                            evidence_level=evidence_level,
                            section_header=f"{section_header} (Part {sub_index})",
                            text_content=joined_text,
                            keywords=keywords,
                            icd10_codes=icd10_codes,
                            source_url=source_url,
                            publication_year=publication_year,
                            triage_urgency=urgency
                        )
                        chunks.append(chunk)
                        sub_index += 1
                        # Retain overlap
                        current_subchunk = current_subchunk[-2:]

                if current_subchunk:
                    joined_text = " ".join(current_subchunk)
                    chunk = ClinicalDocumentChunk(
                        chunk_id=f"{chunk_id}-P{sub_index}",
                        guideline_id=guideline_id,
                        source_title=source_title,
                        clinical_domain=clinical_domain,
                        evidence_level=evidence_level,
                        section_header=f"{section_header} (Part {sub_index})",
                        text_content=joined_text,
                        keywords=keywords,
                        icd10_codes=icd10_codes,
                        source_url=source_url,
                        publication_year=publication_year,
                        triage_urgency=urgency
                    )
                    chunks.append(chunk)

        return chunks
