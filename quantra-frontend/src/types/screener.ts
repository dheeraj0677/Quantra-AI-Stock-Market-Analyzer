export interface ScreenerFilter {
  field: string;
  operator: '>' | '<' | '>=' | '<=' | '=' | 'between' | 'in';
  value: string | number | number[] | string[];
}

export interface ScreenerRequest {
  filters: ScreenerFilter[];
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
  limit?: number;
}

export interface ScreenerResult {
  ticker: string;
  name: string;
  sector: string;
  price: number;
  change_pct: number;
  ml_score: number;
  direction: string;
  rsi: number | null;
  sentiment: number | null;
  pe: number | null;
  volume: number;
}

export interface ScreenerPreset {
  id: string;
  name: string;
  description: string;
  filters: ScreenerFilter[];
}

export const SCREENER_FIELDS = [
  { value: 'pe_ratio', label: 'P/E Ratio', type: 'number' },
  { value: 'pb_ratio', label: 'P/B Ratio', type: 'number' },
  { value: 'rsi_14', label: 'RSI (14)', type: 'number' },
  { value: 'macd_signal', label: 'MACD Signal', type: 'number' },
  { value: 'ml_score', label: 'ML Score', type: 'number' },
  { value: 'sentiment_score', label: 'Sentiment Score', type: 'number' },
  { value: 'market_cap', label: 'Market Cap', type: 'number' },
  { value: 'sector', label: 'Sector', type: 'string' },
  { value: 'direction', label: 'Direction', type: 'string' },
  { value: 'volume_spike', label: 'Volume Spike %', type: 'number' },
] as const;

export const SCREENER_OPERATORS = {
  number: ['>', '<', '>=', '<=', '=', 'between'],
  string: ['=', 'in'],
} as const;
