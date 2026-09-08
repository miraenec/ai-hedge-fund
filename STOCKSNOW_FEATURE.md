# StockSnow Feature Documentation

## Overview

StockSnow is a comprehensive real-time stock monitoring and analysis system that has been added to the AI Hedge Fund project. It provides live stock quotes, price alerts, watchlist management, and technical analysis capabilities.

## 🎯 Key Features

### Real-time Monitoring
- Live stock price updates every 5 seconds
- Volume tracking and historical data collection
- Support for monitoring multiple stocks simultaneously

### Watchlist Management
- Create and manage multiple watchlists
- Add notes and target prices for each stock
- Organize stocks by strategy, sector, or any custom grouping

### Price Alerts
- **Above/Below Alerts**: Get notified when price crosses thresholds
- **Percentage Change Alerts**: Track significant price movements
- **Volume Spike Alerts**: Detect unusual trading activity
- Custom notification messages

### Technical Analysis
- **Moving Averages**: SMA (20, 50, 200), EMA (12, 26)
- **Momentum Indicators**: RSI (14), MACD with signal and histogram
- **Volatility**: Bollinger Bands (20 period, 2 std dev)
- **Support & Resistance**: Automatic level detection
- **Volume Analysis**: Volume moving averages

### Multiple Interfaces
- **CLI Dashboard**: Rich terminal UI with live updates
- **REST API**: FastAPI-based web service
- **Python Library**: Direct programmatic access

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have:
- Python 3.11+
- Poetry installed
- Financial Datasets API key (get one at https://financialdatasets.ai/)

### 2. Installation

```bash
# Install dependencies (if not already done)
poetry install

# Verify StockSnow CLI is available
poetry run stocksnow --help
```

### 3. Configuration

Add your API key to `.env`:

```bash
FINANCIAL_DATASETS_API_KEY=your-api-key-here
```

### 4. Run the CLI

```bash
# Interactive CLI with dashboard
poetry run stocksnow

# Or use the Python module directly
poetry run python -m src.stocksnow.cli
```

### 5. Run the API Server

```bash
# Start the FastAPI server
poetry run python -m src.stocksnow.api

# Access the API at http://localhost:8000
# View docs at http://localhost:8000/docs
```

### 6. Run the Demo

```bash
# Comprehensive demo of all features
poetry run python examples/stocksnow_demo.py
```

## 📚 Usage Examples

### Example 1: Basic Monitoring (Python)

```python
import asyncio
from src.stocksnow import StockMonitor

async def monitor_stocks():
    # Initialize
    monitor = StockMonitor(api_key="your-key")
    
    # Add stocks
    monitor.add_to_watchlist("tech", "AAPL", notes="Apple")
    monitor.add_to_watchlist("tech", "MSFT", notes="Microsoft")
    
    # Start monitoring
    await monitor.start_monitoring()
    await asyncio.sleep(60)  # Monitor for 1 minute
    
    # Get data
    snapshot = monitor.get_snapshot("AAPL")
    print(f"AAPL: ${snapshot.quote.price:.2f}")
    
    await monitor.stop_monitoring()

asyncio.run(monitor_stocks())
```

### Example 2: Price Alerts

```python
import asyncio
from src.stocksnow import StockMonitor

async def setup_alerts():
    monitor = StockMonitor(api_key="your-key")
    
    # Add stock
    monitor.add_to_watchlist("momentum", "NVDA")
    
    # Create alerts
    monitor.create_alert("NVDA", "above", 500.0, "NVDA hit target!")
    monitor.create_alert("NVDA", "below", 400.0, "NVDA support broken!")
    monitor.create_alert("NVDA", "change_percent", 5.0, "Big move!")
    
    await monitor.start_monitoring()
    await asyncio.sleep(300)  # Monitor for 5 minutes
    await monitor.stop_monitoring()

asyncio.run(setup_alerts())
```

### Example 3: Technical Analysis

```python
import asyncio
from src.stocksnow import StockMonitor

async def analyze_stock():
    monitor = StockMonitor(api_key="your-key")
    monitor.add_to_watchlist("analysis", "AAPL")
    
    await monitor.start_monitoring()
    await asyncio.sleep(120)  # Wait for data
    
    snapshot = monitor.get_snapshot("AAPL")
    ti = snapshot.technical_indicators
    
    print(f"Price: ${snapshot.quote.price:.2f}")
    print(f"RSI: {ti.rsi:.1f}")
    print(f"MACD: {ti.macd:.2f}")
    print(f"Support: ${ti.support_level:.2f}")
    print(f"Resistance: ${ti.resistance_level:.2f}")
    
    await monitor.stop_monitoring()

asyncio.run(analyze_stock())
```

### Example 4: REST API Usage

```bash
# Create watchlist
curl -X POST http://localhost:8000/watchlists \
  -H "Content-Type: application/json" \
  -d '{"name": "tech_stocks"}'

# Add stock
curl -X POST http://localhost:8000/watchlists/add \
  -H "Content-Type: application/json" \
  -d '{
    "watchlist_name": "tech_stocks",
    "ticker": "AAPL",
    "notes": "Apple Inc.",
    "target_price": 200.0
  }'

# Get live quote
curl http://localhost:8000/quotes/AAPL

# Create alert
curl -X POST http://localhost:8000/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "alert_type": "above",
    "threshold": 180.0,
    "message": "Apple hit target!"
  }'

# Get all quotes
curl http://localhost:8000/quotes
```

## 🏗️ Architecture

### Components

```
StockSnow System
│
├── StockMonitor (Main orchestrator)
│   ├── WatchlistManager (Manages watchlists)
│   ├── AlertManager (Handles alerts)
│   ├── StockStreamer (Real-time data)
│   └── TechnicalAnalyzer (Technical indicators)
│
├── Data Models (Pydantic models)
│   ├── LiveQuote
│   ├── TechnicalIndicators
│   ├── Watchlist
│   └── PriceAlert
│
└── Interfaces
    ├── CLI (Rich terminal UI)
    ├── API (FastAPI REST)
    └── Python Library
```

### Data Flow

```
Financial Datasets API
        ↓
  StockStreamer (every 5s)
        ↓
  StockMonitor
   ├→ Update quotes
   ├→ Store history
   ├→ Check alerts → Notify
   └→ Calculate indicators
```

## 📁 File Structure

```
src/stocksnow/
├── __init__.py          # Package exports
├── models.py            # Data models
├── monitor.py           # Main StockMonitor class
├── watchlist.py         # Watchlist management
├── alerts.py            # Alert management
├── streaming.py         # Real-time data streaming
├── technical.py         # Technical analysis
├── cli.py              # CLI interface
├── api.py              # REST API
└── README.md           # Detailed documentation

tests/
└── test_stocksnow.py   # Test suite

examples/
└── stocksnow_demo.py   # Comprehensive demo
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
FINANCIAL_DATASETS_API_KEY=your-api-key

# Optional (defaults shown)
STOCKSNOW_UPDATE_INTERVAL=5        # Seconds between updates
STOCKSNOW_HISTORY_SIZE=200         # Max historical data points
```

### Storage Locations

- Watchlists: `~/.stocksnow/watchlists.json`
- Alerts: `~/.stocksnow/alerts.json`

## 🧪 Testing

Run the test suite:

```bash
# Run all StockSnow tests
poetry run pytest tests/test_stocksnow.py -v

# Run specific test
poetry run pytest tests/test_stocksnow.py::TestWatchlistManager -v

# Run with coverage
poetry run pytest tests/test_stocksnow.py --cov=src.stocksnow
```

## 🔗 Integration with AI Hedge Fund

StockSnow integrates seamlessly with the existing AI Hedge Fund:

### Monitor Portfolio Positions

```python
from src.stocksnow import StockMonitor
from v2.fund import Fund

async def monitor_fund_positions(fund: Fund):
    monitor = StockMonitor(api_key="your-key")
    
    # Monitor all fund positions
    for ticker in fund.positions.keys():
        monitor.add_to_watchlist("fund_positions", ticker)
    
    await monitor.start_monitoring()
    # ... monitoring logic
```

### Real-time Alerts for Hedge Fund

```python
# Set up alerts for portfolio positions
for ticker, position in fund.positions.items():
    # Alert if position moves 5%
    monitor.create_alert(
        ticker, 
        "change_percent", 
        5.0, 
        f"Position {ticker} significant move"
    )
```

### Technical Analysis for Trading Decisions

```python
# Use technical indicators in trading strategy
snapshot = monitor.get_snapshot(ticker)
if snapshot.technical_indicators:
    ti = snapshot.technical_indicators
    
    # Example: Use RSI for trading signals
    if ti.rsi < 30:  # Oversold
        # Consider buying
        pass
    elif ti.rsi > 70:  # Overbought
        # Consider selling
        pass
```

## 📊 Technical Indicators Reference

### RSI (Relative Strength Index)
- **Range**: 0-100
- **Overbought**: > 70
- **Oversold**: < 30
- **Period**: 14 days (default)

### MACD (Moving Average Convergence Divergence)
- **Components**: MACD line, Signal line, Histogram
- **Fast EMA**: 12 period
- **Slow EMA**: 26 period
- **Signal**: 9 period EMA of MACD

### Bollinger Bands
- **Middle**: 20-period SMA
- **Upper/Lower**: ± 2 standard deviations
- **Use**: Identify volatility and potential reversals

### Moving Averages
- **SMA 20**: Short-term trend
- **SMA 50**: Medium-term trend
- **SMA 200**: Long-term trend
- **Golden Cross**: SMA 50 crosses above SMA 200 (bullish)
- **Death Cross**: SMA 50 crosses below SMA 200 (bearish)

## 🎨 CLI Dashboard Features

The CLI dashboard provides:

- **Live Quotes Table**: Real-time prices with color-coded changes
- **Technical Indicators Table**: Key metrics at a glance
- **Watchlists Panel**: All your watchlists organized
- **Active Alerts Panel**: Current alert status
- **Auto-refresh**: Updates every second
- **Color coding**: Green for gains, red for losses

## 🌐 API Endpoints

### Watchlists
- `GET /watchlists` - List all watchlists
- `GET /watchlists/{name}` - Get specific watchlist
- `POST /watchlists` - Create watchlist
- `DELETE /watchlists/{name}` - Delete watchlist
- `POST /watchlists/add` - Add stock to watchlist
- `POST /watchlists/remove` - Remove stock from watchlist

### Quotes
- `GET /quotes/{ticker}` - Get quote for ticker
- `GET /quotes` - Get all quotes

### Alerts
- `GET /alerts` - Get all alerts
- `GET /alerts?ticker={ticker}` - Get alerts for ticker
- `POST /alerts` - Create alert

### Health
- `GET /health` - System health check
- `GET /` - API info

## 🚀 Performance Considerations

- Each monitored ticker makes 1 API call every 5 seconds
- Historical data limited to 200 points per ticker (about 16 minutes)
- Technical indicators cached per update cycle
- Watchlists and alerts persisted to disk on every change

## 🔮 Future Enhancements

Planned features:
- [ ] WebSocket support for true real-time streaming
- [ ] More technical indicators (Stochastic, ADX, Ichimoku)
- [ ] Chart visualization using matplotlib
- [ ] Email/SMS notifications via integrations
- [ ] Mobile app companion
- [ ] Options chain monitoring
- [ ] News sentiment analysis
- [ ] ML-based price predictions
- [ ] Portfolio backtesting with alerts

## 📝 License

StockSnow is part of the AI Hedge Fund project and is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Areas for contribution:
1. Additional technical indicators
2. New alert types
3. Improved visualization
4. Mobile app development
5. Integration with other data providers
6. Documentation improvements

## 📞 Support

For questions or issues:
1. Check the documentation in `src/stocksnow/README.md`
2. Run the demo: `poetry run python examples/stocksnow_demo.py`
3. Open an issue on GitHub with `[StockSnow]` prefix

## 🎓 Educational Use Only

Like the main AI Hedge Fund project, StockSnow is for **educational purposes only**:
- Not investment advice
- Not intended for real trading
- No guarantees on data accuracy or system reliability
- Use at your own risk

Always consult a financial advisor for investment decisions.
