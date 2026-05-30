import client from './client';

export interface Alert {
  id: string;
  ticker: string;
  condition: string;
  threshold: number;
  is_active: boolean;
  triggered_at: string | null;
  created_at: string;
}

export interface CreateAlertRequest {
  ticker: string;
  condition: string;
  threshold: number;
}

export const alertsApi = {
  getAlerts: async (): Promise<Alert[]> => {
    const res = await client.get('/api/v1/alerts');
    return res.data;
  },

  createAlert: async (data: CreateAlertRequest): Promise<Alert> => {
    const res = await client.post('/api/v1/alerts', data);
    return res.data;
  },

  deleteAlert: async (id: string): Promise<void> => {
    await client.delete(`/api/v1/alerts/${id}`);
  },

  toggleAlert: async (id: string, isActive: boolean): Promise<Alert> => {
    const res = await client.patch(`/api/v1/alerts/${id}`, { is_active: isActive });
    return res.data;
  },
};
