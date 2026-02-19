# Phase-V Infrastructure Deployment

[![CI](https://github.com/your-org/hackathon-II-PHASEV/actions/workflows/ci.yaml/badge.svg)](https://github.com/your-org/hackathon-II-PHASEV/actions/workflows/ci.yaml)
[![Deploy](https://github.com/your-org/hackathon-II-PHASEV/actions/workflows/deploy-cloud.yaml/badge.svg)](https://github.com/your-org/hackathon-II-PHASEV/actions/workflows/deploy-cloud.yaml)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A production-ready, event-driven todo application deployed on Kubernetes with Dapr microservices building blocks.

## 🎯 Features

### Core Capabilities

- **Event-Driven Architecture** - Kafka-based event streaming with Dapr Pub/Sub
- **Microservices** - Distributed services with Dapr service invocation
- **State Management** - PostgreSQL state store via Dapr
- **Secrets Management** - Kubernetes secrets via Dapr Secrets API
- **Real-Time Sync** - WebSocket-based multi-client synchronization
- **Recurring Tasks** - Automatic recurring task generation
- **Reminders** - Scheduled reminders with cron bindings
- **Full-Text Search** - Advanced task search and filtering
- **Task Priorities** - Priority-based task management
- **Tags** - Tag-based task organization

### Infrastructure

- **Kubernetes** - Container orchestration
- **Dapr** - Distributed application runtime
- **Prometheus** - Metrics collection
- **Grafana** - Visualization and dashboards
- **CI/CD** - GitHub Actions automation
- **Multi-Environment** - Local (Minikube) and Cloud (Oracle Cloud)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Web App   │  │  Mobile App │  │   CLI/API   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          └────────────────┴────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │       Traefik Ingress           │
          │    (HTTPS/TLS Termination)      │
          └────────────────┬────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────┐
│                  Kubernetes Cluster                           │
│                                                               │
│  ┌─────────────────────┐                                     │
│  │   Frontend (React)  │                                     │
│  └─────────────────────┘                                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Backend Services (FastAPI)                 │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │ │
│  │  │ Backend  │ │  Events  │ │ Reminders│ │  Notify  │  │ │
│  │  │   API    │ │ Processor│ │ Scheduler│ │ Service  │  │ │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │ │
│  │       │            │            │            │         │ │
│  │       └────────────┴────────────┴────────────┘         │ │
│  │                         │                               │ │
│  │              ┌──────────▼──────────┐                   │ │
│  │              │   Dapr Sidecars     │                   │ │
│  │              │  - Pub/Sub          │                   │ │
│  │              │  - State Store      │                   │ │
│  │              │  - Secrets          │                   │ │
│  │              │  - Service Invoke   │                   │ │
│  │              │  - Bindings         │                   │ │
│  │              └──────────┬──────────┘                   │ │
│  └─────────────────────────┼───────────────────────────────┘ │
│                            │                                  │
└────────────────────────────┼──────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Redpanda Cloud │ │  Neon PostgreSQL│ │  Kubernetes     │
│   (Pub/Sub)     │ │   (State Store) │ │    Secrets      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 📁 Project Structure

```
hackathon-II-PHASEV/
├── backend/                    # FastAPI backend services
│   ├── src/
│   │   ├── api/               # API endpoints
│   │   ├── dapr/              # Dapr clients
│   │   ├── events/            # Event handlers & schemas
│   │   ├── services/          # Business logic services
│   │   └── config/            # Configuration
│   └── requirements.txt
├── frontend/                   # React frontend application
│   ├── src/
│   └── package.json
├── k8s/                        # Kubernetes manifests
│   ├── base/                  # Base resources
│   ├── local/                 # Minikube overlays
│   └── cloud/                 # Oracle Cloud overlays
├── monitoring/                 # Monitoring stack
│   ├── prometheus/            # Prometheus config
│   └── grafana/               # Grafana dashboards
├── scripts/                    # Deployment scripts
│   ├── setup-minikube.sh
│   ├── deploy-local.sh
│   ├── deploy-cloud.sh
│   └── setup-monitoring.sh
├── docs/                       # Documentation
│   └── oracle-cloud-setup.md
└── .github/workflows/          # CI/CD pipelines
```

## 🚀 Quick Start

### Prerequisites

- Docker (20.10+)
- kubectl (1.25+)
- Helm (3.0+)
- Minikube (1.30+)
- Dapr CLI (1.12+)

### Local Deployment (5 minutes)

```bash
# 1. Start Minikube
./scripts/setup-minikube.sh

# 2. Install Dapr
./scripts/setup-dapr.sh

# 3. Deploy Redis
./scripts/deploy-redis.sh

# 4. Create secrets
./scripts/create-local-secrets.sh

# 5. Deploy application
./scripts/deploy-local.sh

# 6. Validate deployment
./scripts/validate-deployment.sh

# 7. Access application
# Add to /etc/hosts: "$(minikube ip) todo-app.local"
# Open: http://todo-app.local
```

### Cloud Deployment (Oracle Cloud)

```bash
# 1. Provision Oracle Cloud instances
# Follow docs/oracle-cloud-setup.md

# 2. Install k3s
./scripts/install-k3s.sh server
./scripts/install-k3s.sh agent

# 3. Install infrastructure
./scripts/install-traefik.sh
./scripts/install-cert-manager.sh
dapr init -k --wait

# 4. Create secrets
./scripts/create-cloud-secrets.sh

# 5. Deploy application
./scripts/deploy-cloud.sh
```

## 📊 Monitoring

### Access Grafana

```bash
kubectl port-forward -n monitoring svc/grafana 3000:80
# http://localhost:3000 (admin/admin)
```

### Access Prometheus

```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# http://localhost:9090
```

### Dashboards

- **Task Operations** - Task API metrics
- **Event Processing** - Event-driven architecture metrics
- **Reminder Scheduling** - Reminder service metrics
- **System Health** - Overall system health

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET` | JWT signing secret | Required |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `DAPR_HTTP_ENDPOINT` | Dapr HTTP endpoint | http://localhost:3500 |
| `USE_DAPR_SECRETS` | Use Dapr for secrets | true |

### Kubernetes Secrets

```bash
# Create secrets
kubectl create secret generic neon-secret \
  --from-literal=connectionString="postgresql://..."

kubectl create secret generic jwt-secret \
  --from-literal=secret="your-secret"

kubectl create secret generic redpanda-secret \
  --from-literal=username="..." \
  --from-literal=password="..."
```

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# End-to-end tests
python scripts/test-end-to-end.py

# Dapr integration tests
python scripts/test-dapr-integration.py
```

### Test Event Flow

```bash
# Create a task (triggers task.created event)
curl -X POST http://todo-app.local/api/user_123/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Test Task", "priority": "high"}'

# Check event processor logs
kubectl logs -n todo-app -l app=event-processor --tail=50
```

## 📈 CI/CD

### Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| CI | Push/PR | Build and test |
| Docker Build | Push to main | Build and push images |
| Deploy Local | Manual/Develop | Deploy to Minikube |
| Deploy Cloud | Manual/Main | Deploy to Oracle Cloud |

### Manual Deployment

```bash
# Via GitHub CLI
gh workflow run deploy-cloud.yaml \
  --field environment=production \
  --field version=main

# Trigger rollback
gh workflow run deploy-cloud.yaml --field rollback=true
```

## 🛠️ Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app
```

**Dapr sidecar not injecting:**
```bash
dapr status -k
kubectl rollout restart deployment/<name> -n todo-app
```

**Ingress not accessible:**
```bash
kubectl get ingress -n todo-app
grep todo-app.local /etc/hosts
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more issues.

## 📚 Documentation

- [Architecture](ARCHITECTURE.md) - System architecture details
- [Deployment](DEPLOYMENT.md) - Detailed deployment guide
- [Quickstart](specs/013-phasev-infra-deployment/quickstart.md) - Quick start guide
- [Oracle Cloud Setup](docs/oracle-cloud-setup.md) - Cloud provisioning
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues

## 🔐 Security

- JWT authentication for all API endpoints
- Secrets managed via Kubernetes Secrets and Dapr
- HTTPS/TLS for cloud deployment
- Network policies for pod security
- Resource quotas and limits

## 📊 Resource Requirements

### Local (Minikube)

- CPU: 4 cores recommended
- Memory: 8GB RAM
- Disk: 20GB

### Cloud (Oracle Cloud Always Free)

- 2x VM.Standard.E2.1.Micro (1 OCPU, 6GB RAM each)
- Total: 2 OCPU, 12GB RAM (within free tier)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🎓 Learning Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

## 📞 Support

- GitHub Issues: [Create an issue](https://github.com/your-org/hackathon-II-PHASEV/issues)
- Documentation: See `docs/` directory
- Quickstart: `specs/013-phasev-infra-deployment/quickstart.md`

---

**Built with ❤️ using FastAPI, React, Kubernetes, and Dapr**
