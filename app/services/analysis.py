import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
from app.models.schemas import IndicatorValues
from typing import Optional


class TechnicalAnalyzer:
    def __init__(self, prices: list[float]):
        self.df = pd.DataFrame({"close": prices})

    def calculate_all(self) -> IndicatorValues:
        close = self.df["close"]

        rsi = RSIIndicator(close=close, window=14).rsi().iloc[-1]
        sma_20 = SMAIndicator(close=close, window=20).sma_indicator().iloc[-1]
        sma_50 = SMAIndicator(close=close, window=50).sma_indicator().iloc[-1] if len(close) >= 50 else None
        ema_12 = EMAIndicator(close=close, window=12).ema_indicator().iloc[-1]
        ema_26 = EMAIndicator(close=close, window=26).ema_indicator().iloc[-1]

        macd_ind = MACD(close=close)
        macd = macd_ind.macd().iloc[-1]
        macd_signal = macd_ind.macd_signal().iloc[-1]
        macd_hist = macd_ind.macd_diff().iloc[-1]

        return IndicatorValues(
            rsi_14=round(float(rsi), 2) if not np.isnan(rsi) else None,
            sma_20=round(float(sma_20), 4) if not np.isnan(sma_20) else None,
            sma_50=round(float(sma_50), 4) if sma_50 is not None and not np.isnan(sma_50) else None,
            ema_12=round(float(ema_12), 4) if not np.isnan(ema_12) else None,
            ema_26=round(float(ema_26), 4) if not np.isnan(ema_26) else None,
            macd=round(float(macd), 4) if not np.isnan(macd) else None,
            macd_signal=round(float(macd_signal), 4) if not np.isnan(macd_signal) else None,
            macd_hist=round(float(macd_hist), 4) if not np.isnan(macd_hist) else None,
        )


    def find_support_resistance(self, window: int = 10) -> tuple[float | None, float | None]:
        if len(self.df) < window * 2:
            return None, None

        closes = self.df["close"].values
        recent = closes[-window*3:]

        resistance = float(max(recent[-window:]))
        support = float(min(recent[-window:]))

        if resistance - support < (resistance * 0.005):
            return None, None

        return round(support, 4), round(resistance, 4)



    def calculate_atr(self, window: int = 14) -> Optional[float]:
        if len(self.df) < window + 1:
            return None

        high = self.df["high"].values if "high" in self.df.columns else self.df["close"] * 1.01
        low = self.df["low"].values if "low" in self.df.columns else self.df["close"] * 0.99

        tr = np.maximum.reduce([
            high - low,
            np.abs(high - self.df["close"].shift(1).values),
            np.abs(low - self.df["close"].shift(1).values)
        ])

        atr = pd.Series(tr).rolling(window=window).mean().iloc[-1]
        return round(float(atr), 4) if not np.isnan(atr) else None

    def generate_signal(self, indicators: IndicatorValues, current_price: float) -> tuple[str, str, int]:
        reasons = []
        short_score = 0
        medium_score = 0

        # ===== Short-term (RSI + MACD) =====
        if indicators.rsi_14 is not None:
            if indicators.rsi_14 < 30:
                short_score += 2
                reasons.append("RSI oversold")
            elif indicators.rsi_14 < 40:
                short_score += 1
                reasons.append("RSI near oversold")
            elif indicators.rsi_14 > 70:
                short_score -= 2
                reasons.append("RSI overbought")
            elif indicators.rsi_14 > 60:
                short_score -= 1
                reasons.append("RSI near overbought")

        if indicators.macd is not None and indicators.macd_signal is not None:
            if indicators.macd > indicators.macd_signal and indicators.macd_hist is not None and indicators.macd_hist > 0:
                short_score += 2
                reasons.append("MACD strong bullish")
            elif indicators.macd > indicators.macd_signal:
                short_score += 1
                reasons.append("MACD bullish")
            elif indicators.macd < indicators.macd_signal and indicators.macd_hist is not None and indicators.macd_hist < 0:
                short_score -= 2
                reasons.append("MACD strong bearish")
            else:
                short_score -= 1
                reasons.append("MACD bearish")

        # ===== Medium-term (SMA + EMA) =====
        if indicators.sma_20 is not None:
            if current_price > indicators.sma_20:
                medium_score += 1
                reasons.append("Price above SMA20")
            else:
                medium_score -= 1
                reasons.append("Price below SMA20")

        if indicators.sma_50 is not None:
            if current_price > indicators.sma_50:
                medium_score += 1
                reasons.append("Price above SMA50")
            else:
                medium_score -= 1
                reasons.append("Price below SMA50")

        if indicators.ema_12 is not None and indicators.ema_26 is not None:
            if indicators.ema_12 > indicators.ema_26:
                medium_score += 1
                reasons.append("EMA12 above EMA26")
            else:
                medium_score -= 1
                reasons.append("EMA12 below EMA26")

        # ===== Final decision with Multi-Timeframe confirmation =====
        total_score = short_score + medium_score

        # Both sides bullish
        if short_score >= 2 and medium_score >= 1:
            signal = "STRONG_BUY"
        # Both sides bearish
        elif short_score <= -2 and medium_score <= -1:
            signal = "STRONG_SELL"
        # Only short-term strong
        elif short_score >= 2:
            signal = "BUY"
        elif short_score <= -2:
            signal = "SELL"
        # Weak / mixed
        elif total_score >= 2:
            signal = "BUY"
        elif total_score <= -2:
            signal = "SELL"
        else:
            signal = "HOLD"

        reason_text = " | ".join(reasons) if reasons else "Neutral conditions"
        return signal, reason_text, total_score