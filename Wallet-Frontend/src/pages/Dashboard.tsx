import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
  CreditCardIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  EyeSlashIcon,
  PlusIcon,
  ArrowsRightLeftIcon,
  TagIcon,
} from '@heroicons/react/24/outline';
import { formatCurrency, formatPercentage, formatTimeAgo } from '../utils/formatters';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import { accountService } from '../services/accountService';
import { transactionService } from '../services/transactionService';
import { categoryService } from '../services/categoryService';
import { Currency } from '../models/Account';

const Dashboard: React.FC = () => {
  const [balanceVisible, setBalanceVisible] = React.useState(true);

  const { data: accounts = [], isLoading: accountsLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountService.getAccounts,
  });

  const { data: transactions = [], isLoading: transactionsLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: () => transactionService.getTransactions(0, 10),
  });

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: categoryService.getCategories,
  });

  const isLoading = accountsLoading || transactionsLoading;

  // Calculate total balance - if all accounts have the same currency, show that currency
  const calculateTotalBalance = () => {
    if (accounts.length === 0) return { amount: 0, currency: Currency.USD };
    
    // Check if all accounts have the same currency
    const firstCurrency = accounts[0].currency;
    const allSameCurrency = accounts.every(account => account.currency === firstCurrency);
    
    if (allSameCurrency) {
      const total = accounts.reduce((sum, account) => sum + account.initial_balance, 0);
      return { amount: total, currency: firstCurrency };
    } else {
      // Mixed currencies - find the dominant currency
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
  
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  
  const monthlyTransactions = transactions.filter(t => {
    const transactionDate = new Date(t.date);
    return transactionDate.getMonth() === currentMonth && transactionDate.getFullYear() === currentYear;
  });
  
  // Calculate monthly income/expenses in the dominant currency
  const monthlyIncomeTransactions = monthlyTransactions.filter(t => t.type === 'INCOME');
  const monthlyExpenseTransactions = monthlyTransactions.filter(t => t.type === 'EXPENSE');
  
  const monthlyIncome = monthlyIncomeTransactions
    .filter(t => t.currency === totalBalance.currency)
    .reduce((sum, t) => sum + t.amount, 0);
    
  const monthlyExpenses = monthlyExpenseTransactions
    .filter(t => t.currency === totalBalance.currency)
    .reduce((sum, t) => sum + t.amount, 0);

  const recentTransactions = transactions.slice(0, 5);

  const accountData = accounts.map(account => ({
    name: account.name,
    value: account.initial_balance,
  }));

  const expenseData = categories
    .filter(cat => cat.type === 'EXPENSE')
    .map(cat => {
      const categoryTransactions = monthlyTransactions.filter(t => t.category_id === cat.id);
      const total = categoryTransactions.reduce((sum, t) => sum + t.amount, 0);
      return {
        name: cat.name,
        value: total,
      };
    })
    .filter(item => item.value > 0)
    .slice(0, 5);

  const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6'];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between relative z-10">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-dark-400 mt-1">Welcome back! Here's your financial overview.</p>
        </div>
        <button className="btn-primary flex items-center gap-2 relative z-10">
          <PlusIcon className="w-5 h-5" />
          Quick Add
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-primary-600/20 to-accent/20"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-dark-400">Total Balance</h3>
              <button
                onClick={() => setBalanceVisible(!balanceVisible)}
                className="p-1 hover:bg-dark-700 rounded-md transition-colors"
              >
                {balanceVisible ? (
                  <EyeIcon className="w-4 h-4 text-dark-400" />
                ) : (
                  <EyeSlashIcon className="w-4 h-4 text-dark-400" />
                )}
              </button>
            </div>
            <p className="text-2xl font-bold text-white">
              {balanceVisible ? formatCurrency(totalBalance.amount, totalBalance.currency) : '••••••'}
            </p>
            <p className="text-sm text-primary-400 mt-1">
              {accounts.length} account{accounts.length !== 1 ? 's' : ''}
            </p>
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
              <ArrowTrendingUpIcon className="w-5 h-5 text-success" />
              <h3 className="text-sm font-medium text-dark-400">Monthly Income</h3>
            </div>
            <p className="text-2xl font-bold text-white">{formatCurrency(monthlyIncome, totalBalance.currency)}</p>
            <p className="text-sm text-success mt-1">+0% from last month</p>
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
              <ArrowTrendingDownIcon className="w-5 h-5 text-danger" />
              <h3 className="text-sm font-medium text-dark-400">Monthly Expenses</h3>
            </div>
            <p className="text-2xl font-bold text-white">{formatCurrency(monthlyExpenses, totalBalance.currency)}</p>
            <p className="text-sm text-danger mt-1">+0% from last month</p>
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
              <CreditCardIcon className="w-5 h-5 text-warning" />
              <h3 className="text-sm font-medium text-dark-400">Savings Rate</h3>
            </div>
            <p className="text-2xl font-bold text-white">
              {formatPercentage(monthlyIncome > 0 ? ((monthlyIncome - monthlyExpenses) / monthlyIncome) * 100 : 0)}
            </p>
            <p className="text-sm text-dark-400 mt-1">This month</p>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Account Balances</h3>
          {accountData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={accountData}>
                  <XAxis dataKey="name" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                  <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-dark-400">
              <div className="text-center">
                <CreditCardIcon className="w-12 h-12 mx-auto mb-3" />
                <p>No accounts found</p>
              </div>
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Expense Breakdown</h3>
          {expenseData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={expenseData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {expenseData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-dark-400">
              <div className="text-center">
                <TagIcon className="w-12 h-12 mx-auto mb-3" />
                <p>No expense data</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-white mb-4">Recent Transactions</h3>
        {recentTransactions.length > 0 ? (
          <div className="space-y-3">
            {recentTransactions.map((transaction) => {
              const account = accounts.find(a => a.id === transaction.account_id);
              const category = categories.find(c => c.id === transaction.category_id);
              
              return (
                <div key={transaction.id} className="flex items-center justify-between p-3 bg-dark-800/30 rounded-xl">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      transaction.type === 'INCOME' ? 'bg-success/20 text-success' :
                      transaction.type === 'EXPENSE' ? 'bg-danger/20 text-danger' :
                      'bg-warning/20 text-warning'
                    }`}>
                      <ArrowsRightLeftIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="font-medium text-white">
                        {transaction.description || 'No description'}
                      </p>
                      <div className="flex items-center gap-2 text-sm text-dark-400">
                        <span>{account?.name}</span>
                        {category && (
                          <>
                            <span>•</span>
                            <span>{category.name}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${
                      transaction.type === 'INCOME' ? 'text-success' :
                      transaction.type === 'EXPENSE' ? 'text-danger' :
                      'text-white'
                    }`}>
                      {transaction.type === 'INCOME' ? '+' : transaction.type === 'EXPENSE' ? '-' : ''}
                      {formatCurrency(Math.abs(transaction.amount), transaction.currency)}
                    </p>
                    <p className="text-sm text-dark-400">{formatTimeAgo(transaction.date)}</p>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8 text-dark-400">
            <ArrowsRightLeftIcon className="w-12 h-12 mx-auto mb-3" />
            <p>No recent transactions</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Dashboard; 