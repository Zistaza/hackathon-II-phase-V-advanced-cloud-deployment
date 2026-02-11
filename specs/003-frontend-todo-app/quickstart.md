# Quickstart Guide: Frontend Todo Application

## Prerequisites
- Node.js 18+ installed
- Backend API running at `http://localhost:8000` (or configured endpoint)
- Better Auth properly configured with JWT authentication

## Setup Instructions

### 1. Clone and Install Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Configuration
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

### 3. Run Development Server
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## Key Features and Navigation

### Authentication Flow
1. Visit `/login` or `/register` to authenticate
2. After successful authentication, JWT token is securely stored
3. Protected routes become accessible

### Task Management
1. Navigate to `/tasks` to view all your tasks
2. Click "Create Task" to add new tasks
3. Use checkboxes to toggle completion status
4. Click edit/delete buttons to modify tasks

## Development Structure

### Key Components
- `components/auth/` - Authentication UI components
- `components/todo/` - Task management components
- `contexts/` - Global state management
- `hooks/` - Custom React hooks
- `lib/` - Utility functions and API clients
- `services/` - API service implementations

### Authentication
- Implemented with Better Auth
- JWT tokens stored in httpOnly cookies
- Protected routes using Next.js middleware

### State Management
- AuthContext: Manages authentication state
- TodoContext: Manages task data and operations
- useReducer: Handles complex state transitions

## API Integration
- Centralized API client with Axios
- Automatic JWT token attachment
- Global error handling
- Request/response interceptors