import client from './client';
import type { AuthTokens, LoginRequest, RegisterRequest, PreferencesUpdate, User } from '../types/user';

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthTokens> => {
    const form = new URLSearchParams();
    form.append('username', data.email);
    form.append('password', data.password);
    const res = await client.post('/api/v1/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return res.data;
  },

  register: async (data: RegisterRequest): Promise<AuthTokens> => {
    const res = await client.post('/api/v1/auth/register', data);
    return res.data;
  },

  getMe: async (): Promise<User> => {
    const res = await client.get('/api/v1/auth/me');
    return res.data;
  },

  refresh: async (refreshToken: string): Promise<AuthTokens> => {
    const res = await client.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
    return res.data;
  },

  updatePreferences: async (data: PreferencesUpdate): Promise<User> => {
    const res = await client.patch('/api/v1/auth/preferences', data);
    return res.data;
  },
};
