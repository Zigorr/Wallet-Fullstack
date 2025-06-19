import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  PlusIcon,
  CreditCardIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
} from '@heroicons/react/24/outline';
import { accountService } from '../services/accountService';
import { AccountType } from '../models/Account';
import { formatCurrency } from '../utils/formatters';

const AccountsPage: React.FC = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [balanceVisible, setBalanceVisible] = useState(true);
  const queryClient = useQueryClient();

  const { data: accounts = [], isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountService.getAccounts,
  });

  const createAccountMutation = useMutation({
    mutationFn: accountService.createAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      setShowCreateForm(false);
    },
  });

  const deleteAccountMutation = useMutation({
    mutationFn: accountService.deleteAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });

  const [newAccount, setNewAccount] = useState({
    name: '',
    type: AccountType.CHECKING,
    initial_balance: 0,
  });

  const handleCreateAccount = (e: React.FormEvent) => {
    e.preventDefault();
    createAccountMutation.mutate(newAccount);
  };

  const handleDeleteAccount = (id: number) => {
    if (window.confirm('Are you sure you want to delete this account?')) {
      deleteAccountMutation.mutate(id);
    }
  };

  const totalBalance = accounts.reduce((sum, account) => sum + account.initial_balance, 0);

  const accountTypeColors = {
    [AccountType.CHECKING]: 'from-blue-500 to-blue-600',
    [AccountType.SAVINGS]: 'from-green-500 to-green-600',
    [AccountType.CREDIT]: 'from-red-500 to-red-600',
    [AccountType.INVESTMENT]: 'from-purple-500 to-purple-600',
    [AccountType.CASH]: 'from-yellow-500 to-yellow-600',
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white">Loading accounts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Accounts</h1>
          <p className="text-dark-400 mt-1">Manage your financial accounts</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <PlusIcon className="w-5 h-5" />
          Add Account
        </button>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600/20 to-accent/20"></div>
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-white">Total Balance</h3>
            <button
              onClick={() => setBalanceVisible(!balanceVisible)}
              className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
            >
              {balanceVisible ? (
                <EyeIcon className="w-5 h-5 text-dark-400" />
              ) : (
                <EyeSlashIcon className="w-5 h-5 text-dark-400" />
              )}
            </button>
          </div>
          <p className="text-3xl font-bold text-white">
            {balanceVisible ? formatCurrency(totalBalance) : '••••••'}
          </p>
          <p className="text-sm text-dark-400 mt-1">
            Across {accounts.length} account{accounts.length !== 1 ? 's' : ''}
          </p>
        </div>
      </motion.div>

      {accounts.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <CreditCardIcon className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No accounts yet</h3>
          <p className="text-dark-400 mb-6">Create your first account to start tracking your finances</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary"
          >
            Create First Account
          </button>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {accounts.map((account, index) => (
            <motion.div
              key={account.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card relative overflow-hidden group"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${accountTypeColors[account.type]}/20`}></div>
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 bg-gradient-to-br ${accountTypeColors[account.type]} rounded-xl flex items-center justify-center`}>
                    <CreditCardIcon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="p-2 hover:bg-dark-700 rounded-lg transition-colors">
                      <PencilIcon className="w-4 h-4 text-dark-400 hover:text-white" />
                    </button>
                    <button
                      onClick={() => handleDeleteAccount(account.id)}
                      className="p-2 hover:bg-danger/20 rounded-lg transition-colors"
                    >
                      <TrashIcon className="w-4 h-4 text-danger" />
                    </button>
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-white mb-1">{account.name}</h3>
                <p className="text-sm text-dark-400 capitalize mb-3">{account.type.toLowerCase()}</p>
                <p className="text-2xl font-bold text-white">
                  {formatCurrency(account.initial_balance)}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {showCreateForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-dark-900 border border-dark-700 rounded-2xl p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-xl font-bold text-white mb-6">Create New Account</h3>
            <form onSubmit={handleCreateAccount} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white mb-2">Account Name</label>
                <input
                  type="text"
                  value={newAccount.name}
                  onChange={(e) => setNewAccount({ ...newAccount, name: e.target.value })}
                  className="input-field w-full"
                  placeholder="e.g., Main Checking"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white mb-2">Account Type</label>
                <select
                  value={newAccount.type}
                  onChange={(e) => setNewAccount({ ...newAccount, type: e.target.value as AccountType })}
                  className="input-field w-full"
                >
                  {Object.values(AccountType).map((type) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-white mb-2">Initial Balance</label>
                <input
                  type="number"
                  step="0.01"
                  value={newAccount.initial_balance}
                  onChange={(e) => setNewAccount({ ...newAccount, initial_balance: parseFloat(e.target.value) || 0 })}
                  className="input-field w-full"
                  placeholder="0.00"
                />
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
                  disabled={createAccountMutation.isPending}
                  className="btn-primary flex-1"
                >
                  {createAccountMutation.isPending ? 'Creating...' : 'Create Account'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default AccountsPage; 