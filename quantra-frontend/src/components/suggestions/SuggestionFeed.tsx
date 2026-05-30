import { useQuery } from '@tanstack/react-query';
import { Lightbulb } from 'lucide-react';
import { suggestionsApi } from '@/api/suggestions';
import { SuggestionCard } from './SuggestionCard';
import { RefreshSuggestionsBtn } from './RefreshSuggestionsBtn';

export function SuggestionFeed() {
  const { data: suggestions, isLoading } = useQuery({
    queryKey: ['suggestions'],
    queryFn: suggestionsApi.getSuggestions,
    refetchInterval: 300000, // 5 min
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-lg font-semibold tracking-tight">
          <Lightbulb className="h-5 w-5 text-amber-500" />
          AI Trading Ideas
        </h2>
        <RefreshSuggestionsBtn />
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 animate-pulse rounded-xl bg-card border" />
          ))}
        </div>
      ) : !suggestions || suggestions.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border bg-card py-12 text-center text-muted-foreground">
          <Lightbulb className="mb-2 h-8 w-8 opacity-20" />
          <p>No active suggestions</p>
          <p className="text-xs">The AI is currently analyzing the market.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {suggestions.map((suggestion) => (
            <SuggestionCard key={suggestion.id} suggestion={suggestion} />
          ))}
        </div>
      )}
    </div>
  );
}
