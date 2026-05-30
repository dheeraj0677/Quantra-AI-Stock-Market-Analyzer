import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import type { NewsArticle } from '@/types/news';
import { formatRelativeTime } from '@/utils/formatters';
import { SentimentBadge } from './SentimentBadge';

export function NewsCard({ article }: { article: NewsArticle }) {
  return (
    <div className="flex flex-col gap-2 rounded-lg border bg-card p-4 transition-colors hover:bg-accent/20">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Link to={`/stocks/${article.ticker}`} className="font-semibold text-foreground hover:underline">
              {article.ticker}
            </Link>
            <span>•</span>
            <span>{article.source}</span>
            <span>•</span>
            <span>{formatRelativeTime(article.published_at)}</span>
          </div>
          <h3 className="font-medium leading-snug">
            <a href={article.url} target="_blank" rel="noopener noreferrer" className="hover:underline hover:text-primary transition-colors flex items-start gap-1">
              {article.headline}
              <ExternalLink className="h-3 w-3 mt-1 opacity-50 flex-shrink-0" />
            </a>
          </h3>
        </div>
      </div>
      <p className="text-sm text-muted-foreground line-clamp-2">{article.summary}</p>
      <div className="flex items-center justify-between mt-2">
        <SentimentBadge sentiment={article.sentiment} score={article.sentiment_score} />
        {article.impact_level === 'high' && (
          <span className="text-[10px] font-bold uppercase tracking-wider text-red-500 bg-red-500/10 px-2 py-0.5 rounded">High Impact</span>
        )}
      </div>
    </div>
  );
}
