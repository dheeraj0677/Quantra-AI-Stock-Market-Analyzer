export type Direction = 'UP' | 'DOWN' | 'SIDEWAYS';

export interface Prediction {
  ticker: string;
  direction: Direction;
  confidence: number;
  ml_score: number;
  horizon: string;
  summary: string;
  factors: PredictionFactor[];
  sentiment_score: number;
  created_at: string;
}

export interface PredictionFactor {
  name: string;
  direction: 'bullish' | 'bearish' | 'neutral';
  weight: number;
  description: string;
}

export interface DeepResearchResult {
  job_id: string;
  status: 'pending' | 'processing' | 'done' | 'error';
  ticker: string;
  company_overview: string;
  support_levels: number[];
  resistance_levels: number[];
  chart_patterns: string[];
  sector_comparison: string;
  peer_stocks: string[];
  target_price: number | null;
  stop_loss: number | null;
  investment_suggestion: string;
  position_sizing: string;
  created_at: string;
}

export interface DeepResearchJob {
  job_id: string;
  status: 'pending' | 'processing' | 'done' | 'error';
  result?: DeepResearchResult;
}
