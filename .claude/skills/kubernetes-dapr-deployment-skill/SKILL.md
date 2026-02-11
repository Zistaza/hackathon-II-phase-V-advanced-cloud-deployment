# Kubernetes & Dapr Deployment Skill

**Name:** `kubernetes-dapr-deployment-skill`  
**Description:** Deploy Phase-V Todo AI Chatbot services to Minikube or cloud clusters with Dapr sidecars, ensuring proper configuration, security, and observability.

---

## Instructions

### 1. Cluster Deployment
- Deploy services to **Minikube** or cloud clusters (**AKS/GKE/OKE**).
- Configure **ingress, storage, and network policies**.

### 2. Dapr Deployment
- Install **Dapr on Kubernetes** (`dapr init -k`).
- Configure **Dapr sidecars per service**.
- Deploy **Pub/Sub, State, Jobs, and Secrets components**.

### 3. Auth & Security
- Ensure **secure cluster access** and **secret mounting**.
- Validate **service identity** and **RBAC**.

### 4. Validation
- Check **pod health, service connectivity, and sidecar logs**.
- Validate **Helm charts** and **manifests**.

---

## Best Practices
- Maintain **reproducible deployments** via Helm.
- Validate **Dapr component YAML files** before deployment.
- Test **local Minikube deployment** before cloud rollout.

---

## Example Structure

```python
class KubernetesDaprDeploymentSkill:
    def deploy_service(self, service_name):
        # Apply Kubernetes manifests and Helm charts
        pass

    def configure_dapr(self, component_yaml):
        # Deploy Dapr components for service
        pass

    def validate_deployment(self):
        # Check pods, services, and sidecars
        pass
