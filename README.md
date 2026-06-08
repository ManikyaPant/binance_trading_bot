# Binance Futures Testnet Trading Bot

A simplified command-line trading bot for the **Binance Futures Testnet (USDT-M)**.

## Features

- **Order types**: MARKET, LIMIT, and STOP_MARKET
- **Sides**: BUY and SELL
- **Input validation**: All parameters are validated before reaching the API
- **HMAC-SHA256 authentication**: Requests are signed per the Binance specification
- **Rotating log files**: 1 MB limit, 3 backups via `RotatingFileHandler`
- **Clear CLI output**: Pre-flight summary, formatted response, success/failure messages

## Project Structure

```
trading_bot/
├── main.py               # CLI entry point (argparse)
├── requirements.txt      # Python dependencies
├── .env.example          # Template for API credentials
├── .gitignore
├── README.md
├── bot/
│   ├── __init__.py       # Package marker
│   ├── config.py         # Loads API keys from environment / .env file
│   ├── logging_config.py # Rotating file + stream handler setup
│   ├── client.py         # BinanceClient — signing, HTTP, error handling
│   ├── validators.py     # OrderValidator — input validation
│   └── orders.py         # OrderManager — builds params & delegates to client
└── tests/
    ├── __init__.py
    ├── test_validators.py  # Input validation tests
    ├── test_config.py      # Config loading tests
    ├── test_client.py      # HMAC signing & HTTP tests
    ├── test_orders.py      # Order building tests
    └── test_cli.py         # CLI argument parsing tests
```

## Setup

### 1. Clone and install dependencies

```bash
cd trading_bot
pip install -r requirements.txt
```

### 2. Configure API credentials

Copy the example environment file and fill in your **Testnet** API keys:

```bash
cp .env.example .env
# Edit .env with your keys from https://testnet.binancefuture.com
```

Alternatively, export them directly:

```bash
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"
```

## Usage

Run from within the `trading_bot/` directory:

```bash
# MARKET order
python main.py --symbol BTCUSDT --side BUY --order_type MARKET --quantity 0.001

# LIMIT order
python main.py --symbol ETHUSDT --side SELL --order_type LIMIT --quantity 0.5 --price 3200.00

# STOP_MARKET order
python main.py --symbol BTCUSDT --side SELL --order_type STOP_MARKET --quantity 0.001 --stop_price 95000
```

### CLI Arguments

| Argument       | Required | Description                                      |
|----------------|----------|--------------------------------------------------|
| `--symbol`     | Yes      | Trading pair, e.g. `BTCUSDT`                     |
| `--side`       | Yes      | `BUY` or `SELL`                                  |
| `--order_type` | Yes      | `MARKET`, `LIMIT`, or `STOP_MARKET`              |
| `--quantity`   | Yes      | Positive float                                   |
| `--price`      | LIMIT    | Positive float (required for LIMIT orders)       |
| `--stop_price` | STOP     | Positive float (required for STOP_MARKET orders) |

## Testing

The project includes 51 unit tests covering validators, config loading, HMAC signing,
HTTP calls (mocked), order building, and CLI argument parsing.

```bash
# Run all tests with verbose output
python -m unittest discover -s tests -v
```

No API keys or network access are required — all external calls are mocked.

## Error Handling

The bot handles these error categories with clear messages:

- **Validation errors**: Invalid symbol, side, order type, or missing required prices
- **Configuration errors**: Missing API key or secret
- **Network errors**: Timeouts, connection failures
- **API errors**: Non-200 responses from Binance (e.g. insufficient balance)

## Logging

Logs are written to both:
- **Console** (`stdout`): INFO level and above
- **File** (`trading_bot.log`): DEBUG level, rotating at 1 MB with 3 backups
