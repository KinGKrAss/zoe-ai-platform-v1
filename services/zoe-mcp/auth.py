"""Z1 authorization guard for the Zoë MCP gateway."""

from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=True)
Z1_AUTH_SERVICE_URL = os.getenv("Z1_AUTH_SERVICE_URL", "http://z1-auth:8000/v1/validate")
Z1_AUTH_TIMEOUT = float(os.getenv("Z1_AUTH_TIMEOUT_SECONDS", "3"))


async def verify_z1_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict[str, Any]:
    """Validate a bearer token against the Z1 Auth service and return its context."""
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    try:
        async with httpx.AsyncClient(timeout=Z1_AUTH_TIMEOUT) as client:
            response = await client.post(
                Z1_AUTH_SERVICE_URL,
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="Z1 Auth Service unreachable") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Z1 Auth: Invalid or expired token")

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Z1 Auth: invalid response") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="Z1 Auth: invalid response payload")
    if not payload.get("active", False):
        raise HTTPException(status_code=403, detail="Z1 Auth: Token inactive or revoked")

    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Z1 Auth: user context missing")

    scopes = payload.get("scopes", [])
    if isinstance(scopes, str):
        scopes = scopes.split()
    if not isinstance(scopes, list):
        scopes = []

    return {**payload, "user_id": str(user_id), "scopes": scopes}
