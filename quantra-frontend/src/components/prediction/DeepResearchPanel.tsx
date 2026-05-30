import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Brain, FileText, Loader2, PlayCircle, Target, TrendingDown, AlertTriangle } from 'lucide-react';
import { predictionApi } from '@/api/prediction';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatCurrency } from '@/utils/formatters';

export function DeepResearchPanel({ ticker }: { ticker: string }) {
  const [jobId, setJobId] = useState<string | null>(null);

  const { data: job, isLoading: isPolling } = useQuery({
    queryKey: ['deepResearch', ticker, jobId],
    queryFn: () => predictionApi.pollDeep(ticker, jobId!),
    enabled: !!jobId,
    refetchInterval: (data) => {
      // @ts-ignore
      if (data?.status === 'done' || data?.status === 'error') return false;
      return 3000;
    },
  });

  const [isStarting, setIsStarting] = useState(false);

  const handleStart = async () => {
    try {
      setIsStarting(true);
      const res = await predictionApi.startDeepResearch(ticker);
      setJobId(res.job_id);
    } catch (error) {
      console.error('Failed to start deep research', error);
    } finally {
      setIsStarting(false);
    }
  };

  if (!jobId) {
    return (
      <Card className="flex flex-col items-center justify-center p-8 text-center bg-gradient-to-br from-card to-accent/20">
        <Brain className="mb-4 h-12 w-12 text-primary" />
        <h3 className="mb-2 text-xl font-bold">Deep AI Research</h3>
        <p className="mb-6 max-w-md text-sm text-muted-foreground">
          Run a comprehensive analysis using multi-agent LLM reasoning to evaluate fundamentals, technicals, and news sentiment for {ticker}.
        </p>
        <Button onClick={handleStart} disabled={isStarting} size="lg" className="gap-2">
          {isStarting ? <Loader2 className="h-5 w-5 animate-spin" /> : <PlayCircle className="h-5 w-5" />}
          Run Deep Analysis
        </Button>
      </Card>
    );
  }

  if (isPolling || (job && (job.status === 'pending' || job.status === 'processing'))) {
    return (
      <Card className="flex flex-col items-center justify-center p-12 text-center">
        <Loader2 className="mb-4 h-10 w-10 animate-spin text-primary" />
        <h3 className="text-lg font-medium">Analyzing {ticker}...</h3>
        <p className="mt-2 text-sm text-muted-foreground animate-pulse">
          Our AI agents are gathering data, analyzing charts, and reading news...
        </p>
      </Card>
    );
  }

  if (job?.status === 'error' || !job?.result) {
    return (
      <Card className="flex flex-col items-center justify-center p-8 text-center border-destructive">
        <AlertTriangle className="mb-4 h-10 w-10 text-destructive" />
        <h3 className="text-lg font-medium text-destructive">Analysis Failed</h3>
        <p className="mt-2 text-sm text-muted-foreground">There was an error running the deep analysis.</p>
        <Button onClick={() => setJobId(null)} variant="outline" className="mt-4">Try Again</Button>
      </Card>
    );
  }

  const result = job.result;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          Deep Research Results
        </CardTitle>
        <CardDescription>Comprehensive AI evaluation for {ticker}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border p-4 bg-accent/30">
            <h4 className="flex items-center gap-2 text-sm font-semibold mb-2">
              <Target className="h-4 w-4 text-emerald-500" /> Target Price
            </h4>
            <div className="text-2xl font-bold">
              {result.target_price ? formatCurrency(result.target_price, 'USD') : 'N/A'}
            </div>
          </div>
          <div className="rounded-lg border p-4 bg-accent/30">
            <h4 className="flex items-center gap-2 text-sm font-semibold mb-2">
              <TrendingDown className="h-4 w-4 text-red-500" /> Stop Loss
            </h4>
            <div className="text-2xl font-bold">
              {result.stop_loss ? formatCurrency(result.stop_loss, 'USD') : 'N/A'}
            </div>
          </div>
        </div>

        <div>
          <h4 className="flex items-center gap-2 text-base font-semibold mb-2">
            <FileText className="h-4 w-4" /> Company Overview
          </h4>
          <p className="text-sm text-muted-foreground leading-relaxed">{result.company_overview}</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <h4 className="text-sm font-semibold mb-2">Key Support Levels</h4>
            <div className="flex flex-wrap gap-2">
              {result.support_levels.map((lvl, i) => (
                <div key={i} className="rounded bg-emerald-500/10 px-2 py-1 text-sm font-medium text-emerald-500 border border-emerald-500/20">
                  {formatCurrency(lvl, 'USD')}
                </div>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-sm font-semibold mb-2">Key Resistance Levels</h4>
            <div className="flex flex-wrap gap-2">
              {result.resistance_levels.map((lvl, i) => (
                <div key={i} className="rounded bg-red-500/10 px-2 py-1 text-sm font-medium text-red-500 border border-red-500/20">
                  {formatCurrency(lvl, 'USD')}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-semibold mb-2">Investment Suggestion</h4>
          <div className="rounded-md bg-primary/10 p-4 border border-primary/20">
            <p className="text-sm">{result.investment_suggestion}</p>
          </div>
        </div>

        <div className="text-xs text-muted-foreground text-right border-t pt-4">
          Analysis completed at {new Date(result.created_at).toLocaleString()}
        </div>
      </CardContent>
    </Card>
  );
}
