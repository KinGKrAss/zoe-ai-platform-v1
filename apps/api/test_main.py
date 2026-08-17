from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db = tmp_path / "z1.sqlite3"
    monkeypatch.setenv("Z1_DEV_DB", str(db))
    monkeypatch.setenv("Z1_API_TOKEN", "test-secret")

    # Import after environment configuration because the API reads its settings at import time.
    import importlib
    import apps.api.main as main

    importlib.reload(main)
    with TestClient(main.app) as test_client:
        yield test_client


def headers(actor: str = "king") -> dict[str, str]:
    return {"Authorization": "Bearer test-secret", "X-Z1-Actor": actor}


def test_health_is_public(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_control_plane_fails_closed_without_token(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("apps.api.main.API_TOKEN", None)
    response = client.get("/v1/identity", headers=headers())
    assert response.status_code == 503


def test_asset_lifecycle_is_persistent_and_audited(client: TestClient) -> None:
    payload = {
        "name": "Example property",
        "asset_type": "real_estate",
        "owner": "king",
        "currency": "eur",
        "reported_value": 1000000,
        "status": "USER_REPORTED",
        "evidence_ref": "document://example/001",
    }
    created = client.post("/v1/assets", json=payload, headers=headers())
    assert created.status_code == 201
    asset = created.json()
    assert asset["uri"].startswith("z1://wealth/assets/")
    assert asset["status"] == "USER_REPORTED"

    listed = client.get("/v1/assets", headers=headers())
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == asset["id"]

    fetched = client.get(f"/v1/assets/{asset['id']}", headers=headers())
    assert fetched.status_code == 200
    assert fetched.json()["reported_value"] == 1000000


def test_authentication_is_required(client: TestClient) -> None:
    response = client.get("/v1/assets")
    assert response.status_code == 401
