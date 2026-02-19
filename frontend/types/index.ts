// Type definitions for the Todo Application

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  task_id?: string; // Alias for WebSocket compatibility
  title: string;
  description: string | null;
  completed: boolean;
  user_id: string;
  priority?: string; // Phase V: low, medium, high, urgent
  tags?: string[]; // Phase V: Array of tags
  due_date?: string | null; // Phase V: ISO date string
  recurrence_pattern?: string; // Phase V: none, daily, weekly, monthly
  reminder_time?: string | null; // Phase V: Reminder time
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  completed?: boolean;
  priority?: string; // Phase V
  tags?: string[]; // Phase V
  due_date?: string | null; // Phase V
  recurrence_pattern?: string; // Phase V
  reminder_time?: string | null; // Phase V
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
  priority?: string; // Phase V
  tags?: string[]; // Phase V
  due_date?: string | null; // Phase V
  recurrence_pattern?: string; // Phase V
  reminder_time?: string | null; // Phase V
}

export interface UserRegistration {
  email: string;
  name: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// WebSocket Event Types for Phase V
export interface TaskEvent {
  event_type: 'task.created' | 'task.updated' | 'task.completed' | 'task.deleted';
  user_id: string;
  timestamp: string;
  payload: {
    task_id: string;
    title?: string;
    description?: string | null;
    status?: string;
    priority?: string;
    tags?: string[];
    due_date?: string | null;
    recurrence_pattern?: string;
    reminder_time?: string | null;
    updated_fields?: Partial<Task>;
  };
}
