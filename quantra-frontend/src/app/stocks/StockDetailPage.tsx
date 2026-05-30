import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { LayoutDashboard, LineChart, Newspaper, Brain } from 'lucide-react';
import { stocksApi } from '@/api/stocks';
import { predictionApi } from '@/api/prediction';
import { formatCurrency, formatPct, formatLargeNum } from '@/utils/formatters';
import { getPnLColor } from '@/utils/colors';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { CandlestickChart } from '@/components/charts/CandlestickChart';
import { VolumeChart } from '@/components/charts/VolumeChart';
import { PredictionCard } from '@/components/prediction/PredictionCard';
import { DeepResearchPanel } from '@/components/prediction/DeepResearchPanel';
import { NewsFeed } from '@/components/news/NewsFeed';
import { useSSE } from '@/hooks/useSSE';

export function StockDetailPage() {
  const { ticker } = useParams<{ ticker: string }>();

  // Live updates
  useSSE();

  // Queries
  const { data: stock, isLoading: isStockLoading } = useQuery({
    queryKey: ['stock', ticker],
    queryFn: () => stocksApi.getStock(ticker!),
    enabled: !!ticker,
  });

  const { data: ohlcv, isLoading: isChartLoading } = useQuery({
    queryKey: ['ohlcv', ticker],
    queryFn: () => stocksApi.getOHLCV(ticker!),
    enabled: !!ticker,
  });

  const { data: prediction } = useQuery({
    queryKey: ['prediction', ticker, 'quick'],
    queryFn: () => predictionApi.getQuickPrediction(ticker!),
    enabled: !!ticker,
  });

  if (isStockLoading || !stock) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{stock.ticker}</h1>
            <span className="rounded bg-muted px-2 py-1 text-xs font-medium text-muted-foreground">
              {stock.exchange}
            </span>
          </div>
          <h2 className="text-lg text-muted-foreground">{stock.name}</h2>
          <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
            <span>{stock.sector}</span>
            <span>•</span>
            <span>{stock.industry}</span>
          </div>
        </div>

        <div className="text-left md:text-right">
          <div className="text-3xl font-bold">{formatCurrency(stock.current_price, 'USD')}</div>
          <div className={`flex items-center justify-start md:justify-end gap-2 font-medium ${getPnLColor(stock.change_pct)}`}>
            <span>{stock.change > 0 ? '+' : ''}{formatCurrency(stock.change, 'USD')}</span>
            <span>({formatPct(stock.change_pct)})</span>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid gap-6 grid-cols-1 xl:grid-cols-3">
        
        {/* Left Column - Charts & Tabs (2/3 width) */}
        <div className="xl:col-span-2 space-y-6">
          <Tabs defaultValue="chart" className="w-full">
            <TabsList className="grid w-full grid-cols-4 lg:w-[400px]">
              <TabsTrigger value="chart" className="gap-2"><LineChart className="h-4 w-4" /> Chart</TabsTrigger>
              <TabsTrigger value="fundamentals" className="gap-2"><LayoutDashboard className="h-4 w-4" /> Details</TabsTrigger>
              <TabsTrigger value="ai" className="gap-2"><Brain className="h-4 w-4" /> Deep AI</TabsTrigger>
              <TabsTrigger value="news" className="gap-2"><Newspaper className="h-4 w-4" /> News</TabsTrigger>
            </TabsList>
            
            <TabsContent value="chart" className="mt-4 space-y-4">
              <Card>
                <CardContent className="p-1">
                  <div className="flex justify-end gap-2 p-2 border-b bg-muted/20">
                    {/* Timeframe controls could go here */}
                  </div>
                  <div className="h-[400px] w-full p-2">
                    {isChartLoading ? (
                      <div className="flex h-full items-center justify-center">Loading chart...</div>
                    ) : ohlcv ? (
                      <CandlestickChart data={ohlcv} />
                    ) : (
                      <div className="flex h-full items-center justify-center">No chart data</div>
                    )}
                  </div>
                  <div className="h-[120px] w-full p-2 border-t">
                    {ohlcv && <VolumeChart data={ohlcv} />}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="fundamentals" className="mt-4">
              <Card>
                <CardContent className="p-6 grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div>
                    <div className="text-sm text-muted-foreground">Market Cap</div>
                    <div className="font-semibold text-lg">{formatLargeNum(stock.market_cap)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Volume</div>
                    <div className="font-semibold text-lg">{formatLargeNum(stock.volume)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">P/E Ratio</div>
                    <div className="font-semibold text-lg">{stock.pe_ratio?.toFixed(2) || '-'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">P/B Ratio</div>
                    <div className="font-semibold text-lg">{stock.pb_ratio?.toFixed(2) || '-'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">52W High</div>
                    <div className="font-semibold text-lg">{formatCurrency(stock.high_52w, 'USD')}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">52W Low</div>
                    <div className="font-semibold text-lg">{formatCurrency(stock.low_52w, 'USD')}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Dividend Yield</div>
                    <div className="font-semibold text-lg">{stock.dividend_yield ? formatPct(stock.dividend_yield * 100) : '-'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">EPS (TTM)</div>
                    <div className="font-semibold text-lg">{stock.eps ? formatCurrency(stock.eps, 'USD') : '-'}</div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="ai" className="mt-4">
              <DeepResearchPanel ticker={stock.ticker} />
            </TabsContent>

            <TabsContent value="news" className="mt-4 h-[600px]">
              <NewsFeed ticker={stock.ticker} />
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Column - AI Prediction & Technicals (1/3 width) */}
        <div className="space-y-6">
          {prediction ? (
            <PredictionCard prediction={prediction} />
          ) : (
            <Card className="h-64 flex items-center justify-center animate-pulse">
              <div className="text-muted-foreground">Analyzing...</div>
            </Card>
          )}
        </div>

      </div>
    </div>
  );
}
