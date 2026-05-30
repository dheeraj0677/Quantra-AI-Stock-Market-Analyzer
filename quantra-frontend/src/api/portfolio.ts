import client from './client';
import type { Portfolio, Position, AddPositionRequest, CreatePortfolioRequest, PortfolioAIAnalysis } from '../types/portfolio';

export const portfolioApi = {
  getPortfolios: async (): Promise<Portfolio[]> => {
    const res = await client.get('/api/v1/portfolio');
    return res.data;
  },

  getPortfolio: async (id: string): Promise<Portfolio> => {
    const res = await client.get(`/api/v1/portfolio/${id}`);
    return res.data;
  },

  createPortfolio: async (data: CreatePortfolioRequest): Promise<Portfolio> => {
    const res = await client.post('/api/v1/portfolio', data);
    return res.data;
  },

  deletePortfolio: async (id: string): Promise<void> => {
    await client.delete(`/api/v1/portfolio/${id}`);
  },

  getPositions: async (portfolioId: string): Promise<Position[]> => {
    const res = await client.get(`/api/v1/portfolio/${portfolioId}/positions`);
    return res.data;
  },

  addPosition: async (portfolioId: string, data: AddPositionRequest): Promise<Position> => {
    const res = await client.post(`/api/v1/portfolio/${portfolioId}/positions`, data);
    return res.data;
  },

  removePosition: async (portfolioId: string, positionId: string): Promise<void> => {
    await client.delete(`/api/v1/portfolio/${portfolioId}/positions/${positionId}`);
  },

  getAIAnalysis: async (portfolioId: string): Promise<PortfolioAIAnalysis> => {
    const res = await client.get(`/api/v1/portfolio/${portfolioId}/analysis`);
    return res.data;
  },
};
