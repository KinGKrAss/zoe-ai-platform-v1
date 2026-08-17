"""Hybrid lexical/vector memory ranking with an optional OpenAI embedding provider.

The storage contract remains provider-neutral: embeddings are JSON arrays in
`zoe_memory_embeddings`. This allows deterministic local tests and an optional
remote embedding provider without changing the Memory Core schema.
"""

from __future__ import annotations

import math
import os
import re
from hashlib import sha256
from typing import Iterable

TOKEN_RE = re.compile(r"[\wÄÖÜäöüß]+", re.UNICODE)


def content_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def lexical_score(query: str, text: str) -> float:
    q = {token.lower() for token in TOKEN_RE.findall(query)}
    t = {token.lower() for token in TOKEN_RE.findall(text)}
    if not q or not t:
        return 0.0
    return len(q & t) / len(q | t)


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    av = list(a)
    bv = list(b)
    if len(av) != len(bv) or not av:
        return 0.0
    dot = sum(x * y for x, y in zip(av, bv))
    norm_a = math.sqrt(sum(x * x for x in av))
    norm_b = math.sqrt(sum(y * y for y in bv))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def deterministic_embedding(text: str, dimensions: int = 128) -> list[float]:
    """Stable local fallback for development and offline CI.

    This is deliberately not presented as a semantic model. Production can use
    the OpenAI provider by supplying Z1_EMBEDDING_PROVIDER=openai.
    """
    vector = [0.0] * dimensions
    for token in TOKEN_RE.findall(text.lower()):
        digest = sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] & 1 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def embed(text: str) -> tuple[str, list[float]]:
    """Return (model_name, vector) using the configured provider.

    The OpenAI path is intentionally optional so CI never requires an API key.
    """
    provider = os.getenv("Z1_EMBEDDING_PROVIDER", "local").lower()
    if provider != "openai":
        return "z1-local-hash-128", deterministic_embedding(text)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when Z1_EMBEDDING_PROVIDER=openai")

    from openai import OpenAI

    model = os.getenv("Z1_EMBEDDING_MODEL", "text-embedding-3-small")
    result = OpenAI(api_key=api_key).embeddings.create(model=model, input=text)
    return model, result.data[0].embedding


def hybrid_score(query: str, text: str, query_vector: list[float], text_vector: list[float]) -> float:
    """Blend lexical relevance and vector similarity for explainable ranking."""
    vector = max(0.0, cosine_similarity(query_vector, text_vector))
    lexical = lexical_score(query, text)
    return 0.35 * lexical + 0.65 * vector
