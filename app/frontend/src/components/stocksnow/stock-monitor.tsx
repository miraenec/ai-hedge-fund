import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { StockSnowAPI, StockSnapshot, Watchlist } from '@/services/stocksnow-api';
import { Activity, AlertCircle, Plus, TrendingDown, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { LiveQuotesTable } from './live-quotes-table';
import { TechnicalIndicatorsTable } from './technical-indicators-table';
import { WatchlistManager } from './watchlist-manager';
import { AlertsManager } from './alerts-manager';

export function StockMonitor() {
  const [watchlists, setWatchlists] = useState<string[]>([]);
  const [quotes, setQuotes] = useState<StockSnapshot[]>([]);
  const [selectedWatchlist, setSelectedWatchlist] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check API health and load initial data
  useEffect(() => {
    checkHealth();
    loadWatchlists();
  }, []);

  // Poll for quotes every 10 seconds when monitoring
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isMonitoring) {
      loadQuotes();
      interval = setInterval(loadQuotes, 10000); // Update every 10 seconds
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isMonitoring]);

  const checkHealth = async () => {
    try {
      const health = await StockSnowAPI.healthCheck();
      setIsMonitoring(health.monitor_initialized);
      if (!health.monitor_initialized) {
        setError('StockSnow API is not running. Please start it with: poetry run python -m src.stocksnow.api');
      }
    } catch (err) {
      setError('Cannot connect to StockSnow API. Please make sure it is running on http://localhost:8000');
      console.error('Health check failed:', err);
    }
  };

  const loadWatchlists = async () => {
    try {
      setIsLoading(true);
      const lists = await StockSnowAPI.getWatchlists();
      setWatchlists(lists);
      if (lists.length > 0 && !selectedWatchlist) {
        setSelectedWatchlist(lists[0]);
      }
      setError(null);
    } catch (err) {
      console.error('Failed to load watchlists:', err);
      toast.error('Failed to load watchlists');
    } finally {
      setIsLoading(false);
    }
  };

  const loadQuotes = async () => {
    try {
      const allQuotes = await StockSnowAPI.getAllQuotes();
      setQuotes(allQuotes);
    } catch (err) {
      console.error('Failed to load quotes:', err);
    }
  };

  const handleWatchlistChange = (watchlistName: string) => {
    setSelectedWatchlist(watchlistName);
  };

  if (error) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              <CardTitle>StockSnow API Not Available</CardTitle>
            </div>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                To start the StockSnow API server, run:
              </p>
              <pre className="p-4 bg-muted rounded-md overflow-x-auto">
                <code>poetry run python -m src.stocksnow.api</code>
              </pre>
              <p className="text-sm text-muted-foreground">
                The API will be available at http://localhost:8000
              </p>
              <Button onClick={checkHealth} className="w-full">
                Retry Connection
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-full w-full flex flex-col p-6 space-y-6 overflow-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Activity className="h-8 w-8" />
            StockSnow Monitor
          </h1>
          <p className="text-muted-foreground mt-1">
            Real-time stock monitoring, alerts, and technical analysis
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isMonitoring && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 text-green-500 rounded-md">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium">Live</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="quotes" className="flex-1">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="quotes">Live Quotes</TabsTrigger>
          <TabsTrigger value="technicals">Technical Analysis</TabsTrigger>
          <TabsTrigger value="watchlists">Watchlists</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="quotes" className="mt-6">
          <LiveQuotesTable quotes={quotes} isLoading={isLoading} />
        </TabsContent>

        <TabsContent value="technicals" className="mt-6">
          <TechnicalIndicatorsTable quotes={quotes} isLoading={isLoading} />
        </TabsContent>

        <TabsContent value="watchlists" className="mt-6">
          <WatchlistManager
            watchlists={watchlists}
            selectedWatchlist={selectedWatchlist}
            onWatchlistChange={handleWatchlistChange}
            onWatchlistsUpdate={loadWatchlists}
          />
        </TabsContent>

        <TabsContent value="alerts" className="mt-6">
          <AlertsManager />
        </TabsContent>
      </Tabs>

      {/* Stats Footer */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Monitored Stocks</CardDescription>
            <CardTitle className="text-2xl">{quotes.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Watchlists</CardDescription>
            <CardTitle className="text-2xl">{watchlists.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Alerts</CardDescription>
            <CardTitle className="text-2xl">-</CardTitle>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}
