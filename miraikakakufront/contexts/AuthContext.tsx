'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Types
interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  is_admin: boolean;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
}

interface AuthContextType {
  state: AuthState;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
}

// API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://miraikakaku-api-465603676610.us-central1.run.app';

// Create Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth Provider Component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');

        if (accessToken && refreshToken) {
          // Verify token and get user info
          const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
            },
          });

          if (response.ok) {
            const user = await response.json();
            setState({
              user,
              accessToken,
              refreshToken,
              isLoading: false,
              isAuthenticated: true,
            });
          } else {
            // Token invalid, try to refresh
            try {
              await refreshAccessTokenInternal(refreshToken);
            } catch (error) {
              // Refresh failed, clear tokens
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              setState({
                user: null,
                accessToken: null,
                refreshToken: null,
                isLoading: false,
                isAuthenticated: false,
              });
            }
          }
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        setState(prev => ({ ...prev, isLoading: false }));
      }
    };

    initializeAuth();
  }, []);

  // Auto-refresh token before expiry (every 25 minutes)
  useEffect(() => {
    if (!state.refreshToken) return;

    const interval = setInterval(async () => {
      try {
        await refreshAccessToken();
      } catch (error) {
        console.error('Auto-refresh failed:', error);
      }
    }, 25 * 60 * 1000); // 25 minutes

    return () => clearInterval(interval);
  }, [state.refreshToken]);

  // Internal refresh function
  const refreshAccessTokenInternal = async (refreshToken: string) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }

    const data = await response.json();
    const newAccessToken = data.access_token;

    // Update state and localStorage
    setState(prev => ({
      ...prev,
      accessToken: newAccessToken,
    }));
    localStorage.setItem('access_token', newAccessToken);

    // Get updated user info
    const userResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${newAccessToken}`,
      },
    });

    if (userResponse.ok) {
      const user = await userResponse.json();
      setState(prev => ({
        ...prev,
        user,
        isAuthenticated: true,
      }));
    }
  };

  // Login function
  const login = async (username: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    const { access_token, refresh_token } = data;

    // Save tokens to localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    // Get user info
    const userResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${access_token}`,
      },
    });

    if (!userResponse.ok) {
      throw new Error('Failed to get user info');
    }

    const user = await userResponse.json();

    setState({
      user,
      accessToken: access_token,
      refreshToken: refresh_token,
      isLoading: false,
      isAuthenticated: true,
    });
  };

  // Register function
  const register = async (userData: RegisterData) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    // Auto-login after registration
    await login(userData.username, userData.password);
  };

  // Logout function
  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Clear state
    setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,
      isAuthenticated: false,
    });

    // Optional: Call logout endpoint to invalidate token on server
    // This is fire-and-forget, we don't wait for response
    if (state.accessToken) {
      fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${state.accessToken}`,
        },
      }).catch(() => {
        // Ignore errors, user is already logged out on client
      });
    }
  };

  // Refresh access token function
  const refreshAccessToken = async () => {
    if (!state.refreshToken) {
      throw new Error('No refresh token available');
    }

    await refreshAccessTokenInternal(state.refreshToken);
  };

  const value: AuthContextType = {
    state,
    login,
    register,
    logout,
    refreshAccessToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
