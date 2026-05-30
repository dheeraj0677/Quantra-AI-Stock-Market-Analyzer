import { useQuery } from '@tanstack/react-query';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { marketApi } from '@/api/market';
import { formatCurrency, formatPct } from '@/utils/formatters';

export function MarketSummaryBar() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ['marketSummary'],
    queryFn: marketApi.getSummary,
    refetchInterval: 60000, // Refresh every minute
  });

  if (isLoading) {
    return <div className="h-16 w-full animate-pulse rounded-lg bg-card" />;
  }

  if (!summary || summary.length === 0) return null;

  return (
    <div className="flex w-full items-center justify-between rounded-lg border bg-card p-4 shadow-sm overflow-x-auto gap-6">
      {summary.map((idx) => {
        const isUp = idx.change >= 0;
        const Icon = isUp ? TrendingUp : TrendingDown;
        const color = isUp ? 'text-emerald-500' : 'text-red-500';

        return (
          <div key={idx.index} className="flex min-w-[120px] flex-col">
            <span className="text-xs font-medium text-muted-foreground">{idx.index}</span>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-sm font-semibold">{formatCurrency(idx.value, 'USD')}</span>
              <div className={`flex items-center text-xs ${color}`}>
                <Icon className="mr-1 h-3 w-3" />
                {formatPct(idx.change_pct)}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
