'use client';

import React from 'react';
import { Task } from '../../types';
import { FiCalendar, FiCheck } from 'react-icons/fi';

interface TaskMetadataProps {
  task: Task;
}

export const TaskMetadata: React.FC<TaskMetadataProps> = ({ task }) => {
  return (
    <div className="flex flex-wrap items-center gap-5 text-base text-muted-foreground">
      {/* Due Date */}
      {task.due_date && (
        <div className="flex items-center gap-2">
          <FiCalendar className="w-5 h-5" />
          <span className="font-medium">Due: {new Date(task.due_date).toLocaleString()}</span>
        </div>
      )}

      {/* Created Date */}
      <div className="flex items-center gap-2">
        <FiCalendar className="w-5 h-5" />
        <span className="font-medium">Created: {new Date(task.created_at).toLocaleDateString()}</span>
      </div>

      {/* Completed Date */}
      {task.completed && (
        <div className="flex items-center gap-2">
          <FiCheck className="w-5 h-5" />
          <span className="font-medium">Completed: {new Date(task.updated_at || task.created_at).toLocaleDateString()}</span>
        </div>
      )}
    </div>
  );
};
