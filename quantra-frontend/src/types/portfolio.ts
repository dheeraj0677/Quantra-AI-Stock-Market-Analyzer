export interface Portfolio {
  id: string;
  name: string;
  currency: string;
  total_invested: number;
  current_value: number;
  total_return: number;
  total_return_pct: number;
  day_pnl: number;
  day_pnl_pct: number;
  positions_count: number;
  created_at: string;
}

export interface Position {
  id: string;
  portfolio_id: string;
  ticker: string;
  name: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  pnl: number;
  pnl_pct: number;
  day_change: number;
  day_change_pct: number;
  opened_at: string;
}

export interface AddPositionRequest {
  ticker: string;
  quantity: number;
  avg_price: number;
}

export interface CreatePortfolioRequest {
  name: string;
  currency?: string;
}

export interface PortfolioAIAnalysis {
  diversity_score: number;
  risk_assessment: string;
  sector_breakdown: { sector: string; weight: number }[];
  rebalancing_suggestions: string[];
}
