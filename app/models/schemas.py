from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PriceResponse(BaseModel):
    symbol: str
    name: str
    current_price: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    last_updated: datetime


class IndicatorValues(BaseModel):
    rsi_14: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None


class AnalysisResponse(BaseModel):
    symbol: str
    current_price: float
    indicators: IndicatorValues
    signal: str
    signal_reason: str
    volatility_30d: Optional[float] = None
    last_updated: datetime


class CompareItem(BaseModel):
    symbol: str
    current_price: float
    price_change_percentage_24h: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None


class CompareResponse(BaseModel):
    items: List[CompareItem]
    compared_at: datetime