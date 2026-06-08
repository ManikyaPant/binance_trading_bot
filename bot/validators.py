"""Input validation for trading orders.

Centralises all pre-flight checks so invalid data never reaches the API.
"""

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class OrderValidator:
    """Validates order parameters before they are sent to the exchange."""

    @staticmethod
    def validate(
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
    ) -> None:
        """Check every order field and raise ValueError on the first problem.

        Args:
            symbol: Trading pair (e.g. BTCUSDT).
            side: BUY or SELL.
            order_type: MARKET, LIMIT, or STOP_MARKET.
            quantity: Amount to trade - must be positive.
            price: Limit price - required and must be positive for LIMIT orders.
            stop_price: Stop trigger price - required and must be positive for
                STOP_MARKET orders.

        Raises:
            ValueError: When any parameter fails validation.
        """
        # Symbol must be a non-empty alphabetic string.
        if not symbol or not symbol.isalpha():
            raise ValueError(
                f"Invalid symbol '{symbol}': must be a non-empty alphabetic string."
            )

        if side not in VALID_SIDES:
            raise ValueError(
                f"Invalid side '{side}': must be one of {sorted(VALID_SIDES)}."
            )

        if order_type not in VALID_ORDER_TYPES:
            raise ValueError(
                f"Invalid order type '{order_type}': "
                f"must be one of {sorted(VALID_ORDER_TYPES)}."
            )

        # Quantity must be a positive number.
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError(
                f"Invalid quantity '{quantity}': must be a positive number."
            )

        # LIMIT orders require a positive price.
        if order_type == "LIMIT":
            has_price = price is not None and isinstance(price, (int, float))
            if not has_price or price <= 0:
                raise ValueError(
                    "LIMIT orders require a positive --price value."
                )

        # STOP_MARKET orders require a positive stop price.
        if order_type == "STOP_MARKET":
            has_stop_price = (
                stop_price is not None and isinstance(stop_price, (int, float))
            )
            if not has_stop_price or stop_price <= 0:
                raise ValueError(
                    "STOP_MARKET orders require a positive --stop_price value."
                )
