import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { StockSnapshot } from '@/services/stocksnow-api';
import { Activity } from 'lucide-react';

interface TechnicalIndicatorsTableProps {
  quotes: StockSnapshot[];
  isLoading: boolean;
}

export function TechnicalIndicatorsTable({ quotes, isLoading }: TechnicalIndicatorsTableProps) {
  const quotesWithIndicators = quotes.filter((q) => q.technical_indicators);

  if (quotesWithIndicators.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Technical Indicators
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">
            No technical indicators available yet. Technical analysis requires at least 20 data points.
            <br />
            Keep monitoring to accumulate data.
          </p>
        </CardContent>
      </Card>
    );
  }

  const formatNumber = (num?: number, decimals: number = 2) => {
    return num !== undefined ? num.toFixed(decimals) : 'N/A';
  };

  const getRSIStatus = (rsi?: number) => {
    if (!rsi) return null;
    if (rsi > 70) return <Badge variant="destructive">Overbought</Badge>;
    if (rsi < 30) return <Badge variant="default" className="bg-green-500">Oversold</Badge>;
    return <Badge variant="secondary">Neutral</Badge>;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Technical Indicators
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ticker</TableHead>
                <TableHead className="text-right">RSI</TableHead>
                <TableHead className="text-right">MACD</TableHead>
                <TableHead className="text-right">SMA 20</TableHead>
                <TableHead className="text-right">SMA 50</TableHead>
                <TableHead className="text-right">Support</TableHead>
                <TableHead className="text-right">Resistance</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {quotesWithIndicators.map((snapshot) => {
                const ti = snapshot.technical_indicators!;
                
                return (
                  <TableRow key={snapshot.ticker}>
                    <TableCell className="font-mono font-semibold">
                      {snapshot.ticker}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        {ti.rsi ? formatNumber(ti.rsi, 1) : 'N/A'}
                        {getRSIStatus(ti.rsi)}
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatNumber(ti.macd)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      ${formatNumber(ti.sma_20)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      ${formatNumber(ti.sma_50)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-green-500">
                      ${formatNumber(ti.support_level)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-red-500">
                      ${formatNumber(ti.resistance_level)}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
        <div className="mt-4 space-y-2">
          <p className="text-xs text-muted-foreground">
            <strong>RSI (Relative Strength Index):</strong> >70 = Overbought, &lt;30 = Oversold
          </p>
          <p className="text-xs text-muted-foreground">
            <strong>MACD:</strong> Moving Average Convergence Divergence - Trend momentum indicator
          </p>
          <p className="text-xs text-muted-foreground">
            <strong>SMA:</strong> Simple Moving Average - Average price over period
          </p>
          <p className="text-xs text-muted-foreground">
            <strong>Support/Resistance:</strong> Key price levels based on recent highs/lows
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
