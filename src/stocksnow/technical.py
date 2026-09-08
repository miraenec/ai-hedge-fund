"""Technical analysis for StockSnow."""

from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from .models import TechnicalIndicators


class TechnicalAnalyzer:
    """Calculates technical indicators for stocks."""
    
    @staticmethod
    def calculate_sma(prices: list[float], period: int) -> Optional[float]:
        """
        Calculate Simple Moving Average.
        
        Args:
            prices: List of prices (newest last)
            period: Number of periods
            
        Returns:
            SMA value or None if insufficient data
        """
        if len(prices) < period:
            return None
        return float(np.mean(prices[-period:]))
    
    @staticmethod
    def calculate_ema(prices: list[float], period: int) -> Optional[float]:
        """
        Calculate Exponential Moving Average.
        
        Args:
            prices: List of prices (newest last)
            period: Number of periods
            
        Returns:
            EMA value or None if insufficient data
        """
        if len(prices) < period:
            return None
        
        df = pd.DataFrame({'price': prices})
        ema = df['price'].ewm(span=period, adjust=False).mean()
        return float(ema.iloc[-1])
    
    @staticmethod
    def calculate_rsi(prices: list[float], period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index.
        
        Args:
            prices: List of prices (newest last)
            period: Number of periods (default 14)
            
        Returns:
            RSI value or None if insufficient data
        """
        if len(prices) < period + 1:
            return None
        
        # Calculate price changes
        deltas = np.diff(prices)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    @staticmethod
    def calculate_macd(prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: List of prices (newest last)
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)
            
        Returns:
            Tuple of (MACD, Signal, Histogram) or (None, None, None) if insufficient data
        """
        if len(prices) < slow + signal:
            return None, None, None
        
        df = pd.DataFrame({'price': prices})
        
        # Calculate EMAs
        ema_fast = df['price'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['price'].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return (
            float(macd_line.iloc[-1]),
            float(signal_line.iloc[-1]),
            float(histogram.iloc[-1])
        )
    
    @staticmethod
    def calculate_bollinger_bands(prices: list[float], period: int = 20, std_dev: float = 2.0) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: List of prices (newest last)
            period: Number of periods (default 20)
            std_dev: Number of standard deviations (default 2.0)
            
        Returns:
            Tuple of (Upper, Middle, Lower) bands or (None, None, None) if insufficient data
        """
        if len(prices) < period:
            return None, None, None
        
        recent_prices = prices[-period:]
        middle = float(np.mean(recent_prices))
        std = float(np.std(recent_prices))
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        return upper, middle, lower
    
    @staticmethod
    def calculate_support_resistance(prices: list[float], highs: list[float], lows: list[float], lookback: int = 20) -> tuple[Optional[float], Optional[float]]:
        """
        Calculate support and resistance levels.
        
        Args:
            prices: List of closing prices
            highs: List of high prices
            lows: List of low prices
            lookback: Number of periods to look back
            
        Returns:
            Tuple of (support, resistance) levels or (None, None) if insufficient data
        """
        if len(prices) < lookback or len(highs) < lookback or len(lows) < lookback:
            return None, None
        
        recent_highs = highs[-lookback:]
        recent_lows = lows[-lookback:]
        
        # Simple support/resistance using recent highs and lows
        resistance = float(np.max(recent_highs))
        support = float(np.min(recent_lows))
        
        return support, resistance
    
    def analyze(self, ticker: str, prices: list[float], highs: list[float], lows: list[float], volumes: list[float]) -> TechnicalIndicators:
        """
        Calculate all technical indicators.
        
        Args:
            ticker: Stock ticker symbol
            prices: List of closing prices (newest last)
            highs: List of high prices
            lows: List of low prices
            volumes: List of volumes
            
        Returns:
            TechnicalIndicators object with calculated values
        """
        # Calculate moving averages
        sma_20 = self.calculate_sma(prices, 20)
        sma_50 = self.calculate_sma(prices, 50)
        sma_200 = self.calculate_sma(prices, 200)
        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)
        
        # Calculate momentum indicators
        rsi = self.calculate_rsi(prices)
        macd, macd_signal, macd_histogram = self.calculate_macd(prices)
        
        # Calculate volatility
        bollinger_upper, bollinger_middle, bollinger_lower = self.calculate_bollinger_bands(prices)
        
        # Calculate volume average
        volume_sma = self.calculate_sma(volumes, 20) if volumes else None
        
        # Calculate support/resistance
        support_level, resistance_level = self.calculate_support_resistance(prices, highs, lows)
        
        return TechnicalIndicators(
            ticker=ticker,
            timestamp=datetime.now(),
            sma_20=sma_20,
            sma_50=sma_50,
            sma_200=sma_200,
            ema_12=ema_12,
            ema_26=ema_26,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            bollinger_upper=bollinger_upper,
            bollinger_middle=bollinger_middle,
            bollinger_lower=bollinger_lower,
            volume_sma=volume_sma,
            support_level=support_level,
            resistance_level=resistance_level
        )
