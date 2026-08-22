from datetime import datetime, timezone
from cachetools import TTLCache
from app.core.clients.coingecko import CoinGeckoClient
from app.services.analysis import TechnicalAnalyzer
from app.models.schemas import (
    PriceResponse,
    AnalysisResponse,
    CompareItem,
    CompareResponse,
)
from app.config import get_settings
from loguru import logger
import pandas as pd

settings = get_settings()
cache = TTLCache(maxsize=100, ttl=settings.CACHE_TTL)

SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "LINK": "chainlink",
}


class MarketDataService:
    def __init__(self):
        self.client = CoinGeckoClient()

    def _get_coin_id(self, symbol: str) -> str:
        return SYMBOL_TO_ID.get(symbol.upper(), symbol.lower())

    async def get_price(self, symbol: str) -> PriceResponse:
        cache_key = f"price:{symbol.upper()}"
        if cache_key in cache:
            return cache[cache_key]

        coin_id = self._get_coin_id(symbol)
        data = await self.client.get_price(coin_id)

        if not data:
            raise ValueError(f"No data found for {symbol}")

        result = PriceResponse(
            symbol=symbol.upper(),
            name=coin_id,
            current_price=data.get("usd", 0),
            market_cap=data.get("usd_market_cap"),
            volume_24h=data.get("usd_24h_vol"),
            price_change_percentage_24h=data.get("usd_24h_change"),
            last_updated=datetime.now(timezone.utc),
        )
        cache[cache_key] = result
        return result

    async def get_analysis(self, symbol: str, days: int = 60) -> AnalysisResponse:
        cache_key = f"analysis:{symbol.upper()}:{days}"
        if cache_key in cache:
            return cache[cache_key]

        coin_id = self._get_coin_id(symbol)
        chart = await self.client.get_market_chart(coin_id, days=days)

        prices = [p[1] for p in chart.get("prices", [])]
        if len(prices) < 30:
            raise ValueError("Not enough historical data")

        analyzer = TechnicalAnalyzer(prices)
        indicators = analyzer.calculate_all()
        current_price = prices[-1]
        signal, reason, score = analyzer.generate_signal(indicators, current_price)
        support, resistance = analyzer.find_support_resistance()
        atr = analyzer.calculate_atr()
        returns = pd.Series(prices).pct_change().dropna()
        volatility = float(returns.std() * (365 ** 0.5) * 100)

        result = AnalysisResponse(
            symbol=symbol.upper(),
            current_price=round(current_price, 4),
            indicators=indicators,
            signal=signal,
            signal_score=score,
            signal_reason=reason,
            support=support,
            resistance=resistance,
            atr_14=atr,
            volatility_30d=round(volatility, 2),
            last_updated=datetime.now(timezone.utc),
        )
        cache[cache_key] = result
        return result

    async def compare(self, symbols: list[str]) -> CompareResponse:
        items = []
        for symbol in symbols:
            try:
                price_data = await self.get_price(symbol)
                items.append(
                    CompareItem(
                        symbol=price_data.symbol,
                        current_price=price_data.current_price,
                        price_change_percentage_24h=price_data.price_change_percentage_24h,
                        market_cap=price_data.market_cap,
                        volume_24h=price_data.volume_24h,
                    )
                )
            except Exception as e:
                logger.warning(f"Error comparing {symbol}: {e}")
                continue

        return CompareResponse(items=items, compared_at=datetime.now(timezone.utc))