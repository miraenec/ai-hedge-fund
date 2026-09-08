"""FastAPI web API for StockSnow."""

import asyncio
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .monitor import StockMonitor
from .models import AlertType, StockSnapshot, Watchlist

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="StockSnow API",
    description="Real-time stock monitoring and analysis API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global monitor instance
monitor: Optional[StockMonitor] = None
monitor_task: Optional[asyncio.Task] = None


# Request/Response models
class AddToWatchlistRequest(BaseModel):
    watchlist_name: str
    ticker: str
    notes: Optional[str] = None
    target_price: Optional[float] = None


class RemoveFromWatchlistRequest(BaseModel):
    watchlist_name: str
    ticker: str


class CreateAlertRequest(BaseModel):
    ticker: str
    alert_type: str
    threshold: float
    message: Optional[str] = None


class CreateWatchlistRequest(BaseModel):
    name: str


# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize monitor on startup."""
    global monitor, monitor_task
    
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        print("Warning: FINANCIAL_DATASETS_API_KEY not set")
        return
    
    monitor = StockMonitor(api_key)
    
    # Start monitoring in background
    monitor_task = asyncio.create_task(monitor.start_monitoring())


@app.on_event("shutdown")
async def shutdown_event():
    """Stop monitor on shutdown."""
    global monitor, monitor_task
    
    if monitor:
        await monitor.stop_monitoring()
    
    if monitor_task:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


# API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "StockSnow API",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/watchlists", response_model=list[str])
async def get_watchlists():
    """Get all watchlist names."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    return monitor.get_watchlists()


@app.get("/watchlists/{name}", response_model=Watchlist)
async def get_watchlist(name: str):
    """Get a specific watchlist."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    watchlist = monitor.get_watchlist(name)
    if not watchlist:
        raise HTTPException(status_code=404, detail=f"Watchlist '{name}' not found")
    
    return watchlist


@app.post("/watchlists")
async def create_watchlist(request: CreateWatchlistRequest):
    """Create a new watchlist."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    try:
        monitor.watchlist_manager.create_watchlist(request.name)
        return {"message": f"Watchlist '{request.name}' created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/watchlists/{name}")
async def delete_watchlist(name: str):
    """Delete a watchlist."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    success = monitor.watchlist_manager.delete_watchlist(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Watchlist '{name}' not found")
    
    return {"message": f"Watchlist '{name}' deleted successfully"}


@app.post("/watchlists/add")
async def add_to_watchlist(request: AddToWatchlistRequest):
    """Add a stock to a watchlist."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    try:
        monitor.add_to_watchlist(
            request.watchlist_name,
            request.ticker,
            request.notes,
            request.target_price
        )
        return {"message": f"Added {request.ticker} to watchlist '{request.watchlist_name}'"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/watchlists/remove")
async def remove_from_watchlist(request: RemoveFromWatchlistRequest):
    """Remove a stock from a watchlist."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    monitor.remove_from_watchlist(request.watchlist_name, request.ticker)
    return {"message": f"Removed {request.ticker} from watchlist '{request.watchlist_name}'"}


@app.get("/quotes/{ticker}", response_model=StockSnapshot)
async def get_quote(ticker: str):
    """Get current quote and analysis for a ticker."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    snapshot = monitor.get_snapshot(ticker)
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"No data available for {ticker}")
    
    return snapshot


@app.get("/quotes", response_model=list[StockSnapshot])
async def get_all_quotes():
    """Get quotes for all monitored stocks."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    return monitor.get_all_snapshots()


@app.post("/alerts")
async def create_alert(request: CreateAlertRequest):
    """Create a price alert."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    try:
        alert = monitor.create_alert(
            request.ticker,
            request.alert_type,
            request.threshold,
            request.message
        )
        return {
            "message": f"Alert created for {request.ticker}",
            "alert": alert.model_dump(mode='json')
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/alerts")
async def get_alerts(ticker: Optional[str] = None):
    """Get all alerts or alerts for a specific ticker."""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor not initialized")
    
    alerts = monitor.alert_manager.get_alerts(ticker)
    
    # Convert to JSON-serializable format
    result = {}
    for t, alert_list in alerts.items():
        result[t] = [alert.model_dump(mode='json') for alert in alert_list]
    
    return result


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "monitor_initialized": monitor is not None,
        "monitored_tickers": len(monitor.latest_quotes) if monitor else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
