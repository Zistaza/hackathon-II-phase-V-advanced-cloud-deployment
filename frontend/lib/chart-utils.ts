import { Task } from '../types';

export interface TaskCompletionData {
  date: string;
  completed: number;
  total: number;
}

export interface PriorityDistribution {
  priority: string;
  count: number;
  percentage: number;
}

export interface TagAnalytics {
  tag: string;
  count: number;
}

/**
 * Generate task completion data for the last N days
 */
export function generateCompletionTrend(tasks: Task[], days: number = 7): TaskCompletionData[] {
  const today = new Date();
  const data: TaskCompletionData[] = [];

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    date.setHours(0, 0, 0, 0);

    const nextDate = new Date(date);
    nextDate.setDate(nextDate.getDate() + 1);

    const completedOnDay = tasks.filter(task => {
      if (!task.completed || !task.updated_at) return false;
      const updatedDate = new Date(task.updated_at);
      return updatedDate >= date && updatedDate < nextDate;
    }).length;

    const totalOnDay = tasks.filter(task => {
      const createdDate = new Date(task.created_at);
      return createdDate <= nextDate;
    }).length;

    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      completed: completedOnDay,
      total: totalOnDay,
    });
  }

  return data;
}

/**
 * Calculate priority distribution
 */
export function calculatePriorityDistribution(tasks: Task[]): PriorityDistribution[] {
  const priorityCounts: Record<string, number> = {
    urgent: 0,
    high: 0,
    medium: 0,
    low: 0,
  };

  tasks.forEach(task => {
    const priority = task.priority || 'medium';
    priorityCounts[priority] = (priorityCounts[priority] || 0) + 1;
  });

  const total = tasks.length || 1;

  return Object.entries(priorityCounts)
    .map(([priority, count]) => ({
      priority: priority.charAt(0).toUpperCase() + priority.slice(1),
      count,
      percentage: Math.round((count / total) * 100),
    }))
    .filter(item => item.count > 0)
    .sort((a, b) => b.count - a.count);
}

/**
 * Calculate tag usage analytics
 */
export function calculateTagAnalytics(tasks: Task[], limit: number = 10): TagAnalytics[] {
  const tagCounts: Record<string, number> = {};

  tasks.forEach(task => {
    if (task.tags && Array.isArray(task.tags)) {
      task.tags.forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    }
  });

  return Object.entries(tagCounts)
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limit);
}

/**
 * Get chart colors based on theme
 */
export function getChartColors(isDark: boolean) {
  return {
    primary: isDark ? '#60a5fa' : '#3b82f6',
    secondary: isDark ? '#1f2937' : '#f3f4f6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
    text: isDark ? '#ededed' : '#171717',
    muted: isDark ? '#9ca3af' : '#6b7280',
    grid: isDark ? '#374151' : '#e5e7eb',
  };
}
