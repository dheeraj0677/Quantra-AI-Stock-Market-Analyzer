import client from './client';
import type { NewsFeedResponse } from '../types/news';

export const newsApi = {
  getFeed: async (page = 1, pageSize = 20): Promise<NewsFeedResponse> => {
    const res = await client.get('/api/v1/news', { params: { page, page_size: pageSize } });
    return res.data;
  },

  getStockNews: async (ticker: string, page = 1, pageSize = 20): Promise<NewsFeedResponse> => {
    const res = await client.get(`/api/v1/news/${ticker}`, { params: { page, page_size: pageSize } });
    return res.data;
  },
};
