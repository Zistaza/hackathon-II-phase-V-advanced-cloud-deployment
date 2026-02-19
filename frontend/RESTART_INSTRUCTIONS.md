# Fix Login 404 Error - Restart Instructions

## The Problem
Next.js cached the old environment variable. The request is going to:
- ❌ `http://localhost:8000/auth/login` (WRONG - missing `/api`)

It should go to:
- ✅ `http://localhost:8000/api/auth/login` (CORRECT)

## Steps to Fix

1. **Stop your frontend dev server** (press Ctrl+C)

2. **The cache has been cleared** (.next folder deleted)

3. **Restart the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

4. **Check the browser console** - You should see:
   ```
   Auth Service API_BASE_URL: http://localhost:8000/api
   ```

5. **Try logging in again** - The network tab should now show:
   ```
   POST http://localhost:8000/api/auth/login
   ```

## If it still doesn't work

Check if you have multiple terminal windows running the frontend. Kill all of them and start fresh:

```bash
# Kill any running Next.js processes
pkill -f "next dev"

# Start fresh
cd frontend
npm run dev
```

## Verify Backend is Running

Make sure your backend is running on port 8000:
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

Test the endpoint directly:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```
