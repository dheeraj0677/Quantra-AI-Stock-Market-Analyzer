import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { marketApi } from '@/api/market';
import { formatCurrency, formatPct } from '@/utils/formatters';
import { getPnLColor } from '@/utils/colors';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function TopMoversTable() {
  const [activeTab, setActiveTab] = useState<'gainers' | 'losers' | 'active'>('gainers');

  const { data: movers, isLoading } = useQuery({
    queryKey: ['topMovers', activeTab],
    queryFn: () => marketApi.getMovers(activeTab),
    refetchInterval: 60000,
  });

  return (
    <Card className="col-span-1 h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold">Top Movers</CardTitle>
          <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)} className="w-auto">
            <TabsList className="h-8">
              <TabsTrigger value="gainers" className="text-xs px-2">Gainers</TabsTrigger>
              <TabsTrigger value="losers" className="text-xs px-2">Losers</TabsTrigger>
              <TabsTrigger value="active" className="text-xs px-2">Active</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="h-10 w-24 animate-pulse rounded bg-muted" />
                <div className="h-10 w-16 animate-pulse rounded bg-muted" />
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {movers?.map((mover) => (
              <div key={mover.ticker} className="flex items-center justify-between border-b pb-2 last:border-0 last:pb-0">
                <div>
                  <div className="font-semibold text-sm">{mover.ticker}</div>
                  <div className="text-xs text-muted-foreground truncate max-w-[120px]">{mover.name}</div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-sm">{formatCurrency(mover.price, 'USD')}</div>
                  <div className={`text-xs font-semibold ${getPnLColor(mover.change_pct)}`}>
                    {formatPct(mover.change_pct)}
                  </div>
                </div>
              </div>
            ))}
            {(!movers || movers.length === 0) && (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No data available
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
