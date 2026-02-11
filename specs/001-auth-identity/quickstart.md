# Quickstart Guide: Authentication & Identity Implementation

## Overview
This guide provides a quick start for implementing the authentication and identity layer using Better Auth for frontend and JWT verification for backend.

## Prerequisites
- Node.js 18+ for frontend
- Python 3.11+ for backend
- Better Auth configured on frontend
- BETTER_AUTH_SECRET environment variable set

## Setup Steps

### 1. Environment Configuration
Set the shared secret for JWT signing/verification:
```bash
export BETTER_AUTH_SECRET="your-super-secret-jwt-key-here-make-it-long-and-random"
```

### 2. Frontend Authentication Setup
Configure Better Auth to generate JWT tokens:

```javascript
// frontend/src/lib/auth.js
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

const auth = betterAuth({
  plugins: [
    jwt({
      secret: process.env.BETTER_AUTH_SECRET,
    })
  ],
  // ... other auth configuration
});

export default auth;
```

### 3. Backend JWT Verification Setup
Create a JWT verification dependency for FastAPI:

```python
# backend/src/middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt
from typing import Dict, Optional
from pydantic import BaseModel

security = HTTPBearer()

class CurrentUser(BaseModel):
    user_id: str
    email: str

def verify_token(credentials=Depends(security)) -> CurrentUser:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            key=os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"]
        )
        return CurrentUser(user_id=payload.get("sub"), email=payload.get("user_email"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 4. Protected Route Implementation
Apply authentication to routes that require user identity:

```python
# backend/src/api/tasks.py
from fastapi import APIRouter, Depends
from middleware.auth import verify_token, CurrentUser

router = APIRouter()

@router.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, current_user: CurrentUser = Depends(verify_token)):
    # Verify user_id in URL matches JWT user_id for multi-tenant isolation
    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Return tasks for the authenticated user
    return await task_service.get_user_tasks(current_user.user_id)
```

## Key Implementation Points

### Multi-Tenant Isolation
Always verify that the user_id in the URL path matches the user_id in the JWT token:
```python
if path_user_id != jwt_user_id:
    raise HTTPException(status_code=403, detail="Access denied")
```

### Error Handling
Return HTTP 401 for authentication failures:
- Missing Authorization header
- Invalid JWT format
- Expired JWT
- Invalid signature

### Stateless Operation
The backend remains stateless by:
- Not storing session information
- Verifying JWT locally using shared secret
- Extracting user identity from JWT claims

## Testing Authentication Flow

### Positive Test Case
1. Register new user → HTTP 201 with JWT
2. Make API request with JWT → HTTP 200 with data
3. Verify user_id in JWT matches user_id in URL

### Negative Test Cases
1. API request without JWT → HTTP 401
2. API request with invalid JWT → HTTP 401
3. API request with expired JWT → HTTP 401
4. User_id mismatch between URL and JWT → HTTP 403

## Security Best Practices

### JWT Configuration
- Set reasonable expiration (24 hours recommended)
- Include required claims (iss, sub, exp, iat)
- Use HS256 algorithm with strong secret

### Secret Management
- Store BETTER_AUTH_SECRET in environment variables
- Never hardcode secrets in source code
- Rotate secrets regularly in production

### Input Validation
- Validate JWT format before decoding
- Verify required claims are present
- Check token expiration before use