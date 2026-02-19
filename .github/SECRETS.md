# GitHub Secrets Configuration for Phase-V CI/CD

This document describes the required GitHub secrets for the Phase-V CI/CD pipeline.

## Required Secrets

### Container Registry Secrets

These secrets are automatically configured by GitHub Actions when using GHCR (GitHub Container Registry):

| Secret Name | Description | Auto-configured |
|-------------|-------------|-----------------|
| `GITHUB_TOKEN` | GitHub token for pushing images | ✅ Yes |

### Kubernetes Cluster Secrets

#### For Oracle Cloud Deployment

| Secret Name | Description | Required For |
|-------------|-------------|---------------|
| `KUBE_CONFIG` | Base64-encoded kubeconfig for Oracle Cloud k3s cluster | `deploy-cloud.yaml` |

**How to set up:**

```bash
# Get your kubeconfig from Oracle Cloud server
ssh ubuntu@<server-ip> 'sudo cat /etc/rancher/k3s/k3s.yaml' | \
  sed 's/127.0.0.1/<server-public-ip>/g' | \
  base64 -w 0

# Copy the output and add it as a GitHub secret named KUBE_CONFIG
```

#### For Minikube Deployment

No additional secrets required. Minikube is set up dynamically in the workflow.

### Application Secrets (Optional)

These secrets can be used to configure the application during deployment:

| Secret Name | Description | Used In |
|-------------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Deployment scripts |
| `JWT_SECRET` | JWT signing secret | Deployment scripts |
| `REDIS_PASSWORD` | Redis password | Deployment scripts |
| `REDPANDA_USERNAME` | Redpanda Cloud username | Cloud deployment |
| `REDPANDA_PASSWORD` | Redpanda Cloud password | Cloud deployment |
| `OPENAI_API_KEY` | OpenAI API key | Deployment scripts |

## GitHub Environments

Configure the following environments in your GitHub repository:

### 1. Local Environment

**Settings:**
- Name: `local`
- Environment type: Development
- Required reviewers: Optional

**Secrets:**
- None required (Minikube is ephemeral)

### 2. Production Environment

**Settings:**
- Name: `production`
- Environment type: Production
- Required reviewers: Required (add team members)
- Deployment branches: `main` only

**Secrets:**
- `KUBE_CONFIG` (required)
- `DATABASE_URL` (optional, or use Kubernetes secrets)
- `JWT_SECRET` (optional, or use Kubernetes secrets)
- `REDIS_PASSWORD` (optional, or use Kubernetes secrets)
- `REDPANDA_USERNAME` (optional, or use Kubernetes secrets)
- `REDPANDA_PASSWORD` (optional, or use Kubernetes secrets)

### 3. Staging Environment (Optional)

**Settings:**
- Name: `staging`
- Environment type: Staging
- Required reviewers: Optional

**Secrets:**
- Same as production, but with staging values

## How to Configure Secrets

### Via GitHub Web Interface

1. Navigate to your repository on GitHub
2. Click **Settings** > **Secrets and variables** > **Secrets**
3. Click **New repository secret**
4. Enter the secret name and value
5. Click **Add secret**

### Via GitHub CLI

```bash
# Install GitHub CLI if not already installed
gh auth login

# Set repository secrets
gh secret set KUBE_CONFIG < kubeconfig.base64
gh secret set DATABASE_URL --body="postgresql://user:pass@host:5432/db"
gh secret set JWT_SECRET --body="your-jwt-secret"
```

### Via GitHub API

```bash
# Using curl and GitHub CLI for authentication
gh api \
  --method PUT \
  /repos/{owner}/{repo}/actions/secrets/{secret_name} \
  -f encrypted_value="{encrypted_value}" \
  -f key_id="{key_id}"
```

## Security Best Practices

### 1. Use Environments

- Separate secrets for different environments (local, staging, production)
- Require reviewers for production deployments
- Restrict deployment branches

### 2. Rotate Secrets Regularly

- Rotate JWT secrets every 90 days
- Update database passwords periodically
- Regenerate GitHub tokens as needed

### 3. Limit Secret Access

- Use OIDC for cloud provider authentication when possible
- Avoid storing secrets in code or configuration files
- Use Kubernetes Secrets for application-level secrets

### 4. Audit Secret Usage

- Review secret access logs regularly
- Monitor for unauthorized access attempts
- Remove unused secrets

## Kubernetes Secrets vs GitHub Secrets

**Prefer Kubernetes Secrets for:**

- Database connection strings
- API keys used by the application
- JWT secrets
- Service credentials

**Use GitHub Secrets for:**

- Kubernetes kubeconfig
- Container registry credentials (auto-configured)
- Deployment script credentials
- CI/CD pipeline tokens

## Example: Complete Setup

```bash
# 1. Get Oracle Cloud kubeconfig
ssh ubuntu@<server-ip> 'sudo cat /etc/rancher/k3s/k3s.yaml' | \
  sed 's/127.0.0.1/<server-public-ip>/g' > kubeconfig

# 2. Base64 encode
base64 -w 0 < kubeconfig > kubeconfig.base64

# 3. Set GitHub secrets
gh secret set KUBE_CONFIG < kubeconfig.base64
gh secret set DATABASE_URL --body="postgresql://neon-user:pass@ep-xxx.us-east-2.aws.neon.tech/db"
gh secret set JWT_SECRET --body="$(openssl rand -base64 32)"

# 4. Create GitHub environments
# (Do this via GitHub web interface)
# - Settings > Environments > New environment
# - Name: production
# - Add required reviewers
# - Add deployment branches: main
```

## Troubleshooting

### Secret Not Available in Workflow

**Symptoms:**
- Workflow fails with "secret not found" error
- Environment variable is empty

**Solutions:**
1. Verify secret name matches exactly (case-sensitive)
2. Check if secret is set at repository or environment level
3. Ensure workflow has correct environment specified

### Kubeconfig Authentication Fails

**Symptoms:**
- kubectl commands fail with authentication errors
- Cannot connect to cluster

**Solutions:**
1. Verify kubeconfig is properly base64 encoded
2. Check if server IP in kubeconfig is accessible
3. Ensure k3s token hasn't expired
4. Regenerate kubeconfig if needed

### Docker Push Fails

**Symptoms:**
- Docker push returns 401 Unauthorized
- Cannot push to GHCR

**Solutions:**
1. Verify GITHUB_TOKEN has package write permissions
2. Check repository settings for package access
3. Ensure workflow has correct permissions block

## References

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Environments Documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Docker Login Action](https://github.com/docker/login-action)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
