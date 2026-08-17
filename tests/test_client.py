import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.clients.coingecko import CoinGeckoClient


async def main():
    client = CoinGeckoClient()

    print("Testing price endpoint...")
    price_data = await client.get_price("bitcoin")
    print("Price data:", price_data)

    print("\nTesting market chart...")
    chart_data = await client.get_market_chart("bitcoin", days=7)
    print("Number of price points:", len(chart_data.get("prices", [])))
    print("First price point:", chart_data.get("prices", [])[0] if chart_data.get("prices") else None)


if __name__ == "__main__":
    asyncio.run(main())