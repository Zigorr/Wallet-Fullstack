export enum CategoryType {
    INCOME = "INCOME",
    EXPENSE = "EXPENSE"
}

export interface Category {
    id: number;
    name: string;
    type: CategoryType;
    owner_id: number;
    color?: string;
} 