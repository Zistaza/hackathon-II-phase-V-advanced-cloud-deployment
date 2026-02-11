# Data Model: Frontend Todo Application

## Entities

### User
- **Fields**:
  - `id`: string (unique identifier)
  - `email`: string (user's email address)
  - `name`: string (user's display name)
  - `created_at`: string (ISO date format)
  - `updated_at`: string (ISO date format)

### Task (Todo)
- **Fields**:
  - `id`: string (unique identifier)
  - `title`: string (task title, required)
  - `description`: string | null (optional task description)
  - `completed`: boolean (completion status)
  - `user_id`: string (foreign key to user)
  - `created_at`: string (ISO date format)
  - `updated_at`: string (ISO date format)

## Relationships
- One User has many Tasks
- Foreign Key: Task.user_id → User.id

## Validation Rules
- Task title must be at least 1 character
- Task title must not exceed 255 characters
- User email must be valid email format
- User email must be unique

## State Transitions
- Task: pending → completed (via PATCH /api/{user_id}/tasks/{id}/complete)
- Task: completed → pending (via PATCH /api/{user_id}/tasks/{id}/complete)