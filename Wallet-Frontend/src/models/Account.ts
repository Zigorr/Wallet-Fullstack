export enum AccountType {
    CHECKING = "CHECKING",
    SAVINGS = "SAVINGS",
    CREDIT = "CREDIT",
    INVESTMENT = "INVESTMENT",
    CASH = "CASH"
}

export interface Account {
    id: number;
    name: string;
    type: AccountType;
    initial_balance: number;
    owner_id: number;
} 