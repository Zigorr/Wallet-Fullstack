export enum AccountType {
    CHECKING = "CHECKING",
    SAVINGS = "SAVINGS",
    CREDIT = "CREDIT",
    DEBIT = "DEBIT",
    INVESTMENT = "INVESTMENT",
    CASH = "CASH"
}

export enum Currency {
    USD = "USD",
    EGP = "EGP",
    GBP = "GBP",
    EUR = "EUR"
}

export interface Account {
    id: number;
    name: string;
    type: AccountType;
    initial_balance: number;
    currency: Currency;
    owner_id: number;
} 