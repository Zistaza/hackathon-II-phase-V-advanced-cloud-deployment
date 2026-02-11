
---

# ☸️ Skill 2 — Kubernetes Deployment (kubectl-ai)

```md
---
name: kubernetes-deployment-kubectl-ai
description: Deploy, scale, and debug Kubernetes workloads on Minikube using kubectl-ai natural language commands.
---

# Kubernetes Deployment with kubectl-ai

## Instructions

1. **Cluster Validation**
   - Ensure Minikube is running
   - Confirm kubectl context is correct
   - Verify node and namespace availability

2. **Application Deployment**
   - Deploy frontend and backend workloads
   - Configure replicas and container images
   - Expose services using ClusterIP or NodePort

3. **Scaling & Operations**
   - Scale deployments based on requirements
   - Restart or roll out updates safely
   - Inspect logs and pod status

4. **AI-Assisted Debugging**
   - Use kubectl-ai to identify failing pods
   - Diagnose crash loops or image pull errors
   - Validate service connectivity

## Best Practices
- Prefer Deployments over Pods
- Use labels consistently
- Keep replica count explicit
- Avoid hardcoding values in manifests
- Use kubectl-ai before manual kubectl commands

## Example Commands
```bash
kubectl-ai "deploy the backend with 2 replicas"
kubectl-ai "expose the frontend using NodePort"
kubectl-ai "check why the pods are failing"
