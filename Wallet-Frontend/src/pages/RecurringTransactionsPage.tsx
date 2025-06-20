import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  PlayIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { RecurringTransaction, RecurrenceFrequency, TransactionType } from '../models/Transaction';
import { Currency } from '../models/Account';
import { formatCurrency, formatDate, formatTimeAgo, formatFrequency, formatAccountType } from '../utils/formatters';
import { recurringTransactionService, CreateRecurringTransactionData, UpdateRecurringTransactionData } from '../services/recurringTransactionService';
import { accountService } from '../services/accountService';
import { categoryService } from '../services/categoryService';

interface RecurringTransactionFormData {
  name: string;
  amount: number;
  type: TransactionType;
  description: string;
  currency: Currency;
  frequency: RecurrenceFrequency;
  start_date: string;
  end_date: string;
  account_id: number;
  category_id: number;
}

const RecurringTransactionsPage: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<RecurringTransaction | null>(null);
  const [formData, setFormData] = useState<RecurringTransactionFormData>({
    name: '',
    amount: 0,
    type: TransactionType.EXPENSE,
    description: '',
    currency: Currency.USD,
    frequency: RecurrenceFrequency.MONTHLY,
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    account_id: 0,
    category_id: 0,
  });

  const queryClient = useQueryClient();

  const { data: recurringTransactions = [], isLoading } = useQuery({
    queryKey: ['recurring-transactions'],
    queryFn: () => recurringTransactionService.getRecurringTransactions(),
  });

  const { data: accounts = [] } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountService.getAccounts,
  });

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: categoryService.getCategories,
  });

  const createMutation = useMutation({
    mutationFn: recurringTransactionService.createRecurringTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recurring-transactions'] });
      setIsModalOpen(false);
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateRecurringTransactionData }) =>
      recurringTransactionService.updateRecurringTransaction(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recurring-transactions'] });
      setIsModalOpen(false);
      setEditingTransaction(null);
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: recurringTransactionService.deleteRecurringTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recurring-transactions'] });
    },
  });

  const processMutation = useMutation({
    mutationFn: recurringTransactionService.processRecurringTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recurring-transactions'] });
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
  });

  const resetForm = () => {
    setFormData({
      name: '',
      amount: 0,
      type: TransactionType.EXPENSE,
      description: '',
      currency: Currency.USD,
      frequency: RecurrenceFrequency.MONTHLY,
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
      account_id: 0,
      category_id: 0,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const submitData: CreateRecurringTransactionData | UpdateRecurringTransactionData = {
      name: formData.name,
      amount: formData.amount,
      type: formData.type,
      description: formData.description || undefined,
      currency: formData.currency,
      frequency: formData.frequency,
      start_date: formData.start_date,
      end_date: formData.end_date || undefined,
      account_id: formData.account_id,
      category_id: formData.category_id || undefined,
    };

    if (editingTransaction) {
      updateMutation.mutate({ id: editingTransaction.id, data: submitData });
    } else {
      createMutation.mutate(submitData as CreateRecurringTransactionData);
    }
  };

  const handleEdit = (transaction: RecurringTransaction) => {
    setEditingTransaction(transaction);
    setFormData({
      name: transaction.name,
      amount: transaction.amount,
      type: transaction.type,
      description: transaction.description || '',
      currency: transaction.currency,
      frequency: transaction.frequency,
      start_date: transaction.start_date.split('T')[0],
      end_date: transaction.end_date ? transaction.end_date.split('T')[0] : '',
      account_id: transaction.account_id,
      category_id: transaction.category_id || 0,
    });
    setIsModalOpen(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this recurring transaction?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleProcess = (id: number) => {
    if (window.confirm('Process this recurring transaction now?')) {
      processMutation.mutate(id);
    }
  };

  const getTransactionTypeColor = (type: TransactionType) => {
    switch (type) {
      case TransactionType.INCOME:
        return 'text-success';
      case TransactionType.EXPENSE:
        return 'text-danger';
      default:
        return 'text-warning';
    }
  };

  const getAccountName = (accountId: number) => {
    const account = accounts.find(a => a.id === accountId);
    return account?.name || 'Unknown Account';
  };

  const getCategoryName = (categoryId?: number) => {
    if (!categoryId) return 'No Category';
    const category = categories.find(c => c.id === categoryId);
    return category?.name || 'Unknown Category';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white">Loading recurring transactions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between relative z-10">
        <div>
          <h1 className="text-3xl font-bold text-white">Recurring Transactions</h1>
          <p className="text-dark-400 mt-1">Manage your scheduled transactions and subscriptions.</p>
        </div>
        <button
          onClick={() => {
            setEditingTransaction(null);
            resetForm();
            setIsModalOpen(true);
          }}
          className="btn-primary flex items-center gap-2 relative z-10"
        >
          <PlusIcon className="w-5 h-5" />
          Add Recurring Transaction
        </button>
      </div>

      <div className="grid gap-4">
        {recurringTransactions.map((transaction) => (
          <motion.div
            key={transaction.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-white">{transaction.name}</h3>
                  <div className="flex items-center gap-2">
                    {transaction.is_active ? (
                      <CheckCircleIcon className="w-5 h-5 text-success" />
                    ) : (
                      <XCircleIcon className="w-5 h-5 text-danger" />
                    )}
                    <span className="text-sm text-dark-400">
                      {transaction.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-dark-400">Amount:</span>
                    <p className={`font-medium ${getTransactionTypeColor(transaction.type)}`}>
                      {formatCurrency(transaction.amount, transaction.currency)}
                    </p>
                  </div>
                  <div>
                    <span className="text-dark-400">Frequency:</span>
                    <p className="text-white">{formatFrequency(transaction.frequency)}</p>
                  </div>
                  <div>
                    <span className="text-dark-400">Account:</span>
                    <p className="text-white">{getAccountName(transaction.account_id)}</p>
                  </div>
                  <div>
                    <span className="text-dark-400">Next Due:</span>
                    <p className="text-white">{formatDate(transaction.next_due_date)}</p>
                  </div>
                </div>

                {transaction.description && (
                  <p className="text-dark-400 text-sm mt-2">{transaction.description}</p>
                )}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleProcess(transaction.id)}
                  disabled={!transaction.is_active || processMutation.isPending}
                  className="p-2 hover:bg-dark-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Process Now"
                >
                  <PlayIcon className="w-5 h-5 text-primary-400" />
                </button>
                <button
                  onClick={() => handleEdit(transaction)}
                  className="p-2 hover:bg-dark-700 rounded-md transition-colors"
                  title="Edit"
                >
                  <PencilIcon className="w-5 h-5 text-dark-400" />
                </button>
                <button
                  onClick={() => handleDelete(transaction.id)}
                  disabled={deleteMutation.isPending}
                  className="p-2 hover:bg-dark-700 rounded-md transition-colors"
                  title="Delete"
                >
                  <TrashIcon className="w-5 h-5 text-danger" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}

        {recurringTransactions.length === 0 && (
          <div className="text-center py-12">
            <ClockIcon className="w-16 h-16 text-dark-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-dark-400 mb-2">No Recurring Transactions</h3>
            <p className="text-dark-500 mb-6">Set up your first recurring transaction to automate your finances.</p>
            <button
              onClick={() => {
                setEditingTransaction(null);
                resetForm();
                setIsModalOpen(true);
              }}
              className="btn-primary"
            >
              Add Recurring Transaction
            </button>
          </div>
        )}
      </div>

      {/* Modal for creating/editing recurring transactions */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-dark-800/95 backdrop-blur-xl border border-dark-700/50 rounded-2xl p-8 w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl"
          >
            <h2 className="text-xl font-semibold text-white mb-4">
              {editingTransaction ? 'Edit Recurring Transaction' : 'Add Recurring Transaction'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-white mb-2">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                  required
                  placeholder="e.g., Monthly Rent"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">Amount</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                    className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                    required
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">Currency</label>
                  <select
                    value={formData.currency}
                    onChange={(e) => setFormData({ ...formData, currency: e.target.value as Currency })}
                    className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                    required
                  >
                    {Object.values(Currency).map((currency) => (
                      <option key={currency} value={currency} className="bg-dark-800">
                        {currency}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">Type</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value as TransactionType })}
                    className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                    required
                  >
                    <option value={TransactionType.INCOME} className="bg-dark-800">Income</option>
                    <option value={TransactionType.EXPENSE} className="bg-dark-800">Expense</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">Frequency</label>
                  <select
                    value={formData.frequency}
                    onChange={(e) => setFormData({ ...formData, frequency: e.target.value as RecurrenceFrequency })}
                    className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                    required
                  >
                    {Object.values(RecurrenceFrequency).map((frequency) => (
                      <option key={frequency} value={frequency} className="bg-dark-800">
                        {formatFrequency(frequency)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-white mb-2">Account</label>
                <select
                  value={formData.account_id}
                  onChange={(e) => setFormData({ ...formData, account_id: parseInt(e.target.value) })}
                  className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                  required
                >
                  <option value={0} className="bg-dark-800">Select Account</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id} className="bg-dark-800">
                      {account.name} ({formatAccountType(account.type)})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-white mb-2">Category (Optional)</label>
                <select
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: parseInt(e.target.value) })}
                  className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                >
                  <option value={0} className="bg-dark-800">No Category</option>
                  {categories
                    .filter((category) => 
                      formData.type === TransactionType.INCOME 
                        ? category.type === 'INCOME' 
                        : category.type === 'EXPENSE'
                    )
                    .map((category) => (
                      <option key={category.id} value={category.id} className="bg-dark-800">
                        {category.name}
                      </option>
                    ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">Start Date</label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">End Date (Optional)</label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-white mb-2">Description (Optional)</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-3 bg-dark-700/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200 resize-none"
                  rows={3}
                  placeholder="Additional notes..."
                />
              </div>

              <div className="flex gap-3 pt-6">
                <button
                  type="button"
                  onClick={() => {
                    setIsModalOpen(false);
                    setEditingTransaction(null);
                    resetForm();
                  }}
                  className="flex-1 px-6 py-3 bg-dark-700 hover:bg-dark-600 text-white font-medium rounded-xl transition-colors duration-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-medium rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {(createMutation.isPending || updateMutation.isPending) ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      {editingTransaction ? 'Updating...' : 'Creating...'}
                    </div>
                  ) : (
                    editingTransaction ? 'Update' : 'Create'
                  )}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default RecurringTransactionsPage; 