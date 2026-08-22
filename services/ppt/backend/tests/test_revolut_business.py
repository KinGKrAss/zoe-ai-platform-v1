import pytest

from app.revolut_business import RevolutBusinessClient


def test_revolut_client_requires_secret():
    client = RevolutBusinessClient(access_token=None)
    with pytest.raises(RuntimeError, match="REVOLUT_BUSINESS_ACCESS_TOKEN"):
        client._headers()


def test_revolut_client_is_read_only():
    client = RevolutBusinessClient(access_token="test-token")
    assert not hasattr(client, "create_payment")
    assert not hasattr(client, "transfer")
    assert not hasattr(client, "exchange")
