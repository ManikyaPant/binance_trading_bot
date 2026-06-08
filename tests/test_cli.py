"""Unit tests for the CLI entry point (main.py)."""

import unittest
from unittest import mock

from main import build_parser


class TestBuildParser(unittest.TestCase):
    """Tests for CLI argument parsing."""

    def test_market_order_args(self):
        """Parse a complete MARKET order command."""
        parser = build_parser()
        args = parser.parse_args([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--order_type", "MARKET",
            "--quantity", "0.001",
        ])
        self.assertEqual(args.symbol, "BTCUSDT")
        self.assertEqual(args.side, "BUY")
        self.assertEqual(args.order_type, "MARKET")
        self.assertAlmostEqual(args.quantity, 0.001)
        self.assertIsNone(args.price)
        self.assertIsNone(args.stop_price)

    def test_limit_order_args(self):
        """Parse a LIMIT order with --price."""
        parser = build_parser()
        args = parser.parse_args([
            "--symbol", "ETHUSDT",
            "--side", "SELL",
            "--order_type", "LIMIT",
            "--quantity", "1.5",
            "--price", "3200.50",
        ])
        self.assertEqual(args.order_type, "LIMIT")
        self.assertAlmostEqual(args.price, 3200.50)

    def test_stop_market_order_args(self):
        """Parse a STOP_MARKET order with --stop_price."""
        parser = build_parser()
        args = parser.parse_args([
            "--symbol", "BTCUSDT",
            "--side", "SELL",
            "--order_type", "STOP_MARKET",
            "--quantity", "0.01",
            "--stop_price", "95000",
        ])
        self.assertEqual(args.order_type, "STOP_MARKET")
        self.assertAlmostEqual(args.stop_price, 95000.0)

    def test_missing_required_arg_raises(self):
        """Omitting a required argument should cause SystemExit."""
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--symbol", "BTCUSDT"])

    def test_invalid_side_raises(self):
        """An invalid --side value should cause SystemExit."""
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([
                "--symbol", "BTCUSDT",
                "--side", "HOLD",
                "--order_type", "MARKET",
                "--quantity", "1",
            ])

    def test_invalid_order_type_raises(self):
        """An invalid --order_type value should cause SystemExit."""
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([
                "--symbol", "BTCUSDT",
                "--side", "BUY",
                "--order_type", "FOK",
                "--quantity", "1",
            ])


if __name__ == "__main__":
    unittest.main()
