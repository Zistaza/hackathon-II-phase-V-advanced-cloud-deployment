---
name: backend-skill
description: Generate and manage FastAPI routes, handle requests and responses, and connect securely to the database.
---

# Backend Skill

## Instructions

1. **Route generation**
   - Create RESTful API routes using FastAPI
   - Follow consistent URL and HTTP method conventions
   - Support CRUD operations for application resources
   - Organize routes for scalability and clarity

2. **Request handling**
   - Parse and validate incoming requests
   - Enforce required fields and data types
   - Handle authentication and authorization hooks
   - Reject invalid or unauthorized requests gracefully

3. **Response handling**
   - Return structured and consistent API responses
   - Use appropriate HTTP status codes
   - Handle errors and edge cases clearly
   - Ensure responses are frontend-friendly

4. **Database connectivity**
   - Connect to the database using SQLModel or SQLAlchemy
   - Execute queries via Database Agent or Database Skill
   - Manage sessions safely and efficiently
   - Ensure data integrity during read/write operations

5. **Integration**
   - Integrate with Auth Agent for protected routes
   - Coordinate with Database Agent for data operations
   - Expose reusable backend logic for other agents

## Best Practices
- Keep route logic thin and reusable
- Separate request validation from business logic
- Use dependency injection for database sessions
- Return clear error messages without leaking internals
- Design APIs to be scalable and maintainable

## Example Structure
```python
class BackendSkill:
    def register_routes(self, app):
        # Define FastAPI routes
        pass

    def handle_request(self, data):
        # Validate and process incoming request
        pass

    def format_response(self, result):
        # Return structured API response
        pass

    def connect_database(self):
        # Initialize and manage DB connection
        pass