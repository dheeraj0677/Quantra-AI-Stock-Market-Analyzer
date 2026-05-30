import client from './client';
import type { ScreenerRequest, ScreenerResult, ScreenerPreset } from '../types/screener';

export const screenerApi = {
  run: async (request: ScreenerRequest): Promise<ScreenerResult[]> => {
    const res = await client.post('/api/v1/screener/run', request);
    return res.data;
  },

  getPresets: async (): Promise<ScreenerPreset[]> => {
    const res = await client.get('/api/v1/screener/presets');
    return res.data;
  },

  getFields: async (): Promise<{ fields: string[] }> => {
    const res = await client.get('/api/v1/screener/fields');
    return res.data;
  },
};
