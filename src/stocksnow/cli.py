"""Command-line interface for StockSnow."""

import asyncio
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

from .monitor import StockMonitor
from .models import AlertType

console = Console()


class StockSnowCLI:
    """CLI for StockSnow stock monitoring."""
    
    def __init__(self):
        """Initialize the CLI."""
        load_dotenv()
        
        api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
        if not api_key:
            console.print("[red]Error: FINANCIAL_DATASETS_API_KEY not found in environment[/red]")
            sys.exit(1)
        
        self.monitor = StockMonitor(api_key)
        self.running = False
    
    def make_watchlist_table(self) -> Table:
        """Create a table showing all watchlists."""
        table = Table(title="📋 Watchlists", show_header=True, header_style="bold magenta")
        table.add_column("Watchlist", style="cyan")
        table.add_column("Stocks", style="green")
        table.add_column("Count", justify="right", style="yellow")
        
        watchlists = self.monitor.get_watchlists()
        for wl_name in watchlists:
            wl = self.monitor.get_watchlist(wl_name)
            if wl:
                tickers = ", ".join([item.ticker for item in wl.items])
                table.add_row(wl_name, tickers, str(len(wl.items)))
        
        if not watchlists:
            table.add_row("No watchlists", "-", "0")
        
        return table
    
    def make_quotes_table(self) -> Table:
        """Create a table showing live quotes."""
        table = Table(title="📊 Live Quotes", show_header=True, header_style="bold blue")
        table.add_column("Ticker", style="cyan", no_wrap=True)
        table.add_column("Price", justify="right", style="white")
        table.add_column("Change", justify="right")
        table.add_column("Change %", justify="right")
        table.add_column("Volume", justify="right", style="white")
        table.add_column("High", justify="right", style="green")
        table.add_column("Low", justify="right", style="red")
        
        snapshots = self.monitor.get_all_snapshots()
        
        if not snapshots:
            table.add_row("No data", "-", "-", "-", "-", "-", "-")
        else:
            for snapshot in sorted(snapshots, key=lambda x: x.ticker):
                quote = snapshot.quote
                
                # Color code the change
                change_color = "green" if quote.change >= 0 else "red"
                change_symbol = "+" if quote.change >= 0 else ""
                
                table.add_row(
                    quote.ticker,
                    f"${quote.price:.2f}",
                    f"[{change_color}]{change_symbol}{quote.change:.2f}[/{change_color}]",
                    f"[{change_color}]{change_symbol}{quote.change_percent:.2f}%[/{change_color}]",
                    f"{quote.volume:,}",
                    f"${quote.high:.2f}",
                    f"${quote.low:.2f}"
                )
        
        return table
    
    def make_technical_table(self) -> Table:
        """Create a table showing technical indicators."""
        table = Table(title="🔧 Technical Indicators", show_header=True, header_style="bold yellow")
        table.add_column("Ticker", style="cyan")
        table.add_column("RSI", justify="right")
        table.add_column("MACD", justify="right")
        table.add_column("SMA 20", justify="right")
        table.add_column("SMA 50", justify="right")
        table.add_column("Support", justify="right", style="green")
        table.add_column("Resistance", justify="right", style="red")
        
        snapshots = self.monitor.get_all_snapshots()
        has_data = False
        
        for snapshot in sorted(snapshots, key=lambda x: x.ticker):
            if snapshot.technical_indicators:
                has_data = True
                ti = snapshot.technical_indicators
                
                # Color code RSI
                rsi_value = f"{ti.rsi:.1f}" if ti.rsi else "N/A"
                if ti.rsi:
                    if ti.rsi > 70:
                        rsi_value = f"[red]{ti.rsi:.1f}[/red]"
                    elif ti.rsi < 30:
                        rsi_value = f"[green]{ti.rsi:.1f}[/green]"
                    else:
                        rsi_value = f"{ti.rsi:.1f}"
                
                table.add_row(
                    snapshot.ticker,
                    rsi_value,
                    f"{ti.macd:.2f}" if ti.macd else "N/A",
                    f"${ti.sma_20:.2f}" if ti.sma_20 else "N/A",
                    f"${ti.sma_50:.2f}" if ti.sma_50 else "N/A",
                    f"${ti.support_level:.2f}" if ti.support_level else "N/A",
                    f"${ti.resistance_level:.2f}" if ti.resistance_level else "N/A"
                )
        
        if not has_data:
            table.add_row("No data", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")
        
        return table
    
    def make_alerts_table(self) -> Table:
        """Create a table showing active alerts."""
        table = Table(title="🔔 Active Alerts", show_header=True, header_style="bold red")
        table.add_column("Ticker", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Threshold", justify="right", style="white")
        table.add_column("Status", style="green")
        
        all_alerts = self.monitor.alert_manager.get_alerts()
        has_alerts = False
        
        for ticker, alerts in all_alerts.items():
            for alert in alerts:
                if alert.active:
                    has_alerts = True
                    table.add_row(
                        ticker,
                        alert.alert_type.value,
                        str(alert.threshold),
                        "Active" if alert.active else "Triggered"
                    )
        
        if not has_alerts:
            table.add_row("No alerts", "-", "-", "-")
        
        return table
    
    def make_dashboard(self) -> Layout:
        """Create the main dashboard layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="quotes"),
            Layout(name="technical")
        )
        
        layout["right"].split_column(
            Layout(name="watchlists"),
            Layout(name="alerts")
        )
        
        # Add content
        layout["header"].update(
            Panel(
                "[bold white]StockSnow - Real-time Stock Monitor[/bold white]",
                style="bold blue"
            )
        )
        
        layout["quotes"].update(self.make_quotes_table())
        layout["technical"].update(self.make_technical_table())
        layout["watchlists"].update(self.make_watchlist_table())
        layout["alerts"].update(self.make_alerts_table())
        
        layout["footer"].update(
            Panel(
                f"[dim]Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Press Ctrl+C to exit[/dim]",
                style="dim"
            )
        )
        
        return layout
    
    async def run_dashboard(self):
        """Run the live dashboard."""
        console.print("\n[bold green]Starting StockSnow Monitor...[/bold green]\n")
        
        # Start monitoring
        await self.monitor.start_monitoring()
        
        # Wait a bit for initial data
        await asyncio.sleep(3)
        
        try:
            with Live(self.make_dashboard(), refresh_per_second=1, console=console) as live:
                while self.running:
                    live.update(self.make_dashboard())
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopping monitor...[/yellow]")
        finally:
            await self.monitor.stop_monitoring()
    
    async def interactive_setup(self):
        """Interactive setup to add stocks to watchlist."""
        console.print("\n[bold cyan]StockSnow Setup[/bold cyan]\n")
        
        # Create a default watchlist
        try:
            self.monitor.watchlist_manager.create_watchlist("default")
        except ValueError:
            pass  # Already exists
        
        console.print("Enter stock tickers to monitor (comma-separated, e.g., AAPL,MSFT,GOOGL):")
        tickers_input = input("> ").strip()
        
        if not tickers_input:
            console.print("[yellow]No tickers entered. Using example stocks.[/yellow]")
            tickers = ["AAPL", "MSFT", "GOOGL"]
        else:
            tickers = [t.strip().upper() for t in tickers_input.split(",")]
        
        # Add tickers to watchlist
        for ticker in tickers:
            try:
                self.monitor.add_to_watchlist("default", ticker)
                console.print(f"[green]✓[/green] Added {ticker} to watchlist")
            except Exception as e:
                console.print(f"[red]✗[/red] Error adding {ticker}: {e}")
        
        # Ask about alerts
        console.print("\nWould you like to set up price alerts? (y/n):")
        if input("> ").strip().lower() == 'y':
            for ticker in tickers:
                console.print(f"\nSet alert for {ticker}? (y/n):")
                if input("> ").strip().lower() == 'y':
                    console.print(f"Alert type for {ticker} (above/below):")
                    alert_type = input("> ").strip().lower()
                    
                    if alert_type in ['above', 'below']:
                        console.print(f"Price threshold:")
                        try:
                            threshold = float(input("> ").strip())
                            self.monitor.create_alert(ticker, alert_type, threshold)
                            console.print(f"[green]✓[/green] Alert created for {ticker}")
                        except ValueError:
                            console.print("[red]Invalid threshold[/red]")
        
        console.print("\n[bold green]Setup complete![/bold green]\n")
    
    async def start(self):
        """Start the CLI."""
        self.running = True
        
        # Run setup
        await self.interactive_setup()
        
        # Run dashboard
        await self.run_dashboard()


def main():
    """Main entry point for StockSnow CLI."""
    cli = StockSnowCLI()
    
    try:
        asyncio.run(cli.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting StockSnow...[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
