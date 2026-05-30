import { useQuery } from '@tanstack/react-query';
import { Newspaper } from 'lucide-react';
import { newsApi } from '@/api/news';
import { NewsCard } from './NewsCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

export function NewsFeed({ ticker }: { ticker?: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['news', ticker],
    queryFn: () => ticker ? newsApi.getStockNews(ticker) : newsApi.getFeed(),
    refetchInterval: 300000, // 5 min
  });

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3 border-b">
        <CardTitle className="flex items-center gap-2 text-base">
          <Newspaper className="h-5 w-5 text-primary" />
          {ticker ? `${ticker} News` : 'Market News'}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        <ScrollArea className="h-[400px] w-full p-4">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-32 animate-pulse rounded-lg bg-muted" />
              ))}
            </div>
          ) : !data || data.articles.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center text-muted-foreground p-8">
              <Newspaper className="mb-2 h-8 w-8 opacity-20" />
              <p>No news available</p>
            </div>
          ) : (
            <div className="space-y-4 pr-4">
              {data.articles.map((article) => (
                <NewsCard key={article.id} article={article} />
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
