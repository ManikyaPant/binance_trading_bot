"""Unit tests for bot.orders.OrderManager."""

import unittest
from unittest import mock

from bot.orders import OrderManager


class TestPlaceOrder(unittest.TestCase):
    """Tests for OrderManager.place_order."""

    def setUp(self):
        self.mock_client = mock.Mock()
        self.mock_client.send_order.return_value = {
            "orderId": 99999,
            "status": "NEW",
        }
        self.manager = OrderManager(self.mock_client)

    def test_market_order_params(self):
        """MARKET order should send symbol, side, type, and quantity."""
        self.manager.place_order(
            symbol="BTCUSDT", side="BUY", order_type="MARKET",
            quantity=0.5,
        )
        self.mock_client.send_order.assert_called_once()
        params = self.mock_client.send_order.call_args[0][0]
        self.assertEqual(params["symbol"], "BTCUSDT")
        self.assertEqual(params["side"], "BUY")
        self.assertEqual(params["type"], "MARKET")
        self.assertEqual(params["quantity"], "0.5")
        self.assertNotIn("price", params)
        self.assertNotIn("timeInForce", params)

    def test_limit_order_includes_price_and_tif(self):
        """LIMIT order should add price and timeInForce=GTC."""
        self.manager.place_order(
            symbol="ETHUSDT", side="SELL", order_type="LIMIT",
            quantity=1.0, price=3200.0,
        )
        params = self.mock_client.send_order.call_args[0][0]
        self.assertEqual(params["type"], "LIMIT")
        self.assertEqual(params["price"], "3200.0")
        self.assertEqual(params["timeInForce"], "GTC")

    def test_stop_market_order_includes_stop_price(self):
        """STOP_MARKET order should add stopPrice."""
        self.manager.place_order(
            symbol="BTCUSDT", side="SELL", order_type="STOP_MARKET",
            quantity=0.01, stop_price=95000.0,
        )
        params = self.mock_client.send_order.call_args[0][0]
        self.assertEqual(params["type"], "STOP_MARKET")
        self.assertEqual(params["stopPrice"], "95000.0")
        self.assertNotIn("price", params)

    def test_returns_api_response(self):
        """place_order should return whatever the client returns."""
        result = self.manager.place_order(
            symbol="BTCUSDT", side="BUY", order_type="MARKET",
            quantity=1.0,
        )
        self.assertEqual(result["orderId"], 99999)

    def test_validation_error_propagates(self):
        """Invalid inputs should raise ValueError before calling client."""
        with self.assertRaises(ValueError):
            self.manager.place_order(
                symbol="", side="BUY", order_type="MARKET", quantity=1.0,
            )
        self.mock_client.send_order.assert_not_called()

    def test_api_error_propagates(self):
        """RuntimeError from the client should bubble up."""
        self.mock_client.send_order.side_effect = RuntimeError("API fail")
        with self.assertRaises(RuntimeError):
            self.manager.place_order(
                symbol="BTCUSDT", side="BUY", order_type="MARKET",
                quantity=1.0,
            )

    def test_network_error_propagates(self):
        """ConnectionError from the client should bubble up."""
        self.mock_client.send_order.side_effect = ConnectionError("timeout")
        with self.assertRaises(ConnectionError):
            self.manager.place_order(
                symbol="BTCUSDT", side="BUY", order_type="MARKET",
                quantity=1.0,
            )


if __name__ == "__main__":
    unittest.main()
