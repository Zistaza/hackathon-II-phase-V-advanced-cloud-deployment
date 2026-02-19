#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Backend Health Check                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if backend is running
echo "1. Checking if backend is running on port 8001..."
if ps aux | grep -q "[u]vicorn.*8001"; then
    echo "   ✓ Backend is running"
else
    echo "   ✗ Backend is NOT running"
    exit 1
fi

# Check health endpoint
echo ""
echo "2. Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8001/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✓ Health endpoint responding"
    echo "   Response: $HEALTH"
else
    echo "   ✗ Health endpoint not responding"
fi

# Check auth endpoint
echo ""
echo "3. Testing auth login endpoint..."
LOGIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}')

if [ "$LOGIN_RESPONSE" = "200" ] || [ "$LOGIN_RESPONSE" = "401" ]; then
    echo "   ✓ Auth endpoint responding (Status: $LOGIN_RESPONSE)"
else
    echo "   ✗ Auth endpoint not responding properly (Status: $LOGIN_RESPONSE)"
fi

# Check CORS headers
echo ""
echo "4. Checking CORS headers..."
CORS=$(curl -s -I http://localhost:8001/health | grep -i "access-control")
if [ -n "$CORS" ]; then
    echo "   ✓ CORS headers present"
    echo "$CORS"
else
    echo "   ✗ CORS headers missing"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Frontend Environment Check                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd frontend 2>/dev/null || cd ../frontend 2>/dev/null || echo "Could not find frontend directory"

if [ -f .env.local ]; then
    echo "5. Checking .env.local..."
    echo "   Content:"
    cat .env.local | sed 's/^/   /'
else
    echo "   ✗ .env.local not found"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "All checks complete!"
echo "═══════════════════════════════════════════════════════════"
