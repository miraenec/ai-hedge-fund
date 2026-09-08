import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { StockSnapshot } from '@/services/stocksnow-api';
import { ArrowDown, ArrowUp, TrendingUp } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface LiveQuotesTableProps {
  quotes: StockSnapshot[];
  isLoading: boolean;
}

export function LiveQuotesTable({ quotes, isLoading }: LiveQuotesTableProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Live Quotes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (quotes.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Live Quotes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">
            No stocks being monitored. Add stocks to a watchlist to see live quotes.
          </p>
        </CardContent>
      </Card>
    );
  }

  const formatNumber = (num: number, decimals: number = 2) => {
    return num.toFixed(decimals);
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(2)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(2)}K`;
    }
    return volume.toString();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Live Quotes
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ticker</TableHead>
                <TableHead className="text-right">Price</TableHead>
                <TableHead className="text-right">Change</TableHead>
                <TableHead className="text-right">Change %</TableHead>
                <TableHead className="text-right">Volume</TableHead>
                <TableHead className="text-right">High</TableHead>
                <TableHead className="text-right">Low</TableHead>
                <TableHead className="text-right">Previous Close</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {quotes.map((snapshot) => {
                const { quote } = snapshot;
                const isPositive = quote.change >= 0;
                
                return (
                  <TableRow key={quote.ticker}>
                    <TableCell className="font-mono font-semibold">
                      {quote.ticker}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      ${formatNumber(quote.price)}
                    </TableCell>
                    <TableCell className="text-right">
                      <span className={isPositive ? 'text-green-500' : 'text-red-500'}>
                        {isPositive ? '+' : ''}${formatNumber(quote.change)}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        {isPositive ? (
                          <ArrowUp className="h-3 w-3 text-green-500" />
                        ) : (
                          <ArrowDown className="h-3 w-3 text-red-500" />
                        )}
                        <span className={isPositive ? 'text-green-500' : 'text-red-500'}>
                          {isPositive ? '+' : ''}{formatNumber(quote.change_percent)}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatVolume(quote.volume)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-green-500">
                      ${formatNumber(quote.high)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-red-500">
                      ${formatNumber(quote.low)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-muted-foreground">
                      ${formatNumber(quote.previous_close)}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
        <p className="text-xs text-muted-foreground mt-4">
          Last updated: {new Date().toLocaleTimeString()} • Updates every 10 seconds
        </p>
      </CardContent>
    </Card>
  );
}
