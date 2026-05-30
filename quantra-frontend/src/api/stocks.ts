import client from './client';
import type { Stock, OHLCV, TechnicalIndicators, StockSearchResult } from '../types/stock';

export const stocksApi = {
  getStock: async (ticker: string): Promise<Stock> => {
    const res = await client.get(`/api/v1/stocks/${ticker}`);
    return res.data;
  },

  getOHLCV: async (ticker: string, interval = '1d', range = '3mo'): Promise<OHLCV[]> => {
    const res = await client.get(`/api/v1/stocks/${ticker}/ohlcv`, {
      params: { interval, range },
    });
    return res.data;
  },

  getTechnicals: async (ticker: string): Promise<TechnicalIndicators> => {
    const res = await client.get(`/api/v1/stocks/${ticker}/technicals`);
    return res.data;
  },

  search: async (query: string): Promise<StockSearchResult[]> => {
    const res = await client.get('/api/v1/stocks/search', { params: { q: query } });
    return res.data;
  },
};
