import { Link } from 'react-router-dom';
import { Bot, ArrowRight, BrainCircuit } from 'lucide-react';
import type { Suggestion } from '@/api/suggestions';
import { suggestionActionColors } from '@/utils/colors';
import { formatCurrency, formatRelativeTime } from '@/utils/formatters';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export function SuggestionCard({ suggestion }: { suggestion: Suggestion }) {
  const actionColor = suggestionActionColors[suggestion.action] || suggestionActionColors.WATCH;

  return (
    <Card className={`relative overflow-hidden transition-all hover:shadow-md border ${actionColor.border}`}>
      <div className={`absolute top-0 left-0 w-1 h-full ${actionColor.bg}`} />
      <CardContent className="p-4 sm:p-5">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-full ${actionColor.bg} ${actionColor.text}`}>
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <Link to={`/stocks/${suggestion.ticker}`} className="font-bold hover:underline">
                  {suggestion.ticker}
                </Link>
                <Badge variant="outline" className={`text-[10px] uppercase ${actionColor.text} ${actionColor.border}`}>
                  {suggestion.action}
                </Badge>
              </div>
              <div className="text-xs text-muted-foreground">{suggestion.name}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-semibold">{formatCurrency(suggestion.current_price, 'USD')}</div>
            <div className="text-xs text-muted-foreground flex items-center justify-end gap-1">
              <BrainCircuit className="h-3 w-3" />
              {(suggestion.confidence * 100).toFixed(0)}% Conf
            </div>
          </div>
        </div>

        <div className="mt-4">
          <p className="text-sm line-clamp-2 text-muted-foreground">{suggestion.reasoning}</p>
        </div>

        <div className="mt-4 flex items-center justify-between border-t pt-3">
          <div className="text-xs text-muted-foreground">
            {formatRelativeTime(suggestion.generated_at)}
          </div>
          <Link
            to={`/stocks/${suggestion.ticker}`}
            className="flex items-center text-xs font-medium text-primary hover:underline"
          >
            View Analysis <ArrowRight className="ml-1 h-3 w-3" />
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
