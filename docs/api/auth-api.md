# Authentication API Documentation

## Overview
This document describes the authentication API endpoints for the Todo Full-Stack Web Application. The system implements JWT-based authentication with Better Auth integration for frontend authentication and backend JWT verification.

## Authentication Flow
1. User registers/logs in via frontend (Better Auth handles this)
2. Better Auth generates JWT token
3. Client stores token (localStorage)
4. Client sends token in Authorization header for protected API requests
5. Backend verifies JWT using shared secret (BETTER_AUTH_SECRET)
6. Backend extracts user identity from JWT for request processing

## Authentication Endpoints

### POST /api/v1/auth/register
Register a new user and receive JWT token.

#### Request
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

#### Response (200 OK)
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid-string",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

#### Error Responses
- `409 Conflict`: User with email already exists
- `422 Unprocessable Entity`: Invalid request data

---

### POST /api/v1/auth/login
Authenticate user and receive JWT token.

#### Request
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Response (200 OK)
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid-string",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

#### Error Responses
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Invalid request data

---

### POST /api/v1/auth/logout
Logout user (stateless system, just client-side cleanup).

#### Response (200 OK)
```json
{
  "message": "Successfully logged out"
}
```

## Protected API Endpoints

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt-token-here>
```

### GET /api/v1/{user_id}/tasks
Get all tasks for the authenticated user.

#### Path Parameters
- `user_id` (string): User ID from URL path (must match JWT user_id)

#### Headers
- `Authorization: Bearer <jwt-token>`

#### Response (200 OK)
```json
[
  {
    "id": "task-uuid-string",
    "user_id": "user-uuid-string",
    "title": "Sample Task",
    "description": "Sample task description",
    "completed": false,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

#### Error Responses
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: user_id in URL doesn't match JWT user_id
- `404 Not Found`: User not found

---

### POST /api/v1/{user_id}/tasks
Create a new task for the authenticated user.

#### Path Parameters
- `user_id` (string): User ID from URL path (must match JWT user_id)

#### Headers
- `Authorization: Bearer <jwt-token>`

#### Request Body
```json
{
  "title": "New Task",
  "description": "Description of the new task",
  "completed": false
}
```

#### Response (200 OK)
```json
{
  "id": "task-uuid-string",
  "user_id": "user-uuid-string",
  "title": "New Task",
  "description": "Description of the new task",
  "completed": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: user_id in URL doesn't match JWT user_id
- `422 Unprocessable Entity`: Invalid request data

---

### Additional Protected Endpoints
Similar patterns apply to:
- `GET /api/v1/{user_id}/tasks/{id}` - Get specific task
- `PUT /api/v1/{user_id}/tasks/{id}` - Update specific task
- `DELETE /api/v1/{user_id}/tasks/{id}` - Delete specific task
- `PATCH /api/v1/{user_id}/tasks/{id}/complete` - Toggle task completion

## JWT Token Structure

The system uses HS256 algorithm for JWT signing with the BETTER_AUTH_SECRET.

### Claims
- `sub` (Subject): User ID
- `email` (Email): User's email address
- `exp` (Expiration Time): Token expiration timestamp
- `iat` (Issued At): Token creation timestamp
- `iss` (Issuer): "better-auth"
- `aud` (Audience): "todo-app"

### Token Expiration
Tokens expire after 24 hours (86400 seconds) by default.

## Security Considerations

1. **Multi-tenant Isolation**: All user-specific routes validate that the user_id in the URL matches the user_id in the JWT token.
2. **Stateless Authentication**: The backend does not store session information; authentication is verified through JWT signature.
3. **Shared Secret**: Both frontend (Better Auth) and backend use the same BETTER_AUTH_SECRET for JWT signing/verification.
4. **Token Validation**: All protected endpoints verify JWT signature and expiration before processing requests.
5. **Authorization Headers**: All authentication tokens must be sent in the Authorization header with Bearer scheme.

## Error Handling

- `401 Unauthorized`: Returned when no token is provided, token is invalid, or token is expired.
- `403 Forbidden`: Returned when the authenticated user doesn't have access to the requested resource (e.g., user_id mismatch).
- `409 Conflict`: Returned when trying to register a user with an existing email.
- `422 Unprocessable Entity`: Returned when request data is invalid.