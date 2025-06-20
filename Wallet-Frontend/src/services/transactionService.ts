import api from './api';
import { Transaction, TransactionType } from '../models/Transaction';

export interface TransactionCreateRequest {
  amount: number;
  type: TransactionType;
  description?: string;
  account_id: number;
  category_id?: number;
}

export interface TransactionUpdateRequest {
  amount?: number;
  type?: TransactionType;
  description?: string;
  account_id?: number;
  category_id?: number;
}

export interface TransferCreateRequest {
  from_account_id: number;
  to_account_id: number;
  amount: number;
  converted_amount?: number;
  description?: string;
}

export interface TransferResponse {
  expense: Transaction;
  income: Transaction;
  exchange_rate: number;
  converted_amount: number;
}

export const transactionService = {
  async getTransactions(skip = 0, limit = 100): Promise<Transaction[]> {
    const response = await api.get(`/transactions?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async getTransaction(id: number): Promise<Transaction> {
    const response = await api.get(`/transactions/${id}`);
    return response.data;
  },

  async createTransaction(transaction: TransactionCreateRequest): Promise<Transaction> {
    const response = await api.post('/transactions', transaction);
    return response.data;
  },

  async updateTransaction(id: number, transaction: TransactionUpdateRequest): Promise<Transaction> {
    const response = await api.put(`/transactions/${id}`, transaction);
    return response.data;
  },

  async deleteTransaction(id: number): Promise<Transaction> {
    const response = await api.delete(`/transactions/${id}`);
    return response.data;
  },

  async createTransfer(transfer: TransferCreateRequest): Promise<TransferResponse> {
    const response = await api.post('/transactions/transfers', transfer);
    return response.data;
  },

  async getExchangeRates(): Promise<Record<string, number>> {
    const response = await api.get('/transactions/exchange-rates');
    return response.data;
  },

  async getRecentTransactions(limit = 10): Promise<Transaction[]> {
    const response = await api.get(`/transactions?skip=0&limit=${limit}`);
    return response.data;
  },

  async getMonthlyIncome(): Promise<number> {
    const transactions = await this.getTransactions();
    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();
    
    return transactions
      .filter(t => {
        const transactionDate = new Date(t.date);
        return transactionDate.getMonth() === currentMonth && 
               transactionDate.getFullYear() === currentYear &&
               t.type === 'INCOME';
      })
      .reduce((total, t) => total + t.amount, 0);
  },

  async getMonthlyExpenses(): Promise<number> {
    const transactions = await this.getTransactions();
    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();
    
    return transactions
      .filter(t => {
        const transactionDate = new Date(t.date);
        return transactionDate.getMonth() === currentMonth && 
               transactionDate.getFullYear() === currentYear &&
               t.type === 'EXPENSE';
      })
      .reduce((total, t) => total + Math.abs(t.amount), 0);
  },

  async getWeeklySpending(): Promise<{ day: string; amount: number }[]> {
    const transactions = await this.getTransactions();
    const lastWeek = new Date();
    lastWeek.setDate(lastWeek.getDate() - 7);
    
    const weeklyData = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return {
        day: date.toLocaleDateString('en-US', { weekday: 'short' }),
        amount: 0
      };
    });

    transactions
      .filter(t => {
        const transactionDate = new Date(t.date);
        return transactionDate >= lastWeek && t.type === 'EXPENSE';
      })
      .forEach(t => {
        const dayIndex = new Date(t.date).getDay();
        const adjustedIndex = dayIndex === 0 ? 6 : dayIndex - 1; // Adjust for Monday start
        if (weeklyData[adjustedIndex]) {
          weeklyData[adjustedIndex].amount += Math.abs(t.amount);
        }
      });

    return weeklyData;
  },
}; 