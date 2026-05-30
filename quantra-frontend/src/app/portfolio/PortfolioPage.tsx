import { useQuery } from '@tanstack/react-query';
import { Plus, Wallet, PieChart as PieChartIcon } from 'lucide-react';
import { portfolioApi } from '@/api/portfolio';
import { formatCurrency, formatPct } from '@/utils/formatters';
import { getPnLColor } from '@/utils/colors';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Link } from 'react-router-dom';

export function PortfolioPage() {
  const { data: portfolios, isLoading } = useQuery({
    queryKey: ['portfolios'],
    queryFn: portfolioApi.getPortfolios,
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Portfolios</h1>
          <p className="text-muted-foreground">Manage your investments and track performance</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Create Portfolio
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="h-48 animate-pulse bg-muted/50" />
          ))}
        </div>
      ) : !portfolios || portfolios.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-12 text-center">
          <Wallet className="mb-4 h-12 w-12 text-muted-foreground opacity-20" />
          <h3 className="text-lg font-medium">No Portfolios Yet</h3>
          <p className="mt-2 mb-6 text-sm text-muted-foreground">
            Create your first portfolio to start tracking your investments.
          </p>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Create Portfolio
          </Button>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {portfolios.map((p) => (
            <Link key={p.id} to={`/portfolio/${p.id}`}>
              <Card className="h-full transition-all hover:border-primary/50 hover:shadow-md cursor-pointer">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex justify-between items-start">
                    <span className="flex items-center gap-2">
                      <PieChartIcon className="h-5 w-5 text-primary" />
                      {p.name}
                    </span>
                    <span className="text-xs font-normal text-muted-foreground px-2 py-1 rounded bg-secondary">
                      {p.currency}
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mt-2 space-y-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Current Value</div>
                      <div className="text-2xl font-bold">{formatCurrency(p.current_value, p.currency)}</div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-xs text-muted-foreground">Total Return</div>
                        <div className={`font-semibold ${getPnLColor(p.total_return)}`}>
                          {p.total_return > 0 ? '+' : ''}{formatCurrency(p.total_return, p.currency)} ({formatPct(p.total_return_pct)})
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-muted-foreground">Day P&L</div>
                        <div className={`font-semibold ${getPnLColor(p.day_pnl)}`}>
                          {p.day_pnl > 0 ? '+' : ''}{formatCurrency(p.day_pnl, p.currency)} ({formatPct(p.day_pnl_pct)})
                        </div>
                      </div>
                    </div>

                    <div className="text-xs text-muted-foreground flex justify-between pt-2 border-t">
                      <span>{p.positions_count} positions</span>
                      <span>Invested: {formatCurrency(p.total_invested, p.currency)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
