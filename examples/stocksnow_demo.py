"""
StockSnow Demo - Comprehensive example of using StockSnow features.

This script demonstrates:
1. Creating watchlists
2. Adding stocks with notes and target prices
3. Setting up various types of price alerts
4. Monitoring stocks in real-time
5. Viewing technical indicators
6. Getting snapshots of stock data
"""

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from src.stocksnow import StockMonitor, AlertType

# Load environment variables
load_dotenv()


async def demo_basic_monitoring():
    """Demonstrate basic stock monitoring."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Stock Monitoring")
    print("=" * 60 + "\n")
    
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        print("Error: FINANCIAL_DATASETS_API_KEY not set")
        return
    
    # Initialize monitor
    monitor = StockMonitor(api_key)
    
    # Add stocks to watchlist
    print("Adding stocks to 'tech_giants' watchlist...")
    for ticker, name in [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft"),
        ("GOOGL", "Google"),
    ]:
        monitor.add_to_watchlist("tech_giants", ticker, notes=name)
        print(f"  ✓ Added {ticker} - {name}")
    
    # Start monitoring
    print("\nStarting real-time monitoring...")
    await monitor.start_monitoring()
    
    # Wait for some data
    await asyncio.sleep(15)
    
    # Display quotes
    print("\n" + "-" * 60)
    print("Current Quotes:")
    print("-" * 60)
    
    for snapshot in monitor.get_all_snapshots():
        quote = snapshot.quote
        print(f"\n{quote.ticker}:")
        print(f"  Price: ${quote.price:.2f}")
        print(f"  Change: ${quote.change:+.2f} ({quote.change_percent:+.2f}%)")
        print(f"  Volume: {quote.volume:,}")
        print(f"  High: ${quote.high:.2f} | Low: ${quote.low:.2f}")
    
    # Stop monitoring
    await monitor.stop_monitoring()
    print("\n✓ Monitoring stopped")


async def demo_price_alerts():
    """Demonstrate price alert functionality."""
    print("\n" + "=" * 60)
    print("DEMO 2: Price Alerts")
    print("=" * 60 + "\n")
    
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        print("Error: FINANCIAL_DATASETS_API_KEY not set")
        return
    
    monitor = StockMonitor(api_key)
    
    # Add a stock
    print("Adding NVDA to watchlist...")
    monitor.add_to_watchlist("momentum", "NVDA", notes="NVIDIA Corp.", target_price=500.0)
    
    # Set up different types of alerts
    print("\nSetting up alerts:")
    
    alerts = [
        ("NVDA", "above", 500.0, "NVDA hit target price!"),
        ("NVDA", "below", 400.0, "NVDA support broken!"),
        ("NVDA", "change_percent", 5.0, "NVDA big move today!"),
    ]
    
    for ticker, alert_type, threshold, message in alerts:
        monitor.create_alert(ticker, alert_type, threshold, message)
        print(f"  ✓ Alert: {ticker} {alert_type} {threshold} - {message}")
    
    # Start monitoring
    print("\nMonitoring for 30 seconds...")
    await monitor.start_monitoring()
    await asyncio.sleep(30)
    
    # Check current status
    snapshot = monitor.get_snapshot("NVDA")
    if snapshot:
        print(f"\nNVDA Current Price: ${snapshot.quote.price:.2f}")
        print(f"Change: {snapshot.quote.change_percent:+.2f}%")
    
    await monitor.stop_monitoring()
    print("\n✓ Alert monitoring complete")


async def demo_technical_analysis():
    """Demonstrate technical analysis features."""
    print("\n" + "=" * 60)
    print("DEMO 3: Technical Analysis")
    print("=" * 60 + "\n")
    
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        print("Error: FINANCIAL_DATASETS_API_KEY not set")
        return
    
    monitor = StockMonitor(api_key)
    
    # Add stock
    print("Adding AAPL for technical analysis...")
    monitor.add_to_watchlist("analysis", "AAPL", notes="Apple Inc.")
    
    # Start monitoring
    print("Collecting price data...")
    await monitor.start_monitoring()
    
    # Wait for enough data for technical indicators
    print("Waiting for sufficient data (this may take a minute)...")
    await asyncio.sleep(60)
    
    # Get snapshot with technical indicators
    snapshot = monitor.get_snapshot("AAPL")
    
    if snapshot and snapshot.technical_indicators:
        ti = snapshot.technical_indicators
        
        print("\n" + "-" * 60)
        print(f"Technical Analysis for {snapshot.ticker}")
        print("-" * 60)
        print(f"\nCurrent Price: ${snapshot.quote.price:.2f}")
        
        print("\n📊 Moving Averages:")
        if ti.sma_20:
            print(f"  SMA 20:  ${ti.sma_20:.2f}")
        if ti.sma_50:
            print(f"  SMA 50:  ${ti.sma_50:.2f}")
        if ti.sma_200:
            print(f"  SMA 200: ${ti.sma_200:.2f}")
        if ti.ema_12:
            print(f"  EMA 12:  ${ti.ema_12:.2f}")
        if ti.ema_26:
            print(f"  EMA 26:  ${ti.ema_26:.2f}")
        
        print("\n📈 Momentum Indicators:")
        if ti.rsi:
            rsi_status = "Overbought" if ti.rsi > 70 else "Oversold" if ti.rsi < 30 else "Neutral"
            print(f"  RSI (14): {ti.rsi:.1f} - {rsi_status}")
        if ti.macd:
            print(f"  MACD: {ti.macd:.2f}")
        if ti.macd_signal:
            print(f"  MACD Signal: {ti.macd_signal:.2f}")
        if ti.macd_histogram:
            print(f"  MACD Histogram: {ti.macd_histogram:.2f}")
        
        print("\n📉 Volatility (Bollinger Bands):")
        if ti.bollinger_upper and ti.bollinger_lower:
            print(f"  Upper:  ${ti.bollinger_upper:.2f}")
            print(f"  Middle: ${ti.bollinger_middle:.2f}")
            print(f"  Lower:  ${ti.bollinger_lower:.2f}")
        
        print("\n🎯 Support & Resistance:")
        if ti.support_level:
            print(f"  Support:    ${ti.support_level:.2f}")
        if ti.resistance_level:
            print(f"  Resistance: ${ti.resistance_level:.2f}")
        
        print("\n💹 Trading Signal:")
        if ti.rsi and ti.sma_20:
            if ti.rsi < 30 and snapshot.quote.price < ti.sma_20:
                print("  ⚠️  Potentially oversold - consider buying")
            elif ti.rsi > 70 and snapshot.quote.price > ti.sma_20:
                print("  ⚠️  Potentially overbought - consider selling")
            else:
                print("  ℹ️  No clear signal - hold or wait")
    else:
        print("\n⚠️  Not enough data yet for technical indicators")
        print("   (Need at least 20 data points)")
    
    await monitor.stop_monitoring()
    print("\n✓ Technical analysis complete")


async def demo_multiple_watchlists():
    """Demonstrate managing multiple watchlists."""
    print("\n" + "=" * 60)
    print("DEMO 4: Multiple Watchlists")
    print("=" * 60 + "\n")
    
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        print("Error: FINANCIAL_DATASETS_API_KEY not set")
        return
    
    monitor = StockMonitor(api_key)
    
    # Create multiple watchlists
    watchlists = {
        "tech": [("AAPL", "Apple"), ("MSFT", "Microsoft"), ("GOOGL", "Google")],
        "finance": [("JPM", "JPMorgan"), ("BAC", "Bank of America"), ("GS", "Goldman Sachs")],
        "energy": [("XOM", "Exxon"), ("CVX", "Chevron"), ("COP", "ConocoPhillips")],
    }
    
    print("Creating watchlists and adding stocks:\n")
    for wl_name, stocks in watchlists.items():
        print(f"📋 {wl_name.upper()} Watchlist:")
        for ticker, name in stocks:
            monitor.add_to_watchlist(wl_name, ticker, notes=name)
            print(f"  ✓ {ticker} - {name}")
        print()
    
    # Start monitoring
    print("Starting monitoring for all watchlists...")
    await monitor.start_monitoring()
    await asyncio.sleep(15)
    
    # Display by watchlist
    print("\n" + "-" * 60)
    print("Current Status by Watchlist:")
    print("-" * 60)
    
    for wl_name in watchlists.keys():
        wl = monitor.get_watchlist(wl_name)
        print(f"\n📋 {wl_name.upper()}:")
        
        for item in wl.items:
            snapshot = monitor.get_snapshot(item.ticker)
            if snapshot:
                quote = snapshot.quote
                change_symbol = "📈" if quote.change >= 0 else "📉"
                print(f"  {change_symbol} {quote.ticker}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)")
    
    await monitor.stop_monitoring()
    print("\n✓ Multi-watchlist demo complete")


async def demo_custom_alerts():
    """Demonstrate custom alert notifications."""
    print("\n" + "=" * 60)
    print("DEMO 5: Custom Alert Notifications")
    print("=" * 60 + "\n")
    
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        print("Error: FINANCIAL_DATASETS_API_KEY not set")
        return
    
    monitor = StockMonitor(api_key)
    
    # Custom notification handler
    alert_log = []
    
    def custom_notification(alert):
        """Custom notification handler - could send email, SMS, etc."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] ALERT: {alert.ticker} {alert.alert_type.value} {alert.threshold}"
        alert_log.append(log_entry)
        print(f"  🔔 {log_entry}")
        
        # Here you could add:
        # - Send email via SMTP
        # - Send SMS via Twilio
        # - Post to Slack/Discord webhook
        # - Push notification to mobile app
        # etc.
    
    # Register callback
    monitor.alert_manager.register_notification_callback(custom_notification)
    
    # Add stock and alerts
    print("Setting up stock with multiple alert conditions...")
    monitor.add_to_watchlist("alerts_demo", "TSLA", notes="Tesla")
    
    # Note: These thresholds should be adjusted based on current TSLA price
    print("\nConfigured alerts:")
    print("  • Above threshold alert")
    print("  • Below threshold alert")
    print("  • Percentage change alert")
    
    monitor.create_alert("TSLA", "above", 300.0, "TSLA broke $300!")
    monitor.create_alert("TSLA", "below", 200.0, "TSLA dropped below $200!")
    monitor.create_alert("TSLA", "change_percent", 3.0, "TSLA moved 3%+!")
    
    # Monitor
    print("\nMonitoring for alerts (30 seconds)...")
    await monitor.start_monitoring()
    await asyncio.sleep(30)
    
    # Show log
    print("\n" + "-" * 60)
    print("Alert Log:")
    print("-" * 60)
    if alert_log:
        for entry in alert_log:
            print(entry)
    else:
        print("No alerts triggered during monitoring period")
    
    await monitor.stop_monitoring()
    print("\n✓ Custom alerts demo complete")


async def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("StockSnow Comprehensive Demo")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("FINANCIAL_DATASETS_API_KEY"):
        print("\n❌ Error: FINANCIAL_DATASETS_API_KEY not found in environment")
        print("Please set your API key in .env file")
        return
    
    print("\nThis demo will showcase all StockSnow features:")
    print("1. Basic stock monitoring")
    print("2. Price alerts")
    print("3. Technical analysis")
    print("4. Multiple watchlists")
    print("5. Custom alert notifications")
    print("\nPress Ctrl+C at any time to exit")
    
    try:
        await demo_basic_monitoring()
        await asyncio.sleep(2)
        
        await demo_price_alerts()
        await asyncio.sleep(2)
        
        await demo_technical_analysis()
        await asyncio.sleep(2)
        
        await demo_multiple_watchlists()
        await asyncio.sleep(2)
        
        await demo_custom_alerts()
        
        print("\n" + "=" * 60)
        print("✨ All demos completed successfully!")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
