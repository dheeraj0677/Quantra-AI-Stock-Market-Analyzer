export interface NewsArticle {
  id: string;
  ticker: string;
  headline: string;
  summary: string;
  source: string;
  url: string;
  published_at: string;
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  sentiment_score: number;
  impact_level: 'high' | 'medium' | 'low';
}

export interface NewsFeedResponse {
  articles: NewsArticle[];
  total: number;
  page: number;
  page_size: number;
}
