from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from decimal import Decimal


@dataclass(frozen=True)
class ReserveSnapshot:
    asset: str
    quantity: str
    valuation_eur: str
    source: str
    verified: bool
    timestamp: str


class TreasuryLedger:
    """Small deterministic reserve ledger for PPT/Z1 integration.

    It deliberately does not connect to a bank or mint tokens. External
    balances must be supplied by an authorized connector and verified before
    they can be treated as backing evidence.
    """

    def __init__(self) -> None:
        self._snapshots: list[ReserveSnapshot] = []

    def preview(self, *, asset: str, quantity: str, valuation_eur: str, source: str, verified: bool) -> ReserveSnapshot:
        snapshot = ReserveSnapshot(
            asset=asset,
            quantity=quantity,
            valuation_eur=str(Decimal(valuation_eur)),
            source=source,
            verified=verified,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        if not snapshot.verified:
            raise ValueError("reserve snapshot is not verified")
        self._snapshots.append(snapshot)
        return snapshot

    def summary(self) -> dict:
        verified = [s for s in self._snapshots if s.verified]
        total = sum((Decimal(s.valuation_eur) for s in verified), Decimal("0"))
        return {
            "verified_reserve_eur": str(total),
            "verified_snapshot_count": len(verified),
            "snapshots": [asdict(s) for s in self._snapshots],
        }


ledger = TreasuryLedger()
