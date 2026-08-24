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



    async def get_trade_idea(self, symbol: str, account_balance: float = 1000, risk_percent: float = 1.0) -> dict:
        analysis = await self.get_analysis(symbol)

        current_price = analysis.current_price
        atr = analysis.atr_14 or 0
        support = analysis.support
        resistance = analysis.resistance
        signal = analysis.signal
        score = analysis.signal_score

        suggested_stop_loss = None
        suggested_take_profit = None
        risk_reward_ratio = None
        position_size = None
        position_value = None
        recommendation = "No clear trade idea. Wait for better setup."

        if signal in ["BUY", "STRONG_BUY"] and atr > 0:
            suggested_stop_loss = round(current_price - (atr * 1.5), 4)
            suggested_take_profit = round(current_price + (atr * 3), 4)
            risk = current_price - suggested_stop_loss
            reward = suggested_take_profit - current_price
            risk_reward_ratio = round(reward / risk, 2) if risk > 0 else None

            risk_amount = account_balance * (risk_percent / 100)
            position_size = round(risk_amount / risk, 6) if risk > 0 else None
            position_value = round(position_size * current_price, 2) if position_size else None

            recommendation = "Consider LONG. Risk/Reward looks acceptable." if risk_reward_ratio and risk_reward_ratio >= 1.5 else "LONG signal exists but Risk/Reward is weak."

        elif signal in ["SELL", "STRONG_SELL"] and atr > 0:
            suggested_stop_loss = round(current_price + (atr * 1.5), 4)
            suggested_take_profit = round(current_price - (atr * 3), 4)
            risk = suggested_stop_loss - current_price
            reward = current_price - suggested_take_profit
            risk_reward_ratio = round(reward / risk, 2) if risk > 0 else None

            risk_amount = account_balance * (risk_percent / 100)
            position_size = round(risk_amount / risk, 6) if risk > 0 else None
            position_value = round(position_size * current_price, 2) if position_size else None

            recommendation = "Consider SHORT. Risk/Reward looks acceptable." if risk_reward_ratio and risk_reward_ratio >= 1.5 else "SHORT signal exists but Risk/Reward is weak."

        return {
            "symbol": analysis.symbol,
            "current_price": current_price,
            "signal": signal,
            "signal_score": score,
            "signal_reason": analysis.signal_reason,
            "support": support,
            "resistance": resistance,
            "atr_14": atr,
            "suggested_stop_loss": suggested_stop_loss,
            "suggested_take_profit": suggested_take_profit,
            "risk_reward_ratio": risk_reward_ratio,
            "position_size": position_size,
            "position_value": position_value,
            "recommendation": recommendation,
            "last_updated": analysis.last_updated,
        }