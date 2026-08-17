from fastapi.testclient import TestClient

from finanzfuchs.api import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok", "service": "z1-finanzfuchs"}


def test_ppt_account_and_transfer_flow() -> None:
    asset_id = "ppt-api-test"
    treasury = "treasury-api-test"
    merchant = "merchant-api-test"
    assert client.post("/assets", json={"asset_id": asset_id, "symbol": "PPT", "asset_type": "erc20"}).status_code == 201
    assert client.post("/accounts", json={"account_id": treasury}).status_code == 201
    assert client.post("/accounts", json={"account_id": merchant}).status_code == 201
    assert client.post("/credits", json={"asset_id": asset_id, "account_id": treasury, "quantity": "50"}).status_code == 201
    response = client.post("/transfers", json={"asset_id": asset_id, "account_id": treasury, "destination_account": merchant, "quantity": "12.5"})
    assert response.status_code == 201
    assert client.get(f"/balances/{treasury}/{asset_id}").json()["quantity"] == "37.5"
    assert client.get(f"/balances/{merchant}/{asset_id}").json()["quantity"] == "12.5"


def test_insufficient_transfer_is_rejected() -> None:
    asset_id = "ppt-api-insufficient"
    treasury = "treasury-api-insufficient"
    merchant = "merchant-api-insufficient"
    client.post("/assets", json={"asset_id": asset_id, "symbol": "PPT", "asset_type": "erc20"})
    client.post("/accounts", json={"account_id": treasury})
    client.post("/accounts", json={"account_id": merchant})
    client.post("/credits", json={"asset_id": asset_id, "account_id": treasury, "quantity": "1"})
    response = client.post("/transfers", json={"asset_id": asset_id, "account_id": treasury, "destination_account": merchant, "quantity": "2"})
    assert response.status_code == 400
