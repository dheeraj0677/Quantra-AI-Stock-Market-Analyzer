import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { stocksApi } from '@/api/stocks';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';

export function StockSearchPage() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const { data: results, isLoading } = useQuery({
    queryKey: ['stockSearch', query],
    queryFn: () => stocksApi.search(query),
    enabled: query.length > 1,
  });

  return (
    <div className="mx-auto max-w-2xl space-y-6 pt-10">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Search Stocks</h1>
        <p className="text-muted-foreground">Find a company by ticker or name to analyze</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
        <Input
          type="search"
          placeholder="e.g. AAPL, Microsoft, TSLA"
          className="h-12 w-full pl-10 text-lg"
          value={query}
          onChange={(e: any) => setQuery(e.target.value)}
        />
      </div>

      {query.length > 1 && (
        <Card>
          <CardContent className="p-2">
            {isLoading ? (
              <div className="p-4 text-center text-sm text-muted-foreground">Searching...</div>
            ) : !results || results.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">No stocks found</div>
            ) : (
              <div className="flex flex-col gap-1">
                {results.map((stock) => (
                  <button
                    key={stock.ticker}
                    className="flex items-center justify-between rounded-md p-3 hover:bg-accent text-left transition-colors"
                    onClick={() => navigate(`/stocks/${stock.ticker}`)}
                  >
                    <div>
                      <div className="font-bold">{stock.ticker}</div>
                      <div className="text-sm text-muted-foreground">{stock.name}</div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {stock.exchange} • {stock.sector}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
