import client from './client';
import type { BacktestRequest, BacktestResult } from '../types/backtest';

export const backtestApi = {
  run: async (data: BacktestRequest): Promise<{ job_id: string }> => {
    const res = await client.post('/api/v1/backtest/run', data);
    return res.data;
  },

  poll: async (jobId: string): Promise<BacktestResult> => {
    const res = await client.get(`/api/v1/backtest/${jobId}`);
    return res.data;
  },

  getHistory: async (): Promise<BacktestResult[]> => {
    const res = await client.get('/api/v1/backtest');
    return res.data;
  },
};
