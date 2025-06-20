import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { loginFormState } from '../utils/loginFormState';
import {
  EyeIcon,
  EyeSlashIcon,
  WalletIcon,
  UserIcon,
  LockClosedIcon,
} from '@heroicons/react/24/outline';

const LoginPage: React.FC = () => {
  // Use global state manager that persists across component unmounts
  const [username, setUsername] = useState(() => loginFormState.getUsername());
  const [password, setPassword] = useState(() => loginFormState.getPassword());
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(() => {
    // Restore error from session storage if it exists
    const savedError = sessionStorage.getItem('login_error');
    return savedError || '';
  });

  const { login, isLoading: authLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  // Use a ref to track if we're currently in a login attempt
  const loginAttemptRef = useRef(false);
  const componentIdRef = useRef(Math.random().toString(36).substr(2, 9));

  // Add debugging to track component lifecycle
  useEffect(() => {
    console.log(`[${componentIdRef.current}] LoginPage mounted/updated`, {
      isAuthenticated,
      authLoading,
      loginAttempt: loginAttemptRef.current,
      username,
      password: password ? '***' : '(empty)',
      globalUsername: loginFormState.getUsername(),
      globalPassword: loginFormState.getPassword() ? '***' : '(empty)'
    });
    
    // If local state is empty but global state has data, restore it
    const globalUsername = loginFormState.getUsername();
    const globalPassword = loginFormState.getPassword();
    
    if (!username && globalUsername) {
      console.log(`[${componentIdRef.current}] Restoring username from global state:`, globalUsername);
      setUsername(globalUsername);
    }
    if (!password && globalPassword) {
      console.log(`[${componentIdRef.current}] Restoring password from global state`);
      setPassword(globalPassword);
    }

    // Cleanup function to clear error when component unmounts due to successful navigation
    return () => {
      if (isAuthenticated) {
        console.log(`[${componentIdRef.current}] Component unmounting due to successful auth, clearing error`);
        sessionStorage.removeItem('login_error');
      }
    };
  });

  // Only redirect if authenticated AND we're not in the middle of a login attempt
  useEffect(() => {
    console.log(`[${componentIdRef.current}] Auth effect triggered`, {
      isAuthenticated,
      authLoading,
      loginAttempt: loginAttemptRef.current,
      error: !!error
    });
    
    // Only navigate if auth system is fully loaded, user is authenticated, 
    // not in login attempt, and no error is present
    if (isAuthenticated && !authLoading && !loginAttemptRef.current && !error) {
      console.log(`[${componentIdRef.current}] Navigating to dashboard`);
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, authLoading, error]);

  // Clear error when user starts typing in either field
  const handleUsernameChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    console.log(`[${componentIdRef.current}] Username changed:`, value);
    loginFormState.setUsername(value);
    setUsername(value);
    if (error) {
      setError(''); // Clear error when user types
      sessionStorage.removeItem('login_error'); // Also clear from session storage
    }
  }, [error]);

  const handlePasswordChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    console.log(`[${componentIdRef.current}] Password changed:`, value ? '***' : '(empty)');
    loginFormState.setPassword(value);
    setPassword(value);
    if (error) {
      setError(''); // Clear error when user types
      sessionStorage.removeItem('login_error'); // Also clear from session storage
    }
  }, [error]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Prevent multiple submissions or submission during auth loading
    if (loading || authLoading) {
      console.log(`[${componentIdRef.current}] Form submission blocked - loading:${loading}, authLoading:${authLoading}`);
      return;
    }
    
    console.log(`[${componentIdRef.current}] Form submitted`, { username, password: '***' });
    
    loginAttemptRef.current = true;
    setLoading(true);
    setError('');

    try {
      console.log(`[${componentIdRef.current}] Calling login...`);
      await login(username, password);
      console.log(`[${componentIdRef.current}] Login successful`);
      // Clear form data and any stored error on successful login
      loginFormState.clear();
      sessionStorage.removeItem('login_error');
      // Navigation will be handled by the useEffect when isAuthenticated changes
      // Don't navigate here to avoid race conditions
    } catch (err: any) {
      console.log(`[${componentIdRef.current}] Login failed:`, err);
      // Extract error message
      let errorMessage = 'Login failed. Please try again.';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      console.log(`[${componentIdRef.current}] Setting error:`, errorMessage);
      setError(errorMessage);
      
      // Also store error in session storage to persist across potential re-renders
      sessionStorage.setItem('login_error', errorMessage);
    } finally {
      console.log(`[${componentIdRef.current}] Login attempt finished`);
      setLoading(false);
      loginAttemptRef.current = false;
    }
  }, [login, username, password, loading, authLoading]);

  // Show loading spinner while auth context is initializing
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950 flex items-center justify-center p-4">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-600/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent/20 rounded-full blur-3xl"></div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md"
      >
        {/* Login Card */}
        <div className="bg-dark-900/40 backdrop-blur-xl border border-dark-700/50 rounded-2xl p-8 shadow-2xl">
          {/* Logo */}
          <div className="flex items-center justify-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-accent rounded-2xl flex items-center justify-center">
              <WalletIcon className="w-8 h-8 text-white" />
            </div>
          </div>

          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-white mb-2">Welcome Back</h1>
            <p className="text-dark-400">Sign in to your account to continue</p>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              className="mb-6 p-4 bg-danger/10 border border-danger/20 rounded-xl"
            >
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-danger rounded-full flex-shrink-0"></div>
                <p className="text-danger text-sm font-medium">{error}</p>
              </div>
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-white mb-2">
                Username
              </label>
              <div className="relative">
                <UserIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={handleUsernameChange}
                  className="w-full pl-10 pr-4 py-3 bg-dark-800/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                  placeholder="Enter your username"
                  required
                  autoComplete="username"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-white mb-2">
                Password
              </label>
              <div className="relative">
                <LockClosedIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={handlePasswordChange}
                  className="w-full pl-10 pr-12 py-3 bg-dark-800/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-colors duration-200"
                  placeholder="Enter your password"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-dark-400 hover:text-white transition-colors"
                >
                  {showPassword ? (
                    <EyeSlashIcon className="w-5 h-5" />
                  ) : (
                    <EyeIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-medium py-3 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Signing In...
                </div>
              ) : (
                'Sign In'
              )}
            </motion.button>
          </form>

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-dark-400">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="text-primary-400 hover:text-primary-300 font-medium transition-colors"
              >
                Sign up
              </Link>
            </p>
          </div>
        </div>

        {/* Bottom Text */}
        <div className="mt-8 text-center">
          <p className="text-dark-500 text-sm">
            Secure • Private • Modern
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage; 