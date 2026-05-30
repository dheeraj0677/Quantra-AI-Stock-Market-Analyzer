import client from './client';

export interface Suggestion {
  id: string;
  ticker: string;
  name: string;
  action: 'BUY' | 'WATCH' | 'AVOID';
  ml_score: number;
  confidence: number;
  current_price: number;
  target_price: number | null;
  risk_level: 'low' | 'medium' | 'high';
  reasoning: string;
  generated_at: string;
  is_read: boolean;
}

export const suggestionsApi = {
  getSuggestions: async (): Promise<Suggestion[]> => {
    const res = await client.get('/api/v1/suggestions');
    return res.data;
  },

  refreshSuggestions: async (): Promise<{ status: string }> => {
    const res = await client.post('/api/v1/suggestions/refresh');
    return res.data;
  },

  markRead: async (id: string): Promise<void> => {
    await client.patch(`/api/v1/suggestions/${id}/read`);
  },
};
