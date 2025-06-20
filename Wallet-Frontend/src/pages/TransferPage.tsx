import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowsRightLeftIcon,
  CurrencyDollarIcon,
  CalculatorIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import { accountService } from '../services/accountService';
import { transactionService, TransferCreateRequest } from '../services/transactionService';
import { formatCurrency, formatAccountType } from '../utils/formatters';
import { Currency } from '../models/Account';

const TransferPage: React.FC = () => {
  const [transferData, setTransferData] = useState<TransferCreateRequest>({
    from_account_id: 0,
    to_account_id: 0,
    amount: 0,
    converted_amount: undefined,
    description: '',
  });

  const [useCustomRate, setUseCustomRate] = useState(false);
  
  const [showPreview, setShowPreview] = useState(false);
  const [transferResult, setTransferResult] = useState<any>(null);

  const queryClient = useQueryClient();

  const { data: accounts = [] } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountService.getAccounts,
  });

  const { data: exchangeRates = {} } = useQuery({
    queryKey: ['exchange-rates'],
    queryFn: transactionService.getExchangeRates,
  });

  const transferMutation = useMutation({
    mutationFn: transactionService.createTransfer,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      setTransferResult(result);
      setShowPreview(false);
      // Reset form
      setTransferData({
        from_account_id: 0,
        to_account_id: 0,
        amount: 0,
        converted_amount: undefined,
        description: '',
      });
      setUseCustomRate(false);
    },
  });

  const fromAccount = accounts.find(a => a.id === transferData.from_account_id);
  const toAccount = accounts.find(a => a.id === transferData.to_account_id);

  // Calculate conversion preview
  const getConversionPreview = () => {
    if (!fromAccount || !toAccount || transferData.amount <= 0) return null;
    
    if (fromAccount.currency === toAccount.currency) {
      return {
        originalAmount: transferData.amount,
        convertedAmount: transferData.amount,
        exchangeRate: 1,
        sameCurrency: true,
        isCustomRate: false,
      };
    }

    // Use custom rate if specified
    if (useCustomRate && transferData.converted_amount && transferData.converted_amount > 0) {
      const exchangeRate = transferData.converted_amount / transferData.amount;
      return {
        originalAmount: transferData.amount,
        convertedAmount: transferData.converted_amount,
        exchangeRate: Math.round(exchangeRate * 10000) / 10000,
        sameCurrency: false,
        isCustomRate: true,
      };
    }

    // Convert using default exchange rates
    const fromRate = exchangeRates[fromAccount.currency] || 1;
    const toRate = exchangeRates[toAccount.currency] || 1;
    const usdAmount = transferData.amount / fromRate;
    const convertedAmount = usdAmount * toRate;
    const exchangeRate = convertedAmount / transferData.amount;

    return {
      originalAmount: transferData.amount,
      convertedAmount: Math.round(convertedAmount * 100) / 100,
      exchangeRate: Math.round(exchangeRate * 10000) / 10000,
      sameCurrency: false,
      isCustomRate: false,
    };
  };

  const conversionPreview = getConversionPreview();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (transferData.from_account_id === transferData.to_account_id) {
      alert('Please select different source and destination accounts');
      return;
    }
    setShowPreview(true);
  };

  const confirmTransfer = () => {
    transferMutation.mutate(transferData);
  };

  const availableToAccounts = accounts.filter(a => a.id !== transferData.from_account_id);
  const availableFromAccounts = accounts.filter(a => a.id !== transferData.to_account_id);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Transfer Money</h1>
          <p className="text-dark-400 mt-1">Move money between your accounts with automatic currency conversion</p>
        </div>
        <div className="flex items-center gap-2 text-dark-400">
          <ArrowsRightLeftIcon className="w-6 h-6" />
        </div>
      </div>

      {/* Success Message */}
      {transferResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-r from-success/20 to-green-600/20 border-success/30"
        >
          <div className="flex items-center gap-3">
            <CheckCircleIcon className="w-6 h-6 text-success" />
            <div>
              <h3 className="text-success font-semibold">Transfer Successful!</h3>
              <p className="text-dark-300 text-sm">
                Transferred {formatCurrency(transferResult.expense.amount, transferResult.expense.currency)} 
                {transferResult.exchange_rate !== 1 && (
                  <span> → {formatCurrency(transferResult.converted_amount, transferResult.income.currency)}</span>
                )}
              </p>
                             {transferResult.exchange_rate !== 1 && (
                 <p className="text-dark-400 text-xs mt-1">
                   Exchange rate: 1 {transferResult.expense.currency} = {transferResult.exchange_rate.toFixed(4)} {transferResult.income.currency}
                   {useCustomRate && <span className="text-primary-400"> (Custom Rate)</span>}
                 </p>
               )}
            </div>
          </div>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transfer Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="card"
        >
          <h2 className="text-xl font-semibold text-white mb-6">Transfer Details</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-white mb-2">From Account</label>
              <select
                value={transferData.from_account_id}
                onChange={(e) => setTransferData({ ...transferData, from_account_id: parseInt(e.target.value) })}
                className="input-field w-full"
                required
              >
                <option value={0}>Select source account</option>
                {availableFromAccounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name} ({formatAccountType(account.type)}) - {formatCurrency(account.initial_balance, account.currency)}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex justify-center">
              <div className="w-10 h-10 bg-gradient-to-r from-primary-600 to-accent rounded-full flex items-center justify-center">
                <ArrowsRightLeftIcon className="w-5 h-5 text-white" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-white mb-2">To Account</label>
              <select
                value={transferData.to_account_id}
                onChange={(e) => setTransferData({ ...transferData, to_account_id: parseInt(e.target.value) })}
                className="input-field w-full"
                required
              >
                <option value={0}>Select destination account</option>
                {availableToAccounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name} ({formatAccountType(account.type)}) - {formatCurrency(account.initial_balance, account.currency)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-white mb-2">
                Amount {fromAccount && `(${fromAccount.currency})`}
              </label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={transferData.amount}
                onChange={(e) => setTransferData({ ...transferData, amount: parseFloat(e.target.value) || 0 })}
                className="input-field w-full"
                placeholder="0.00"
                required
              />
            </div>

            {/* Custom Rate Toggle */}
            {fromAccount && toAccount && fromAccount.currency !== toAccount.currency && (
              <div className="flex items-center gap-3 p-3 bg-dark-800 rounded-lg">
                <input
                  type="checkbox"
                  id="useCustomRate"
                  checked={useCustomRate}
                  onChange={(e) => {
                    setUseCustomRate(e.target.checked);
                    if (!e.target.checked) {
                      setTransferData({ ...transferData, converted_amount: undefined });
                    }
                  }}
                  className="w-4 h-4 text-primary-600 bg-dark-700 border-dark-600 rounded focus:ring-primary-500"
                />
                <label htmlFor="useCustomRate" className="text-white text-sm">
                  I know the exact exchange rate
                </label>
              </div>
            )}

            {/* Custom Converted Amount */}
            {useCustomRate && toAccount && (
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Converted Amount {`(${toAccount.currency})`}
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={transferData.converted_amount || ''}
                  onChange={(e) => setTransferData({ ...transferData, converted_amount: parseFloat(e.target.value) || undefined })}
                  className="input-field w-full"
                  placeholder="0.00"
                  required={useCustomRate}
                />
                {transferData.amount > 0 && transferData.converted_amount && transferData.converted_amount > 0 && (
                  <p className="text-xs text-dark-400 mt-1">
                    Rate: 1 {fromAccount?.currency} = {(transferData.converted_amount / transferData.amount).toFixed(4)} {toAccount.currency}
                  </p>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-white mb-2">Description (Optional)</label>
              <input
                type="text"
                value={transferData.description}
                onChange={(e) => setTransferData({ ...transferData, description: e.target.value })}
                className="input-field w-full"
                placeholder="e.g., Monthly savings transfer"
              />
            </div>

            <button
              type="submit"
              disabled={
                !transferData.from_account_id || 
                !transferData.to_account_id || 
                transferData.amount <= 0 ||
                (useCustomRate && (!transferData.converted_amount || transferData.converted_amount <= 0))
              }
              className="btn-primary w-full"
            >
              Preview Transfer
            </button>
          </form>
        </motion.div>

        {/* Conversion Preview */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          {conversionPreview && (
            <div className="card">
              <div className="flex items-center gap-3 mb-4">
                <CalculatorIcon className="w-6 h-6 text-primary-500" />
                <h3 className="text-lg font-semibold text-white">Conversion Preview</h3>
              </div>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-dark-800 rounded-lg">
                  <span className="text-dark-300">You send</span>
                  <span className="text-white font-semibold">
                    {formatCurrency(conversionPreview.originalAmount, fromAccount?.currency)}
                  </span>
                </div>

                {!conversionPreview.sameCurrency && (
                  <>
                    <div className="flex justify-center">
                      <div className={`text-xs px-3 py-1 rounded-full ${
                        conversionPreview.isCustomRate 
                          ? 'text-primary-400 bg-primary-600/20 border border-primary-500/30' 
                          : 'text-dark-400 bg-dark-800'
                      }`}>
                        {conversionPreview.isCustomRate ? '✓ Custom Rate: ' : ''}
                        1 {fromAccount?.currency} = {conversionPreview.exchangeRate.toFixed(4)} {toAccount?.currency}
                      </div>
                    </div>
                  </>
                )}

                <div className="flex justify-between items-center p-3 bg-gradient-to-r from-primary-600/20 to-accent/20 rounded-lg border border-primary-600/30">
                  <span className="text-dark-300">Recipient gets</span>
                  <span className="text-white font-semibold">
                    {formatCurrency(conversionPreview.convertedAmount, toAccount?.currency)}
                  </span>
                </div>

                {conversionPreview.sameCurrency && (
                  <div className="text-center text-sm text-success">
                    ✓ Same currency - No conversion fees
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Account Summary */}
          {fromAccount && toAccount && (
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">Account Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-white font-medium">{fromAccount.name}</p>
                    <p className="text-xs text-dark-400">{formatAccountType(fromAccount.type)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-white">{formatCurrency(fromAccount.initial_balance, fromAccount.currency)}</p>
                    <p className="text-xs text-dark-400">{fromAccount.currency}</p>
                  </div>
                </div>
                
                <div className="border-t border-dark-700 pt-3">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-white font-medium">{toAccount.name}</p>
                      <p className="text-xs text-dark-400">{formatAccountType(toAccount.type)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-white">{formatCurrency(toAccount.initial_balance, toAccount.currency)}</p>
                      <p className="text-xs text-dark-400">{toAccount.currency}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Confirmation Modal */}
      {showPreview && conversionPreview && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-dark-900 border border-dark-700 rounded-2xl p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-xl font-bold text-white mb-6">Confirm Transfer</h3>
            
            <div className="space-y-4 mb-6">
              <div className="flex justify-between">
                <span className="text-dark-300">From:</span>
                <span className="text-white">{fromAccount?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-300">To:</span>
                <span className="text-white">{toAccount?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-dark-300">Amount:</span>
                <span className="text-white font-semibold">
                  {formatCurrency(conversionPreview.originalAmount, fromAccount?.currency)}
                </span>
              </div>
              {!conversionPreview.sameCurrency && (
                <div className="flex justify-between">
                  <span className="text-dark-300">Converted:</span>
                  <span className="text-white font-semibold">
                    {formatCurrency(conversionPreview.convertedAmount, toAccount?.currency)}
                  </span>
                </div>
              )}
              {transferData.description && (
                <div className="flex justify-between">
                  <span className="text-dark-300">Description:</span>
                  <span className="text-white">{transferData.description}</span>
                </div>
              )}
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setShowPreview(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={confirmTransfer}
                disabled={transferMutation.isPending}
                className="btn-primary flex-1"
              >
                {transferMutation.isPending ? 'Processing...' : 'Confirm Transfer'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default TransferPage; 