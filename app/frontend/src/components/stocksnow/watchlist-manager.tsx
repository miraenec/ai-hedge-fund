import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { StockSnowAPI, Watchlist } from '@/services/stocksnow-api';
import { ListPlus, Plus, Trash2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

interface WatchlistManagerProps {
  watchlists: string[];
  selectedWatchlist: string;
  onWatchlistChange: (name: string) => void;
  onWatchlistsUpdate: () => void;
}

export function WatchlistManager({
  watchlists,
  selectedWatchlist,
  onWatchlistChange,
  onWatchlistsUpdate,
}: WatchlistManagerProps) {
  const [watchlistData, setWatchlistData] = useState<Watchlist | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [newStockTicker, setNewStockTicker] = useState('');
  const [newStockNotes, setNewStockNotes] = useState('');
  const [newStockTarget, setNewStockTarget] = useState('');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  useEffect(() => {
    if (selectedWatchlist) {
      loadWatchlistData();
    }
  }, [selectedWatchlist]);

  const loadWatchlistData = async () => {
    if (!selectedWatchlist) return;
    
    try {
      setIsLoading(true);
      const data = await StockSnowAPI.getWatchlist(selectedWatchlist);
      setWatchlistData(data);
    } catch (err) {
      console.error('Failed to load watchlist data:', err);
      toast.error('Failed to load watchlist data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateWatchlist = async () => {
    if (!newWatchlistName.trim()) {
      toast.error('Please enter a watchlist name');
      return;
    }

    try {
      await StockSnowAPI.createWatchlist(newWatchlistName);
      toast.success(`Watchlist "${newWatchlistName}" created`);
      setNewWatchlistName('');
      setIsCreateDialogOpen(false);
      onWatchlistsUpdate();
    } catch (err) {
      console.error('Failed to create watchlist:', err);
      toast.error('Failed to create watchlist');
    }
  };

  const handleAddStock = async () => {
    if (!newStockTicker.trim()) {
      toast.error('Please enter a stock ticker');
      return;
    }

    try {
      const targetPrice = newStockTarget ? parseFloat(newStockTarget) : undefined;
      await StockSnowAPI.addToWatchlist(
        selectedWatchlist,
        newStockTicker.toUpperCase(),
        newStockNotes || undefined,
        targetPrice
      );
      toast.success(`${newStockTicker.toUpperCase()} added to watchlist`);
      setNewStockTicker('');
      setNewStockNotes('');
      setNewStockTarget('');
      setIsAddDialogOpen(false);
      loadWatchlistData();
    } catch (err) {
      console.error('Failed to add stock:', err);
      toast.error('Failed to add stock to watchlist');
    }
  };

  const handleRemoveStock = async (ticker: string) => {
    try {
      await StockSnowAPI.removeFromWatchlist(selectedWatchlist, ticker);
      toast.success(`${ticker} removed from watchlist`);
      loadWatchlistData();
    } catch (err) {
      console.error('Failed to remove stock:', err);
      toast.error('Failed to remove stock');
    }
  };

  const handleDeleteWatchlist = async () => {
    if (!selectedWatchlist) return;
    
    if (!confirm(`Are you sure you want to delete watchlist "${selectedWatchlist}"?`)) {
      return;
    }

    try {
      await StockSnowAPI.deleteWatchlist(selectedWatchlist);
      toast.success(`Watchlist "${selectedWatchlist}" deleted`);
      onWatchlistsUpdate();
    } catch (err) {
      console.error('Failed to delete watchlist:', err);
      toast.error('Failed to delete watchlist');
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <ListPlus className="h-5 w-5" />
              Watchlist Manager
            </CardTitle>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  New Watchlist
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Watchlist</DialogTitle>
                  <DialogDescription>
                    Create a new watchlist to organize your stocks.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="watchlist-name">Watchlist Name</Label>
                    <Input
                      id="watchlist-name"
                      placeholder="e.g., Tech Stocks, Blue Chips"
                      value={newWatchlistName}
                      onChange={(e) => setNewWatchlistName(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleCreateWatchlist()}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateWatchlist}>Create</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {watchlists.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              No watchlists yet. Create your first watchlist to get started.
            </p>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <Label>Select Watchlist</Label>
                  <Select value={selectedWatchlist} onValueChange={onWatchlistChange}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a watchlist" />
                    </SelectTrigger>
                    <SelectContent>
                      {watchlists.map((name) => (
                        <SelectItem key={name} value={name}>
                          {name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                {selectedWatchlist && (
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={handleDeleteWatchlist}
                    className="mt-6"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </Button>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {watchlistData && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{watchlistData.name} Stocks</CardTitle>
              <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Stock
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add Stock to {watchlistData.name}</DialogTitle>
                    <DialogDescription>
                      Add a new stock to your watchlist with optional notes and target price.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="ticker">Stock Ticker *</Label>
                      <Input
                        id="ticker"
                        placeholder="e.g., AAPL, MSFT"
                        value={newStockTicker}
                        onChange={(e) => setNewStockTicker(e.target.value.toUpperCase())}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="notes">Notes</Label>
                      <Input
                        id="notes"
                        placeholder="Optional notes about this stock"
                        value={newStockNotes}
                        onChange={(e) => setNewStockNotes(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="target">Target Price</Label>
                      <Input
                        id="target"
                        type="number"
                        step="0.01"
                        placeholder="Optional target price"
                        value={newStockTarget}
                        onChange={(e) => setNewStockTarget(e.target.value)}
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddStock}>Add Stock</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            {watchlistData.items.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                No stocks in this watchlist. Add some stocks to start monitoring.
              </p>
            ) : (
              <div className="space-y-2">
                {watchlistData.items.map((item) => (
                  <div
                    key={item.ticker}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span className="font-mono font-semibold text-lg">{item.ticker}</span>
                        {item.target_price && (
                          <span className="text-sm text-muted-foreground">
                            Target: ${item.target_price.toFixed(2)}
                          </span>
                        )}
                      </div>
                      {item.notes && (
                        <p className="text-sm text-muted-foreground mt-1">{item.notes}</p>
                      )}
                      <p className="text-xs text-muted-foreground mt-1">
                        Added: {new Date(item.added_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveStock(item.ticker)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
