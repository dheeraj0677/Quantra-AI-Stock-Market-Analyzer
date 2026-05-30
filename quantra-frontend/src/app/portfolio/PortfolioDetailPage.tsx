import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Plus, ArrowLeft, TrendingUp, TrendingDown } from 'lucide-react';
import { portfolioApi } from '@/api/portfolio';
import { formatCurrency, formatPct } from '@/utils/formatters';
import { getPnLColor } from '@/utils/colors';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Link } from 'react-router-dom';
import { useSSE } from '@/hooks/useSSE';

export function PortfolioDetailPage() {
  const { id } = useParams<{ id: string }>();
  useSSE(); // For live price updates

  const { data: portfolio, isLoading: isPortfolioLoading } = useQuery({
    queryKey: ['portfolio', id],
    queryFn: () => portfolioApi.getPortfolio(id!),
    enabled: !!id,
  });

  const { data: positions, isLoading: isPositionsLoading } = useQuery({
    queryKey: ['positions', id],
    queryFn: () => portfolioApi.getPositions(id!),
    enabled: !!id,
  });

  const { data: analysis } = useQuery({
    queryKey: ['portfolioAnalysis', id],
    queryFn: () => portfolioApi.getAIAnalysis(id!),
    enabled: !!id,
  });

  if (isPortfolioLoading || !portfolio) {
    return <div className="p-8 text-center">Loading portfolio...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to="/portfolio" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4 transition-colors">
          <ArrowLeft className="mr-1 h-4 w-4" /> Back to Portfolios
        </Link>
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{portfolio.name}</h1>
            <p className="text-muted-foreground">Detailed view and AI analysis</p>
          </div>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Add Position
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Current Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(portfolio.current_value, portfolio.currency)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Invested</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(portfolio.total_invested, portfolio.currency)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Return</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`flex items-center gap-2 text-2xl font-bold ${getPnLColor(portfolio.total_return)}`}>
              {portfolio.total_return >= 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
              {portfolio.total_return > 0 ? '+' : ''}{formatCurrency(portfolio.total_return, portfolio.currency)}
            </div>
            <p className={`text-xs mt-1 ${getPnLColor(portfolio.total_return_pct)}`}>
              {formatPct(portfolio.total_return_pct)} all time
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Day P&L</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getPnLColor(portfolio.day_pnl)}`}>
              {portfolio.day_pnl > 0 ? '+' : ''}{formatCurrency(portfolio.day_pnl, portfolio.currency)}
            </div>
            <p className={`text-xs mt-1 ${getPnLColor(portfolio.day_pnl_pct)}`}>
              {formatPct(portfolio.day_pnl_pct)} today
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Positions Table (Takes 2/3 space) */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Positions</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted/50 text-muted-foreground">
                  <tr className="border-b text-left">
                    <th className="font-medium p-4">Asset</th>
                    <th className="font-medium p-4 text-right">Qty</th>
                    <th className="font-medium p-4 text-right">Avg Price</th>
                    <th className="font-medium p-4 text-right">Current Price</th>
                    <th className="font-medium p-4 text-right">Total P&L</th>
                    <th className="font-medium p-4 text-right hidden sm:table-cell">Day P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {isPositionsLoading ? (
                    <tr><td colSpan={6} className="p-8 text-center text-muted-foreground">Loading positions...</td></tr>
                  ) : !positions || positions.length === 0 ? (
                    <tr><td colSpan={6} className="p-8 text-center text-muted-foreground">No positions in this portfolio</td></tr>
                  ) : (
                    positions.map((pos) => (
                      <tr key={pos.id} className="border-b transition-colors hover:bg-muted/50 last:border-0">
                        <td className="p-4 font-semibold">
                          <Link to={`/stocks/${pos.ticker}`} className="hover:underline text-primary">
                            {pos.ticker}
                          </Link>
                          <div className="text-xs font-normal text-muted-foreground truncate w-24 md:w-auto">{pos.name}</div>
                        </td>
                        <td className="p-4 text-right">{pos.quantity}</td>
                        <td className="p-4 text-right">{formatCurrency(pos.avg_price, portfolio.currency)}</td>
                        <td className="p-4 text-right">{formatCurrency(pos.current_price, portfolio.currency)}</td>
                        <td className="p-4 text-right">
                          <div className={`font-semibold ${getPnLColor(pos.pnl)}`}>
                            {pos.pnl > 0 ? '+' : ''}{formatCurrency(pos.pnl, portfolio.currency)}
                          </div>
                          <div className={`text-xs ${getPnLColor(pos.pnl_pct)}`}>
                            {formatPct(pos.pnl_pct)}
                          </div>
                        </td>
                        <td className="p-4 text-right hidden sm:table-cell">
                          <div className={`font-semibold ${getPnLColor(pos.day_change)}`}>
                            {pos.day_change > 0 ? '+' : ''}{formatCurrency(pos.day_change, portfolio.currency)}
                          </div>
                          <div className={`text-xs ${getPnLColor(pos.day_change_pct)}`}>
                            {formatPct(pos.day_change_pct)}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* AI Analysis (Takes 1/3 space) */}
        <Card className="lg:col-span-1 border-primary/20 bg-primary/5">
          <CardHeader>
            <CardTitle className="text-primary flex items-center gap-2">
              Portfolio AI Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {!analysis ? (
              <div className="text-center text-sm text-muted-foreground animate-pulse">Generating insights...</div>
            ) : (
              <>
                <div>
                  <div className="text-sm font-semibold mb-1">Diversity Score</div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 flex-1 rounded-full bg-secondary overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${analysis.diversity_score}%` }} />
                    </div>
                    <span className="text-sm font-medium">{analysis.diversity_score}/100</span>
                  </div>
                </div>

                <div>
                  <div className="text-sm font-semibold mb-1">Risk Assessment</div>
                  <p className="text-sm text-muted-foreground">{analysis.risk_assessment}</p>
                </div>

                <div>
                  <div className="text-sm font-semibold mb-2">Rebalancing Suggestions</div>
                  <ul className="space-y-2">
                    {analysis.rebalancing_suggestions.map((s, i) => (
                      <li key={i} className="text-sm bg-background p-2 rounded border flex items-start gap-2">
                        <span className="text-primary mt-0.5">•</span>
                        <span className="text-muted-foreground leading-snug">{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
