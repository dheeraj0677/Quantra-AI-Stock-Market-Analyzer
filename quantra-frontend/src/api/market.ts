import client from './client';
import type { MarketSummary, TopMover, SectorPerformance } from '../types/stock';

export const marketApi = {
  getSummary: async (): Promise<MarketSummary[]> => {
    const res = await client.get('/api/v1/market/summary');
    return res.data;
  },

  getMovers: async (type: 'gainers' | 'losers' | 'active' = 'gainers'): Promise<TopMover[]> => {
    const res = await client.get('/api/v1/market/movers', { params: { type } });
    return res.data;
  },

  getSectors: async (): Promise<SectorPerformance[]> => {
    const res = await client.get('/api/v1/market/sectors');
    return res.data;
  },
};
