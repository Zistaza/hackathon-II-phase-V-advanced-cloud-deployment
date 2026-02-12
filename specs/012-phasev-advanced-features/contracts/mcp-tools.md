# MCP Tool Contracts: Phase-V Advanced Features

**Version**: 2.0.0
**Date**: 2026-02-12
**Feature**: 012-phasev-advanced-features

## Overview

This document defines the extended MCP tool schemas for Phase-V advanced features. All tools maintain backward compatibility with Phase-III implementations.

---

## add_task (Extended)

**Description**: Creates a new task with advanced features (priority, tags, due date, recurrence, reminder)

**Tool Schema**:
```json
{
  "name": "add_task",
  "description": "Create a new task with optional priority, tags, due date, recurrence pattern, and reminder",
  "input_schema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Task title (required, 1-200 characters)",
        "minLength": 1,
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "Task description (optional, max 2000 characters)",
        "maxLength": 2000
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high", "urgent"],
        "description": "Task priority level (optional, default: medium)",
        "default": "medium"
      },
      "tags": {
        "type": "array",
        "items": {
          "type": "string",
          "maxLength": 50
        },
        "description": "Array of tags (optional, max 20 tags)",
        "maxItems": 20,
        "default": []
      },
      "due_date": {
        "type": "string",
        "format": "date-time",
        "description": "Task due date in ISO 8601 format (optional, must be in future)"
      },
      "recurrence_pattern": {
        "type": "string",
        "enum": ["none", "daily", "weekly", "monthly"],
        "description": "Recurrence pattern (optional, default: none)",
        "default": "none"
      },
      "reminder_time": {
        "type": "string",
        "pattern": "^\\d+[hdw]$",
        "description": "Reminder time relative to due_date (optional, format: <number><h|d|w>, e.g., '1h', '2d', '1w')"
      }
    },
    "required": ["title"]
  }
}
```

**Request Example**:
```json
{
  "title": "Complete project proposal",
  "description": "Write and submit the Q1 project proposal",
  "priority": "high",
  "tags": ["work", "urgent", "client"],
  "due_date": "2026-02-15T11:00:00Z",
  "recurrence_pattern": "none",
  "reminder_time": "1h"
}
```

**Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Operation success status"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Created task ID"
    },
    "message": {
      "type": "string",
      "description": "Human-readable confirmation message"
    },
    "reminder_scheduled": {
      "type": "boolean",
      "description": "Whether reminder was successfully scheduled"
    }
  },
  "required": ["success", "task_id", "message"]
}
```

**Response Example**:
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Task 'Complete project proposal' created successfully with high priority and reminder set for 1 hour before due date",
  "reminder_scheduled": true
}
```

**Error Responses**:
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Due date cannot be in the past",
  "details": {
    "field": "due_date",
    "value": "2026-01-01T10:00:00Z"
  }
}
```

**Side Effects**:
- Creates task record in database
- Publishes task.created event to task-events topic
- Publishes task.created event to task-updates topic (for multi-client sync)
- Schedules reminder job via Dapr Jobs API (if reminder_time provided)

---

## update_task (Extended)

**Description**: Updates an existing task's properties including priority, tags, due date, recurrence, and reminder

**Tool Schema**:
```json
{
  "name": "update_task",
  "description": "Update an existing task's properties",
  "input_schema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "Task ID to update (required)"
      },
      "title": {
        "type": "string",
        "description": "New task title (optional, 1-200 characters)",
        "minLength": 1,
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "New task description (optional, max 2000 characters)",
        "maxLength": 2000
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high", "urgent"],
        "description": "New priority level (optional)"
      },
      "tags": {
        "type": "array",
        "items": {
          "type": "string",
          "maxLength": 50
        },
        "description": "New tags array (optional, replaces existing tags, max 20)",
        "maxItems": 20
      },
      "due_date": {
        "type": "string",
        "format": "date-time",
        "description": "New due date in ISO 8601 format (optional)"
      },
      "recurrence_pattern": {
        "type": "string",
        "enum": ["none", "daily", "weekly", "monthly"],
        "description": "New recurrence pattern (optional)"
      },
      "reminder_time": {
        "type": "string",
        "pattern": "^\\d+[hdw]$",
        "description": "New reminder time (optional, format: <number><h|d|w>)"
      }
    },
    "required": ["task_id"]
  }
}
```

**Request Example**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "priority": "urgent",
  "tags": ["work", "urgent", "client", "deadline"],
  "due_date": "2026-02-14T11:00:00Z"
}
```

**Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Operation success status"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Updated task ID"
    },
    "message": {
      "type": "string",
      "description": "Human-readable confirmation message"
    },
    "updated_fields": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of fields that were updated"
    },
    "reminder_rescheduled": {
      "type": "boolean",
      "description": "Whether reminder was rescheduled (if due_date or reminder_time changed)"
    }
  },
  "required": ["success", "task_id", "message", "updated_fields"]
}
```

**Response Example**:
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Task updated successfully",
  "updated_fields": ["priority", "tags", "due_date"],
  "reminder_rescheduled": true
}
```

**Side Effects**:
- Updates task record in database
- Publishes task.updated event to task-events topic
- Publishes task.updated event to task-updates topic (for multi-client sync)
- Cancels existing reminder job (if due_date or reminder_time changed)
- Schedules new reminder job (if due_date or reminder_time changed)

---

## list_tasks (Extended)

**Description**: Lists tasks with advanced filtering, searching, and sorting capabilities

**Tool Schema**:
```json
{
  "name": "list_tasks",
  "description": "List tasks with optional filtering, searching, and sorting",
  "input_schema": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["complete", "incomplete"],
        "description": "Filter by task status (optional)"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high", "urgent"],
        "description": "Filter by priority level (optional)"
      },
      "tags": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Filter by tags (optional, AND logic - task must have all specified tags)"
      },
      "due_date_filter": {
        "type": "string",
        "enum": ["overdue", "today", "this_week", "this_month"],
        "description": "Filter by due date range (optional)"
      },
      "search": {
        "type": "string",
        "description": "Full-text search on title and description (optional, case-insensitive)"
      },
      "sort_by": {
        "type": "string",
        "enum": ["created_at", "due_date", "priority", "status"],
        "description": "Sort field (optional, default: created_at)",
        "default": "created_at"
      },
      "sort_order": {
        "type": "string",
        "enum": ["asc", "desc"],
        "description": "Sort order (optional, default: desc)",
        "default": "desc"
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "description": "Maximum number of tasks to return (optional, default: 50)",
        "default": 50
      },
      "offset": {
        "type": "integer",
        "minimum": 0,
        "description": "Number of tasks to skip for pagination (optional, default: 0)",
        "default": 0
      }
    },
    "required": []
  }
}
```

**Request Example**:
```json
{
  "status": "incomplete",
  "priority": "urgent",
  "tags": ["work", "client"],
  "due_date_filter": "this_week",
  "sort_by": "due_date",
  "sort_order": "asc",
  "limit": 20
}
```

**Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Operation success status"
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "task_id": {
            "type": "string",
            "format": "uuid"
          },
          "title": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "status": {
            "type": "string",
            "enum": ["complete", "incomplete"]
          },
          "priority": {
            "type": "string",
            "enum": ["low", "medium", "high", "urgent"]
          },
          "tags": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "due_date": {
            "type": "string",
            "format": "date-time"
          },
          "recurrence_pattern": {
            "type": "string",
            "enum": ["none", "daily", "weekly", "monthly"]
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          },
          "updated_at": {
            "type": "string",
            "format": "date-time"
          },
          "completed_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      }
    },
    "total_count": {
      "type": "integer",
      "description": "Total number of tasks matching filters (for pagination)"
    },
    "message": {
      "type": "string",
      "description": "Human-readable summary"
    }
  },
  "required": ["success", "tasks", "total_count", "message"]
}
```

**Response Example**:
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project proposal",
      "description": "Write and submit the Q1 project proposal",
      "status": "incomplete",
      "priority": "urgent",
      "tags": ["work", "client"],
      "due_date": "2026-02-14T11:00:00Z",
      "recurrence_pattern": "none",
      "created_at": "2026-02-12T10:00:00Z",
      "updated_at": "2026-02-12T15:00:00Z",
      "completed_at": null
    }
  ],
  "total_count": 1,
  "message": "Found 1 incomplete urgent task with tags ['work', 'client'] due this week"
}
```

**Side Effects**: None (read-only operation)

---

## complete_task (Unchanged)

**Description**: Marks a task as complete (no schema changes from Phase-III)

**Side Effects** (Extended):
- Updates task record in database
- Publishes task.completed event to task-events topic (consumed by Recurring Task Service)
- Publishes task.completed event to task-updates topic (for multi-client sync)
- Cancels any pending reminder jobs for the task

---

## delete_task (Unchanged)

**Description**: Deletes a task (no schema changes from Phase-III)

**Side Effects** (Extended):
- Deletes task record from database
- Publishes task.deleted event to task-events topic
- Publishes task.deleted event to task-updates topic (for multi-client sync)
- Cancels any pending reminder jobs for the task

---

## Backward Compatibility

All new parameters are optional with sensible defaults:
- `priority`: defaults to "medium"
- `tags`: defaults to empty array
- `due_date`: defaults to null (no due date)
- `recurrence_pattern`: defaults to "none"
- `reminder_time`: defaults to null (no reminder)
- `sort_by`: defaults to "created_at"
- `sort_order`: defaults to "desc"

Existing Phase-III tool calls continue to work without modification.

---

## Authorization

All tools MUST validate:
1. JWT token is present and valid
2. user_id from JWT matches user_id in URL path
3. For update/complete/delete operations: task belongs to authenticated user

Unauthorized requests return HTTP 403 Forbidden.

---

## Rate Limiting

- add_task: 100 requests per minute per user
- update_task: 100 requests per minute per user
- list_tasks: 200 requests per minute per user
- complete_task: 100 requests per minute per user
- delete_task: 100 requests per minute per user

Exceeded limits return HTTP 429 Too Many Requests.
