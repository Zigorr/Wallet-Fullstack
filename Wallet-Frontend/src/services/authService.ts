import api from './api';
import { Currency } from '../models/Account';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  default_currency?: Currency;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  default_currency: Currency;
}

export const authService = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    return response.data;
  },

  async register(username: string, email: string, password: string, defaultCurrency: Currency = Currency.USD): Promise<User> {
    const response = await api.post('/auth/register', {
      username,
      email,
      password,
      default_currency: defaultCurrency,
    });
    
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No access token found');
    }

    const response = await api.get('/auth/users/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    
    return response.data;
  },

  async getPasswordValidationRules() {
    const response = await api.get('/auth/config/validation');
    return response.data;
  },

  async getCurrencies(): Promise<Currency[]> {
    const response = await api.get('/auth/currencies');
    return response.data.currencies;
  },
}; 