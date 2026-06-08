"""Order management layer.

Builds parameter dicts that match the Binance Futures REST API specification,
validates inputs, and delegates actual HTTP calls to BinanceClient.
"""

import logging

from bot.client import BinanceClient
from bot.validators import OrderValidator

logger = logging.getLogger(__name__)


class OrderManager:
    """High-level helper that validates, builds, and sends orders."""

    def __init__(self, client: BinanceClient) -> None:
        """Create an OrderManager backed by the given BinanceClient.

        Args:
            client: An authenticated BinanceClient instance.
        """
        self.client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
    ) -> dict:
        """Validate inputs, build the request, and send the order.

        Args:
            symbol: Trading pair (e.g. BTCUSDT).
            side: BUY or SELL.
            order_type: MARKET, LIMIT, or STOP_MARKET.
            quantity: Amount to trade.
            price: Limit price (required for LIMIT).
            stop_price: Stop trigger price (required for STOP_MARKET).

        Returns:
            The parsed JSON response from the Binance API.

        Raises:
            ValueError: If any parameter is invalid.
            RuntimeError: If the API returns an error.
            ConnectionError: If a network problem occurs.
        """
        OrderValidator.validate(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )

        params: dict = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": str(quantity),
        }

        if order_type == "LIMIT":
            # GTC (Good Till Cancel) is the standard time-in-force for limits.
            params["timeInForce"] = "GTC"
            params["price"] = str(price)

        if order_type == "STOP_MARKET":
            params["stopPrice"] = str(stop_price)
            # closePosition is not set; the user controls quantity explicitly.

        logger.info(
            "Placing %s %s order for %s %s",
            side, order_type, quantity, symbol,
        )

        response = self.client.send_order(params)

        logger.info("Order placed successfully: orderId=%s", response.get("orderId"))
        return response
