// Auth service for handling authentication API calls

import axios from 'axios';
import { UserRegistration, LoginRequest, AuthResponse } from '../types';
import { setCookie, removeCookie, getCookie } from '../lib/cookies';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

// Debug: Log the API base URL to verify it's correct
if (typeof window !== 'undefined') {
  console.log('Auth Service API_BASE_URL:', API_BASE_URL);
}

const authApiInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
authApiInstance.interceptors.request.use(
  (config) => {
    const token = getCookie('authToken') ||
      (typeof window !== 'undefined' ? localStorage.getItem('authToken') : null);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 unauthorized responses
authApiInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stored tokens and redirect to login
      removeCookie('authToken');
      removeCookie('userData');
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  register: async (userData: UserRegistration): Promise<AuthResponse> => {
    try {
      const response = await authApiInstance.post('/auth/register', userData);
      // Set cookie for Next.js middleware and localStorage for client-side access
      if (response.data && response.data.token) {
        setCookie('authToken', response.data.token, 7); // Store for 7 days
        if (typeof window !== 'undefined') {
          localStorage.setItem('authToken', response.data.token);
        }
        if (response.data.user) {
          setCookie('userData', JSON.stringify(response.data.user), 7);
          if (typeof window !== 'undefined') {
            localStorage.setItem('userData', JSON.stringify(response.data.user));
          }
        }
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Registration failed');
    }
  },

  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    try {
      const response = await authApiInstance.post('/auth/login', credentials);
      // Set cookie for Next.js middleware and localStorage for client-side access
      if (response.data && response.data.token) {
        setCookie('authToken', response.data.token, 7); // Store for 7 days
        if (typeof window !== 'undefined') {
          localStorage.setItem('authToken', response.data.token);
        }
        if (response.data.user) {
          setCookie('userData', JSON.stringify(response.data.user), 7);
          if (typeof window !== 'undefined') {
            localStorage.setItem('userData', JSON.stringify(response.data.user));
          }
        }
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  },

  logout: async (): Promise<void> => {
    try {
      await authApiInstance.post('/auth/logout');
    } catch (error: any) {
      console.error('Logout error:', error);
    } finally {
      // Always clear cookies and localStorage
      removeCookie('authToken');
      removeCookie('userData');
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
      }
    }
  },

  verifyToken: async (token: string): Promise<boolean> => {
    try {
      // Make a request to verify the token with the backend
      const response = await authApiInstance.get('/auth/verify', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  },

  getCurrentUser: async (): Promise<AuthResponse['user'] | null> => {
    try {
      const response = await authApiInstance.get('/auth/me');
      return response.data;
    } catch (error) {
      return null;
    }
  },
};
