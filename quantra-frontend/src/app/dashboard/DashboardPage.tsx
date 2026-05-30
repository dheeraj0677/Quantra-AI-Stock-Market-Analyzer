import { MarketSummaryBar } from '@/components/market/MarketSummaryBar';
import { TopMoversTable } from '@/components/market/TopMoversTable';
import { MarketSentimentWidget } from '@/components/market/MarketSentimentWidget';
import { SuggestionFeed } from '@/components/suggestions/SuggestionFeed';
import { NewsFeed } from '@/components/news/NewsFeed';
import { useSSE } from '@/hooks/useSSE';

export function DashboardPage() {
  // Connect to SSE for live market updates
  useSSE();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Market Overview</h1>
        <p className="text-muted-foreground">Live market data and AI insights</p>
      </div>

      <MarketSummaryBar />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <TopMoversTable />
        <MarketSentimentWidget />
        <div className="col-span-1 md:col-span-2 lg:col-span-1">
          <NewsFeed />
        </div>
      </div>

      <div className="mt-4">
        <SuggestionFeed />
      </div>
    </div>
  );
}
