import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import { transactionService } from '../services/transactionService';
import { accountService } from '../services/accountService';
import { formatCurrency, formatPercentage, formatAccountType } from '../utils/formatters';
import { Currency } from '../models/Account';

const AnalyticsPage: React.FC = () => {
  const { data: transactions = [], isLoading: transactionsLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: () => transactionService.getTransactions(0, 100),
  });

  const { data: accounts = [], isLoading: accountsLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountService.getAccounts,
  });

  const isLoading = transactionsLoading || accountsLoading;

  // Calculate total balance with currency handling
  const calculateTotalBalance = () => {
    if (accounts.length === 0) return { amount: 0, currency: Currency.USD };
    
    const firstCurrency = accounts[0].currency;
    const allSameCurrency = accounts.every(account => account.currency === firstCurrency);
    
    if (allSameCurrency) {
      const total = accounts.reduce((sum, account) => sum + account.initial_balance, 0);
      return { amount: total, currency: firstCurrency };
    } else {
      const currencyTotals = accounts.reduce((acc, account) => {
        acc[account.currency] = (acc[account.currency] || 0) + account.initial_balance;
        return acc;
      }, {} as Record<Currency, number>);
      
      const dominantCurrency = Object.entries(currencyTotals).reduce((max, [currency, amount]) => 
        amount > max.amount ? { currency: currency as Currency, amount } : max,
        { currency: Currency.USD, amount: 0 }
      );
      
      return dominantCurrency;
    }
  };

  const totalBalance = calculateTotalBalance();
  
  // Calculate monthly stats from transactions
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  
  const monthlyTransactions = transactions.filter(t => {
    const transactionDate = new Date(t.date);
    return transactionDate.getMonth() === currentMonth && transactionDate.getFullYear() === currentYear;
  });
  
  const totalIncome = monthlyTransactions
    .filter(t => t.type === 'INCOME' && t.currency === totalBalance.currency)
    .reduce((sum, t) => sum + t.amount, 0);
    
  const totalExpenses = monthlyTransactions
    .filter(t => t.type === 'EXPENSE' && t.currency === totalBalance.currency)
    .reduce((sum, t) => sum + t.amount, 0);
    
  const netIncome = totalIncome - totalExpenses;
  const savingsRate = totalIncome > 0 ? (netIncome / totalIncome) * 100 : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Analytics</h1>
          <p className="text-dark-400 mt-1">Your financial insights</p>
        </div>
        <div className="flex items-center gap-2 text-dark-400">
          <CalendarIcon className="w-5 h-5" />
          <span>This Month</span>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-primary-600/20 to-accent/20"></div>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent rounded-xl flex items-center justify-center">
                <ChartBarIcon className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-sm font-medium text-dark-400">Total Balance</h3>
            </div>
            <p className="text-2xl font-bold text-white">{formatCurrency(totalBalance.amount, totalBalance.currency)}</p>
            <p className="text-sm text-dark-400 mt-1">Across all accounts</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-success/20 to-green-600/20"></div>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-gradient-to-br from-success to-green-600 rounded-xl flex items-center justify-center">
                <ArrowTrendingUpIcon className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-sm font-medium text-dark-400">Monthly Income</h3>
            </div>
            <p className="text-2xl font-bold text-white">{formatCurrency(totalIncome, totalBalance.currency)}</p>
            <p className="text-sm text-success mt-1">+0% vs last month</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-danger/20 to-red-600/20"></div>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-gradient-to-br from-danger to-red-600 rounded-xl flex items-center justify-center">
                <ArrowTrendingDownIcon className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-sm font-medium text-dark-400">Monthly Expenses</h3>
            </div>
            <p className="text-2xl font-bold text-white">{formatCurrency(totalExpenses, totalBalance.currency)}</p>
            <p className="text-sm text-danger mt-1">+0% vs last month</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-warning/20 to-yellow-600/20"></div>
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-gradient-to-br from-warning to-yellow-600 rounded-xl flex items-center justify-center">
                <ChartBarIcon className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-sm font-medium text-dark-400">Savings Rate</h3>
            </div>
            <p className="text-2xl font-bold text-white">{formatPercentage(savingsRate)}</p>
            <p className="text-sm text-dark-400 mt-1">Net savings this month</p>
          </div>
        </motion.div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Income vs Expenses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Income vs Expenses</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-dark-400">Income</span>
                <span className="text-success font-medium">{formatCurrency(totalIncome, totalBalance.currency)}</span>
              </div>
              <div className="w-full bg-dark-800 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-success to-green-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: totalIncome > 0 ? '100%' : '0%' }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-dark-400">Expenses</span>
                <span className="text-danger font-medium">{formatCurrency(totalExpenses, totalBalance.currency)}</span>
              </div>
              <div className="w-full bg-dark-800 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-danger to-red-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: totalIncome > 0 ? `${(totalExpenses / totalIncome) * 100}%` : '0%' }}
                ></div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Account Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Account Breakdown</h3>
          <div className="space-y-3">
            {accounts.length === 0 ? (
              <p className="text-dark-400 text-center py-4">No accounts to display</p>
            ) : (
              accounts.map((account) => (
                <div key={account.id} className="flex justify-between items-center">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-primary-500"></div>
                    <span className="text-white">{account.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-white font-medium">{formatCurrency(account.initial_balance, account.currency)}</span>
                    <p className="text-xs text-dark-400">{formatAccountType(account.type)}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-white mb-4">Financial Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-1">{transactions.length}</div>
            <div className="text-sm text-dark-400">Total Transactions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-1">{accounts.length}</div>
            <div className="text-sm text-dark-400">Active Accounts</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold mb-1 ${netIncome >= 0 ? 'text-success' : 'text-danger'}`}>
              {formatCurrency(netIncome, totalBalance.currency)}
            </div>
            <div className="text-sm text-dark-400">Net Income</div>
          </div>
        </div>
      </motion.div>

      {/* Empty State */}
      {transactions.length === 0 && accounts.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <ChartBarIcon className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No data available</h3>
          <p className="text-dark-400 mb-6">Start by adding accounts and transactions to see your analytics</p>
        </motion.div>
      )}
    </div>
  );
};

export default AnalyticsPage; 