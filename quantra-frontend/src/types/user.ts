export interface User {
  id: string;
  email: string;
  name: string | null;
  plan: 'free' | 'pro' | 'premium';
  risk_profile: 'conservative' | 'moderate' | 'aggressive';
  preferred_sectors: string[] | null;
  investment_horizon: 'short' | 'medium' | 'long';
  created_at: string;
  last_login: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface PreferencesUpdate {
  risk_profile?: string;
  preferred_sectors?: string[];
  investment_horizon?: string;
}
