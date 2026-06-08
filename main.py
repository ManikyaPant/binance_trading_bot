"""CLI entry point for the Binance Futures Testnet trading bot.

Parses command-line arguments with argparse, validates inputs, prints a
pre-flight summary, sends the order, and displays the result.

Usage examples:
    python main.py --symbol BTCUSDT --side BUY --order_type MARKET --quantity 0.001
    python main.py --symbol ETHUSDT --side SELL --order_type LIMIT --quantity 0.5 --price 3200.00
    python main.py --symbol BTCUSDT --side SELL --order_type STOP_MARKET --quantity 0.001 --stop_price 95000
"""

import argparse
import sys
import logging

from bot.config import load_config
from bot.client import BinanceClient
from bot.logging_config import setup_logging
from bot.orders import OrderManager

logger = logging.getLogger(__name__)




def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Returns:
        A configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Place orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        type=str,
        required=True,
        choices=["BUY", "SELL"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--order_type",
        type=str,
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type: MARKET, LIMIT, or STOP_MARKET",
    )
    parser.add_argument(
        "--quantity",
        type=float,
        required=True,
        help="Order quantity (must be positive)",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Limit price (required for LIMIT orders, must be positive)",
    )
    parser.add_argument(
        "--stop_price",
        type=float,
        default=None,
        help="Stop trigger price (required for STOP_MARKET orders, must be positive)",
    )

    return parser




SEPARATOR = "=" * 50


def print_order_summary(args: argparse.Namespace) -> None:
    """Print a human-readable summary of the order before it is sent.

    Args:
        args: Parsed CLI arguments.
    """
    print(f"\n{SEPARATOR}")
    print("  ORDER REQUEST SUMMARY")
    print(SEPARATOR)
    print(f"  Symbol     : {args.symbol}")
    print(f"  Side       : {args.side}")
    print(f"  Type       : {args.order_type}")
    print(f"  Quantity   : {args.quantity}")
    if args.order_type == "LIMIT":
        print(f"  Price      : {args.price}")
    if args.order_type == "STOP_MARKET":
        print(f"  Stop Price : {args.stop_price}")
    print(SEPARATOR)


def print_order_response(response: dict) -> None:
    """Print the key fields from the Binance order response.

    Args:
        response: Parsed JSON response dict from the API.
    """
    print(f"\n{SEPARATOR}")
    print("  ORDER RESPONSE")
    print(SEPARATOR)
    print(f"  Order ID     : {response.get('orderId', 'N/A')}")
    print(f"  Status       : {response.get('status', 'N/A')}")
    print(f"  Executed Qty : {response.get('executedQty', 'N/A')}")
    print(f"  Avg Price    : {response.get('avgPrice', 'N/A')}")
    print(f"  Symbol       : {response.get('symbol', 'N/A')}")
    print(f"  Side         : {response.get('side', 'N/A')}")
    print(f"  Type         : {response.get('type', 'N/A')}")
    print(SEPARATOR)





def main() -> None:
    """Parse arguments, send the order, and display results."""
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    # Pre-flight validation for conditional arguments.
    if args.order_type == "LIMIT" and args.price is None:
        parser.error("--price is required for LIMIT orders.")

    if args.order_type == "STOP_MARKET" and args.stop_price is None:
        parser.error("--stop_price is required for STOP_MARKET orders.")

    # Load configuration.
    try:
        config = load_config()
    except EnvironmentError as exc:
        logger.error("Configuration error: %s", exc)
        print(f"\n✗ Configuration error: {exc}")
        sys.exit(1)

    # Print order summary.
    print_order_summary(args)

    # Place the order.
    client = BinanceClient(
        api_key=config["api_key"],
        api_secret=config["api_secret"],
    )
    manager = OrderManager(client)

    try:
        response = manager.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        print(f"\n✗ Validation error: {exc}")
        sys.exit(1)
    except ConnectionError as exc:
        logger.error("Network error: %s", exc)
        print(f"\n✗ Network error: {exc}")
        sys.exit(1)
    except RuntimeError as exc:
        logger.error("API error: %s", exc)
        print(f"\n✗ API error: {exc}")
        sys.exit(1)

    # Display success.
    print_order_response(response)
    print("\n✓ Order placed successfully!\n")


if __name__ == "__main__":
    main()
