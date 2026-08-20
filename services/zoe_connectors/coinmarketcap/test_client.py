import os
import unittest
from unittest.mock import Mock, patch

from services.zoe_connectors.coinmarketcap.client import CoinMarketCapClient, CoinMarketCapError


class CoinMarketCapClientTests(unittest.TestCase):
    def test_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CoinMarketCapError):
                CoinMarketCapClient()

    @patch("services.zoe_connectors.coinmarketcap.client.requests.get")
    def test_latest_quotes_uses_v3_endpoint(self, get):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "status": {"error_code": 0},
            "data": {"BTC": {"symbol": "BTC", "quote": {"USD": {"price": 1}}}},
        }
        get.return_value = response

        result = CoinMarketCapClient(api_key="test").latest_quotes(["BTC"])

        self.assertEqual(result[0]["symbol"], "BTC")
        self.assertEqual(
            get.call_args.args[0],
            "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/latest",
        )

    @patch("services.zoe_connectors.coinmarketcap.client.requests.get")
    def test_api_error_is_exposed_as_connector_error(self, get):
        response = Mock()
        response.ok = False
        response.status_code = 401
        response.text = "unauthorized"
        response.json.return_value = {
            "status": {"error_code": 1006, "error_message": "API_KEY_INVALID"}
        }
        get.return_value = response

        with self.assertRaisesRegex(CoinMarketCapError, "API_KEY_INVALID"):
            CoinMarketCapClient(api_key="bad").latest_quotes(["BTC"])


if __name__ == "__main__":
    unittest.main()
