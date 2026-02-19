// Task service for handling todo API calls

import { apiInstance, API_BASE_URL } from '../lib/api';
import { Task, TaskCreate, TaskUpdate } from '../types';
import axios from 'axios';
import { getCookie, removeCookie } from '../lib/cookies';

// Get the current user ID from cookies
const getCurrentUserId = (): string | null => {
  const userDataStr = getCookie('userData');
  if (userDataStr) {
    try {
      // Try parsing directly first
      let user;
      try {
        user = JSON.parse(userDataStr);
      } catch {
        // If direct parsing fails, try decoding first
        user = JSON.parse(decodeURIComponent(userDataStr));
      }

      // Validate that the user object has an id property
      if (!user || !user.id || typeof user.id !== 'string' || user.id.trim() === '') {
        console.error('Invalid user data in cookie - missing or invalid id:', user);
        return null;
      }

      console.log('Retrieved user ID:', user.id); // Debug log
      return user.id.trim();
    } catch (error) {
      console.error('Failed to parse user data from cookie:', error);
      return null;
    }
  }
  console.log('No userData cookie found'); // Debug log
  return null;
};

export const todoService = {
  // Get all tasks for the authenticated user
  getTasks: async (): Promise<Task[]> => {
    const userId = getCurrentUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    try {
      // Validate user ID format (should be a UUID-like string and URL-safe)
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      // Log for debugging
      console.log('Fetching tasks for userId:', userId);

      // Construct the full URL for debugging - apiInstance already includes /api prefix
      const url = `/${userId}/tasks`;
      console.log('Making request to URL:', url);

      // Make sure the URL starts with a slash for relative path
      const normalizedUrl = url.startsWith('/') ? url : `/${url}`;
      const response = await apiInstance.get<any[]>(normalizedUrl);

      // Transform backend response (task_id) to frontend format (id)
      const tasks: Task[] = response.data.map((task: any) => ({
        id: task.task_id || task.id, // Backend uses task_id, frontend uses id
        title: task.title,
        description: task.description,
        completed: task.completed,
        user_id: task.user_id,
        priority: task.priority || 'medium',
        tags: task.tags || [],
        due_date: task.due_date || null,
        recurrence_pattern: task.recurrence_pattern || 'none',
        reminder_time: task.reminder_time || null,
        created_at: task.created_at,
        updated_at: task.updated_at
      }));

      return tasks;
    } catch (error: any) {
      console.error('Error fetching tasks:', error);
      console.error('Full error response:', error.response);
      console.error('Error code:', error.code);
      console.error('Request URL:', error.config?.url);
      console.error('Request method:', error.config?.method);

      // Check if it's a 401 error specifically
      if (error.response?.status === 401) {
        // Clear auth cookies and localStorage
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }

      // Check if it's a 404 error
      if (error.response?.status === 404) {
        console.error('404 error - User ID may be invalid or user does not exist:', userId);
        // This might indicate that the user account was deleted or the ID is incorrect
        // For safety, clear auth data and redirect to login
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('User account not found. Please log in again.');
      }

      // Provide more detailed error information for debugging
      const errorMessage = error.response?.data?.message || error.message || 'Failed to fetch tasks';
      const errorDetails = {
        message: errorMessage,
        code: error.code,
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        response_data: error.response?.data
      };

      console.error('Detailed error information:', errorDetails);
      throw new Error(errorMessage);
    }
  },

  // Create a new task
  createTask: async (taskData: TaskCreate): Promise<Task> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for task creation:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      // Debug logging
      console.log('Creating task with data:', taskData);
      console.log('User ID:', userId);
      console.log('Request URL:', `/${userId}/tasks`);
      console.log('API Base URL:', API_BASE_URL);

      const response = await apiInstance.post<any>(`/${userId}/tasks`, taskData);

      console.log('Task created successfully:', response.data);

      // Transform backend response (task_id) to frontend format (id)
      const task: Task = {
        id: response.data.task_id || response.data.id,
        title: response.data.title,
        description: response.data.description,
        completed: response.data.completed,
        user_id: response.data.user_id,
        priority: response.data.priority || 'medium',
        tags: response.data.tags || [],
        due_date: response.data.due_date || null,
        recurrence_pattern: response.data.recurrence_pattern || 'none',
        reminder_time: response.data.reminder_time || null,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at
      };

      return task;
    } catch (error: any) {
      console.error('Error creating task:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.message || error.message || 'Failed to create task');
    }
  },

  // Get a specific task by ID
  getTaskById: async (taskId: string): Promise<Task> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for getting task:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      const response = await apiInstance.get<any>(`/${userId}/tasks/${taskId}`);

      // Transform backend response (task_id) to frontend format (id)
      const task: Task = {
        id: response.data.task_id || response.data.id,
        title: response.data.title,
        description: response.data.description,
        completed: response.data.completed,
        user_id: response.data.user_id,
        priority: response.data.priority || 'medium',
        tags: response.data.tags || [],
        due_date: response.data.due_date || null,
        recurrence_pattern: response.data.recurrence_pattern || 'none',
        reminder_time: response.data.reminder_time || null,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at
      };

      return task;
    } catch (error: any) {
      console.error('Error fetching task by ID:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.message || error.message || 'Failed to fetch task');
    }
  },

  // Update a task
  updateTask: async (taskId: string, taskData: TaskUpdate): Promise<Task> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for updating task:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      const response = await apiInstance.put<any>(`/${userId}/tasks/${taskId}`, taskData);

      // Transform backend response (task_id) to frontend format (id)
      const task: Task = {
        id: response.data.task_id || response.data.id,
        title: response.data.title,
        description: response.data.description,
        completed: response.data.completed,
        user_id: response.data.user_id,
        priority: response.data.priority || 'medium',
        tags: response.data.tags || [],
        due_date: response.data.due_date || null,
        recurrence_pattern: response.data.recurrence_pattern || 'none',
        reminder_time: response.data.reminder_time || null,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at
      };

      return task;
    } catch (error: any) {
      console.error('Error updating task:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.message || error.message || 'Failed to update task');
    }
  },

  // Delete a task
  deleteTask: async (taskId: string): Promise<void> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for deleting task:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      await apiInstance.delete(`/${userId}/tasks/${taskId}`);
    } catch (error: any) {
      console.error('Delete task error:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.detail || error.response?.data?.message || 'Failed to delete task');
    }
  },

  // Toggle task completion status
  toggleTaskCompletion: async (taskId: string): Promise<{ id: string; completed: boolean; message: string }> => {
    try {
      const userId = getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      // Validate user ID format before making the request
      if (!userId || typeof userId !== 'string' || userId.length < 10 || /[^\w\-]/.test(userId)) {
        console.error('Invalid user ID format for toggling task completion:', userId, '- Length:', userId?.length, '- Contains invalid chars:', userId ? /[^\w\-]/.test(userId) : 'N/A');
        throw new Error('Invalid user ID format');
      }

      const response = await apiInstance.patch(`/${userId}/tasks/${taskId}/complete`);
      return response.data;
    } catch (error: any) {
      console.error('Error toggling task completion:', error);
      if (error.response?.status === 401) {
        removeCookie('authToken');
        removeCookie('userData');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        window.location.href = '/login';
        throw new Error('Authentication expired. Please log in again.');
      }
      if (error.response?.status === 403) {
        console.error('Access forbidden - user ID in URL does not match JWT user ID');
        throw new Error('Access denied. Please log out and log back in to refresh your session.');
      }
      throw new Error(error.response?.data?.message || error.message || 'Failed to toggle task completion');
    }
  },
};