/**
 * StockSnow API Service
 * Handles all communication with the StockSnow backend API
 */

export interface LiveQuote {
  ticker: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  previous_close: number;
}

export interface TechnicalIndicators {
  ticker: string;
  timestamp: string;
  sma_20?: number;
  sma_50?: number;
  sma_200?: number;
  ema_12?: number;
  ema_26?: number;
  rsi?: number;
  macd?: number;
  macd_signal?: number;
  macd_histogram?: number;
  bollinger_upper?: number;
  bollinger_middle?: number;
  bollinger_lower?: number;
  volume_sma?: number;
  support_level?: number;
  resistance_level?: number;
}

export interface StockSnapshot {
  ticker: string;
  timestamp: string;
  quote: LiveQuote;
  technical_indicators?: TechnicalIndicators;
  sentiment?: any;
  news_summary?: string;
}

export interface WatchlistItem {
  ticker: string;
  added_at: string;
  notes?: string;
  target_price?: number;
}

export interface Watchlist {
  name: string;
  items: WatchlistItem[];
  created_at: string;
  updated_at: string;
}

export interface PriceAlert {
  ticker: string;
  alert_type: 'above' | 'below' | 'change_percent' | 'volume_spike';
  threshold: number;
  active: boolean;
  created_at: string;
  triggered_at?: string;
  message?: string;
}

const API_BASE_URL = 'http://localhost:8000';

export class StockSnowAPI {
  // Watchlist operations
  static async getWatchlists(): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/watchlists`);
    if (!response.ok) throw new Error('Failed to fetch watchlists');
    return response.json();
  }

  static async getWatchlist(name: string): Promise<Watchlist> {
    const response = await fetch(`${API_BASE_URL}/watchlists/${name}`);
    if (!response.ok) throw new Error(`Failed to fetch watchlist: ${name}`);
    return response.json();
  }

  static async createWatchlist(name: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/watchlists`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    if (!response.ok) throw new Error('Failed to create watchlist');
    return response.json();
  }

  static async deleteWatchlist(name: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/watchlists/${name}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete watchlist');
    return response.json();
  }

  static async addToWatchlist(
    watchlistName: string,
    ticker: string,
    notes?: string,
    targetPrice?: number
  ): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/watchlists/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        watchlist_name: watchlistName,
        ticker,
        notes,
        target_price: targetPrice,
      }),
    });
    if (!response.ok) throw new Error('Failed to add stock to watchlist');
    return response.json();
  }

  static async removeFromWatchlist(
    watchlistName: string,
    ticker: string
  ): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/watchlists/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        watchlist_name: watchlistName,
        ticker,
      }),
    });
    if (!response.ok) throw new Error('Failed to remove stock from watchlist');
    return response.json();
  }

  // Quote operations
  static async getQuote(ticker: string): Promise<StockSnapshot> {
    const response = await fetch(`${API_BASE_URL}/quotes/${ticker}`);
    if (!response.ok) throw new Error(`Failed to fetch quote for ${ticker}`);
    return response.json();
  }

  static async getAllQuotes(): Promise<StockSnapshot[]> {
    const response = await fetch(`${API_BASE_URL}/quotes`);
    if (!response.ok) throw new Error('Failed to fetch quotes');
    return response.json();
  }

  // Alert operations
  static async createAlert(
    ticker: string,
    alertType: 'above' | 'below' | 'change_percent' | 'volume_spike',
    threshold: number,
    message?: string
  ): Promise<{ message: string; alert: PriceAlert }> {
    const response = await fetch(`${API_BASE_URL}/alerts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ticker,
        alert_type: alertType,
        threshold,
        message,
      }),
    });
    if (!response.ok) throw new Error('Failed to create alert');
    return response.json();
  }

  static async getAlerts(ticker?: string): Promise<Record<string, PriceAlert[]>> {
    const url = ticker
      ? `${API_BASE_URL}/alerts?ticker=${ticker}`
      : `${API_BASE_URL}/alerts`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch alerts');
    return response.json();
  }

  // Health check
  static async healthCheck(): Promise<{
    status: string;
    monitor_initialized: boolean;
    monitored_tickers: number;
  }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  }
}
