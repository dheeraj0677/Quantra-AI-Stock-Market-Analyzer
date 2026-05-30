import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { marketApi } from '@/api/market';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

export function MarketSentimentWidget() {
  const { data: sectors, isLoading } = useQuery({
    queryKey: ['marketSectors'],
    queryFn: marketApi.getSectors,
    refetchInterval: 120000,
  });

  return (
    <Card className="col-span-1 h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-semibold">Sector Performance</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex h-48 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        ) : !sectors || sectors.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
            No sector data available
          </div>
        ) : (
          <div className="h-56 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sectors} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                <XAxis type="number" hide domain={['dataMin', 'dataMax']} />
                <YAxis dataKey="sector" type="category" hide />
                <Tooltip
                  cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      const isUp = data.change_pct >= 0;
                      return (
                        <div className="rounded-md border bg-background p-2 shadow-sm">
                          <div className="text-xs font-semibold">{data.sector}</div>
                          <div className={`text-xs ${isUp ? 'text-emerald-500' : 'text-red-500'}`}>
                            {isUp ? '+' : ''}{data.change_pct.toFixed(2)}%
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="change_pct" radius={[0, 4, 4, 0]} barSize={12}>
                  {sectors.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.change_pct >= 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            
            <div className="mt-2 space-y-1.5 h-32 overflow-y-auto pr-2">
              {sectors.map(s => (
                <div key={s.sector} className="flex items-center justify-between text-xs">
                  <span className="truncate w-24 text-muted-foreground" title={s.sector}>{s.sector}</span>
                  <span className={s.change_pct >= 0 ? 'text-emerald-500' : 'text-red-500'}>
                    {s.change_pct > 0 ? '+' : ''}{s.change_pct.toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}


