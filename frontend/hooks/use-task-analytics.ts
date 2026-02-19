'use client';

import { useState, useEffect } from 'react';
import { Task } from '../types';
import { todoService } from '../services/todo-service';
import {
  generateCompletionTrend,
  calculatePriorityDistribution,
  calculateTagAnalytics,
  TaskCompletionData,
  PriorityDistribution,
  TagAnalytics,
} from '../lib/chart-utils';

interface TaskAnalytics {
  completionTrend: TaskCompletionData[];
  priorityDistribution: PriorityDistribution[];
  tagAnalytics: TagAnalytics[];
  loading: boolean;
  error: string | null;
}

export function useTaskAnalytics(days: number = 7) {
  const [analytics, setAnalytics] = useState<TaskAnalytics>({
    completionTrend: [],
    priorityDistribution: [],
    tagAnalytics: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setAnalytics(prev => ({ ...prev, loading: true, error: null }));

        const tasks = await todoService.getTasks();

        const completionTrend = generateCompletionTrend(tasks, days);
        const priorityDistribution = calculatePriorityDistribution(tasks);
        const tagAnalytics = calculateTagAnalytics(tasks, 10);

        setAnalytics({
          completionTrend,
          priorityDistribution,
          tagAnalytics,
          loading: false,
          error: null,
        });
      } catch (error) {
        setAnalytics(prev => ({
          ...prev,
          loading: false,
          error: error instanceof Error ? error.message : 'Failed to fetch analytics',
        }));
      }
    };

    fetchAnalytics();
  }, [days]);

  return analytics;
}
