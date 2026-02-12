/**
 * TaskMessage Component - Phase-V Advanced Features
 * Displays task with priority, tags, due date, and recurrence information
 * Supports real-time updates via WebSocket
 */
import React from 'react';
import { Task } from '../types/task';
import { useTaskSync } from '../hooks/useTaskSync';

interface TaskMessageProps {
  task: Task;
  userId?: string;
  enableRealTimeSync?: boolean;
}

const TaskMessage: React.FC<TaskMessageProps> = ({
  task,
  userId,
  enableRealTimeSync = false
}) => {
  // Enable real-time sync if userId provided
  const { tasks, isConnected } = useTaskSync({
    userId: userId || '',
    enabled: enableRealTimeSync && !!userId
  });

  // Find the current task in synced tasks (if real-time sync enabled)
  const syncedTask = enableRealTimeSync && userId
    ? tasks.find(t => t.task_id === task.task_id) || task
    : task;

  // Use synced task data if available, otherwise use prop
  const displayTask = syncedTask;
  // Priority badge colors
  const priorityColors = {
    urgent: 'bg-red-500 text-white',
    high: 'bg-orange-500 text-white',
    medium: 'bg-yellow-500 text-gray-900',
    low: 'bg-gray-400 text-gray-900'
  };

  // Format due date
  const formatDueDate = (dueDate: string | null) => {
    if (!dueDate) return null;
    const date = new Date(dueDate);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)} days`;
    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return 'Due tomorrow';
    return `Due in ${diffDays} days`;
  };

  return (
    <div className="task-message p-4 border rounded-lg mb-2 hover:shadow-md transition-shadow">
      {/* Real-time sync indicator */}
      {enableRealTimeSync && (
        <div className="flex items-center gap-1 mb-2 text-xs">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          <span className="text-gray-500">
            {isConnected ? 'Live' : 'Disconnected'}
          </span>
        </div>
      )}

      {/* Task Title */}
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-lg font-semibold flex-1">{displayTask.title}</h3>

        {/* Priority Badge */}
        <span className={`px-2 py-1 rounded text-xs font-medium ${priorityColors[displayTask.priority]}`}>
          {displayTask.priority.toUpperCase()}
        </span>
      </div>

      {/* Task Description */}
      {displayTask.description && (
        <p className="text-gray-700 mb-3">{displayTask.description}</p>
      )}

      {/* Task Metadata */}
      <div className="flex flex-wrap gap-2 items-center text-sm">
        {/* Tags */}
        {displayTask.tags && displayTask.tags.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            {displayTask.tags.map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Due Date */}
        {displayTask.due_date && (
          <span className="flex items-center gap-1 text-gray-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {formatDueDate(displayTask.due_date)}
          </span>
        )}

        {/* Recurrence Pattern */}
        {displayTask.recurrence_pattern && displayTask.recurrence_pattern !== 'none' && (
          <span className="flex items-center gap-1 text-purple-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Repeats: {displayTask.recurrence_pattern}
          </span>
        )}

        {/* Status */}
        <span className={`px-2 py-1 rounded text-xs ${
          displayTask.status === 'complete'
            ? 'bg-green-100 text-green-800'
            : 'bg-gray-100 text-gray-800'
        }`}>
          {displayTask.status === 'complete' ? '✓ Complete' : 'Incomplete'}
        </span>
      </div>

      {/* Timestamps */}
      <div className="mt-2 text-xs text-gray-500">
        Created: {new Date(displayTask.created_at).toLocaleDateString()}
        {displayTask.completed_at && (
          <> • Completed: {new Date(displayTask.completed_at).toLocaleDateString()}</>
        )}
      </div>
    </div>
  );
};

export default TaskMessage;
