# API Documentation - Phase-V Advanced Features

**Version**: 1.0.0
**Base URL**: `http://localhost:8000/api`
**Authentication**: JWT Bearer Token

---

## MCP Tools API

### 1. Add Task

**Tool Name**: `add_task`

**Description**: Create a new task with advanced features including priority, tags, due dates, recurrence, and reminders.

**Input Schema**:
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 2000 chars)",
  "priority": "low | medium | high | urgent (optional, default: medium)",
  "tags": ["string"] (optional, max 20 tags, max 50 chars each),
  "due_date": "ISO 8601 datetime (optional, must be in future)",
  "recurrence_pattern": "none | daily | weekly | monthly (optional, default: none)",
  "reminder_time": "string (optional, format: <number><h|d|w>, e.g., '1h', '2d', '1w')"
}
```

**Example Request**:
```json
{
  "title": "Complete project proposal",
  "description": "Write and submit Q1 project proposal",
  "priority": "high",
  "tags": ["work", "urgent"],
  "due_date": "2026-02-15T11:00:00Z",
  "recurrence_pattern": "none",
  "reminder_time": "1h"
}
```

**Response**:
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Task 'Complete project proposal' created successfully",
  "reminder_scheduled": true
}
```

---

### 2. Update Task

**Tool Name**: `update_task`

**Description**: Update an existing task's properties.

**Input Schema**:
```json
{
  "task_id": "uuid (required)",
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 2000 chars)",
  "priority": "low | medium | high | urgent (optional)",
  "tags": ["string"] (optional, replaces existing tags)",
  "due_date": "ISO 8601 datetime (optional)",
  "recurrence_pattern": "none | daily | weekly | monthly (optional)",
  "reminder_time": "string (optional, format: <number><h|d|w>)"
}
```

**Example Request**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "priority": "urgent",
  "tags": ["work", "urgent", "client"]
}
```

**Response**:
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Task updated successfully",
  "updated_fields": ["priority", "tags"],
  "reminder_rescheduled": false
}
```

---

### 3. List Tasks

**Tool Name**: `list_tasks`

**Description**: List tasks with advanced filtering, searching, and sorting capabilities.

**Input Schema**:
```json
{
  "status": "complete | incomplete (optional)",
  "priority": "low | medium | high | urgent (optional)",
  "tags": ["string"] (optional, AND logic - task must have all specified tags)",
  "due_date_filter": "overdue | today | this_week | this_month (optional)",
  "search": "string (optional, full-text search on title and description)",
  "sort_by": "created_at | due_date | priority | status (optional, default: created_at)",
  "sort_order": "asc | desc (optional, default: desc)",
  "limit": "integer (optional, 1-100, default: 50)",
  "offset": "integer (optional, default: 0)"
}
```

**Example Request**:
```json
{
  "status": "incomplete",
  "priority": "high",
  "tags": ["work"],
  "due_date_filter": "this_week",
  "sort_by": "due_date",
  "sort_order": "asc",
  "limit": 20
}
```

**Response**:
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project proposal",
      "description": "Write and submit Q1 project proposal",
      "status": "incomplete",
      "priority": "high",
      "tags": ["work", "urgent"],
      "due_date": "2026-02-15T11:00:00Z",
      "recurrence_pattern": "none",
      "created_at": "2026-02-12T10:00:00Z",
      "updated_at": "2026-02-12T10:00:00Z",
      "completed_at": null
    }
  ],
  "total_count": 1,
  "message": "Found 1 tasks"
}
```

---

### 4. Complete Task

**Tool Name**: `complete_task`

**Description**: Mark a task as complete and cancel pending reminders.

**Input Schema**:
```json
{
  "task_id": "uuid (required)"
}
```

**Response**:
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Task 'Complete project proposal' marked as complete"
}
```

---

### 5. Delete Task

**Tool Name**: `delete_task`

**Description**: Delete a task and cancel pending reminders.

**Input Schema**:
```json
{
  "task_id": "uuid (required)"
}
```

**Response**:
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Task deleted successfully"
}
```

---

## REST API Endpoints

### Reminder Handler

**Endpoint**: `POST /api/reminders/trigger`

**Description**: Dapr Jobs API callback endpoint for reminder triggers.

**Request Body**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "task_title": "Complete project proposal",
  "due_date": "2026-02-15T11:00:00Z",
  "reminder_message": "Task 'Complete project proposal' is due in 1 hour",
  "scheduled_time": "2026-02-15T10:00:00Z"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Reminder event published successfully",
  "event_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

---

### WebSocket Connection

**Endpoint**: `GET /ws/{user_id}?token={jwt_token}`

**Description**: WebSocket endpoint for real-time task updates.

**Query Parameters**:
- `token`: JWT authentication token (required)

**Connection Flow**:
1. Client connects with JWT token in query parameter
2. Server validates token and user_id match
3. Connection established with Dapr sidecar subscription to task-updates topic
4. Server pushes task events to client in real-time

**Message Format**:
```json
{
  "event_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "event_type": "task.created | task.updated | task.completed | task.deleted",
  "user_id": "user123",
  "timestamp": "2026-02-12T10:00:00Z",
  "payload": {
    // Event-specific payload
  }
}
```

---

### Health Checks

**Endpoint**: `GET /health`

**Description**: Health check for main API service.

**Response**:
```json
{
  "status": "healthy",
  "service": "todo-api"
}
```

**Endpoint**: `GET /api/reminders/health`

**Description**: Health check for reminder handler.

**Endpoint**: `GET /ws/health`

**Description**: Health check for WebSocket service.

---

## Metrics Endpoint

**Endpoint**: `GET /metrics`

**Description**: Prometheus metrics endpoint.

**Response**: Prometheus text format with all Phase-V metrics.

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes**:
- `200 OK`: Successful operation
- `400 Bad Request`: Invalid input parameters
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Task not found
- `500 Internal Server Error`: Server-side error

---

## Authentication

All API endpoints require JWT authentication via Bearer token:

```
Authorization: Bearer <jwt_token>
```

The JWT token must contain:
- `sub` or `user_id`: User identifier
- `exp`: Expiration timestamp

---

## Rate Limiting

- Default: 100 requests per minute per user
- Burst: 200 requests per minute

---

## Backward Compatibility

All new parameters in Phase-V are optional with sensible defaults:
- `priority`: Defaults to "medium"
- `tags`: Defaults to empty array
- `recurrence_pattern`: Defaults to "none"
- Existing tool calls without new parameters continue to work unchanged
