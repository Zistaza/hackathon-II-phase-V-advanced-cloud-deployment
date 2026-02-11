#!/bin/bash
# Script to start Minikube service tunnels for Todo App

echo "🚀 Starting Minikube service tunnels..."
echo ""
echo "This will create tunnels to access your services from Windows browser"
echo "Keep this terminal open while using the application"
echo ""

# Start backend tunnel in background
echo "Starting backend tunnel..."
minikube service todo-app-todo-chatbot-backend --namespace todo-app --url > /tmp/backend-url.txt 2>&1 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend tunnel in background
echo "Starting frontend tunnel..."
minikube service todo-app-todo-chatbot-frontend --namespace todo-app --url > /tmp/frontend-url.txt 2>&1 &
FRONTEND_PID=$!

# Wait for tunnels to establish
sleep 5

# Read the URLs
BACKEND_URL=$(head -1 /tmp/backend-url.txt)
FRONTEND_URL=$(head -1 /tmp/frontend-url.txt)

echo ""
echo "✅ Tunnels established!"
echo ""
echo "📍 Access URLs:"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend:  $BACKEND_URL"
echo ""
echo "⚠️  IMPORTANT: Update frontend to use backend URL: $BACKEND_URL"
echo ""
echo "Press Ctrl+C to stop the tunnels"
echo ""

# Keep script running
wait $BACKEND_PID $FRONTEND_PID
