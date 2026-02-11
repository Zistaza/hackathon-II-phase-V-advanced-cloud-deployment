# Auth & Security Skill

**Name:** `auth-security-skill`  
**Description:** Handle all authentication, authorization, and secret management for Phase-V Todo AI Chatbot services securely and consistently.

---

## Instructions

### 1. Authentication
- Implement **JWT**, **API key**, and **service identity flows**.
- Ensure **secure login** and **internal service communication**.

### 2. Authorization
- Enforce **role-based access control (RBAC)** for all task operations.
- Validate **user permissions** before any mutation.

### 3. Secrets Management
- Configure **Kubernetes Secrets** or **Dapr Secret Store**.
- Avoid **embedding secrets in code or logs**.
- Ensure secrets are **accessible only to authorized services**.

### 4. Validation
- Validate **access tokens and credentials**.
- Audit **changes to access controls or sensitive data**.

---

## Best Practices
- Never **store secrets in source code**.
- Use **centralized secret management** for multi-cloud portability.
- Validate **all access** before performing sensitive actions.

---

## Example Structure

```python
class AuthSecuritySkill:
    def authenticate_user(self, token):
        # Verify JWT or API key
        pass

    def authorize_action(self, user, action):
        # Check RBAC permissions
        pass

    def fetch_secret(self, key):
        # Retrieve secret securely from Kubernetes or Dapr
        pass
