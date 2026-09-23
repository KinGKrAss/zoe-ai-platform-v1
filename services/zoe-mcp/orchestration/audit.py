from __future__ import annotations

import os
from typing import Any

import httpx


async def z1_audit(event: dict[str, Any]) -> None:
    """Forward orchestration events to a configured Z1 audit endpoint.

    No endpoint means audit forwarding is disabled; the orchestrator still runs.
    """
    endpoint = os.getenv("Z1_AUDIT_URL")
    token = os.getenv("Z1_AUDIT_TOKEN")
    if not endpoint or not token:
        return
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(endpoint, json=event, headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
