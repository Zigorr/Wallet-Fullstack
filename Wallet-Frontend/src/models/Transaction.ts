export enum TransactionType {
    INCOME = "INCOME",
    EXPENSE = "EXPENSE",
    TRANSFER = "TRANSFER",
}

export interface Transaction {
  id: number;
  amount: number;
  type: TransactionType;
  description?: string;
  date: string;
  account_id: number;
  category_id?: number;
  owner_id: number;
} 