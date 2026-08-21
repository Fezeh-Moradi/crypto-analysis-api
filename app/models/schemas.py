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
    signal_score: int
    signal_reason: str
    support: Optional[float] = None
    resistance: Optional[float] = None
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


class PositionSizeRequest(BaseModel):
    account_balance: float
    risk_percent: float
    entry_price: float
    stop_loss_price: float


class PositionSizeResponse(BaseModel):
    account_balance: float
    risk_percent: float
    risk_amount: float
    entry_price: float
    stop_loss_price: float
    stop_loss_percent: float
    position_size: float
    position_value: float