/**
 * TypeScript type definitions for Phase-V Advanced Features
 */

export type TaskStatus = 'incomplete' | 'complete';

export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export type RecurrencePattern = 'none' | 'daily' | 'weekly' | 'monthly';

export interface Task {
  task_id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  tags: string[];
  due_date: string | null;
  recurrence_pattern: RecurrencePattern;
  reminder_time: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  priority?: TaskPriority;
  tags?: string[];
  due_date?: string;
  recurrence_pattern?: RecurrencePattern;
  reminder_time?: string;
}

export interface TaskUpdateRequest {
  task_id: string;
  title?: string;
  description?: string;
  priority?: TaskPriority;
  tags?: string[];
  due_date?: string;
  recurrence_pattern?: RecurrencePattern;
  reminder_time?: string;
}

export interface TaskListRequest {
  status?: TaskStatus;
  priority?: TaskPriority;
  tags?: string[];
  due_date_filter?: 'overdue' | 'today' | 'this_week' | 'this_month';
  search?: string;
  sort_by?: 'created_at' | 'due_date' | 'priority' | 'status';
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export interface TaskResponse {
  success: boolean;
  task_id?: string;
  message: string;
  reminder_scheduled?: boolean;
  updated_fields?: string[];
  reminder_rescheduled?: boolean;
}

export interface TaskListResponse {
  success: boolean;
  tasks: Task[];
  total_count: number;
  message: string;
}
