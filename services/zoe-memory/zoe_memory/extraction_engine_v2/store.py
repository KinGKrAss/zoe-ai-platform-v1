from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import CandidateDecision, MemoryCandidate


class JsonlCandidateStore:
    """Append-only candidate/decision store used between extraction and Memory Core."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, candidate: MemoryCandidate) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"kind": "candidate", **asdict(candidate)}, ensure_ascii=False) + "\n")

    def append_decision(self, decision: CandidateDecision) -> None:
        decision.validate()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"kind": "decision", **asdict(decision)}, ensure_ascii=False) + "\n")

    def read_candidates(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, object]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    if row.get("kind") == "candidate":
                        rows.append(row)
        return rows
