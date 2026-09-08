"""Data models for StockSnow feature."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """Types of price alerts."""
    ABOVE = "above"
    BELOW = "below"
    CHANGE_PERCENT = "change_percent"
    VOLUME_SPIKE = "volume_spike"


class PriceAlert(BaseModel):
    """Price alert configuration."""
    ticker: str
    alert_type: AlertType
    threshold: float
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    triggered_at: Optional[datetime] = None
    message: Optional[str] = None


class WatchlistItem(BaseModel):
    """Item in a watchlist."""
    ticker: str
    added_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    target_price: Optional[float] = None


class Watchlist(BaseModel):
    """A watchlist containing multiple stocks."""
    name: str
    items: list[WatchlistItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LiveQuote(BaseModel):
    """Real-time stock quote data."""
    ticker: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    open: float
    high: float
    low: float
    previous_close: float


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators."""
    ticker: str
    timestamp: datetime
    
    # Moving averages
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    
    # Momentum indicators
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    
    # Volatility
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    
    # Volume
    volume_sma: Optional[float] = None
    
    # Support/Resistance
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None


class MarketSentiment(BaseModel):
    """Market sentiment analysis for a stock."""
    ticker: str
    timestamp: datetime
    sentiment_score: float  # -1 to 1
    news_count: int
    positive_mentions: int
    negative_mentions: int
    neutral_mentions: int
    trending: bool = False


class StockSnapshot(BaseModel):
    """Complete snapshot of stock data."""
    ticker: str
    timestamp: datetime
    quote: LiveQuote
    technical_indicators: Optional[TechnicalIndicators] = None
    sentiment: Optional[MarketSentiment] = None
    news_summary: Optional[str] = None
