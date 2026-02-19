'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../../../contexts/auth-context';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { todoService } from '../../../services/todo-service';
import AnimatedButton from '../../../components/ui/animated-button';
import { FiHome } from 'react-icons/fi';
import { useTaskAnalytics } from '../../../hooks/use-task-analytics';
import { ChartCard } from '../../../components/charts/chart-card';
import { TaskCompletionChart } from '../../../components/charts/task-completion-chart';
import { PriorityDistributionChart } from '../../../components/charts/priority-distribution-chart';
import { TagAnalyticsChart } from '../../../components/charts/tag-analytics-chart';

export default function DashboardPage() {
  const { state } = useAuth();
  const [stats, setStats] = useState({
    totalTasks: 0,
    completedTasks: 0,
    pendingTasks: 0,
  });
  const [loading, setLoading] = useState(true);
  const analytics = useTaskAnalytics(7);

  useEffect(() => {
    const fetchTaskStats = async () => {
      try {
        const tasks = await todoService.getTasks();
        setStats({
          totalTasks: tasks.length,
          completedTasks: tasks.filter(t => t.completed).length,
          pendingTasks: tasks.filter(t => !t.completed).length,
        });
      } catch {
        setStats({ totalTasks: 0, completedTasks: 0, pendingTasks: 0 });
      } finally {
        setLoading(false);
      }
    };

    fetchTaskStats();
  }, []);

  return (
    <section className="min-h-[calc(100vh-4rem)] flex justify-center px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-6xl py-12 animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-12 text-center sm:text-left">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-foreground mb-2">
              Dashboard
            </h1>
            <p className="text-base sm:text-lg text-muted-foreground">
              Welcome back, {state.user?.name}!
            </p>
          </div>

          <Link href="/">
            <AnimatedButton
              variant="ghost"
              size="sm"
              className="flex items-center gap-2 px-4 text-muted-foreground hover:text-foreground"
            >
              <FiHome className="w-4 h-4" />
              Back to Home
            </AnimatedButton>
          </Link>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          <Card className="transition-shadow duration-200 hover:shadow-lg">
            <CardHeader className="p-6">
              <CardTitle className="text-xl">Manage Your Tasks</CardTitle>
            </CardHeader>
            <CardContent className="p-6 pt-0 space-y-4">
              <p className="text-base text-muted-foreground">
                Create, view, and manage your todo items efficiently.
              </p>
              <Link href="/tasks">
                <Button size="lg" className="w-full sm:w-auto px-8 rounded-lg text-base font-semibold">
                  View Tasks
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="transition-shadow duration-200 hover:shadow-lg">
            <CardHeader className="p-6">
              <CardTitle className="text-xl">Add New Task</CardTitle>
            </CardHeader>
            <CardContent className="p-6 pt-0 space-y-4">
              <p className="text-base text-muted-foreground">
                Get started by creating your first task.
              </p>
              <Link href="/tasks/create">
                <Button size="lg" className="w-full sm:w-auto px-8 rounded-lg text-base font-semibold">
                  Create Task
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Stats */}
        <div className="bg-card rounded-xl border p-6 mb-8">
          <h2 className="text-xl font-bold mb-8 text-center">Quick Stats</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { label: 'Total Tasks', value: stats.totalTasks },
              { label: 'Completed', value: stats.completedTasks },
              { label: 'Pending', value: stats.pendingTasks },
            ].map((item, i) => (
              <div
                key={i}
                className="p-6 bg-secondary rounded-xl transition-shadow duration-200 hover:shadow-md"
              >
                <p className="text-4xl font-bold text-primary mb-2">
                  {loading ? <span className="animate-pulse">...</span> : item.value}
                </p>
                <p className="text-base text-muted-foreground">{item.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Analytics Charts */}
        <div className="space-y-8">
          {/* Task Completion Trend - Full Width */}
          <ChartCard
            title="Task Completion Trend (Last 7 Days)"
            loading={analytics.loading}
            error={analytics.error}
          >
            <TaskCompletionChart data={analytics.completionTrend} />
          </ChartCard>

          {/* Priority Distribution and Tag Analytics - Side by Side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ChartCard
              title="Priority Distribution"
              loading={analytics.loading}
              error={analytics.error}
            >
              <PriorityDistributionChart data={analytics.priorityDistribution} />
            </ChartCard>

            <ChartCard
              title="Top Tags"
              loading={analytics.loading}
              error={analytics.error}
            >
              <TagAnalyticsChart data={analytics.tagAnalytics} />
            </ChartCard>
          </div>
        </div>
      </div>
    </section>
  );
}
