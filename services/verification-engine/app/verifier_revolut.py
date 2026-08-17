from __future__ import annotations

from typing import Protocol

from .models import Claim


class RevolutVerifier(Protocol):
    async def verify(self, claim: Claim) -> tuple[bool, list[str]]: ...


class UnconfiguredRevolutVerifier:
    async def verify(self, claim: Claim) -> tuple[bool, list[str]]:
        return False, ["Revolut connector is not configured"]
