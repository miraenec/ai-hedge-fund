"""Tests for StockSnow module."""

import asyncio
from datetime import datetime
from pathlib import Path
import tempfile
import pytest

from src.stocksnow.models import (
    AlertType,
    PriceAlert,
    WatchlistItem,
    Watchlist,
    LiveQuote,
    TechnicalIndicators,
)
from src.stocksnow.watchlist import WatchlistManager
from src.stocksnow.alerts import AlertManager
from src.stocksnow.technical import TechnicalAnalyzer


class TestWatchlistManager:
    """Tests for WatchlistManager."""
    
    def test_create_watchlist(self):
        """Test creating a watchlist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WatchlistManager(Path(tmpdir) / "watchlists.json")
            
            wl = manager.create_watchlist("test")
            assert wl.name == "test"
            assert len(wl.items) == 0
            assert "test" in manager.list_watchlists()
    
    def test_create_duplicate_watchlist(self):
        """Test that creating duplicate watchlist raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WatchlistManager(Path(tmpdir) / "watchlists.json")
            
            manager.create_watchlist("test")
            with pytest.raises(ValueError):
                manager.create_watchlist("test")
    
    def test_add_stock(self):
        """Test adding a stock to watchlist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WatchlistManager(Path(tmpdir) / "watchlists.json")
            
            manager.create_watchlist("tech")
            manager.add_stock("tech", "AAPL", notes="Apple Inc.", target_price=200.0)
            
            wl = manager.get_watchlist("tech")
            assert len(wl.items) == 1
            assert wl.items[0].ticker == "AAPL"
            assert wl.items[0].notes == "Apple Inc."
            assert wl.items[0].target_price == 200.0
    
    def test_add_duplicate_stock(self):
        """Test that adding duplicate stock raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WatchlistManager(Path(tmpdir) / "watchlists.json")
            
            manager.create_watchlist("tech")
            manager.add_stock("tech", "AAPL")
            
            with pytest.raises(ValueError):
                manager.add_stock("tech", "AAPL")
    
    def test_remove_stock(self):
        """Test removing a stock from watchlist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WatchlistManager(Path(tmpdir) / "watchlists.json")
            
            manager.create_watchlist("tech")
            manager.add_stock("tech", "AAPL")
            manager.add_stock("tech", "MSFT")
            
            assert manager.remove_stock("tech", "AAPL") is True
            
            wl = manager.get_watchlist("tech")
            assert len(wl.items) == 1
            assert wl.items[0].ticker == "MSFT"
    
    def test_get_all_tickers(self):
        """Test getting all tickers across watchlists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WatchlistManager(Path(tmpdir) / "watchlists.json")
            
            manager.create_watchlist("tech")
            manager.add_stock("tech", "AAPL")
            manager.add_stock("tech", "MSFT")
            
            manager.create_watchlist("finance")
            manager.add_stock("finance", "JPM")
            manager.add_stock("finance", "BAC")
            
            tickers = manager.get_all_tickers()
            assert tickers == {"AAPL", "MSFT", "JPM", "BAC"}
    
    def test_persistence(self):
        """Test that watchlists persist to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "watchlists.json"
            
            # Create and save
            manager1 = WatchlistManager(storage_path)
            manager1.create_watchlist("tech")
            manager1.add_stock("tech", "AAPL")
            
            # Load in new instance
            manager2 = WatchlistManager(storage_path)
            wl = manager2.get_watchlist("tech")
            assert wl is not None
            assert len(wl.items) == 1
            assert wl.items[0].ticker == "AAPL"


class TestAlertManager:
    """Tests for AlertManager."""
    
    def test_add_alert(self):
        """Test adding an alert."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(Path(tmpdir) / "alerts.json")
            
            alert = manager.add_alert("AAPL", AlertType.ABOVE, 180.0, "Test alert")
            
            assert alert.ticker == "AAPL"
            assert alert.alert_type == AlertType.ABOVE
            assert alert.threshold == 180.0
            assert alert.message == "Test alert"
            assert alert.active is True
    
    def test_get_alerts(self):
        """Test getting alerts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(Path(tmpdir) / "alerts.json")
            
            manager.add_alert("AAPL", AlertType.ABOVE, 180.0)
            manager.add_alert("AAPL", AlertType.BELOW, 150.0)
            manager.add_alert("MSFT", AlertType.ABOVE, 400.0)
            
            # Get all alerts
            all_alerts = manager.get_alerts()
            assert len(all_alerts) == 2
            assert len(all_alerts["AAPL"]) == 2
            assert len(all_alerts["MSFT"]) == 1
            
            # Get ticker-specific alerts
            aapl_alerts = manager.get_alerts("AAPL")
            assert len(aapl_alerts["AAPL"]) == 2
    
    def test_check_alert_above(self):
        """Test checking alert above threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(Path(tmpdir) / "alerts.json")
            
            manager.add_alert("AAPL", AlertType.ABOVE, 180.0)
            
            quote = LiveQuote(
                ticker="AAPL",
                price=185.0,
                change=5.0,
                change_percent=2.78,
                volume=100000,
                timestamp=datetime.now(),
                open=180.0,
                high=186.0,
                low=179.0,
                previous_close=180.0
            )
            
            triggered = manager.check_alerts(quote)
            assert len(triggered) == 1
            assert triggered[0].ticker == "AAPL"
            assert triggered[0].active is False  # Should be deactivated
    
    def test_check_alert_below(self):
        """Test checking alert below threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(Path(tmpdir) / "alerts.json")
            
            manager.add_alert("AAPL", AlertType.BELOW, 150.0)
            
            quote = LiveQuote(
                ticker="AAPL",
                price=145.0,
                change=-5.0,
                change_percent=-3.33,
                volume=100000,
                timestamp=datetime.now(),
                open=150.0,
                high=151.0,
                low=144.0,
                previous_close=150.0
            )
            
            triggered = manager.check_alerts(quote)
            assert len(triggered) == 1
    
    def test_alert_notification_callback(self):
        """Test alert notification callbacks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AlertManager(Path(tmpdir) / "alerts.json")
            
            triggered_alerts = []
            
            def callback(alert):
                triggered_alerts.append(alert)
            
            manager.register_notification_callback(callback)
            manager.add_alert("AAPL", AlertType.ABOVE, 180.0)
            
            quote = LiveQuote(
                ticker="AAPL",
                price=185.0,
                change=5.0,
                change_percent=2.78,
                volume=100000,
                timestamp=datetime.now(),
                open=180.0,
                high=186.0,
                low=179.0,
                previous_close=180.0
            )
            
            manager.check_alerts(quote)
            assert len(triggered_alerts) == 1
            assert triggered_alerts[0].ticker == "AAPL"


class TestTechnicalAnalyzer:
    """Tests for TechnicalAnalyzer."""
    
    def test_calculate_sma(self):
        """Test SMA calculation."""
        analyzer = TechnicalAnalyzer()
        prices = [100, 102, 101, 103, 105, 104, 106, 108]
        
        sma = analyzer.calculate_sma(prices, 5)
        assert sma is not None
        assert 103 < sma < 106  # Should be around 104.6
    
    def test_calculate_sma_insufficient_data(self):
        """Test SMA with insufficient data."""
        analyzer = TechnicalAnalyzer()
        prices = [100, 102, 101]
        
        sma = analyzer.calculate_sma(prices, 5)
        assert sma is None
    
    def test_calculate_ema(self):
        """Test EMA calculation."""
        analyzer = TechnicalAnalyzer()
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 112]
        
        ema = analyzer.calculate_ema(prices, 5)
        assert ema is not None
        assert ema > prices[-1] * 0.9  # Sanity check
    
    def test_calculate_rsi(self):
        """Test RSI calculation."""
        analyzer = TechnicalAnalyzer()
        # Uptrend prices
        prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114]
        
        rsi = analyzer.calculate_rsi(prices, 14)
        assert rsi is not None
        assert 50 < rsi <= 100  # Uptrend should have RSI > 50
    
    def test_calculate_macd(self):
        """Test MACD calculation."""
        analyzer = TechnicalAnalyzer()
        prices = list(range(100, 150))  # Uptrend
        
        macd, signal, histogram = analyzer.calculate_macd(prices)
        assert macd is not None
        assert signal is not None
        assert histogram is not None
    
    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        analyzer = TechnicalAnalyzer()
        prices = [100] * 10 + [105] * 10  # Stable then jump
        
        upper, middle, lower = analyzer.calculate_bollinger_bands(prices, 20)
        assert upper is not None
        assert middle is not None
        assert lower is not None
        assert upper > middle > lower
    
    def test_calculate_support_resistance(self):
        """Test support/resistance calculation."""
        analyzer = TechnicalAnalyzer()
        prices = [100, 102, 98, 103, 99, 104, 100, 105]
        highs = [101, 103, 99, 104, 100, 105, 101, 106]
        lows = [99, 101, 97, 102, 98, 103, 99, 104]
        
        support, resistance = analyzer.calculate_support_resistance(prices, highs, lows, 8)
        assert support is not None
        assert resistance is not None
        assert resistance > support
    
    def test_analyze_complete(self):
        """Test complete analysis."""
        analyzer = TechnicalAnalyzer()
        
        # Generate sample data
        prices = list(range(100, 150))
        highs = [p + 2 for p in prices]
        lows = [p - 2 for p in prices]
        volumes = [1000000] * 50
        
        indicators = analyzer.analyze("AAPL", prices, highs, lows, volumes)
        
        assert indicators.ticker == "AAPL"
        assert indicators.sma_20 is not None
        assert indicators.ema_12 is not None
        assert indicators.rsi is not None
        assert indicators.macd is not None
        assert indicators.bollinger_upper is not None
        assert indicators.support_level is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
