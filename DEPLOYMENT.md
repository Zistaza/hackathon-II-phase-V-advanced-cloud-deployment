# Todo App - Local Kubernetes Deployment

## 🎉 Deployment Complete!

Your Todo Chatbot application is successfully deployed on Minikube with the following components:

### Deployed Services
- ✅ **Backend (FastAPI)**: Running on Kubernetes
- ✅ **Frontend (Next.js)**: Running on Kubernetes
- ✅ **Port Forwarding**: Active for local access

---

## 🌐 Access Your Application

### From Windows Browser:

**Frontend URL:** http://localhost:3000
**Backend API:** http://localhost:8000
**Backend Health:** http://localhost:8000/health

---

## 🚀 How to Use

### 1. Start Port Forwarding (Required)

Run this script in your WSL2 terminal and **keep it running**:

```bash
cd /home/emizee/hackathon-II-phase-IV
./port-forward.sh
```

Or manually start port forwards:

```bash
# Terminal 1 - Backend
kubectl port-forward -n todo-app svc/todo-app-todo-chatbot-backend 8000:8000

# Terminal 2 - Frontend (open new terminal)
kubectl port-forward -n todo-app svc/todo-app-todo-chatbot-frontend 3000:3000
```

### 2. Access the Application

Open your Windows browser and navigate to:
```
http://localhost:3000
```

The frontend will automatically connect to the backend at `http://localhost:8000`

---

## 🔧 Troubleshooting

### CORS Error Fixed ✅
- **Problem:** Frontend couldn't reach backend from Windows browser
- **Solution:** Port forwarding makes both services accessible via localhost
- **Configuration:** Frontend env variable set to `http://localhost:8000`

### If Port Forwarding Stops

Restart the port forwarding script:
```bash
./port-forward.sh
```

### Check Deployment Status

```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# View logs
kubectl logs -f deployment/todo-app-todo-chatbot-backend -n todo-app
kubectl logs -f deployment/todo-app-todo-chatbot-frontend -n todo-app
```

---

## 📊 Kubernetes Resources

### Pods
- `todo-app-todo-chatbot-backend-*`: Backend API server
- `todo-app-todo-chatbot-frontend-*`: Frontend Next.js app

### Services
- `todo-app-todo-chatbot-backend`: NodePort 30800 (internal)
- `todo-app-todo-chatbot-frontend`: NodePort 30300 (internal)

### Namespace
- `todo-app`

---

## 🛠️ Management Commands

### Update Deployment
```bash
helm upgrade todo-app ./todo-chatbot --namespace todo-app
```

### Restart Pods
```bash
kubectl rollout restart deployment/todo-app-todo-chatbot-backend -n todo-app
kubectl rollout restart deployment/todo-app-todo-chatbot-frontend -n todo-app
```

### Uninstall
```bash
helm uninstall todo-app --namespace todo-app
```

### Stop Port Forwarding
Press `Ctrl+C` in the terminal running the port-forward script

---

## 📝 Configuration

### Backend Environment Variables
- `DATABASE_URL`: Neon PostgreSQL connection string
- `JWT_SECRET`: JWT token secret
- `BETTER_AUTH_SECRET`: Better Auth secret

### Frontend Environment Variables
- `NEXT_PUBLIC_API_BASE_URL`: http://localhost:8000

---

## ✅ What Was Accomplished

1. ✅ Built Docker images for frontend and backend
2. ✅ Loaded images into Minikube
3. ✅ Created Helm charts with proper configuration
4. ✅ Deployed to Kubernetes with NodePort services
5. ✅ Set up port forwarding for Windows browser access
6. ✅ Configured frontend to use correct backend URL
7. ✅ Fixed CORS error by using localhost for both services

---

## 🎯 Next Steps

Your application is ready to use! Simply:
1. Keep the port forwarding running
2. Open http://localhost:3000 in your browser
3. Start using your Todo Chatbot application

For production deployment, consider:
- Setting up Ingress with proper domain
- Using LoadBalancer service type
- Configuring TLS/SSL certificates
- Setting up monitoring and logging
