# Crypto Analysis API

This project provides real-time price data, technical indicators, trading signals, support/resistance levels, and position size calculation to help with manual trading decisions.

## Features

- Real-time price data (CoinGecko)
- Technical Indicators: RSI, SMA, EMA, MACD
- Advanced trading signals with score (`STRONG_BUY`, `BUY`, `HOLD`, `SELL`, `STRONG_SELL`)
- Support & Resistance levels
- Position Size Calculator (Risk Management)
- Multi-coin comparison
- Simple in-memory caching

## Tech Stack

- Python 3.11+
- FastAPI
- Pandas + `ta` library
- httpx
- Pydantic
- cachetools

## Project Structure

```text
app/
├── api/            # API routes
├── core/           # External clients (CoinGecko)
├── models/         # Pydantic schemas
├── services/       # Business logic (analysis, risk, market data)
└── main.py         # Application entry point
```

## Installation

```bash
git clone https://github.com/Fezeh-Moradi/crypto-analysis-api.git
cd crypto-analysis-api

python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open the interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/price/{symbol}` | Get current price |
| GET | `/api/v1/analysis/{symbol}` | Full technical analysis + signal |
| GET | `/api/v1/compare` | Compare multiple coins |
| POST | `/api/v1/position-size` | Calculate position size |

### Example: Position Size

```http
POST /api/v1/position-size
```

```json
{
  "account_balance": 1000,
  "risk_percent": 1,
  "entry_price": 77000,
  "stop_loss_price": 75500
}
```

## Notes

- This project is designed for **manual trading assistance**, not automated trading.
- Data is provided by CoinGecko (free tier).
- Always do your own research before making trading decisions.

## License

MIT