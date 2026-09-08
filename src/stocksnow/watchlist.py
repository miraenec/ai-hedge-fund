"""Watchlist management for StockSnow."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import Watchlist, WatchlistItem


class WatchlistManager:
    """Manages stock watchlists."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the watchlist manager.
        
        Args:
            storage_path: Path to store watchlist data. Defaults to ~/.stocksnow/watchlists.json
        """
        if storage_path is None:
            storage_path = Path.home() / ".stocksnow" / "watchlists.json"
        
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.watchlists: dict[str, Watchlist] = {}
        self._load()
    
    def create_watchlist(self, name: str) -> Watchlist:
        """
        Create a new watchlist.
        
        Args:
            name: Name of the watchlist
            
        Returns:
            The created watchlist
            
        Raises:
            ValueError: If watchlist with this name already exists
        """
        if name in self.watchlists:
            raise ValueError(f"Watchlist '{name}' already exists")
        
        watchlist = Watchlist(name=name)
        self.watchlists[name] = watchlist
        self._save()
        return watchlist
    
    def get_watchlist(self, name: str) -> Optional[Watchlist]:
        """
        Get a watchlist by name.
        
        Args:
            name: Name of the watchlist
            
        Returns:
            The watchlist or None if not found
        """
        return self.watchlists.get(name)
    
    def list_watchlists(self) -> list[str]:
        """
        List all watchlist names.
        
        Returns:
            List of watchlist names
        """
        return list(self.watchlists.keys())
    
    def delete_watchlist(self, name: str) -> bool:
        """
        Delete a watchlist.
        
        Args:
            name: Name of the watchlist to delete
            
        Returns:
            True if deleted, False if not found
        """
        if name in self.watchlists:
            del self.watchlists[name]
            self._save()
            return True
        return False
    
    def add_stock(self, watchlist_name: str, ticker: str, notes: Optional[str] = None, target_price: Optional[float] = None) -> bool:
        """
        Add a stock to a watchlist.
        
        Args:
            watchlist_name: Name of the watchlist
            ticker: Stock ticker symbol
            notes: Optional notes about the stock
            target_price: Optional target price
            
        Returns:
            True if added successfully
            
        Raises:
            ValueError: If watchlist not found or stock already in watchlist
        """
        watchlist = self.watchlists.get(watchlist_name)
        if watchlist is None:
            raise ValueError(f"Watchlist '{watchlist_name}' not found")
        
        # Check if already exists
        if any(item.ticker.upper() == ticker.upper() for item in watchlist.items):
            raise ValueError(f"Stock '{ticker}' already in watchlist '{watchlist_name}'")
        
        item = WatchlistItem(
            ticker=ticker.upper(),
            notes=notes,
            target_price=target_price
        )
        watchlist.items.append(item)
        watchlist.updated_at = datetime.now()
        self._save()
        return True
    
    def remove_stock(self, watchlist_name: str, ticker: str) -> bool:
        """
        Remove a stock from a watchlist.
        
        Args:
            watchlist_name: Name of the watchlist
            ticker: Stock ticker symbol
            
        Returns:
            True if removed, False if not found
        """
        watchlist = self.watchlists.get(watchlist_name)
        if watchlist is None:
            return False
        
        ticker = ticker.upper()
        original_count = len(watchlist.items)
        watchlist.items = [item for item in watchlist.items if item.ticker != ticker]
        
        if len(watchlist.items) < original_count:
            watchlist.updated_at = datetime.now()
            self._save()
            return True
        return False
    
    def get_all_tickers(self) -> set[str]:
        """
        Get all unique tickers across all watchlists.
        
        Returns:
            Set of all ticker symbols
        """
        tickers = set()
        for watchlist in self.watchlists.values():
            for item in watchlist.items:
                tickers.add(item.ticker)
        return tickers
    
    def _load(self):
        """Load watchlists from storage."""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.watchlists = {
                    name: Watchlist.model_validate(wl_data)
                    for name, wl_data in data.items()
                }
        except Exception as e:
            print(f"Error loading watchlists: {e}")
            self.watchlists = {}
    
    def _save(self):
        """Save watchlists to storage."""
        try:
            data = {
                name: watchlist.model_dump(mode='json')
                for name, watchlist in self.watchlists.items()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving watchlists: {e}")
