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
import { Badge } from '@/components/ui/badge';
import { StockSnowAPI, PriceAlert } from '@/services/stocksnow-api';
import { Bell, Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

export function AlertsManager() {
  const [alerts, setAlerts] = useState<Record<string, PriceAlert[]>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newAlertTicker, setNewAlertTicker] = useState('');
  const [newAlertType, setNewAlertType] = useState<'above' | 'below' | 'change_percent' | 'volume_spike'>('above');
  const [newAlertThreshold, setNewAlertThreshold] = useState('');
  const [newAlertMessage, setNewAlertMessage] = useState('');

  useEffect(() => {
    loadAlerts();
    // Poll for alerts every 30 seconds
    const interval = setInterval(loadAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadAlerts = async () => {
    try {
      setIsLoading(true);
      const allAlerts = await StockSnowAPI.getAlerts();
      setAlerts(allAlerts);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateAlert = async () => {
    if (!newAlertTicker.trim()) {
      toast.error('Please enter a stock ticker');
      return;
    }

    if (!newAlertThreshold.trim()) {
      toast.error('Please enter a threshold value');
      return;
    }

    try {
      const threshold = parseFloat(newAlertThreshold);
      await StockSnowAPI.createAlert(
        newAlertTicker.toUpperCase(),
        newAlertType,
        threshold,
        newAlertMessage || undefined
      );
      toast.success(`Alert created for ${newAlertTicker.toUpperCase()}`);
      setNewAlertTicker('');
      setNewAlertThreshold('');
      setNewAlertMessage('');
      setIsDialogOpen(false);
      loadAlerts();
    } catch (err) {
      console.error('Failed to create alert:', err);
      toast.error('Failed to create alert');
    }
  };

  const getAlertTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      above: 'bg-green-500',
      below: 'bg-red-500',
      change_percent: 'bg-blue-500',
      volume_spike: 'bg-purple-500',
    };
    return (
      <Badge className={colors[type] || 'bg-gray-500'}>
        {type.replace('_', ' ')}
      </Badge>
    );
  };

  const getStatusBadge = (alert: PriceAlert) => {
    if (alert.triggered_at) {
      return <Badge variant="outline" className="text-orange-500 border-orange-500">Triggered</Badge>;
    }
    return alert.active ? (
      <Badge variant="default" className="bg-green-500">Active</Badge>
    ) : (
      <Badge variant="secondary">Inactive</Badge>
    );
  };

  const allAlertsList = Object.entries(alerts).flatMap(([ticker, tickerAlerts]) =>
    tickerAlerts.map((alert) => ({ ...alert, ticker }))
  );

  const activeAlerts = allAlertsList.filter((a) => a.active);
  const triggeredAlerts = allAlertsList.filter((a) => a.triggered_at);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Active Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{activeAlerts.length}</p>
            <p className="text-xs text-muted-foreground">Currently monitoring</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Triggered Today</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{triggeredAlerts.length}</p>
            <p className="text-xs text-muted-foreground">Alerts triggered</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Price Alerts
            </CardTitle>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  New Alert
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Price Alert</DialogTitle>
                  <DialogDescription>
                    Get notified when a stock price meets your conditions.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="alert-ticker">Stock Ticker *</Label>
                    <Input
                      id="alert-ticker"
                      placeholder="e.g., AAPL, MSFT"
                      value={newAlertTicker}
                      onChange={(e) => setNewAlertTicker(e.target.value.toUpperCase())}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="alert-type">Alert Type *</Label>
                    <Select value={newAlertType} onValueChange={(v: any) => setNewAlertType(v)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="above">Price Above</SelectItem>
                        <SelectItem value="below">Price Below</SelectItem>
                        <SelectItem value="change_percent">Percentage Change</SelectItem>
                        <SelectItem value="volume_spike">Volume Spike</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="alert-threshold">
                      Threshold * {newAlertType === 'change_percent' ? '(%)' : '($)'}
                    </Label>
                    <Input
                      id="alert-threshold"
                      type="number"
                      step="0.01"
                      placeholder={newAlertType === 'change_percent' ? 'e.g., 5.0' : 'e.g., 150.00'}
                      value={newAlertThreshold}
                      onChange={(e) => setNewAlertThreshold(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="alert-message">Custom Message</Label>
                    <Input
                      id="alert-message"
                      placeholder="Optional notification message"
                      value={newAlertMessage}
                      onChange={(e) => setNewAlertMessage(e.target.value)}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateAlert}>Create Alert</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {allAlertsList.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              No alerts configured. Create your first price alert to get started.
            </p>
          ) : (
            <div className="space-y-3">
              {allAlertsList.map((alert, index) => (
                <div
                  key={`${alert.ticker}-${index}`}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono font-semibold">{alert.ticker}</span>
                      {getAlertTypeBadge(alert.alert_type)}
                      {getStatusBadge(alert)}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <p>
                        {alert.alert_type === 'above' && `Trigger when price goes above $${alert.threshold}`}
                        {alert.alert_type === 'below' && `Trigger when price goes below $${alert.threshold}`}
                        {alert.alert_type === 'change_percent' && `Trigger when price changes by ${alert.threshold}%`}
                        {alert.alert_type === 'volume_spike' && `Trigger when volume exceeds ${alert.threshold}`}
                      </p>
                      {alert.message && <p className="mt-1 italic">"{alert.message}"</p>}
                      {alert.triggered_at && (
                        <p className="mt-1 text-orange-500">
                          Triggered: {new Date(alert.triggered_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="text-sm">Alert Types</CardTitle>
        </CardHeader>
        <CardContent className="text-xs space-y-2">
          <p><strong>Price Above:</strong> Triggers when stock price crosses above the threshold</p>
          <p><strong>Price Below:</strong> Triggers when stock price crosses below the threshold</p>
          <p><strong>Percentage Change:</strong> Triggers when price changes by the percentage amount</p>
          <p><strong>Volume Spike:</strong> Triggers when trading volume exceeds the threshold</p>
        </CardContent>
      </Card>
    </div>
  );
}
