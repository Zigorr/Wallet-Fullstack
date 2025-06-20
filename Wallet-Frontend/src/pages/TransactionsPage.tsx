import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  PlusIcon,
  ArrowsRightLeftIcon,
  PencilIcon,
  TrashIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import { transactionService } from '../services/transactionService';
import { accountService } from '../services/accountService';
import { categoryService } from '../services/categoryService';
import { TransactionType } from '../models/Transaction';
import { formatCurrency, formatDateTime } from '../utils/formatters';

const TransactionsPage: React.FC = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<TransactionType | 'ALL'>('ALL');
  const queryClient = useQueryClient();

  const { data: transactions = [], isLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: () => transactionService.getTransactions(0, 100),
  });

  const { data: accounts = [] } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountService.getAccounts,
  });

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: categoryService.getCategories,
  });

  const createTransactionMutation = useMutation({
    mutationFn: transactionService.createTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      setShowCreateForm(false);
    },
  });

  const deleteTransactionMutation = useMutation({
    mutationFn: transactionService.deleteTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });

  const [newTransaction, setNewTransaction] = useState({
    amount: 0,
    type: TransactionType.EXPENSE,
    description: '',
    account_id: 0,
    category_id: 0,
  });

  const handleCreateTransaction = (e: React.FormEvent) => {
    e.preventDefault();
    const transactionData = {
      ...newTransaction,
      category_id: newTransaction.category_id || undefined,
    };
    createTransactionMutation.mutate(transactionData);
  };

  const handleDeleteTransaction = (id: number) => {
    if (window.confirm('Are you sure you want to delete this transaction?')) {
      deleteTransactionMutation.mutate(id);
    }
  };

  // Filter and search transactions
  const filteredTransactions = transactions
    .filter(transaction => {
      const matchesSearch = !searchTerm || 
        transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        accounts.find(a => a.id === transaction.account_id)?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        categories.find(c => c.id === transaction.category_id)?.name.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesFilter = filterType === 'ALL' || transaction.type === filterType;
      
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  const getTransactionIcon = (type: TransactionType) => {
    switch (type) {
      case TransactionType.INCOME:
        return '↗️';
      case TransactionType.EXPENSE:
        return '↙️';
      case TransactionType.TRANSFER:
        return '↔️';
      default:
        return '💰';
    }
  };

  const getTransactionColor = (type: TransactionType) => {
    switch (type) {
      case TransactionType.INCOME:
        return 'text-success';
      case TransactionType.EXPENSE:
        return 'text-danger';
      case TransactionType.TRANSFER:
        return 'text-warning';
      default:
        return 'text-white';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white">Loading transactions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Transactions</h1>
          <p className="text-dark-400 mt-1">Track your income and expenses</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <PlusIcon className="w-5 h-5" />
          Add Transaction
        </button>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
          <input
            type="text"
            placeholder="Search transactions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field w-full pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <FunnelIcon className="w-5 h-5 text-dark-400" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as TransactionType | 'ALL')}
            className="input-field"
          >
            <option value="ALL">All Types</option>
            <option value={TransactionType.INCOME}>Income</option>
            <option value={TransactionType.EXPENSE}>Expense</option>
            <option value={TransactionType.TRANSFER}>Transfer</option>
          </select>
        </div>
      </div>

      {/* Transactions List */}
      {filteredTransactions.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <ArrowsRightLeftIcon className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            {searchTerm || filterType !== 'ALL' ? 'No matching transactions' : 'No transactions yet'}
          </h3>
          <p className="text-dark-400 mb-6">
            {searchTerm || filterType !== 'ALL' 
              ? 'Try adjusting your search or filter criteria'
              : 'Start by adding your first transaction'
            }
          </p>
          {!searchTerm && filterType === 'ALL' && (
            <button
              onClick={() => setShowCreateForm(true)}
              className="btn-primary"
            >
              Add First Transaction
            </button>
          )}
        </motion.div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-dark-700">
                  <th className="text-left p-4 text-dark-300 font-medium">Type</th>
                  <th className="text-left p-4 text-dark-300 font-medium">Description</th>
                  <th className="text-left p-4 text-dark-300 font-medium">Account</th>
                  <th className="text-left p-4 text-dark-300 font-medium">Category</th>
                  <th className="text-left p-4 text-dark-300 font-medium">Amount</th>
                  <th className="text-left p-4 text-dark-300 font-medium">Date</th>
                  <th className="text-left p-4 text-dark-300 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredTransactions.map((transaction, index) => {
                  const account = accounts.find(a => a.id === transaction.account_id);
                  const category = categories.find(c => c.id === transaction.category_id);
                  
                  return (
                    <motion.tr
                      key={transaction.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="border-b border-dark-800 hover:bg-dark-800/30 transition-colors"
                    >
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getTransactionIcon(transaction.type)}</span>
                          <span className={`text-sm font-medium capitalize ${getTransactionColor(transaction.type)}`}>
                            {transaction.type.toLowerCase()}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="text-white font-medium">
                          {transaction.description || 'No description'}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="text-dark-300">
                          {account?.name || 'Unknown Account'}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="text-dark-300">
                          {category?.name || 'Uncategorized'}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className={`font-semibold ${getTransactionColor(transaction.type)}`}>
                          {transaction.type === TransactionType.INCOME ? '+' : transaction.type === TransactionType.EXPENSE ? '-' : ''}
                          {formatCurrency(Math.abs(transaction.amount), transaction.currency)}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="text-dark-300 text-sm">
                          {formatDateTime(transaction.date)}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex gap-2">
                          <button className="p-2 hover:bg-dark-700 rounded-lg transition-colors">
                            <PencilIcon className="w-4 h-4 text-dark-400 hover:text-white" />
                          </button>
                          <button
                            onClick={() => handleDeleteTransaction(transaction.id)}
                            className="p-2 hover:bg-danger/20 rounded-lg transition-colors"
                          >
                            <TrashIcon className="w-4 h-4 text-danger" />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Transaction Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-dark-900 border border-dark-700 rounded-2xl p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-xl font-bold text-white mb-6">Add New Transaction</h3>
            <form onSubmit={handleCreateTransaction} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white mb-2">Type</label>
                <select
                  value={newTransaction.type}
                  onChange={(e) => setNewTransaction({ ...newTransaction, type: e.target.value as TransactionType })}
                  className="input-field w-full"
                >
                  <option value={TransactionType.INCOME}>Income</option>
                  <option value={TransactionType.EXPENSE}>Expense</option>
                  <option value={TransactionType.TRANSFER}>Transfer</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-white mb-2">Amount</label>
                <input
                  type="number"
                  step="0.01"
                  value={newTransaction.amount}
                  onChange={(e) => setNewTransaction({ ...newTransaction, amount: parseFloat(e.target.value) || 0 })}
                  className="input-field w-full"
                  placeholder="0.00"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white mb-2">Description</label>
                <input
                  type="text"
                  value={newTransaction.description}
                  onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
                  className="input-field w-full"
                  placeholder="e.g., Grocery shopping"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white mb-2">Account</label>
                <select
                  value={newTransaction.account_id}
                  onChange={(e) => setNewTransaction({ ...newTransaction, account_id: parseInt(e.target.value) })}
                  className="input-field w-full"
                  required
                >
                  <option value={0}>Select an account</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>{account.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-white mb-2">Category (Optional)</label>
                <select
                  value={newTransaction.category_id}
                  onChange={(e) => setNewTransaction({ ...newTransaction, category_id: parseInt(e.target.value) })}
                  className="input-field w-full"
                >
                  <option value={0}>No category</option>
                  {categories
                    .filter(cat => {
                      if (newTransaction.type === 'INCOME') return cat.type === 'INCOME';
                      if (newTransaction.type === 'EXPENSE') return cat.type === 'EXPENSE';
                      return false;
                    })
                    .map((category) => (
                      <option key={category.id} value={category.id}>{category.name}</option>
                    ))}
                </select>
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createTransactionMutation.isPending}
                  className="btn-primary flex-1"
                >
                  {createTransactionMutation.isPending ? 'Adding...' : 'Add Transaction'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default TransactionsPage; 