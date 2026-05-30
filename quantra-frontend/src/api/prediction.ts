import client from './client';
import type { Prediction, DeepResearchJob } from '../types/prediction';

export const predictionApi = {
  getQuickPrediction: async (ticker: string): Promise<Prediction> => {
    const res = await client.get(`/api/v1/prediction/${ticker}/quick`);
    return res.data;
  },

  startDeepResearch: async (ticker: string): Promise<{ job_id: string }> => {
    const res = await client.post(`/api/v1/prediction/${ticker}/deep`);
    return res.data;
  },

  pollDeep: async (ticker: string, jobId: string): Promise<DeepResearchJob> => {
    const res = await client.get(`/api/v1/prediction/${ticker}/deep/${jobId}`);
    return res.data;
  },
};
