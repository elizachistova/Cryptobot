import datetime
from typing import Optional
from pydantic import BaseModel

# Technical indicators sub-model
class Indicator(BaseModel):
    BB_MA: float
    BB_UPPER: float
    BB_LOWER: float
    RSI: float
    DOJI: int
    HAMMER: int
    SHOOTING_STAR: int

# Main Model
class MarketData(BaseModel):
    symbol: str
    last_updated: datetime.datetime
    rows: int
    openTime: datetime.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trend: int
    volume_price_ratio: float
    indicator: Indicator

# Models updates
class UpdateIndicator(BaseModel):
    BB_MA: Optional[float]
    BB_UPPER: Optional[float]
    BB_LOWER: Optional[float]
    RSI: Optional[float]
    DOJI: Optional[int]
    HAMMER: Optional[int]
    SHOOTING_STAR: Optional[int]


class UpdateMarketData(BaseModel):
    symbol: Optional[str]
    last_updated: Optional[datetime.datetime]
    rows: Optional[int]
    openTime: Optional[datetime.datetime]
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    volume: Optional[float]
    trend: Optional[int]
    volume_price_ratio: Optional[float]
    indicator: UpdateIndicator

class PredictionRequest(BaseModel):
    symbol: str
    interval_hours: int = 4

