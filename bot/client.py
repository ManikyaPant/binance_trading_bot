"""Binance Futures Testnet REST client.

Handles authentication (HMAC SHA-256 signing) and HTTP communication with
the Binance Futures Testnet API. All order-related network calls flow
through the send_order method defined here.
"""

import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

BASE_URL = "https://testnet.binancefuture.com"
ORDER_ENDPOINT = "/fapi/v1/order"
DEFAULT_TIMEOUT = 10  # seconds

logger = logging.getLogger(__name__)


class BinanceClient:
    """Low-level REST client for Binance Futures Testnet."""

    def __init__(self, api_key: str, api_secret: str) -> None:
        """Initialise the client with API credentials.

        Args:
            api_key: Binance API key.
            api_secret: Binance API secret used for request signing.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self._time_offset = self._calculate_time_offset()

    def _calculate_time_offset(self) -> int:
        """Fetch Binance server time and return the offset in milliseconds.

        This avoids timestamp rejection when the local clock drifts from
        Binance's server clock by more than 1 000 ms.

        Returns:
            Offset in ms (server_time - local_time).
        """
        url = f"{BASE_URL}/fapi/v1/time"
        try:
            response = requests.get(url, timeout=DEFAULT_TIMEOUT)
            server_time = response.json()["serverTime"]
            local_time = int(time.time() * 1000)
            offset = server_time - local_time
            logger.debug("Server time offset: %d ms", offset)
            return offset
        except Exception as exc:
            logger.warning("Could not sync server time: %s. Using 0 offset.", exc)
            return 0

    def _sign_request(self, params: dict) -> dict:
        """Add a timestamp and HMAC-SHA256 signature to the params dict.

        Args:
            params: Existing request parameters (modified in place).

        Returns:
            The same params dict with 'timestamp' and 'signature' added.
        """
        params["timestamp"] = int(time.time() * 1000) + self._time_offset
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def send_order(self, params: dict) -> dict:
        """POST an order to the Binance Futures Testnet.

        Args:
            params: Order parameters (symbol, side, type, quantity, etc.).

        Returns:
            Parsed JSON response from Binance.

        Raises:
            RuntimeError: If the API returns a non-200 status code.
            ConnectionError: If the request fails due to network issues.
        """
        signed_params = self._sign_request(params.copy())

        # Mask signature in logs to avoid leaking secrets.
        masked_params = {
            key: ("***" if key == "signature" else value)
            for key, value in signed_params.items()
        }
        logger.info("Sending order request: %s", masked_params)

        url = f"{BASE_URL}{ORDER_ENDPOINT}"
        headers = {"X-MBX-APIKEY": self.api_key}

        try:
            response = requests.post(
                url,
                params=signed_params,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            logger.error("Request timed out after %s seconds", DEFAULT_TIMEOUT)
            raise ConnectionError(
                f"Request timed out after {DEFAULT_TIMEOUT} seconds. "
                "Please check your network and try again."
            )
        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection failed: %s", exc)
            raise ConnectionError(
                "Could not connect to Binance Futures Testnet. "
                "Please verify your network connection."
            ) from exc
        except requests.exceptions.RequestException as exc:
            logger.error("Unexpected request error: %s", exc)
            raise ConnectionError(
                f"Network error: {exc}"
            ) from exc

        logger.debug("Raw response [%s]: %s", response.status_code, response.text)

        if response.status_code != 200:
            error_body = response.text
            logger.error(
                "API error %s: %s", response.status_code, error_body
            )
            raise RuntimeError(
                f"Binance API error (HTTP {response.status_code}): {error_body}"
            )

        return response.json()
