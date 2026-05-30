import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Play, Settings2, History } from 'lucide-react';
import { backtestApi } from '@/api/backtest';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { formatRelativeTime } from '@/utils/formatters';

export function BacktestPage() {
  const navigate = useNavigate();
  const [strategyId, setStrategyId] = useState('');
  const [ticker, setTicker] = useState('AAPL');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2023-12-31');
  const [initialCapital, setInitialCapital] = useState('10000');
  const [isStarting, setIsStarting] = useState(false);

  const { data: history } = useQuery({
    queryKey: ['backtestHistory'],
    queryFn: backtestApi.getHistory,
  });

  const handleRun = async () => {
    try {
      setIsStarting(true);
      const res = await backtestApi.run({
        strategy_id: strategyId || 'momentum_ai', // default
        ticker,
        start_date: startDate,
        end_date: endDate,
        initial_capital: Number(initialCapital),
        parameters: {}
      });
      navigate(`/backtest/${res.job_id}`);
    } catch (error) {
      console.error('Failed to start backtest', error);
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Strategy Backtesting</h1>
        <p className="text-muted-foreground">Test AI and technical strategies against historical data</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings2 className="h-5 w-5" /> New Backtest
            </CardTitle>
            <CardDescription>Configure your strategy parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="strategy">Strategy</Label>
              <Select value={strategyId} onValueChange={setStrategyId}>
                <SelectTrigger id="strategy">
                  <SelectValue placeholder="Select a strategy" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="momentum_ai">AI Momentum Scanner</SelectItem>
                  <SelectItem value="mean_reversion">Mean Reversion (RSI + BB)</SelectItem>
                  <SelectItem value="breakout">Volatility Breakout</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="ticker">Target Symbol</Label>
              <Input id="ticker" value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} placeholder="e.g. AAPL" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start">Start Date</Label>
                <Input id="start" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end">End Date</Label>
                <Input id="end" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="capital">Initial Capital ($)</Label>
              <Input id="capital" type="number" value={initialCapital} onChange={(e) => setInitialCapital(e.target.value)} />
            </div>

            <Button onClick={handleRun} disabled={isStarting || !strategyId || !ticker} className="w-full gap-2 mt-4">
              {isStarting ? <Play className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              Run Backtest
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" /> Recent Backtests
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!history || history.length === 0 ? (
              <div className="text-center text-sm text-muted-foreground py-8">
                No recent backtests
              </div>
            ) : (
              <div className="space-y-3">
                {history.map(job => (
                  <div key={job.job_id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent/50 cursor-pointer transition-colors" onClick={() => navigate(`/backtest/${job.job_id}`)}>
                    <div>
                      <div className="font-semibold text-sm">{job.strategy_id}</div>
                      <div className="text-xs text-muted-foreground">{job.ticker} • {job.start_date} to {job.end_date}</div>
                    </div>
                    <div className="text-right">
                      <div className={`text-sm font-bold ${
                        job.status === 'done' ? 'text-emerald-500' :
                        job.status === 'error' ? 'text-destructive' : 'text-amber-500'
                      }`}>
                        {job.status.toUpperCase()}
                      </div>
                      <div className="text-xs text-muted-foreground">{formatRelativeTime(job.created_at)}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
