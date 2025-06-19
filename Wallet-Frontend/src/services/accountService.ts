import api from './api';
import { Account, AccountType } from '../models/Account';

export interface AccountCreateRequest {
  name: string;
  type: AccountType;
  initial_balance: number;
}

export interface AccountUpdateRequest {
  name?: string;
  type?: AccountType;
  initial_balance?: number;
}

export const accountService = {
  async getAccounts(): Promise<Account[]> {
    const response = await api.get('/accounts');
    return response.data;
  },

  async getAccount(id: number): Promise<Account> {
    const response = await api.get(`/accounts/${id}`);
    return response.data;
  },

  async createAccount(account: AccountCreateRequest): Promise<Account> {
    const response = await api.post('/accounts', account);
    return response.data;
  },

  async updateAccount(id: number, account: AccountUpdateRequest): Promise<Account> {
    const response = await api.put(`/accounts/${id}`, account);
    return response.data;
  },

  async deleteAccount(id: number): Promise<Account> {
    const response = await api.delete(`/accounts/${id}`);
    return response.data;
  },

  async getTotalBalance(): Promise<number> {
    const accounts = await this.getAccounts();
    return accounts.reduce((total, account) => total + account.initial_balance, 0);
  },
}; 