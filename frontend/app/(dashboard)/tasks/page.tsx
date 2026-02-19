'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';

import { useTodo } from '../../../contexts/todo-context';
import { TaskList } from '../../../components/todo/task-list';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import AnimatedButton from '../../../components/ui/animated-button';

import {
  FiPlus,
  FiHome,
  FiRefreshCw,
  FiFilter,
  FiCheckSquare,
} from 'react-icons/fi';

export default function TasksPage() {
  const router = useRouter();
  const { state, fetchTasks, deleteTask, toggleTaskCompletion } = useTodo();
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  const filteredTasks = state.tasks.filter(task => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  return (
    <section className="flex justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="w-full max-w-5xl">

        {/* ===== Header ===== */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mb-12"
        >
          {/* Title + Subtitle */}
          <div className="text-center lg:text-left mb-8">
            <h1 className="text-3xl sm:text-4xl font-bold text-primary mb-2">
              My Tasks
            </h1>
            <p className="text-muted-foreground text-base sm:text-lg">
              Manage your daily activities efficiently
            </p>
          </div>

          {/* ===== Action Buttons ===== */}
          <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
            {/* Left: Back to Home */}
            <Link href="/">
              <AnimatedButton
                variant="ghost"
                size="sm"
                className="flex items-center gap-2 px-4 rounded-lg text-muted-foreground hover:text-foreground"
              >
                <FiHome className="w-4 h-4" />
                Back to Home
              </AnimatedButton>
            </Link>

            {/* Right: Create Task - Primary Action */}
            <Link href="/tasks/create">
              <AnimatedButton
                variant="primary"
                size="lg"
                className="flex items-center gap-2 px-8 rounded-lg text-base font-semibold shadow-md hover:shadow-lg"
              >
                <FiPlus className="w-5 h-5" />
                Create Task
              </AnimatedButton>
            </Link>
          </div>

          {/* ===== Filters ===== */}
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            {/* Filter label */}
            <div className="flex items-center gap-2 text-muted-foreground">
              <FiFilter className="w-4 h-4" />
              <span className="text-sm font-medium">Filter:</span>
            </div>

            {/* Filter buttons */}
            <div className="flex flex-wrap gap-4 bg-muted/50 rounded-lg p-2">
              {(['all', 'active', 'completed'] as const).map(option => (
                <button
                  key={option}
                  onClick={() => setFilter(option)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    filter === option
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground hover:bg-background/50'
                  }`}
                >
                  {option.charAt(0).toUpperCase() + option.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* ===== Task List Card ===== */}
        <Card className="border shadow-lg rounded-xl">
          <CardHeader className="p-6">
            <CardTitle className="flex items-center justify-center gap-2 text-xl">
              <FiCheckSquare className="text-primary" />
              Your Tasks
            </CardTitle>
          </CardHeader>

          <CardContent className="p-6 pt-0">
            <TaskList
              tasks={filteredTasks}
              loading={state.loading}
              onToggleCompletion={toggleTaskCompletion}
              onDelete={deleteTask}
              onEdit={(id) => router.push(`/tasks/${id}/edit`)}
            />

            {state.error && (
              <div className="mt-6 p-4 border border-destructive rounded-lg">
                <p className="text-destructive text-sm mb-4">{state.error}</p>
                <AnimatedButton
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2 px-4 rounded-lg"
                  onClick={fetchTasks}
                >
                  <FiRefreshCw className="w-4 h-4" />
                  Retry
                </AnimatedButton>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
