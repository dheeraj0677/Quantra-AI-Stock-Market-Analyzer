import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { Prediction, PredictionFactor } from '@/types/prediction';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { directionColors } from '@/utils/colors';
import { Badge } from '@/components/ui/badge';

export function ConfidenceMeter({ confidence }: { confidence: number }) {
  const pct = confidence * 100;
  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between text-xs font-medium text-muted-foreground">
        <span>Confidence</span>
        <span>{pct.toFixed(0)}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
        <div 
          className="h-full bg-primary transition-all duration-500 ease-in-out" 
          style={{ width: `${pct}%` }} 
        />
      </div>
    </div>
  );
}

export function FactorList({ factors }: { factors: PredictionFactor[] }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold">Key Driving Factors</h4>
      <div className="space-y-2">
        {factors.map((factor, i) => (
          <div key={i} className="flex flex-col gap-1 rounded-md border p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{factor.name}</span>
              <Badge variant="outline" className={`text-[10px] ${
                factor.direction === 'bullish' ? 'text-emerald-500' :
                factor.direction === 'bearish' ? 'text-red-500' : 'text-amber-500'
              }`}>
                {factor.direction}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">{factor.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function PredictionCard({ prediction }: { prediction: Prediction }) {
  const color = directionColors[prediction.direction];
  const Icon = prediction.direction === 'UP' ? TrendingUp : 
               prediction.direction === 'DOWN' ? TrendingDown : Minus;

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base font-semibold">AI Prediction</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className={`flex flex-col items-center justify-center rounded-lg border p-6 text-center ${color.bg} ${color.border}`}>
          <Icon className={`mb-2 h-10 w-10 ${color.text}`} />
          <h3 className={`text-2xl font-bold uppercase tracking-widest ${color.text}`}>
            {prediction.direction}
          </h3>
          <p className="mt-1 text-sm text-muted-foreground">{prediction.horizon} horizon</p>
        </div>

        <ConfidenceMeter confidence={prediction.confidence} />

        <div className="rounded-md bg-accent/50 p-4">
          <p className="text-sm italic text-muted-foreground">"{prediction.summary}"</p>
        </div>

        <FactorList factors={prediction.factors} />
      </CardContent>
    </Card>
  );
}
