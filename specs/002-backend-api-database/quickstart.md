# Quickstart Guide: Backend API & Database for Todo Full-Stack Web Application

## Overview
This guide provides step-by-step instructions to set up and run the backend API for the todo application with database integration.

## Prerequisites
- Python 3.11+
- PostgreSQL database (Neon Serverless recommended)
- pip package manager

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Hackathon-II-phase-II-todo-full-stack
```

### 2. Set up Virtual Environment
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the backend directory with the following variables:

```env
DATABASE_URL=postgresql://username:password@host:port/database_name
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
```

For Neon Serverless PostgreSQL, your DATABASE_URL will look like:
```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
```

## Database Setup

### 1. Create the Database Tables
The application uses SQLModel for database operations. To initialize the database:

```bash
# From the backend directory
python -c "from src.database import init_db; init_db()"
```

### 2. (Optional) Set up Alembic for Migrations
If using Alembic for database migrations:

```bash
# Install alembic if not already installed
pip install alembic

# Initialize alembic (only needed once)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply the migration
alembic upgrade head
```

## Running the Application

### 1. Start the Development Server
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Verify the API is Running
Visit `http://localhost:8000/health` to check if the API is running correctly.

## API Usage Examples

### 1. Authentication
First, obtain a JWT token through the authentication endpoints (refer to auth API documentation).

### 2. Working with Tasks
Once authenticated, you can perform task operations using the JWT token in the Authorization header:

```bash
# Get all tasks for a user
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/user-id-here/tasks

# Create a new task
curl -X POST \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "New Task", "description": "Task description"}' \
     http://localhost:8000/api/user-id-here/tasks

# Update a task
curl -X PUT \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "Updated Task", "completed": true}' \
     http://localhost:8000/api/user-id-here/tasks/task-id-here

# Delete a task
curl -X DELETE \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/user-id-here/tasks/task-id-here

# Toggle task completion
curl -X PATCH \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/user-id-here/tasks/task-id-here/complete
```

## Testing

### 1. Run Unit Tests
```bash
cd backend
pytest tests/unit/ -v
```

### 2. Run Integration Tests
```bash
cd backend
pytest tests/integration/ -v
```

## Production Deployment

### 1. Environment Configuration
For production, ensure these environment variables are set:
- `DATABASE_URL`: Production database URL
- `BETTER_AUTH_SECRET`: Secure JWT secret
- `DEBUG`: Set to `false` for production

### 2. Deploy the Application
The application can be deployed to any platform that supports Python applications (Heroku, AWS, Google Cloud, etc.).

Example for deploying with gunicorn:
```bash
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Verify your DATABASE_URL is correct and the database is accessible.

2. **JWT Authentication Error**: Ensure the BETTER_AUTH_SECRET matches between the authentication service and the API.

3. **Multi-tenant Access Error**: Verify that the user_id in the URL matches the user_id in the JWT token.

4. **Missing Dependencies**: Run `pip install -r requirements.txt` again to ensure all dependencies are installed.

## Next Steps
- Implement proper logging and monitoring
- Set up automated testing pipeline
- Configure database connection pooling for production
- Add caching layer for improved performance