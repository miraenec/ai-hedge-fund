"""Real-time data streaming for StockSnow."""

import asyncio
from datetime import datetime
from typing import Callable, Optional

import httpx

from .models import LiveQuote


class StockStreamer:
    """Streams real-time stock data."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.financialdatasets.ai"):
        """
        Initialize the stock streamer.
        
        Args:
            api_key: Financial Datasets API key
            base_url: Base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.subscribers: dict[str, list[Callable[[LiveQuote], None]]] = {}
        self.running = False
        self._tasks: list[asyncio.Task] = []
    
    def subscribe(self, ticker: str, callback: Callable[[LiveQuote], None]):
        """
        Subscribe to real-time updates for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            callback: Function to call with updates
        """
        ticker = ticker.upper()
        if ticker not in self.subscribers:
            self.subscribers[ticker] = []
        self.subscribers[ticker].append(callback)
    
    def unsubscribe(self, ticker: str, callback: Optional[Callable[[LiveQuote], None]] = None):
        """
        Unsubscribe from updates for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            callback: Specific callback to remove, or None to remove all
        """
        ticker = ticker.upper()
        if ticker not in self.subscribers:
            return
        
        if callback is None:
            del self.subscribers[ticker]
        else:
            self.subscribers[ticker] = [cb for cb in self.subscribers[ticker] if cb != callback]
            if not self.subscribers[ticker]:
                del self.subscribers[ticker]
    
    async def _fetch_quote(self, ticker: str) -> Optional[LiveQuote]:
        """
        Fetch current quote for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            LiveQuote or None if error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/prices/snapshot",
                    params={"ticker": ticker},
                    headers={"X-API-KEY": self.api_key},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                
                # Parse the response into LiveQuote
                # This is a simplified version - adjust based on actual API response
                if not data:
                    return None
                
                snapshot = data[0] if isinstance(data, list) else data
                
                return LiveQuote(
                    ticker=ticker,
                    price=snapshot.get("close", 0.0),
                    change=snapshot.get("close", 0.0) - snapshot.get("previous_close", 0.0),
                    change_percent=((snapshot.get("close", 0.0) - snapshot.get("previous_close", 1.0)) / snapshot.get("previous_close", 1.0)) * 100,
                    volume=snapshot.get("volume", 0),
                    timestamp=datetime.now(),
                    open=snapshot.get("open", 0.0),
                    high=snapshot.get("high", 0.0),
                    low=snapshot.get("low", 0.0),
                    previous_close=snapshot.get("previous_close", 0.0)
                )
        except Exception as e:
            print(f"Error fetching quote for {ticker}: {e}")
            return None
    
    async def _stream_ticker(self, ticker: str):
        """
        Stream updates for a ticker.
        
        Args:
            ticker: Stock ticker symbol
        """
        while self.running and ticker in self.subscribers:
            quote = await self._fetch_quote(ticker)
            
            if quote:
                # Notify all subscribers
                for callback in self.subscribers.get(ticker, []):
                    try:
                        callback(quote)
                    except Exception as e:
                        print(f"Error in subscriber callback for {ticker}: {e}")
            
            # Wait before next fetch (adjust interval as needed)
            await asyncio.sleep(5)  # Update every 5 seconds
    
    async def start(self):
        """Start streaming for all subscribed tickers."""
        self.running = True
        
        # Start a streaming task for each ticker
        for ticker in list(self.subscribers.keys()):
            task = asyncio.create_task(self._stream_ticker(ticker))
            self._tasks.append(task)
    
    async def stop(self):
        """Stop all streaming."""
        self.running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
    
    def get_subscribed_tickers(self) -> list[str]:
        """
        Get list of tickers currently subscribed.
        
        Returns:
            List of ticker symbols
        """
        return list(self.subscribers.keys())
