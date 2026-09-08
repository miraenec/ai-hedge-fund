"""Alert management for StockSnow."""

import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from .models import AlertType, PriceAlert, LiveQuote


class AlertManager:
    """Manages price alerts and notifications."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the alert manager.
        
        Args:
            storage_path: Path to store alert data. Defaults to ~/.stocksnow/alerts.json
        """
        if storage_path is None:
            storage_path = Path.home() / ".stocksnow" / "alerts.json"
        
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.alerts: dict[str, list[PriceAlert]] = {}  # ticker -> list of alerts
        self.notification_callbacks: list[Callable[[PriceAlert], None]] = []
        self._load()
    
    def add_alert(self, ticker: str, alert_type: AlertType, threshold: float, message: Optional[str] = None) -> PriceAlert:
        """
        Add a price alert.
        
        Args:
            ticker: Stock ticker symbol
            alert_type: Type of alert
            threshold: Price threshold or percentage
            message: Optional custom message
            
        Returns:
            The created alert
        """
        ticker = ticker.upper()
        alert = PriceAlert(
            ticker=ticker,
            alert_type=alert_type,
            threshold=threshold,
            message=message
        )
        
        if ticker not in self.alerts:
            self.alerts[ticker] = []
        
        self.alerts[ticker].append(alert)
        self._save()
        return alert
    
    def remove_alert(self, ticker: str, alert_index: int) -> bool:
        """
        Remove an alert by index.
        
        Args:
            ticker: Stock ticker symbol
            alert_index: Index of the alert to remove
            
        Returns:
            True if removed, False if not found
        """
        ticker = ticker.upper()
        if ticker not in self.alerts:
            return False
        
        if 0 <= alert_index < len(self.alerts[ticker]):
            self.alerts[ticker].pop(alert_index)
            if not self.alerts[ticker]:
                del self.alerts[ticker]
            self._save()
            return True
        return False
    
    def get_alerts(self, ticker: Optional[str] = None) -> dict[str, list[PriceAlert]]:
        """
        Get alerts for a ticker or all alerts.
        
        Args:
            ticker: Optional ticker to filter by
            
        Returns:
            Dictionary of ticker to alerts
        """
        if ticker is None:
            return self.alerts
        
        ticker = ticker.upper()
        return {ticker: self.alerts.get(ticker, [])}
    
    def check_alerts(self, quote: LiveQuote) -> list[PriceAlert]:
        """
        Check if any alerts should be triggered for a quote.
        
        Args:
            quote: Current stock quote
            
        Returns:
            List of triggered alerts
        """
        ticker = quote.ticker.upper()
        if ticker not in self.alerts:
            return []
        
        triggered = []
        
        for alert in self.alerts[ticker]:
            if not alert.active:
                continue
            
            should_trigger = False
            
            if alert.alert_type == AlertType.ABOVE:
                should_trigger = quote.price >= alert.threshold
            
            elif alert.alert_type == AlertType.BELOW:
                should_trigger = quote.price <= alert.threshold
            
            elif alert.alert_type == AlertType.CHANGE_PERCENT:
                should_trigger = abs(quote.change_percent) >= alert.threshold
            
            elif alert.alert_type == AlertType.VOLUME_SPIKE:
                # Volume spike is when current volume exceeds threshold multiple
                # This is a simplified implementation
                should_trigger = quote.volume >= alert.threshold
            
            if should_trigger:
                alert.triggered_at = datetime.now()
                alert.active = False  # Deactivate after triggering
                triggered.append(alert)
                self._notify(alert)
        
        if triggered:
            self._save()
        
        return triggered
    
    def register_notification_callback(self, callback: Callable[[PriceAlert], None]):
        """
        Register a callback to be called when an alert is triggered.
        
        Args:
            callback: Function to call with the triggered alert
        """
        self.notification_callbacks.append(callback)
    
    def _notify(self, alert: PriceAlert):
        """Notify all registered callbacks about a triggered alert."""
        for callback in self.notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Error in notification callback: {e}")
    
    def _load(self):
        """Load alerts from storage."""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.alerts = {
                    ticker: [PriceAlert.model_validate(alert_data) for alert_data in alerts]
                    for ticker, alerts in data.items()
                }
        except Exception as e:
            print(f"Error loading alerts: {e}")
            self.alerts = {}
    
    def _save(self):
        """Save alerts to storage."""
        try:
            data = {
                ticker: [alert.model_dump(mode='json') for alert in alerts]
                for ticker, alerts in self.alerts.items()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving alerts: {e}")
