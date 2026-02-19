// Centralized API service with JWT integration

import axios from 'axios';

// Environment variable already includes /api, so don't append it again
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001/api';

// Log the API base URL for debugging
if (typeof window !== 'undefined') {
  console.log('API Instance Base URL:', API_BASE_URL);
}

const apiInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
  validateStatus: (status) => status < 500, // Don't throw on 4xx errors
});

// Import the cookie helper functions
import { getCookie, removeCookie } from './cookies';

// Request interceptor to attach JWT token
apiInstance.interceptors.request.use(
  (config) => {
    const token = getCookie('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Debug logging
    console.log('API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      hasAuth: !!token
    });

    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 unauthorized responses
apiInstance.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    return response;
  },
  (error) => {
    // More detailed error logging
    console.error('API Error Details:', {
      message: error.message || 'No message',
      code: error.code || 'No code',
      hasResponse: !!error.response,
      responseStatus: error.response?.status,
      responseData: error.response?.data,
      requestURL: error.config?.url,
      requestBaseURL: error.config?.baseURL,
      requestMethod: error.config?.method,
      isNetworkError: error.message === 'Network Error',
      errorType: error.constructor.name,
      stack: error.stack
    });

    if (error.response?.status === 401) {
      // Clear stored tokens and redirect to login
      removeCookie('authToken');
      removeCookie('userData');
      // Also clear localStorage for consistency (only in browser)
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export { apiInstance, API_BASE_URL };