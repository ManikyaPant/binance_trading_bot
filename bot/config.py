"""Configuration loader for the trading bot.

Reads API credentials from environment variables or a .env file so that
secrets are never hard-coded in source.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Required environment variables for Binance Futures Testnet.
_REQUIRED_VARS = ("BINANCE_API_KEY", "BINANCE_API_SECRET")


def _load_dotenv(path: str = ".env") -> None:
    """Read a .env file and inject key=value pairs into os.environ.

    This is a minimal implementation that avoids an external dependency on
    python-dotenv.  Lines starting with '#' and blank lines are skipped.

    Args:
        path: Path to the .env file.  Defaults to '.env' in the current
              working directory.
    """
    if not os.path.isfile(path):
        return

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            os.environ.setdefault(key, value)


def load_config() -> dict:
    """Return a dict with validated API credentials.

    The function first attempts to load a .env file, then reads the two
    required environment variables.

    Returns:
        A dict with keys 'api_key' and 'api_secret'.

    Raises:
        EnvironmentError: If either required variable is missing or empty.
    """
    _load_dotenv()

    missing = [var for var in _REQUIRED_VARS if not os.environ.get(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Set them in your shell or in a .env file."
        )

    config = {
        "api_key": os.environ["BINANCE_API_KEY"],
        "api_secret": os.environ["BINANCE_API_SECRET"],
    }

    logger.debug(
        "Loaded API key: %s...%s",
        config["api_key"][:4],
        config["api_key"][-4:],
    )
    return config
