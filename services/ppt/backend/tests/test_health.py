from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['service'] == 'ppt'


def test_token_metadata_is_safe_without_deployment_config():
    response = client.get('/v1/token')
    assert response.status_code == 200
    body = response.json()
    assert body['symbol'] == 'PPT'
    assert body['decimals'] == 18


def test_unverified_reserve_cannot_be_accepted():
    response = client.post('/v1/reserves/preview', json={
        'asset': 'test',
        'quantity': '1',
        'valuation_eur': '1',
        'source': 'test',
        'verified': False,
    })
    assert response.status_code == 409


def test_z1_summary_exposes_canonical_ppt_uri():
    response = client.get('/v1/z1/summary')
    assert response.status_code == 200
    assert response.json()['canonical_uri'] == 'z1://ppt/token/PPT'
