
---

# 📦 Skill 3 — Helm Packaging (Spec-Driven)

```md
---
name: helm-packaging-spec-driven
description: Create clean, reusable Helm charts for Kubernetes deployments following spec-driven infrastructure principles.
---

# Helm Chart Packaging

## Instructions

1. **Chart Structure Creation**
   - Initialize Helm chart
   - Define Chart.yaml metadata
   - Organize templates directory properly

2. **Template Generation**
   - Create deployment.yaml template
   - Create service.yaml template
   - Parameterize replicas, images, ports

3. **Configuration Management**
   - Define all variables in values.yaml
   - Avoid hardcoded configuration
   - Support environment-based overrides

4. **Deployment Validation**
   - Lint Helm charts
   - Install and upgrade releases
   - Verify rendered manifests

## Best Practices
- Keep templates simple and readable
- Use Helm functions sparingly
- Follow Kubernetes naming conventions
- Separate concerns between templates and values
- Ensure charts are reusable across environments

## Example Commands
```bash
helm create todo-backend
helm lint todo-backend
helm install todo-backend ./todo-backend
