export interface Stock {
  ticker: string;
  name: string;
  exchange: string;
  sector: string;
  industry: string;
  market_cap: number;
  current_price: number;
  change: number;
  change_pct: number;
  volume: number;
  pe_ratio: number | null;
  pb_ratio: number | null;
  dividend_yield: number | null;
  eps: number | null;
  roe: number | null;
  high_52w: number;
  low_52w: number;
}

export interface OHLCV {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TechnicalIndicators {
  rsi_14: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_hist: number | null;
  ema_9: number | null;
  ema_21: number | null;
  ema_50: number | null;
  ema_200: number | null;
  bb_upper: number | null;
  bb_middle: number | null;
  bb_lower: number | null;
  atr_14: number | null;
  obv: number | null;
  adx: number | null;
  stoch_k: number | null;
  stoch_d: number | null;
}

export interface StockSearchResult {
  ticker: string;
  name: string;
  exchange: string;
  sector: string;
}

export interface MarketSummary {
  index: string;
  value: number;
  change: number;
  change_pct: number;
}

export interface TopMover {
  ticker: string;
  name: string;
  price: number;
  change_pct: number;
  volume: number;
}

export interface SectorPerformance {
  sector: string;
  change_pct: number;
  market_cap: number;
}
