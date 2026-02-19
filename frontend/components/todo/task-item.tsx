'use client';

import React from 'react';
import { Task } from '../../types';
import { Button } from '../ui/button';
import AnimatedButton from '../ui/animated-button';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiEdit2, FiTrash2, FiCheck, FiStar, FiHeart, FiZap, FiTarget, FiAward, FiTrendingUp, FiCoffee, FiSun, FiMoon, FiCloud } from 'react-icons/fi';
import { TaskBadges } from './task-badges';
import { TaskMetadata } from './task-metadata';

interface TaskItemProps {
  task: Task;
  onToggleCompletion: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string) => void;
}

// Array of unique icons for tasks
const taskIcons = [
  FiStar,
  FiHeart,
  FiZap,
  FiTarget,
  FiAward,
  FiTrendingUp,
  FiCoffee,
  FiSun,
  FiMoon,
  FiCloud,
];

// Hash function to deterministically assign an icon based on task ID
const getTaskIcon = (taskId: string) => {
  let hash = 0;
  for (let i = 0; i < taskId.length; i++) {
    hash = taskId.charCodeAt(i) + ((hash << 5) - hash);
  }
  const IconComponent = taskIcons[Math.abs(hash) % taskIcons.length];
  return IconComponent;
};

export const TaskItem: React.FC<TaskItemProps> = ({
  task,
  onToggleCompletion,
  onDelete,
  onEdit
}) => {
  const prefersReducedMotion = typeof window !== 'undefined'
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false;

  const TaskIcon = getTaskIcon(task.id);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.2 }}
      whileHover={!prefersReducedMotion ? {
        scale: 1.03,
        y: -6,
        transition: { duration: 0.3, ease: "easeOut" }
      } : {}}
      className={`group relative rounded-xl border-2 transition-all duration-300 ${
        task.completed
          ? 'bg-muted/30 dark:bg-gray-800/50 border-border hover:shadow-2xl hover:bg-muted/60 dark:hover:bg-gray-800/80 hover:border-primary/30'
          : 'bg-card dark:bg-gray-900 border-border hover:shadow-2xl hover:bg-primary/5 dark:hover:bg-primary/10 hover:border-primary/50'
      }`}
    >
      <div className="p-8">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start space-x-4 flex-1 min-w-0">
            <motion.button
              whileTap={!prefersReducedMotion ? { scale: 0.9 } : {}}
              onClick={() => onToggleCompletion(task.id)}
              className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center mt-1 transition-colors duration-200 ${
                task.completed
                  ? 'bg-primary border-primary text-white'
                  : 'border-input hover:border-primary'
              }`}
              aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
            >
              {task.completed && (
                <motion.svg
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </motion.svg>
              )}
            </motion.button>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center transition-all duration-300 group-hover:bg-primary/20 dark:group-hover:bg-primary/30 group-hover:scale-110">
                  <TaskIcon className="w-5 h-5 text-primary transition-transform duration-300 group-hover:rotate-12" />
                </div>
                <h3 className={`font-semibold text-lg ${
                  task.completed
                    ? 'line-through text-muted-foreground'
                    : 'text-foreground'
                }`}>
                  {task.title}
                </h3>
                {task.completed && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">
                    <FiCheck className="w-3 h-3 mr-1" />
                    Done
                  </span>
                )}
              </div>

              {task.description && (
                <p className={`text-base mb-3 break-words ${
                  task.completed
                    ? 'line-through text-muted-foreground'
                    : 'text-muted-foreground'
                }`}>
                  {task.description}
                </p>
              )}

              <div className="mt-4">
                <TaskBadges task={task} />
              </div>

              <div className="mt-5">
                <TaskMetadata task={task} />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link href={`/tasks/${task.id}/edit`}>
              <AnimatedButton
                variant="outline"
                size="md"
                className="h-10 w-10 p-0 hover:bg-primary/10 hover:text-primary rounded-lg"
                aria-label="Edit task"
              >
                <FiEdit2 className="w-4 h-4" />
              </AnimatedButton>
            </Link>
            <AnimatedButton
              variant="outline"
              size="md"
              className="h-10 w-10 p-0 hover:bg-destructive/10 hover:text-destructive border-destructive/20 rounded-lg"
              onClick={() => onDelete(task.id)}
              aria-label="Delete task"
            >
              <FiTrash2 className="w-4 h-4" />
            </AnimatedButton>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
