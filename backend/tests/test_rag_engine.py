import pytest
from app.ingestion.chunker import ClinicalSemanticChunker
from app.ingestion.vector_store import ClinicalVectorStore
from app.engine.rag_pipeline import ClinicalRAGEngine


def test_clinical_semantic_chunker():
    chunker = ClinicalSemanticChunker(max_token_window=100, token_overlap=20)
    mock_doc = {
        "guideline_id": "TEST-CARD-99",
        "source_title": "Test Cardiac Protocol",
        "clinical_domain": "Cardiology",
        "evidence_level": "Level I",
        "source_url": "https://clinical.test",
        "chunks": [
            {
                "chunk_id": "TEST-CARD-99-C1",
                "section_header": "Acute Angina Management",
                "text_content": "Administer sublingual nitroglycerin if systolic pressure exceeds 90 mmHg.",
                "keywords": ["angina", "nitroglycerin"],
                "triage_urgency": "URGENT"
            }
        ]
    }
    chunks = chunker.chunk_structured_guideline(mock_doc)
    assert len(chunks) == 1
    assert chunks[0].guideline_id == "TEST-CARD-99"
    assert chunks[0].section_header == "Acute Angina Management"
    assert "nitroglycerin" in chunks[0].keywords


def test_vector_store_indexing_and_search():
    store = ClinicalVectorStore(storage_path="./data/test_vectors")
    sample_chunk = {
        "chunk_id": "TEST-C1",
        "guideline_id": "TEST-01",
        "source_title": "Endocrine Protocol",
        "clinical_domain": "Endocrinology",
        "evidence_level": "Level I",
        "section_header": "Hypoglycemia Management",
        "text_content": "Ingest 15 grams of fast-acting glucose tablets and recheck in 15 minutes.",
        "keywords": ["glucose", "hypoglycemia", "sugar", "tablets"],
        "triage_urgency": "ROUTINE"
    }
    store.add_chunks([sample_chunk])
    assert store.total_count() >= 1

    results = store.search("feeling shaky with low blood glucose level", top_k=1, similarity_threshold=0.2)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert top_chunk["guideline_id"] == "TEST-01"
    assert score > 0.30


def test_rag_groundedness_calculation():
    engine = ClinicalRAGEngine()
    mock_context = [
        {"text_content": "Rule of 15 states ingest 15 grams of fast-acting carbohydrates for low blood sugar."}
    ]
    response = "Following the institutional protocol, ingest 15 grams of fast-acting carbohydrates to normalize blood sugar."
    groundedness = engine._calculate_groundedness(response, mock_context)
    assert groundedness > 0.50
