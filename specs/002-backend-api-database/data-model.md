# Data Model: Backend API & Database for Todo Full-Stack Web Application

## Overview
This document defines the data models for the todo application backend, including the entities, their attributes, relationships, and validation rules.

## Entity: User

### Attributes
- **id** (str, Primary Key)
  - Type: String (UUID format)
  - Constraints: Primary key, not null, unique
  - Generated: Automatically using UUID
  - Description: Unique identifier for each user

- **email** (str)
  - Type: String (max 255 characters)
  - Constraints: Unique, not null
  - Validation: Must be valid email format
  - Description: User's email address for authentication

- **name** (str, optional)
  - Type: String (max 255 characters)
  - Constraints: Nullable
  - Description: User's display name

- **created_at** (datetime)
  - Type: DateTime
  - Constraints: Not null, default to current timestamp
  - Description: Timestamp when the user account was created

- **updated_at** (datetime)
  - Type: DateTime
  - Constraints: Not null, updates to current timestamp
  - Description: Timestamp when the user account was last updated

### Relationships
- One-to-Many: User has many Tasks

### Validation Rules
- Email must be unique across all users
- Email must follow valid email format
- Name is optional but if provided must be under 255 characters

## Entity: Task

### Attributes
- **id** (str, Primary Key)
  - Type: String (UUID format)
  - Constraints: Primary key, not null, unique
  - Generated: Automatically using UUID
  - Description: Unique identifier for each task

- **title** (str)
  - Type: String (max 255 characters)
  - Constraints: Not null
  - Validation: Required field, minimum 1 character
  - Description: Title or subject of the task

- **description** (str, optional)
  - Type: Text
  - Constraints: Nullable
  - Description: Detailed description of the task

- **completed** (bool)
  - Type: Boolean
  - Constraints: Not null, default false
  - Description: Whether the task has been completed or not

- **user_id** (str, Foreign Key)
  - Type: String
  - Constraints: Not null, foreign key reference to User.id
  - Description: Reference to the user who owns this task

- **created_at** (datetime)
  - Type: DateTime
  - Constraints: Not null, default to current timestamp
  - Description: Timestamp when the task was created

- **updated_at** (datetime)
  - Type: DateTime
  - Constraints: Not null, updates to current timestamp
  - Description: Timestamp when the task was last updated

### Relationships
- Many-to-One: Task belongs to one User (via user_id foreign key)

### Validation Rules
- Title is required and must be at least 1 character
- Title must be under 255 characters
- Description is optional with no length restriction
- Completed status defaults to false
- user_id must reference an existing user
- Tasks can only be accessed by their owner user

### State Transitions
- New Task: `completed = false` (default)
- Task Completion: `completed = true` (via PATCH endpoint)
- Task Reopening: `completed = false` (via PUT endpoint)

## Database Schema

### Tables

#### users table
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### tasks table
```sql
CREATE TABLE tasks (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
- Index on `users.email` for efficient login lookups
- Index on `tasks.user_id` for efficient user-based filtering
- Composite index on `tasks.user_id` and `tasks.completed` for common queries

## API Data Models

### TaskBase (Shared fields)
- title: str (required)
- description: str (optional, default: "")
- completed: bool (optional, default: false)

### TaskCreate (Extends TaskBase)
- No additional fields (inherits from TaskBase)

### TaskUpdate
- title: str (optional, nullable)
- description: str (optional, nullable)
- completed: bool (optional, nullable)

### Task (Response model extends TaskBase)
- id: str
- user_id: str
- created_at: datetime
- updated_at: datetime
- Inherits title, description, completed from TaskBase

### TaskListResponse
- tasks: List[Task]
- total_count: int
- completed_count: int
- pending_count: int