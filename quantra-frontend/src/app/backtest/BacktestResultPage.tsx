import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Loader2, AlertTriangle, TrendingUp, Activity } from 'lucide-react';
import { backtestApi } from '@/api/backtest';
import { formatCurrency, formatPct } from '@/utils/formatters';
import { getPnLColor } from '@/utils/colors';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { EquityCurveChart } from '@/components/charts/EquityCurveChart';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function BacktestResultPage() {
  const { id } = useParams<{ id: string }>();

  const { data: job, isLoading } = useQuery({
    queryKey: ['backtestJob', id],
    queryFn: () => backtestApi.poll(id!),
    refetchInterval: (data) => {
      // @ts-ignore
      if (data?.status === 'done' || data?.status === 'error') return false;
      return 3000;
    },
  });

  if (isLoading || !job) {
    return <div className="p-12 text-center text-muted-foreground"><Loader2 className="animate-spin h-8 w-8 mx-auto mb-4" />Loading backtest data...</div>;
  }

  if (job.status === 'pending' || job.status === 'processing') {
    return (
      <Card className="flex flex-col items-center justify-center p-16 text-center mt-8">
        <Loader2 className="mb-4 h-12 w-12 animate-spin text-primary" />
        <h3 className="text-xl font-bold">Running Backtest</h3>
        <p className="mt-2 text-muted-foreground animate-pulse">
          Simulating strategy across historical data...
        </p>
      </Card>
    );
  }

  if (job.status === 'error' || !job.result) {
    return (
      <Card className="flex flex-col items-center justify-center p-16 text-center border-destructive mt-8">
        <AlertTriangle className="mb-4 h-12 w-12 text-destructive" />
        <h3 className="text-xl font-bold text-destructive">Simulation Failed</h3>
        <p className="mt-2 text-muted-foreground">The backtest encountered an error.</p>
        <Link to="/backtest" className="mt-6 text-primary hover:underline">Return to Backtest Configuration</Link>
      </Card>
    );
  }

  const result = job.result;
  const metrics = result.metrics;

  return (
    <div className="space-y-6">
      <div>
        <Link to="/backtest" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4 transition-colors">
          <ArrowLeft className="mr-1 h-4 w-4" /> Back to Configuration
        </Link>
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Backtest Results</h1>
            <p className="text-muted-foreground">{job.strategy_id} • {job.ticker} • {job.start_date} to {job.end_date}</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-muted-foreground">Final Equity</div>
            <div className="text-2xl font-bold">{formatCurrency(metrics.final_equity, 'USD')}</div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 grid-cols-2 md:grid-cols-4 lg:grid-cols-6">
        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Total Return</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className={`text-xl font-bold ${getPnLColor(metrics.total_return_pct)}`}>
              {formatPct(metrics.total_return_pct)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Win Rate</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xl font-bold">{formatPct(metrics.win_rate)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Max Drawdown</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xl font-bold text-destructive">{formatPct(metrics.max_drawdown)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Sharpe Ratio</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xl font-bold">{metrics.sharpe_ratio.toFixed(2)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Total Trades</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xl font-bold">{metrics.total_trades}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">Profit Factor</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-xl font-bold">{metrics.profit_factor.toFixed(2)}</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="chart" className="w-full">
        <TabsList>
          <TabsTrigger value="chart" className="gap-2"><TrendingUp className="h-4 w-4" /> Equity Curve</TabsTrigger>
          <TabsTrigger value="trades" className="gap-2"><Activity className="h-4 w-4" /> Trade Log</TabsTrigger>
        </TabsList>
        <TabsContent value="chart" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Value Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[500px] w-full">
                <EquityCurveChart data={result.equity_curve} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="trades" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Execution Log</CardTitle>
              <CardDescription>All simulated trades during the backtest period</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50 text-muted-foreground">
                    <tr className="border-b text-left">
                      <th className="p-4 font-medium">Date</th>
                      <th className="p-4 font-medium">Action</th>
                      <th className="p-4 font-medium text-right">Price</th>
                      <th className="p-4 font-medium text-right">Qty</th>
                      <th className="p-4 font-medium text-right">P&L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.trades.map((trade: any, i: number) => (
                      <tr key={i} className="border-b hover:bg-muted/50 last:border-0">
                        <td className="p-4">{new Date(trade.date).toLocaleDateString()}</td>
                        <td className="p-4 font-semibold">
                          <span className={trade.action === 'buy' ? 'text-emerald-500' : 'text-amber-500'}>
                            {trade.action.toUpperCase()}
                          </span>
                        </td>
                        <td className="p-4 text-right">{formatCurrency(trade.price, 'USD')}</td>
                        <td className="p-4 text-right">{trade.quantity}</td>
                        <td className="p-4 text-right">
                          {trade.pnl !== undefined ? (
                            <span className={getPnLColor(trade.pnl)}>
                              {trade.pnl > 0 ? '+' : ''}{formatCurrency(trade.pnl, 'USD')}
                            </span>
                          ) : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
