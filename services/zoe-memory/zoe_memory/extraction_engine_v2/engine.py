from __future__ import annotations

import hashlib
import re
import uuid
from difflib import SequenceMatcher

from .models import MemoryCandidate, Message, SourceReference

EXTRACTION_VERSION = "2.0"
_SYNTHESIS = re.compile(r"\b(also|zusammengefasst|zusammengefasst ergibt|insgesamt|damit|folglich|daraus folgt|in summe|therefore|in summary|overall)\b", re.I)
_FACT = re.compile(r"\b(ich|mein|meine|wir|unser|unsere|ich habe|wir haben|i am|my|we have|our)\b", re.I)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().casefold())


def sha256_key(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def _source(message: Message, excerpt: str | None = None) -> SourceReference:
    text = excerpt if excerpt is not None else message.content
    return SourceReference(message.conversation_id, message.message_id, message.role, text[:500])


class ExtractionEngineV2:
    """Conservative evidence -> candidate extractor.

    The engine emits candidates only. It never creates/promotes MemoryEntry records.
    Reconstruction requires explicit synthesis language and at least two related
    source messages; connector words alone are insufficient.
    """

    def __init__(self, version: str = EXTRACTION_VERSION, similarity_threshold: float = 0.92):
        self.version = version
        self.similarity_threshold = similarity_threshold

    def extract(self, messages: list[Message]) -> list[MemoryCandidate]:
        candidates: list[MemoryCandidate] = []
        for message in messages:
            candidate = self._extract_candidate(message)
            if candidate is not None:
                candidates.append(candidate)
        candidates.extend(self._reconstruct(messages))
        return self.deduplicate(candidates)

    def _extract_candidate(self, message: Message) -> MemoryCandidate | None:
        content = message.content.strip()
        if not content or message.role != "user":
            return None
        # Do not treat discourse markers as facts. A concrete first-person assertion
        # or an explicit stable preference/constraint is stronger evidence.
        if not _FACT.search(content) or len(content.split()) < 4:
            return None
        candidate_id = str(uuid.uuid4())
        return MemoryCandidate(
            candidate_id=candidate_id,
            content=content,
            candidate_type="fact",
            source_references=(_source(message),),
            dedupe_key=sha256_key(content),
            extraction_version=self.version,
        )

    def _reconstruct(self, messages: list[Message]) -> list[MemoryCandidate]:
        by_thread: dict[str, list[Message]] = {}
        for message in messages:
            by_thread.setdefault(message.conversation_id, []).append(message)

        results: list[MemoryCandidate] = []
        for thread in by_thread.values():
            for message in thread:
                if message.role != "user" or not _SYNTHESIS.search(message.content):
                    continue
                related = [
                    prior for prior in thread
                    if prior.message_id != message.message_id
                    and prior.role == "user"
                    and self._related(prior.content, message.content)
                ]
                if len(related) < 2:
                    continue
                sources = tuple(_source(m) for m in (*related, message))
                content = message.content.strip()
                results.append(MemoryCandidate(
                    candidate_id=str(uuid.uuid4()),
                    content=content,
                    candidate_type="reconstruction",
                    source_references=sources,
                    dedupe_key=sha256_key(content),
                    extraction_version=self.version,
                    metadata={"synthesis_message_id": message.message_id},
                ))
        return results

    @staticmethod
    def _related(source: str, synthesis: str) -> bool:
        source_tokens = set(re.findall(r"\w+", normalize(source)))
        synthesis_tokens = set(re.findall(r"\w+", normalize(synthesis)))
        return len(source_tokens & synthesis_tokens) >= 2

    def deduplicate(self, candidates: list[MemoryCandidate]) -> list[MemoryCandidate]:
        # Candidate types represent different evidence semantics. A synthesis
        # message can legitimately yield both a fact candidate and a reconstruction
        # candidate, so deduplicate within each type rather than collapsing them.
        exact: dict[tuple[str, str], MemoryCandidate] = {}
        for candidate in candidates:
            exact.setdefault((candidate.candidate_type, candidate.dedupe_key), candidate)

        result: list[MemoryCandidate] = []
        for candidate in exact.values():
            duplicate = False
            for existing in result:
                if candidate.candidate_type != existing.candidate_type:
                    continue
                same_thread = bool({s.conversation_id for s in candidate.source_references}
                                    & {s.conversation_id for s in existing.source_references})
                if same_thread and SequenceMatcher(None, normalize(candidate.content), normalize(existing.content)).ratio() >= self.similarity_threshold:
                    duplicate = True
                    break
            if not duplicate:
                result.append(candidate)
        return result
