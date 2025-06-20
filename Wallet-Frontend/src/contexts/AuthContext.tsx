import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../services/authService';
import { Currency } from '../models/Account';

interface User {
  id: number;
  username: string;
  email: string;
  default_currency: Currency;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    console.log('AuthProvider: initializing with token:', token ? 'present' : 'none');
    
    if (token) {
      // Validate token and get user info
      authService.getCurrentUser()
        .then(userData => {
          console.log('AuthProvider: user data loaded:', userData.username);
          setUser(userData);
        })
        .catch((error) => {
          console.log('AuthProvider: token validation failed:', error);
          localStorage.removeItem('access_token');
        })
        .finally(() => {
          console.log('AuthProvider: initialization complete');
          setIsLoading(false);
          setIsInitialized(true);
        });
    } else {
      console.log('AuthProvider: no token, initialization complete');
      setIsLoading(false);
      setIsInitialized(true);
    }
  }, []);

  const login = async (username: string, password: string) => {
    // Don't set global loading state during login attempts
    // The login form should handle its own loading state
    console.log('AuthContext: login called with username:', username);
    
    // Don't proceed if not initialized yet
    if (!isInitialized) {
      console.log('AuthContext: not initialized yet, waiting...');
      throw new Error('Authentication system not ready');
    }
    
    try {
      console.log('AuthContext: calling authService.login...');
      const response = await authService.login(username, password);
      console.log('AuthContext: login response received');
      localStorage.setItem('access_token', response.access_token);
      console.log('AuthContext: token stored, getting user data...');
      const userData = await authService.getCurrentUser();
      console.log('AuthContext: user data received, setting user...');
      setUser(userData);
      console.log('AuthContext: user set successfully');
    } catch (error) {
      console.log('AuthContext: login error:', error);
      // Don't change any auth state on error - keep everything stable
      throw error;
    }
  };

  const register = async (username: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      await authService.register(username, email, password);
      // Auto-login after registration using username
      await login(username, password);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    register,
    logout,
    isAuthenticated: !!user && isInitialized,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 