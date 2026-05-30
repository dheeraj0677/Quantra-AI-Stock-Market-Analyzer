import { RefreshCw } from 'lucide-react';
import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { suggestionsApi } from '@/api/suggestions';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';

export function RefreshSuggestionsBtn() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const queryClient = useQueryClient();

  const handleRefresh = async () => {
    try {
      setIsRefreshing(true);
      await suggestionsApi.refreshSuggestions();
      toast.success('Suggestions refreshed');
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
    } catch (error) {
      toast.error('Failed to refresh suggestions');
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleRefresh}
      disabled={isRefreshing}
      className="h-8 gap-2 text-xs"
    >
      <RefreshCw className={`h-3 w-3 ${isRefreshing ? 'animate-spin' : ''}`} />
      Refresh AI Suggestions
    </Button>
  );
}
