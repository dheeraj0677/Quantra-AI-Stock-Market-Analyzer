export interface BacktestRequest {
  strategy_id: string;
  ticker: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  parameters?: Record<string, any>;
}

export interface BacktestResult {
  job_id: string;
  strategy_id: string;
  ticker: string;
  start_date: string;
  end_date: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'done' | 'error' | 'processing';
  created_at: string;
  metrics?: BacktestMetrics;
  equity_curve?: EquityPoint[];
  trades?: BacktestTrade[];
  error?: string;
  result?: any;
}

export interface BacktestMetrics {
  cagr: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  total_return: number;
  avg_trade_pnl: number;
}

export interface EquityPoint {
  date: string;
  value: number;
}

export interface BacktestTrade {
  date: string;
  ticker: string;
  entry_price: number;
  exit_price: number;
  pnl: number;
  pnl_pct: number;
  reason: string;
}
