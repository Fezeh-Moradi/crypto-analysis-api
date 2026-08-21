import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.services.market_data import MarketDataService


async def main():
    service = MarketDataService()

    print("=== Testing get_price ===")
    price = await service.get_price("BTC")
    print(f"Symbol: {price.symbol}")
    print(f"Price: {price.current_price}")
    print(f"24h Change: {price.price_change_percentage_24h}")
    print()

    print("=== Testing get_analysis ===")
    analysis = await service.get_analysis("ETH", days=60)
    print(f"Symbol: {analysis.symbol}")
    print(f"Current Price: {analysis.current_price}")
    print(f"RSI: {analysis.indicators.rsi_14}")
    print(f"SMA 20: {analysis.indicators.sma_20}")
    print(f"Signal: {analysis.signal}")
    print(f"Reason: {analysis.signal_reason}")
    print(f"Volatility: {analysis.volatility_30d}")
    print()

    print("=== Testing compare ===")
    comparison = await service.compare(["BTC", "ETH", "SOL"])
    for item in comparison.items:
        print(f"{item.symbol}: {item.current_price} | 24h: {item.price_change_percentage_24h}")


if __name__ == "__main__":
    asyncio.run(main())