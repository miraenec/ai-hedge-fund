"""Main monitoring interface for StockSnow."""

import asyncio
from datetime import datetime
from typing import Optional

from .alerts import AlertManager
from .models import LiveQuote, StockSnapshot, TechnicalIndicators
from .streaming import StockStreamer
from .technical import TechnicalAnalyzer
from .watchlist import WatchlistManager


class StockMonitor:
    """
    Main interface for stock monitoring.
    
    Integrates watchlists, alerts, streaming data, and technical analysis.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the stock monitor.
        
        Args:
            api_key: Financial Datasets API key
        """
        self.api_key = api_key
        self.watchlist_manager = WatchlistManager()
        self.alert_manager = AlertManager()
        self.streamer = StockStreamer(api_key)
        self.technical_analyzer = TechnicalAnalyzer()
        
        # Store historical data for technical analysis
        self.price_history: dict[str, list[float]] = {}
        self.high_history: dict[str, list[float]] = {}
        self.low_history: dict[str, list[float]] = {}
        self.volume_history: dict[str, list[float]] = {}
        
        # Store latest quotes
        self.latest_quotes: dict[str, LiveQuote] = {}
        
        # Set up alert notification
        self.alert_manager.register_notification_callback(self._on_alert_triggered)
    
    def _on_quote_update(self, quote: LiveQuote):
        """
        Handle quote updates from streamer.
        
        Args:
            quote: Updated quote
        """
        ticker = quote.ticker
        
        # Store latest quote
        self.latest_quotes[ticker] = quote
        
        # Update price history
        if ticker not in self.price_history:
            self.price_history[ticker] = []
            self.high_history[ticker] = []
            self.low_history[ticker] = []
            self.volume_history[ticker] = []
        
        self.price_history[ticker].append(quote.price)
        self.high_history[ticker].append(quote.high)
        self.low_history[ticker].append(quote.low)
        self.volume_history[ticker].append(float(quote.volume))
        
        # Keep only last 200 data points for efficiency
        max_history = 200
        if len(self.price_history[ticker]) > max_history:
            self.price_history[ticker] = self.price_history[ticker][-max_history:]
            self.high_history[ticker] = self.high_history[ticker][-max_history:]
            self.low_history[ticker] = self.low_history[ticker][-max_history:]
            self.volume_history[ticker] = self.volume_history[ticker][-max_history:]
        
        # Check alerts
        self.alert_manager.check_alerts(quote)
    
    def _on_alert_triggered(self, alert):
        """
        Handle triggered alerts.
        
        Args:
            alert: Triggered alert
        """
        print(f"\n🔔 ALERT TRIGGERED: {alert.ticker}")
        print(f"   Type: {alert.alert_type.value}")
        print(f"   Threshold: {alert.threshold}")
        if alert.message:
            print(f"   Message: {alert.message}")
        print(f"   Time: {alert.triggered_at}")
    
    def add_to_watchlist(self, watchlist_name: str, ticker: str, notes: Optional[str] = None, target_price: Optional[float] = None):
        """
        Add a stock to a watchlist and start monitoring it.
        
        Args:
            watchlist_name: Name of the watchlist
            ticker: Stock ticker symbol
            notes: Optional notes
            target_price: Optional target price
        """
        # Create watchlist if it doesn't exist
        if self.watchlist_manager.get_watchlist(watchlist_name) is None:
            self.watchlist_manager.create_watchlist(watchlist_name)
        
        # Add to watchlist
        self.watchlist_manager.add_stock(watchlist_name, ticker, notes, target_price)
        
        # Subscribe to streaming updates
        self.streamer.subscribe(ticker, self._on_quote_update)
    
    def remove_from_watchlist(self, watchlist_name: str, ticker: str):
        """
        Remove a stock from a watchlist.
        
        Args:
            watchlist_name: Name of the watchlist
            ticker: Stock ticker symbol
        """
        self.watchlist_manager.remove_stock(watchlist_name, ticker)
        
        # Check if ticker is in any other watchlist
        all_tickers = self.watchlist_manager.get_all_tickers()
        if ticker.upper() not in all_tickers:
            # Not in any watchlist, stop monitoring
            self.streamer.unsubscribe(ticker)
    
    def create_alert(self, ticker: str, alert_type: str, threshold: float, message: Optional[str] = None):
        """
        Create a price alert for a stock.
        
        Args:
            ticker: Stock ticker symbol
            alert_type: Type of alert (above, below, change_percent, volume_spike)
            threshold: Threshold value
            message: Optional custom message
        """
        from .models import AlertType
        alert_type_enum = AlertType(alert_type)
        return self.alert_manager.add_alert(ticker, alert_type_enum, threshold, message)
    
    def get_snapshot(self, ticker: str) -> Optional[StockSnapshot]:
        """
        Get a complete snapshot of a stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            StockSnapshot or None if not available
        """
        ticker = ticker.upper()
        quote = self.latest_quotes.get(ticker)
        
        if quote is None:
            return None
        
        # Calculate technical indicators if we have enough history
        technical_indicators = None
        if ticker in self.price_history and len(self.price_history[ticker]) >= 20:
            technical_indicators = self.technical_analyzer.analyze(
                ticker,
                self.price_history[ticker],
                self.high_history[ticker],
                self.low_history[ticker],
                self.volume_history[ticker]
            )
        
        return StockSnapshot(
            ticker=ticker,
            timestamp=datetime.now(),
            quote=quote,
            technical_indicators=technical_indicators
        )
    
    def get_all_snapshots(self) -> list[StockSnapshot]:
        """
        Get snapshots for all monitored stocks.
        
        Returns:
            List of stock snapshots
        """
        snapshots = []
        for ticker in self.latest_quotes.keys():
            snapshot = self.get_snapshot(ticker)
            if snapshot:
                snapshots.append(snapshot)
        return snapshots
    
    async def start_monitoring(self):
        """Start monitoring all stocks in watchlists."""
        # Subscribe to all tickers in all watchlists
        all_tickers = self.watchlist_manager.get_all_tickers()
        for ticker in all_tickers:
            self.streamer.subscribe(ticker, self._on_quote_update)
        
        # Start streaming
        await self.streamer.start()
    
    async def stop_monitoring(self):
        """Stop monitoring all stocks."""
        await self.streamer.stop()
    
    def get_watchlists(self):
        """Get all watchlists."""
        return self.watchlist_manager.list_watchlists()
    
    def get_watchlist(self, name: str):
        """Get a specific watchlist."""
        return self.watchlist_manager.get_watchlist(name)
