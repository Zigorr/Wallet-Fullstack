import api from './api';
import { RecurringTransaction, RecurrenceFrequency, TransactionType } from '../models/Transaction';
import { Currency } from '../models/Account';

export interface CreateRecurringTransactionData {
  name: string;
  amount: number;
  type: TransactionType;
  description?: string;
  currency: Currency;
  frequency: RecurrenceFrequency;
  start_date: string;
  end_date?: string;
  account_id: number;
  category_id?: number;
}

export interface UpdateRecurringTransactionData {
  name?: string;
  amount?: number;
  type?: TransactionType;
  description?: string;
  currency?: Currency;
  frequency?: RecurrenceFrequency;
  start_date?: string;
  end_date?: string;
  account_id?: number;
  category_id?: number;
  is_active?: boolean;
}

export const recurringTransactionService = {
  async getRecurringTransactions(skip: number = 0, limit: number = 100, activeOnly: boolean = false): Promise<RecurringTransaction[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      active_only: activeOnly.toString(),
    });
    
    const response = await api.get(`/recurring-transactions?${params}`);
    return response.data;
  },

  async getRecurringTransaction(id: number): Promise<RecurringTransaction> {
    const response = await api.get(`/recurring-transactions/${id}`);
    return response.data;
  },

  async createRecurringTransaction(data: CreateRecurringTransactionData): Promise<RecurringTransaction> {
    const response = await api.post('/recurring-transactions', data);
    return response.data;
  },

  async updateRecurringTransaction(id: number, data: UpdateRecurringTransactionData): Promise<RecurringTransaction> {
    const response = await api.put(`/recurring-transactions/${id}`, data);
    return response.data;
  },

  async deleteRecurringTransaction(id: number): Promise<RecurringTransaction> {
    const response = await api.delete(`/recurring-transactions/${id}`);
    return response.data;
  },

  async processRecurringTransaction(id: number) {
    const response = await api.post(`/recurring-transactions/${id}/process`);
    return response.data;
  },

  async processDueTransactions() {
    const response = await api.post('/recurring-transactions/process-due');
    return response.data;
  },
}; 