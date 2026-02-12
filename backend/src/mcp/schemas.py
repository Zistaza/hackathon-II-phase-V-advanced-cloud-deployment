"""
MCP Tool Schemas for Phase-V Advanced Features
Extended schemas for add_task, update_task, list_tasks with new parameters
"""

# Extended add_task schema
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Create a new task with optional priority, tags, due date, recurrence, and reminder",
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

# Extended update_task schema
UPDATE_TASK_SCHEMA = {
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

# Extended list_tasks schema
LIST_TASKS_SCHEMA = {
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

# Complete_task schema (unchanged from Phase-III)
COMPLETE_TASK_SCHEMA = {
    "name": "complete_task",
    "description": "Mark a task as complete",
    "input_schema": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "format": "uuid",
                "description": "Task ID to complete (required)"
            }
        },
        "required": ["task_id"]
    }
}

# Delete_task schema (unchanged from Phase-III)
DELETE_TASK_SCHEMA = {
    "name": "delete_task",
    "description": "Delete a task",
    "input_schema": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "format": "uuid",
                "description": "Task ID to delete (required)"
            }
        },
        "required": ["task_id"]
    }
}

# All MCP tool schemas
MCP_TOOL_SCHEMAS = [
    ADD_TASK_SCHEMA,
    UPDATE_TASK_SCHEMA,
    LIST_TASKS_SCHEMA,
    COMPLETE_TASK_SCHEMA,
    DELETE_TASK_SCHEMA
]
