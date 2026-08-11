from zoe_memory.extraction_engine_v2.engine import ExtractionEngineV2
from zoe_memory.extraction_engine_v2.models import Message


def test_connector_word_alone_does_not_reconstruct():
    messages = [
        Message("c1", "a", "user", "Also."),
        Message("c1", "b", "user", "Das ist ein weiterer Gedanke."),
    ]
    candidates = ExtractionEngineV2().extract(messages)
    assert all(c.candidate_type != "reconstruction" for c in candidates)


def test_reconstruction_requires_multiple_sources_and_keeps_provenance():
    messages = [
        Message("c1", "a", "user", "Mein Projekt nutzt PostgreSQL als Datenbank."),
        Message("c1", "b", "user", "Meine API läuft als FastAPI Backend."),
        Message("c1", "c", "user", "Zusammengefasst: Mein Projekt nutzt PostgreSQL und meine API läuft als FastAPI Backend."),
    ]
    candidates = ExtractionEngineV2().extract(messages)
    reconstructed = [c for c in candidates if c.candidate_type == "reconstruction"]
    assert len(reconstructed) == 1
    assert {s.message_id for s in reconstructed[0].source_references} == {"a", "b", "c"}
    assert reconstructed[0].review_status == "draft"


def test_exact_deduplication_uses_sha256():
    messages = [
        Message("c1", "a", "user", "Ich nutze PostgreSQL als Datenbank."),
        Message("c1", "b", "user", "Ich nutze PostgreSQL als Datenbank."),
    ]
    candidates = ExtractionEngineV2().extract(messages)
    assert len([c for c in candidates if c.candidate_type == "fact"]) == 1
