from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['service'] == 'ppt'

def test_unverified_reserve_rejected():
    response = client.post('/v1/reserves/preview', json={
        'asset': 'gold', 'quantity': 100, 'valuation_eur': 100,
        'source': 'test', 'verified': False,
    })
    assert response.status_code == 409

def test_payment_quote():
    response = client.post('/v1/payments/quote', json={
        'merchant_id': 'demo', 'amount_eur': '12.50', 'ppt_per_eur': '1'
    })
    assert response.status_code == 200
    assert response.json()['amount_ppt'] == '12.50'

def test_payment_intent_requires_address():
    response = client.post('/v1/payments/intents', json={
        'merchant_id': 'demo', 'amount_ppt': '12.5', 'chain_id': 1,
        'token_contract': '0xabc', 'recipient': 'not-an-address'
    })
    assert response.status_code == 400
