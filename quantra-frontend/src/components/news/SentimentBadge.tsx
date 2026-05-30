import { Badge } from '@/components/ui/badge';
import { sentimentColors } from '@/utils/colors';

export function SentimentBadge({ sentiment, score, className = '' }: { sentiment: string; score?: number; className?: string }) {
  const color = sentimentColors[sentiment] || sentimentColors.NEUTRAL;
  
  return (
    <Badge variant="outline" className={`${color.bg} ${color.text} border-0 font-medium ${className}`}>
      {sentiment} {score !== undefined ? `(${(score * 100).toFixed(0)})` : ''}
    </Badge>
  );
}
