// Custom hook for authentication state management

import { useState, useEffect } from 'react';
import { authService } from '../services/auth-service';
import { User, AuthResponse, UserRegistration, LoginRequest } from '../types';

interface UseAuthReturn {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  register: (userData: UserRegistration) => Promise<AuthResponse>;
  login: (credentials: LoginRequest) => Promise<AuthResponse>;
  logout: () => Promise<void>;
  verifyToken: (token: string) => Promise<boolean>;
}

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check for existing token on initial load
    const storedToken = localStorage.getItem('authToken');
    const storedUserData = localStorage.getItem('userData');

    if (storedToken && storedUserData) {
      try {
        const parsedUser = JSON.parse(storedUserData);
        setToken(storedToken);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Failed to parse stored user data:', error);
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
      }
    }

    setIsLoading(false);
  }, []);

  const register = async (userData: UserRegistration): Promise<AuthResponse> => {
    const result = await authService.register(userData);

    // Store the token and user data locally
    localStorage.setItem('authToken', result.token);
    localStorage.setItem('userData', JSON.stringify(result.user));

    setToken(result.token);
    setUser(result.user);
    setIsAuthenticated(true);

    return result;
  };

  const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
    const result = await authService.login(credentials);

    // Store the token and user data locally
    localStorage.setItem('authToken', result.token);
    localStorage.setItem('userData', JSON.stringify(result.user));

    setToken(result.token);
    setUser(result.user);
    setIsAuthenticated(true);

    return result;
  };

  const logout = async (): Promise<void> => {
    await authService.logout();

    // Clear local storage and state
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');

    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  const verifyToken = async (token: string): Promise<boolean> => {
    return await authService.verifyToken(token);
  };

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    register,
    login,
    logout,
    verifyToken,
  };
};