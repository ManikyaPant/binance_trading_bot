"""Unit tests for bot.validators.OrderValidator."""

import unittest

from bot.validators import OrderValidator


class TestValidateSymbol(unittest.TestCase):
    """Tests for the symbol parameter."""

    def test_valid_symbol(self):
        """Accept a normal uppercase symbol."""
        OrderValidator.validate(
            symbol="BTCUSDT", side="BUY", order_type="MARKET",
            quantity=1.0,
        )

    def test_empty_symbol_raises(self):
        """Reject an empty string."""
        with self.assertRaises(ValueError) as ctx:
            OrderValidator.validate(
                symbol="", side="BUY", order_type="MARKET", quantity=1.0,
            )
        self.assertIn("symbol", str(ctx.exception).lower())

    def test_numeric_symbol_raises(self):
        """Reject symbols containing digits."""
        with self.assertRaises(ValueError):
            OrderValidator.validate(
                symbol="BTC123", side="BUY", order_type="MARKET",
                quantity=1.0,
            )

    def test_none_symbol_raises(self):
        """Reject None as a symbol."""
        with self.assertRaises(ValueError):
            OrderValidator.validate(
                symbol=None, side="BUY", order_type="MARKET", quantity=1.0,
            )


class TestValidateSide(unittest.TestCase):
    """Tests for the side parameter."""

    def test_buy_accepted(self):
        OrderValidator.validate(
            symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity=1.0,
        )

    def test_sell_accepted(self):
        OrderValidator.validate(
            symbol="BTCUSDT", side="SELL", order_type="MARKET", quantity=1.0,
        )

    def test_invalid_side_raises(self):
        with self.assertRaises(ValueError) as ctx:
            OrderValidator.validate(
                symbol="BTCUSDT", side="HOLD", order_type="MARKET",
                quantity=1.0,
            )
        self.assertIn("side", str(ctx.exception).lower())

    def test_lowercase_side_raises(self):
        """Sides must be uppercase."""
        with self.assertRaises(ValueError):
            OrderValidator.validate(
                symbol="BTCUSDT", side="buy", order_type="MARKET",
                quantity=1.0,
            )


class TestValidateOrderType(unittest.TestCase):
    """Tests for the order_type parameter."""

    def test_market_accepted(self):
        OrderValidator.validate(
            symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity=1.0,
        )

    def test_limit_with_price_accepted(self):
        OrderValidator.validate(
            symbol="BTCUSDT", side="BUY", order_type="LIMIT",
            quantity=1.0, price=50000.0,
        )

    def test_stop_market_with_stop_price_accepted(self):
        OrderValidator.validate(
            symbol="BTCUSDT", side="SELL", order_type="STOP_MARKET",
            quantity=0.5, stop_price=95000.0,
        )

    def test_unknown_order_type_raises(self):
        with self.assertRaises(ValueError) as ctx:
            OrderValidator.validate(
                symbol="BTCUSDT", side="BUY", order_type="FOK",
                quantity=1.0,
            )
        self.assertIn("order type", str(ctx.exception).lower())


class TestValidateQuantity(unittest.TestCase):
    """Tests for the quantity parameter."""

    def test_positive_quantity_accepted(self):
        OrderValidator.validate(
            symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity=0.001,
        )

    def test_zero_quantity_raises(self):
        with self.assertRaises(ValueError) as ctx:
            OrderValidator.validate(
                symbol="BTCUSDT", side="BUY", order_type="MARKET",
                quantity=0,
            )
        self.assertIn("quantity", str(ctx.exception).lower())

    def test_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            OrderValidator.validate(
                symbol="BTCUSDT", side="BUY", order_type="MARKET",
                quantity=-1.0,
            )


class TestValidateLimitPrice(unittest.TestCase):
    """Tests for the price parameter on LIMIT orders."""

    def test_missing_price_raises(self):
        """LIMIT without --price must fail."""
        with self.assertRaises(ValueError) as ctx:
            OrderValidator.validate(
                symbol="BTCUSDT", side="BUY", order_type="LIMIT",
                quantity=1.0, price=None,
            )
        self.assertIn("price", str(ctx.exception).lower())

    def test_zero_price_raises(self):
        with self.assertRaises(ValueError):
            OrderValidator.validate(
                symbol="BTCUSDT", side="BUY", order_type="LIMIT",
                quantity=1.0, price=0,
            )

    def test_negative_price_raises(self):
        with self.assertRaises(ValueError):
            OrderValidator.validate(
                symbol="BTCUSDT", side="BUY", order_type="LIMIT",
                quantity=1.0, price=-100.0,
            )


class TestValidateStopPrice(unittest.TestCase):
    """Tests for the stop_price parameter on STOP_MARKET orders."""

    def test_missing_stop_price_raises(self):
        """STOP_MARKET without --stop_price must fail."""
        with self.assertRaises(ValueError) as ctx:
            OrderValidator.validate(
                symbol="BTCUSDT", side="SELL", order_type="STOP_MARKET",
                quantity=1.0, stop_price=None,
            )
        self.assertIn("stop_price", str(ctx.exception).lower())

    def test_zero_stop_price_raises(self):
        with self.assertRaises(ValueError):
            OrderValidator.validate(
                symbol="BTCUSDT", side="SELL", order_type="STOP_MARKET",
                quantity=1.0, stop_price=0,
            )

    def test_negative_stop_price_raises(self):
        with self.assertRaises(ValueError):
            OrderValidator.validate(
                symbol="BTCUSDT", side="SELL", order_type="STOP_MARKET",
                quantity=1.0, stop_price=-500.0,
            )

    def test_market_order_ignores_stop_price(self):
        """stop_price should be irrelevant for MARKET orders."""
        OrderValidator.validate(
            symbol="BTCUSDT", side="BUY", order_type="MARKET",
            quantity=1.0, stop_price=99999.0,
        )


if __name__ == "__main__":
    unittest.main()
