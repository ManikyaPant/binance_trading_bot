"""Unit tests for bot.client.BinanceClient."""

import hashlib
import hmac
import unittest
from unittest import mock
from urllib.parse import urlencode

from bot.client import BASE_URL, ORDER_ENDPOINT


class TestSignRequest(unittest.TestCase):
    """Tests for HMAC-SHA256 request signing."""

    @mock.patch("bot.client.requests.get")
    def setUp(self, mock_get):
        """Create a client with a mocked time offset of 0."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"serverTime": 1700000000000}
        mock_get.return_value = mock_response

        with mock.patch("bot.client.time") as mock_time:
            mock_time.time.return_value = 1700000000.0
            from bot.client import BinanceClient
            self.client = BinanceClient(
                api_key="test_api_key",
                api_secret="test_api_secret",
            )

    @mock.patch("bot.client.time")
    def test_adds_timestamp_and_signature(self, mock_time):
        """The signed params should contain timestamp and a valid HMAC."""
        mock_time.time.return_value = 1700000000.0

        params = {"symbol": "BTCUSDT", "side": "BUY"}
        signed = self.client._sign_request(params)

        self.assertIn("timestamp", signed)
        self.assertIn("signature", signed)
        # Offset is 0, so timestamp = local time.
        self.assertEqual(signed["timestamp"], 1700000000000)

    @mock.patch("bot.client.time")
    def test_signature_is_deterministic(self, mock_time):
        """Same inputs must produce the same signature."""
        mock_time.time.return_value = 1700000000.0

        params_a = {"symbol": "BTCUSDT", "side": "BUY"}
        signed_a = self.client._sign_request(params_a.copy())

        params_b = {"symbol": "BTCUSDT", "side": "BUY"}
        signed_b = self.client._sign_request(params_b.copy())

        self.assertEqual(signed_a["signature"], signed_b["signature"])

    @mock.patch("bot.client.time")
    def test_signature_matches_manual_computation(self, mock_time):
        """Verify the HMAC against a manually computed value."""
        mock_time.time.return_value = 1700000000.0

        params = {"symbol": "ETHUSDT", "side": "SELL"}
        signed = self.client._sign_request(params.copy())

        # Recompute expected signature manually.
        expected_params = {
            "symbol": "ETHUSDT",
            "side": "SELL",
            "timestamp": 1700000000000,
        }
        query_string = urlencode(expected_params)
        expected_sig = hmac.new(
            b"test_api_secret",
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        self.assertEqual(signed["signature"], expected_sig)


class TestSendOrder(unittest.TestCase):
    """Tests for the send_order HTTP call."""

    @mock.patch("bot.client.requests.get")
    def setUp(self, mock_get):
        """Create a client with a mocked time offset of 0."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"serverTime": 1700000000000}
        mock_get.return_value = mock_response

        with mock.patch("bot.client.time") as mock_time:
            mock_time.time.return_value = 1700000000.0
            from bot.client import BinanceClient
            self.client = BinanceClient(
                api_key="test_api_key",
                api_secret="test_api_secret",
            )

    @mock.patch("bot.client.requests.post")
    def test_successful_order(self, mock_post):
        """A 200 response should return parsed JSON."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "orderId": 12345,
            "status": "FILLED",
        }
        mock_response.text = '{"orderId": 12345, "status": "FILLED"}'
        mock_post.return_value = mock_response

        result = self.client.send_order({"symbol": "BTCUSDT", "side": "BUY"})

        self.assertEqual(result["orderId"], 12345)
        self.assertEqual(result["status"], "FILLED")
        mock_post.assert_called_once()

    @mock.patch("bot.client.requests.post")
    def test_api_error_raises_runtime_error(self, mock_post):
        """A non-200 status should raise RuntimeError."""
        mock_response = mock.Mock()
        mock_response.status_code = 400
        mock_response.text = '{"code": -1102, "msg": "Param error"}'
        mock_post.return_value = mock_response

        with self.assertRaises(RuntimeError) as ctx:
            self.client.send_order({"symbol": "INVALID"})
        self.assertIn("400", str(ctx.exception))

    @mock.patch("bot.client.requests.post")
    def test_timeout_raises_connection_error(self, mock_post):
        """A timeout should raise ConnectionError."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("timed out")

        with self.assertRaises(ConnectionError) as ctx:
            self.client.send_order({"symbol": "BTCUSDT"})
        self.assertIn("timed out", str(ctx.exception).lower())

    @mock.patch("bot.client.requests.post")
    def test_network_failure_raises_connection_error(self, mock_post):
        """A connection failure should raise ConnectionError."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("refused")

        with self.assertRaises(ConnectionError):
            self.client.send_order({"symbol": "BTCUSDT"})

    @mock.patch("bot.client.requests.post")
    def test_sends_api_key_header(self, mock_post):
        """The X-MBX-APIKEY header must contain the API key."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.text = "{}"
        mock_post.return_value = mock_response

        self.client.send_order({"symbol": "BTCUSDT"})

        call_kwargs = mock_post.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        self.assertEqual(headers["X-MBX-APIKEY"], "test_api_key")

    @mock.patch("bot.client.requests.post")
    def test_posts_to_correct_url(self, mock_post):
        """Requests must go to the testnet order endpoint."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.text = "{}"
        mock_post.return_value = mock_response

        self.client.send_order({"symbol": "BTCUSDT"})

        call_args = mock_post.call_args
        url = call_args.args[0] if call_args.args else call_args[0][0]
        self.assertEqual(url, f"{BASE_URL}{ORDER_ENDPOINT}")


if __name__ == "__main__":
    unittest.main()
