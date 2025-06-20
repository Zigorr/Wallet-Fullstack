import { Currency } from './Account';

export enum TransactionType {
    INCOME = "INCOME",
    EXPENSE = "EXPENSE",
    TRANSFER = "TRANSFER",
}

export enum RecurrenceFrequency {
    DAILY = "DAILY",
    WEEKLY = "WEEKLY",
    MONTHLY = "MONTHLY",
    QUARTERLY = "QUARTERLY",
    YEARLY = "YEARLY",
}

export interface Transaction {
  id: number;
  amount: number;
  type: TransactionType;
  description?: string;
  date: string;
  currency: Currency;
  account_id: number;
  category_id?: number;
  owner_id: number;
  recurring_transaction_id?: number;
}

export interface RecurringTransaction {
  id: number;
  name: string;
  amount: number;
  type: TransactionType;
  description?: string;
  currency: Currency;
  frequency: RecurrenceFrequency;
  start_date: string;
  end_date?: string;
  next_due_date: string;
  is_active: boolean;
  created_at: string;
  account_id: number;
  category_id?: number;
  owner_id: number;
} 