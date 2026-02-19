'use client';

import React from 'react';
import { Task } from '../../types';

interface TaskBadgesProps {
  task: Task;
}

const priorityConfig = {
  urgent: {
    icon: '🔴',
    label: 'Urgent',
    className: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  },
  high: {
    icon: '🟠',
    label: 'High',
    className: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
  },
  medium: {
    icon: '🟡',
    label: 'Medium',
    className: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
  },
  low: {
    icon: '🟢',
    label: 'Low',
    className: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
  }
};

export const TaskBadges: React.FC<TaskBadgesProps> = ({ task }) => {
  const priority = task.priority as keyof typeof priorityConfig;
  const priorityInfo = priority ? priorityConfig[priority] : null;

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Priority Badge */}
      {priorityInfo && (
        <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold ${priorityInfo.className}`}>
          <span className="mr-1.5 text-base">{priorityInfo.icon}</span>
          {priorityInfo.label}
        </span>
      )}

      {/* Tags */}
      {task.tags && task.tags.length > 0 && task.tags.map((tag) => (
        <span
          key={tag}
          className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
        >
          #{tag}
        </span>
      ))}

      {/* Recurrence Pattern */}
      {task.recurrence_pattern && task.recurrence_pattern !== 'none' && (
        <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
          <span className="mr-1.5 text-base">🔄</span>
          {task.recurrence_pattern.charAt(0).toUpperCase() + task.recurrence_pattern.slice(1)}
        </span>
      )}

      {/* Reminder */}
      {task.reminder_time && (
        <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400">
          <span className="mr-1.5 text-base">🔔</span>
          {task.reminder_time}
        </span>
      )}
    </div>
  );
};
