#!/bin/bash
# Port forwarding script for Todo App
# Run this script and keep it running while using the application

echo "🚀 Starting port forwarding for Todo App..."
echo ""
echo "This will forward Kubernetes services to localhost"
echo "Keep this terminal open while using the application"
echo ""

# Kill any existing port forwards
pkill -f "kubectl port-forward.*todo-app" 2>/dev/null

# Start backend port forward
echo "📡 Forwarding backend to localhost:8000..."
kubectl port-forward -n todo-app svc/todo-app-todo-chatbot-backend 8000:8000 &
BACKEND_PID=$!

# Wait a bit
sleep 2

# Start frontend port forward
echo "📡 Forwarding frontend to localhost:3000..."
kubectl port-forward -n todo-app svc/todo-app-todo-chatbot-frontend 3000:3000 &
FRONTEND_PID=$!

# Wait for port forwards to establish
sleep 3

echo ""
echo "✅ Port forwarding active!"
echo ""
echo "📍 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Backend Health: http://localhost:8000/health"
echo ""
echo "🌐 Open http://localhost:3000 in your Windows browser"
echo ""
echo "⚠️  Keep this terminal open. Press Ctrl+C to stop."
echo ""

# Trap Ctrl+C to cleanup
trap "echo ''; echo '🛑 Stopping port forwards...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Keep script running
wait $BACKEND_PID $FRONTEND_PID
