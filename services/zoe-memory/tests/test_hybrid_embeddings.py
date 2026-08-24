from zoe_memory.hybrid_embeddings import (
    cosine_similarity,
    deterministic_embedding,
    hybrid_score,
    lexical_score,
)


def test_deterministic_embedding_is_stable():
    assert deterministic_embedding("Zoë Z1 Memory") == deterministic_embedding("Zoë Z1 Memory")


def test_cosine_identity():
    vector = [1.0, 0.0, 0.0]
    assert cosine_similarity(vector, vector) == 1.0


def test_lexical_score_rewards_shared_terms():
    assert lexical_score("Z1 memory", "Z1 memory engine") > lexical_score("Z1 memory", "weather report")


def test_hybrid_score_is_bounded():
    vector = deterministic_embedding("Z1 memory")
    score = hybrid_score("Z1 memory", "Z1 memory engine", vector, deterministic_embedding("Z1 memory engine"))
    assert 0.0 <= score <= 1.0
