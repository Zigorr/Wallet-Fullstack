import { format, formatDistanceToNow } from 'date-fns';
import { Currency } from '../models/Account';

// Currency to locale mapping for proper formatting with English numbers
const currencyLocales: Record<Currency, string> = {
  [Currency.USD]: 'en-US',
  [Currency.EUR]: 'en-GB', // Use UK English for EUR formatting
  [Currency.GBP]: 'en-GB',
  [Currency.EGP]: 'en-US', // Use English locale for EGP to get English numbers
};

// Currency symbols
const currencySymbols: Record<Currency, string> = {
  [Currency.USD]: '$',
  [Currency.EUR]: '€',
  [Currency.GBP]: '£',
  [Currency.EGP]: 'ج.م',
};

export const formatCurrency = (amount: number, currency: Currency = Currency.USD): string => {
  const locale = currencyLocales[currency];
  const symbol = currencySymbols[currency];
  
  try {
    // For EGP, use manual formatting to ensure English numbers with EGP symbol
    if (currency === Currency.EGP) {
      const formattedNumber = new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(amount);
      return `${symbol}${formattedNumber}`;
    }
    
    // For other currencies, use standard currency formatting
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  } catch (error) {
    // Fallback formatting if Intl.NumberFormat fails
    const formattedNumber = amount.toFixed(2);
    return `${symbol}${formattedNumber}`;
  }
};

export const getCurrencySymbol = (currency: Currency): string => {
  return currencySymbols[currency];
};

export const formatCurrencyCompact = (amount: number, currency: Currency = Currency.USD): string => {
  const symbol = currencySymbols[currency];
  
  if (Math.abs(amount) >= 1000000) {
    const formattedAmount = (amount / 1000000).toFixed(1);
    return `${symbol}${formattedAmount}M`;
  }
  if (Math.abs(amount) >= 1000) {
    const formattedAmount = (amount / 1000).toFixed(1);
    return `${symbol}${formattedAmount}K`;
  }
  const formattedAmount = amount.toFixed(2);
  return `${symbol}${formattedAmount}`;
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num);
};

export const formatDate = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return format(dateObj, 'MMM dd, yyyy');
};

export const formatDateTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return format(dateObj, 'MMM dd, yyyy • h:mm a');
};

export const formatTimeAgo = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return formatDistanceToNow(dateObj, { addSuffix: true });
};

export const formatPercentage = (value: number, decimals = 1): string => {
  return `${value.toFixed(decimals)}%`;
};

export const formatCompactNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

// Helper function to get user-friendly frequency labels
export const formatFrequency = (frequency: string): string => {
  const frequencies: Record<string, string> = {
    DAILY: 'Daily',
    WEEKLY: 'Weekly',
    MONTHLY: 'Monthly',
    QUARTERLY: 'Quarterly',
    YEARLY: 'Yearly',
  };
  return frequencies[frequency] || frequency;
};

// Helper function to format account types
export const formatAccountType = (accountType: string): string => {
  const accountTypes: Record<string, string> = {
    CHECKING: 'Checking',
    SAVINGS: 'Savings',
    CREDIT: 'Credit',
    DEBIT: 'Debit',
    INVESTMENT: 'Investment',
    CASH: 'Cash',
  };
  return accountTypes[accountType] || accountType;
}; 