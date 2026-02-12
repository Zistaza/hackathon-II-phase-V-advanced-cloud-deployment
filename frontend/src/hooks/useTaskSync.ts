/**
 * React hook for real-time task synchronization
 * Manages WebSocket connection and task list updates
 */

import { useEffect, useState, useCallback } from 'react';
import { Task, TaskEvent } from '../types/task';
import { getWebSocketService } from '../services/websocket';

interface UseTaskSyncOptions {
  userId: string;
  enabled?: boolean;
}

interface UseTaskSyncReturn {
  tasks: Task[];
  isConnected: boolean;
  addTask: (task: Task) => void;
  updateTask: (taskId: string, updates: Partial<Task>) => void;
  removeTask: (taskId: string) => void;
  setTasks: (tasks: Task[]) => void;
}

/**
 * Hook for managing real-time task synchronization
 *
 * @param options - Configuration options
 * @returns Task list and sync utilities
 */
export function useTaskSync(options: UseTaskSyncOptions): UseTaskSyncReturn {
  const { userId, enabled = true } = options;
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Handle task events from WebSocket
  const handleTaskEvent = useCallback((event: TaskEvent) => {
    console.log('Processing task event:', event.event_type, event.payload);

    switch (event.event_type) {
      case 'task.created':
        // Add new task to list
        if ('task_id' in event.payload) {
          const newTask: Task = {
            task_id: event.payload.task_id,
            user_id: event.user_id,
            title: event.payload.title,
            description: event.payload.description,
            status: event.payload.status as any,
            priority: event.payload.priority as any,
            tags: event.payload.tags,
            due_date: event.payload.due_date,
            recurrence_pattern: event.payload.recurrence_pattern as any,
            reminder_time: event.payload.reminder_time,
            created_at: event.timestamp,
            updated_at: event.timestamp,
            completed_at: null
          };

          setTasks(prev => {
            // Avoid duplicates
            if (prev.some(t => t.task_id === newTask.task_id)) {
              return prev;
            }
            return [newTask, ...prev];
          });
        }
        break;

      case 'task.updated':
        // Update existing task
        if ('task_id' in event.payload && 'updated_fields' in event.payload) {
          setTasks(prev => prev.map(task => {
            if (task.task_id === event.payload.task_id) {
              return {
                ...task,
                ...event.payload.updated_fields,
                updated_at: event.timestamp
              };
            }
            return task;
          }));
        }
        break;

      case 'task.completed':
        // Mark task as complete
        if ('task_id' in event.payload) {
          setTasks(prev => prev.map(task => {
            if (task.task_id === event.payload.task_id) {
              return {
                ...task,
                status: 'complete',
                completed_at: event.timestamp,
                updated_at: event.timestamp
              };
            }
            return task;
          }));
        }
        break;

      case 'task.deleted':
        // Remove task from list
        if ('task_id' in event.payload) {
          setTasks(prev => prev.filter(task => task.task_id !== event.payload.task_id));
        }
        break;
    }
  }, []);

  // Setup WebSocket connection
  useEffect(() => {
    if (!enabled || !userId) {
      return;
    }

    const wsService = getWebSocketService(userId);

    // Connect to WebSocket
    wsService.connect();
    setIsConnected(wsService.isConnected());

    // Register event handler
    const unsubscribe = wsService.onEvent(handleTaskEvent);

    // Check connection status periodically
    const connectionCheckInterval = setInterval(() => {
      setIsConnected(wsService.isConnected());
    }, 1000);

    // Cleanup on unmount
    return () => {
      clearInterval(connectionCheckInterval);
      unsubscribe();
      wsService.disconnect();
    };
  }, [userId, enabled, handleTaskEvent]);

  // Manual task manipulation functions
  const addTask = useCallback((task: Task) => {
    setTasks(prev => {
      if (prev.some(t => t.task_id === task.task_id)) {
        return prev;
      }
      return [task, ...prev];
    });
  }, []);

  const updateTask = useCallback((taskId: string, updates: Partial<Task>) => {
    setTasks(prev => prev.map(task => {
      if (task.task_id === taskId) {
        return { ...task, ...updates };
      }
      return task;
    }));
  }, []);

  const removeTask = useCallback((taskId: string) => {
    setTasks(prev => prev.filter(task => task.task_id !== taskId));
  }, []);

  return {
    tasks,
    isConnected,
    addTask,
    updateTask,
    removeTask,
    setTasks
  };
}
