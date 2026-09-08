# StockSnow - Real-time Stock Monitoring System

StockSnow is a comprehensive real-time stock monitoring and analysis system that provides:

- 📊 **Real-time stock quotes** - Live price updates for your watchlist
- 🔔 **Price alerts** - Get notified when stocks hit your targets
- 📋 **Watchlist management** - Organize stocks into custom watchlists
- 🔧 **Technical analysis** - RSI, MACD, moving averages, Bollinger Bands, and more
- 📈 **Support/Resistance levels** - Automatic calculation of key price levels
- 🖥️ **Multiple interfaces** - CLI dashboard, REST API, and Python library

## Features

### Watchlist Management
- Create multiple watchlists for different trading strategies
- Add notes and target prices for each stock
- Automatic monitoring of all stocks in your watchlists

### Real-time Monitoring
- Live price updates every 5 seconds
- Volume tracking and spike detection
- Historical data collection for technical analysis

### Price Alerts
- **Above/Below alerts** - Get notified when price crosses a threshold
- **Percentage change alerts** - Track significant price movements
- **Volume spike alerts** - Detect unusual trading activity
- Customizable alert messages

### Technical Analysis
- **Moving Averages**: SMA (20, 50, 200), EMA (12, 26)
- **Momentum Indicators**: RSI, MACD with signal and histogram
- **Volatility**: Bollinger Bands
- **Support & Resistance**: Automatic level detection
- **Volume Analysis**: Volume moving averages

## Installation

The StockSnow module is included in the AI Hedge Fund project. Make sure you have all dependencies installed:

```bash
poetry install
```

## Usage

### Quick Start

#### 1. Set up API Key

Make sure you have your Financial Datasets API key in your `.env` file:

```bash
FINANCIAL_DATASETS_API_KEY=your-api-key-here
```

#### 2. Using the CLI

Run the interactive dashboard:

```bash
poetry run python -m src.stocksnow.cli
```

This will:
1. Ask you which stocks to monitor
2. Set up optional price alerts
3. Show a live dashboard with quotes, technical indicators, and alerts

#### 3. Using the Python API

```python
import asyncio
from src.stocksnow import StockMonitor

async def main():
    # Initialize monitor
    monitor = StockMonitor(api_key="your-api-key")
    
    # Create a watchlist and add stocks
    monitor.add_to_watchlist("tech_stocks", "AAPL", notes="Apple Inc.", target_price=200.0)
    monitor.add_to_watchlist("tech_stocks", "MSFT", notes="Microsoft")
    monitor.add_to_watchlist("tech_stocks", "GOOGL", notes="Google")
    
    # Create price alerts
    monitor.create_alert("AAPL", "above", 180.0, "Apple hit target!")
    monitor.create_alert("MSFT", "below", 350.0, "Microsoft dip")
    
    # Start monitoring
    await monitor.start_monitoring()
    
    # Let it run for a while
    await asyncio.sleep(60)
    
    # Get snapshots
    snapshot = monitor.get_snapshot("AAPL")
    print(f"AAPL: ${snapshot.quote.price:.2f}")
    print(f"RSI: {snapshot.technical_indicators.rsi:.1f}")
    
    # Stop monitoring
    await monitor.stop_monitoring()

asyncio.run(main())
```

#### 4. Using the REST API

Start the API server:

```bash
poetry run python -m src.stocksnow.api
```

The API will be available at `http://localhost:8000`. View the interactive docs at `http://localhost:8000/docs`.

#### Example API Calls

Create a watchlist:
```bash
curl -X POST http://localhost:8000/watchlists \
  -H "Content-Type: application/json" \
  -d '{"name": "my_stocks"}'
```

Add a stock to watchlist:
```bash
curl -X POST http://localhost:8000/watchlists/add \
  -H "Content-Type: application/json" \
  -d '{
    "watchlist_name": "my_stocks",
    "ticker": "AAPL",
    "notes": "Apple Inc.",
    "target_price": 200.0
  }'
```

Get live quote:
```bash
curl http://localhost:8000/quotes/AAPL
```

Create price alert:
```bash
curl -X POST http://localhost:8000/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "alert_type": "above",
    "threshold": 180.0,
    "message": "Apple hit $180!"
  }'
```

## Architecture

### Components

1. **StockMonitor** - Main orchestrator that integrates all components
2. **WatchlistManager** - Manages watchlists and persists them to disk
3. **AlertManager** - Handles price alerts and notifications
4. **StockStreamer** - Streams real-time price data from API
5. **TechnicalAnalyzer** - Calculates technical indicators

### Data Flow

```
Financial Datasets API
         ↓
   StockStreamer (fetches every 5s)
         ↓
   StockMonitor (updates quotes & history)
         ↓
   ┌────┴────┐
   ↓         ↓
AlertManager  TechnicalAnalyzer
   ↓         ↓
Notifications  Technical Indicators
```

### Storage

- Watchlists are stored in `~/.stocksnow/watchlists.json`
- Alerts are stored in `~/.stocksnow/alerts.json`
- Price history is kept in memory (last 200 data points per ticker)

## API Reference

### StockMonitor

Main interface for stock monitoring.

```python
monitor = StockMonitor(api_key: str)
```

Methods:
- `add_to_watchlist(watchlist_name, ticker, notes=None, target_price=None)`
- `remove_from_watchlist(watchlist_name, ticker)`
- `create_alert(ticker, alert_type, threshold, message=None)`
- `get_snapshot(ticker) -> StockSnapshot`
- `get_all_snapshots() -> list[StockSnapshot]`
- `async start_monitoring()`
- `async stop_monitoring()`

### WatchlistManager

Manages stock watchlists.

```python
manager = WatchlistManager(storage_path=None)
```

Methods:
- `create_watchlist(name) -> Watchlist`
- `get_watchlist(name) -> Watchlist`
- `delete_watchlist(name) -> bool`
- `add_stock(watchlist_name, ticker, notes=None, target_price=None)`
- `remove_stock(watchlist_name, ticker) -> bool`
- `get_all_tickers() -> set[str]`

### AlertManager

Manages price alerts.

```python
manager = AlertManager(storage_path=None)
```

Methods:
- `add_alert(ticker, alert_type, threshold, message=None) -> PriceAlert`
- `remove_alert(ticker, alert_index) -> bool`
- `get_alerts(ticker=None) -> dict[str, list[PriceAlert]]`
- `check_alerts(quote) -> list[PriceAlert]`
- `register_notification_callback(callback)`

### TechnicalAnalyzer

Calculates technical indicators.

```python
analyzer = TechnicalAnalyzer()
```

Methods:
- `calculate_sma(prices, period) -> float`
- `calculate_ema(prices, period) -> float`
- `calculate_rsi(prices, period=14) -> float`
- `calculate_macd(prices, fast=12, slow=26, signal=9) -> tuple`
- `calculate_bollinger_bands(prices, period=20, std_dev=2.0) -> tuple`
- `calculate_support_resistance(prices, highs, lows, lookback=20) -> tuple`
- `analyze(ticker, prices, highs, lows, volumes) -> TechnicalIndicators`

## Alert Types

- `above` - Trigger when price goes above threshold
- `below` - Trigger when price goes below threshold
- `change_percent` - Trigger when price changes by percentage
- `volume_spike` - Trigger when volume exceeds threshold

## Technical Indicators

All indicators are calculated automatically when you have sufficient price history (minimum 20 data points):

- **SMA 20/50/200** - Simple moving averages
- **EMA 12/26** - Exponential moving averages (used in MACD)
- **RSI** - Relative Strength Index (14 period)
  - > 70: Overbought
  - < 30: Oversold
- **MACD** - Moving Average Convergence Divergence
  - MACD line, Signal line, Histogram
- **Bollinger Bands** - Volatility bands (20 period, 2 std dev)
- **Support/Resistance** - Based on recent highs and lows (20 period)

## Examples

### Example 1: Basic Monitoring

```python
import asyncio
from src.stocksnow import StockMonitor

async def monitor_tech_stocks():
    monitor = StockMonitor(api_key="your-key")
    
    # Add tech stocks
    for ticker in ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]:
        monitor.add_to_watchlist("tech", ticker)
    
    # Start monitoring
    await monitor.start_monitoring()
    
    # Run for 5 minutes
    for _ in range(60):
        await asyncio.sleep(5)
        snapshots = monitor.get_all_snapshots()
        for s in snapshots:
            print(f"{s.ticker}: ${s.quote.price:.2f} ({s.quote.change_percent:+.2f}%)")
    
    await monitor.stop_monitoring()

asyncio.run(monitor_tech_stocks())
```

### Example 2: Advanced Alerts

```python
import asyncio
from src.stocksnow import StockMonitor

async def advanced_alerts():
    monitor = StockMonitor(api_key="your-key")
    
    # Add stock
    monitor.add_to_watchlist("momentum", "NVDA", target_price=500.0)
    
    # Multiple alert types
    monitor.create_alert("NVDA", "above", 500.0, "NVDA hit target!")
    monitor.create_alert("NVDA", "below", 400.0, "NVDA support broken")
    monitor.create_alert("NVDA", "change_percent", 5.0, "NVDA big move!")
    
    # Custom notification handler
    def my_notification(alert):
        print(f"🚨 ALERT: {alert.ticker} - {alert.message}")
        # Send email, SMS, push notification, etc.
    
    monitor.alert_manager.register_notification_callback(my_notification)
    
    await monitor.start_monitoring()
    await asyncio.sleep(300)  # 5 minutes
    await monitor.stop_monitoring()

asyncio.run(advanced_alerts())
```

### Example 3: Technical Analysis

```python
import asyncio
from src.stocksnow import StockMonitor

async def technical_analysis():
    monitor = StockMonitor(api_key="your-key")
    
    monitor.add_to_watchlist("analysis", "AAPL")
    
    await monitor.start_monitoring()
    
    # Wait for data to accumulate
    await asyncio.sleep(120)
    
    snapshot = monitor.get_snapshot("AAPL")
    ti = snapshot.technical_indicators
    
    if ti:
        print(f"\n📊 {snapshot.ticker} Technical Analysis")
        print(f"Price: ${snapshot.quote.price:.2f}")
        print(f"\nMoving Averages:")
        print(f"  SMA 20:  ${ti.sma_20:.2f}")
        print(f"  SMA 50:  ${ti.sma_50:.2f}" if ti.sma_50 else "  SMA 50:  N/A")
        print(f"  SMA 200: ${ti.sma_200:.2f}" if ti.sma_200 else "  SMA 200: N/A")
        print(f"\nMomentum:")
        print(f"  RSI:  {ti.rsi:.1f}")
        print(f"  MACD: {ti.macd:.2f}")
        print(f"\nLevels:")
        print(f"  Support:    ${ti.support_level:.2f}")
        print(f"  Resistance: ${ti.resistance_level:.2f}")
    
    await monitor.stop_monitoring()

asyncio.run(technical_analysis())
```

## Integration with AI Hedge Fund

StockSnow can be integrated with the AI Hedge Fund to provide real-time monitoring of portfolio positions:

```python
from src.stocksnow import StockMonitor
from v2.fund import Fund

async def monitor_fund(fund: Fund):
    monitor = StockMonitor(api_key="your-key")
    
    # Add all fund positions to watchlist
    for ticker in fund.positions.keys():
        monitor.add_to_watchlist("fund_positions", ticker)
    
    await monitor.start_monitoring()
    
    # Monitor in background while fund runs
    # ...
```

## Troubleshooting

### No data appearing
- Check that your `FINANCIAL_DATASETS_API_KEY` is set correctly
- Verify the API key has access to real-time data
- Check your internet connection

### Alerts not triggering
- Ensure alerts are marked as `active: true`
- Check that the threshold values are correct
- Verify the alert type matches your expectation

### Technical indicators showing N/A
- Technical indicators require at least 20 data points
- Wait a few minutes after starting monitoring
- Some indicators (SMA 50, SMA 200) require more data

## Performance Notes

- Real-time updates occur every 5 seconds
- Price history is limited to last 200 data points per ticker
- Each ticker makes one API call every 5 seconds
- For many tickers, consider implementing rate limiting

## Future Enhancements

- [ ] WebSocket support for true real-time streaming
- [ ] More technical indicators (Stochastic, ADX, etc.)
- [ ] Chart visualization
- [ ] Backtesting with historical alerts
- [ ] Mobile app
- [ ] Email/SMS notifications
- [ ] Integration with more data providers
- [ ] Machine learning price predictions
- [ ] Options chain monitoring

## License

This module is part of the AI Hedge Fund project and follows the same MIT License.

## Support

For issues or questions, please open an issue on the main AI Hedge Fund repository.
