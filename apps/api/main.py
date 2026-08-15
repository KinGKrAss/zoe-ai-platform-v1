"""Runnable Z1 control-plane API.

This is the first real vertical slice of the platform: authenticated API access,
health reporting, a persistent development wealth registry, and append-only audit
records. Production deployments should use PostgreSQL and the existing Z1
migration set; SQLite is intentionally limited to local development/tests.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

APP_VERSION = "1.0.0"
DEFAULT_DB = Path(os.getenv("Z1_DEV_DB", ".z1/z1-dev.sqlite3"))
API_TOKEN = os.getenv("Z1_API_TOKEN")

app = FastAPI(
    title="Z1 Control Plane",
    version=APP_VERSION,
    description="Authenticated control-plane API for the Z1 administration system.",
)


class AssetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    asset_type: str = Field(min_length=1, max_length=100)
    owner: str = Field(min_length=1, max_length=200)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    reported_value: float | None = Field(default=None, ge=0)
    status: str = Field(default="USER_REPORTED", pattern="^(USER_REPORTED|UNVERIFIED|VERIFIED|DERIVED|CONFLICT)$")
    evidence_ref: str | None = Field(default=None, max_length=500)


class Asset(BaseModel):
    id: str
    uri: str
    name: str
    asset_type: str
    owner: str
    currency: str
    reported_value: float | None
    status: str
    evidence_ref: str | None
    created_at: str
    updated_at: str


def _connect() -> sqlite3.Connection:
    DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DEFAULT_DB)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _init_db() -> None:
    with closing(_connect()) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS z1_assets (
                id TEXT PRIMARY KEY,
                uri TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                owner TEXT NOT NULL,
                currency TEXT NOT NULL,
                reported_value REAL,
                status TEXT NOT NULL,
                evidence_ref TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS z1_audit_events (
                id TEXT PRIMARY KEY,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                target_uri TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        db.commit()


@app.on_event("startup")
def startup() -> None:
    _init_db()


def require_auth(
    authorization: str | None = Header(default=None),
    x_z1_actor: str | None = Header(default=None),
) -> str:
    """Require an explicit API token; missing configuration is fail-closed."""
    if not API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Z1_API_TOKEN is not configured; control-plane access is disabled",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    supplied = authorization.removeprefix("Bearer ")
    if not hmac.compare_digest(supplied, API_TOKEN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Z1 credential")
    actor = (x_z1_actor or "").strip()
    if not actor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Z1-Actor required")
    return actor


def _audit(actor: str, action: str, target_uri: str, result: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with closing(_connect()) as db:
        db.execute(
            "INSERT INTO z1_audit_events (id, actor, action, target_uri, result, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), actor, action, target_uri, result, now),
        )
        db.commit()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "z1-control-plane",
        "version": APP_VERSION,
        "api_auth_configured": bool(API_TOKEN),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/v1/identity")
def identity(actor: str = Depends(require_auth)) -> dict[str, str]:
    return {
        "actor": actor,
        "system": "Z1",
        "role": "administration-control-plane",
        "zoe": "Zoë",
    }


@app.post("/v1/assets", response_model=Asset, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, actor: str = Depends(require_auth)) -> Asset:
    asset_id = str(uuid.uuid4())
    uri = f"z1://wealth/assets/{asset_id}"
    now = datetime.now(timezone.utc).isoformat()
    with closing(_connect()) as db:
        db.execute(
            """INSERT INTO z1_assets
               (id, uri, name, asset_type, owner, currency, reported_value, status, evidence_ref, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                asset_id,
                uri,
                payload.name,
                payload.asset_type,
                payload.owner,
                payload.currency.upper(),
                payload.reported_value,
                payload.status,
                payload.evidence_ref,
                now,
                now,
            ),
        )
        db.commit()
    _audit(actor, "asset.create", uri, "accepted")
    return Asset(id=asset_id, uri=uri, **payload.model_dump(), created_at=now, updated_at=now)


@app.get("/v1/assets", response_model=list[Asset])
def list_assets(actor: str = Depends(require_auth)) -> list[Asset]:
    with closing(_connect()) as db:
        rows = db.execute("SELECT * FROM z1_assets ORDER BY created_at DESC").fetchall()
    _audit(actor, "asset.list", "z1://wealth/assets", "accepted")
    return [Asset(**dict(row)) for row in rows]


@app.get("/v1/assets/{asset_id}", response_model=Asset)
def get_asset(asset_id: str, actor: str = Depends(require_auth)) -> Asset:
    with closing(_connect()) as db:
        row = db.execute("SELECT * FROM z1_assets WHERE id = ?", (asset_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    _audit(actor, "asset.read", row["uri"], "accepted")
    return Asset(**dict(row))


def content_fingerprint(text: str) -> str:
    """Return a deterministic fingerprint for audit/provenance without storing source content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
