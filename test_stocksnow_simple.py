"""Simple test runner for StockSnow without pytest."""

import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, '/workspace')

from src.stocksnow.models import AlertType, PriceAlert, WatchlistItem, Watchlist, LiveQuote
from src.stocksnow.watchlist import WatchlistManager
from src.stocksnow.alerts import AlertManager
from src.stocksnow.technical import TechnicalAnalyzer


def test_watchlist_manager():
    """Test WatchlistManager."""
    print("\n" + "="*60)
    print("Testing WatchlistManager")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = WatchlistManager(Path(tmpdir) / "watchlists.json")
        
        # Test create watchlist
        wl = manager.create_watchlist("test")
        assert wl.name == "test"
        assert len(wl.items) == 0
        print("✓ Create watchlist")
        
        # Test add stock
        manager.add_stock("test", "AAPL", notes="Apple Inc.", target_price=200.0)
        wl = manager.get_watchlist("test")
        assert len(wl.items) == 1
        assert wl.items[0].ticker == "AAPL"
        print("✓ Add stock to watchlist")
        
        # Test remove stock
        manager.add_stock("test", "MSFT")
        manager.remove_stock("test", "AAPL")
        wl = manager.get_watchlist("test")
        assert len(wl.items) == 1
        assert wl.items[0].ticker == "MSFT"
        print("✓ Remove stock from watchlist")
        
        # Test get all tickers
        manager.create_watchlist("tech")
        manager.add_stock("tech", "GOOGL")
        tickers = manager.get_all_tickers()
        assert "MSFT" in tickers and "GOOGL" in tickers
        print("✓ Get all tickers")
        
    print("✅ WatchlistManager tests passed")


def test_alert_manager():
    """Test AlertManager."""
    print("\n" + "="*60)
    print("Testing AlertManager")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = AlertManager(Path(tmpdir) / "alerts.json")
        
        # Test add alert
        alert = manager.add_alert("AAPL", AlertType.ABOVE, 180.0, "Test alert")
        assert alert.ticker == "AAPL"
        assert alert.alert_type == AlertType.ABOVE
        assert alert.threshold == 180.0
        print("✓ Add alert")
        
        # Test get alerts
        manager.add_alert("AAPL", AlertType.BELOW, 150.0)
        manager.add_alert("MSFT", AlertType.ABOVE, 400.0)
        all_alerts = manager.get_alerts()
        assert len(all_alerts) == 2
        assert len(all_alerts["AAPL"]) == 2
        print("✓ Get alerts")
        
        # Test check alert
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
        assert triggered[0].active is False
        print("✓ Check and trigger alert")
        
    print("✅ AlertManager tests passed")


def test_technical_analyzer():
    """Test TechnicalAnalyzer."""
    print("\n" + "="*60)
    print("Testing TechnicalAnalyzer")
    print("="*60)
    
    analyzer = TechnicalAnalyzer()
    
    # Test SMA
    prices = [100, 102, 101, 103, 105, 104, 106, 108]
    sma = analyzer.calculate_sma(prices, 5)
    assert sma is not None
    assert 103 < sma < 106
    print("✓ Calculate SMA")
    
    # Test EMA
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 112]
    ema = analyzer.calculate_ema(prices, 5)
    assert ema is not None
    print("✓ Calculate EMA")
    
    # Test RSI
    prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114]
    rsi = analyzer.calculate_rsi(prices, 14)
    assert rsi is not None
    assert 50 < rsi <= 100
    print("✓ Calculate RSI")
    
    # Test MACD
    prices = list(range(100, 150))
    macd, signal, histogram = analyzer.calculate_macd(prices)
    assert macd is not None
    assert signal is not None
    assert histogram is not None
    print("✓ Calculate MACD")
    
    # Test Bollinger Bands
    prices = [100] * 10 + [105] * 10
    upper, middle, lower = analyzer.calculate_bollinger_bands(prices, 20)
    assert upper is not None and middle is not None and lower is not None
    assert upper > middle > lower
    print("✓ Calculate Bollinger Bands")
    
    # Test complete analysis
    prices = list(range(100, 150))
    highs = [p + 2 for p in prices]
    lows = [p - 2 for p in prices]
    volumes = [1000000] * 50
    indicators = analyzer.analyze("AAPL", prices, highs, lows, volumes)
    assert indicators.ticker == "AAPL"
    assert indicators.sma_20 is not None
    assert indicators.rsi is not None
    print("✓ Complete analysis")
    
    print("✅ TechnicalAnalyzer tests passed")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("StockSnow Simple Test Suite")
    print("="*60)
    
    try:
        test_watchlist_manager()
        test_alert_manager()
        test_technical_analyzer()
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60 + "\n")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
