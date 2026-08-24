from pydantic import BaseModel , Field
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
    atr_14: Optional[float] = None
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
    atr_14: float = Field(..., gt=0, description="ATR 14-period")


class PositionSizeResponse(BaseModel):
    account_balance: float
    risk_percent: float
    risk_amount: float
    entry_price: float
    stop_loss_price: float
    stop_loss_percent: float
    position_size: float
    position_value: float
    atr_based_stop_loss_percent: float


class TrailingStopRequest(BaseModel):
    entry_price: float
    current_price: float
    atr_14: float
    side: str = Field(..., description="long or short")
    multiplier: float = Field(1.5, ge=0.5, le=5.0, description="ATR multiplier (default 1.5)")


class TrailingStopResponse(BaseModel):
    entry_price: float
    current_price: float
    side: str
    atr_14: float
    multiplier: float
    initial_stop_loss: float
    trailing_stop_loss: float
    distance_percent: float
    is_profitable: bool
    recommendation: str



class TradeIdeaRequest(BaseModel):
    symbol: str
    account_balance: float = 1000
    risk_percent: float = 1.0


class TradeIdeaResponse(BaseModel):
    symbol: str
    current_price: float
    signal: str
    signal_score: int
    signal_reason: str
    support: Optional[float] = None
    resistance: Optional[float] = None
    atr_14: Optional[float] = None
    suggested_stop_loss: Optional[float] = None
    suggested_take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    position_size: Optional[float] = None
    position_value: Optional[float] = None
    recommendation: str
    last_updated: datetime