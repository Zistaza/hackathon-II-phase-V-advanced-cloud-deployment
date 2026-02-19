'use client';

import React, { useState } from 'react';
import { TaskCreate } from '../../types';
import { Input } from '../ui/input';
import { Button } from '../ui/button';

interface TaskFormProps {
  onSubmit: (taskData: TaskCreate) => void;
  onCancel?: () => void;
  initialData?: Partial<TaskCreate>;
  submitButtonText?: string;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  onSubmit,
  onCancel,
  initialData = {},
  submitButtonText = 'Create Task',
}) => {
  const [title, setTitle] = useState(initialData.title || '');
  const [description, setDescription] = useState(initialData.description || '');
  const [priority, setPriority] = useState(initialData.priority || 'medium');
  const [tags, setTags] = useState<string[]>(initialData.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [dueDate, setDueDate] = useState(initialData.due_date || '');
  const [recurrencePattern, setRecurrencePattern] = useState(initialData.recurrence_pattern || 'none');
  const [reminderTime, setReminderTime] = useState(initialData.reminder_time || '');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (title.length > 255) {
      setError('Title must be less than 255 characters');
      return;
    }

    setError('');
    onSubmit({
      title: title.trim(),
      description: description || null,
      completed: initialData.completed || false,
      priority,
      tags,
      due_date: dueDate || null,
      recurrence_pattern: recurrencePattern,
      reminder_time: reminderTime || null,
    });
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-destructive text-sm">{error}</div>}

      {/* Title input */}
      <Input
        label="Title"
        id="title"
        type="text"
        placeholder="Enter task title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />

      {/* Description textarea */}
      <Input
        label="Description"
        id="description"
        placeholder="Enter task description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        as="textarea"
        rows={3}
      />

      {/* Priority selector */}
      <div className="space-y-2">
        <label htmlFor="priority" className="text-sm font-medium">Priority</label>
        <select
          id="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      {/* Tags input */}
      <div className="space-y-2">
        <label htmlFor="tags" className="text-sm font-medium">Tags</label>
        <div className="flex gap-2">
          <input
            id="tags"
            type="text"
            placeholder="Add a tag"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <Button type="button" onClick={handleAddTag} variant="secondary">
            Add
          </Button>
        </div>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-destructive"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Due date */}
      <div className="space-y-2">
        <label htmlFor="dueDate" className="text-sm font-medium">Due Date</label>
        <input
          id="dueDate"
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {/* Recurrence pattern */}
      <div className="space-y-2">
        <label htmlFor="recurrence" className="text-sm font-medium">Recurrence</label>
        <select
          id="recurrence"
          value={recurrencePattern}
          onChange={(e) => setRecurrencePattern(e.target.value)}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="none">None</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>

      {/* Reminder time */}
      <div className="space-y-2">
        <label htmlFor="reminder" className="text-sm font-medium">Reminder</label>
        <input
          id="reminder"
          type="text"
          placeholder="e.g., 1 hour before, 1 day before"
          value={reminderTime}
          onChange={(e) => setReminderTime(e.target.value)}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <p className="text-xs text-muted-foreground">
          Enter reminder time (e.g., "1 hour before", "1 day before")
        </p>
      </div>

      <div className="flex flex-col sm:flex-row sm:justify-between space-y-3 sm:space-y-0">
        <Button type="submit" className="rounded-lg hover-lift">{submitButtonText}</Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel} className="rounded-lg hover-lift bg-red-600 text-white hover:bg-red-400 border-red-600 hover:border-red-400">
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};
