# Phase-V System Architect Skill

**Name:** `phase-v-system-architect-skill`  
**Description:** Design scalable, event-driven microservices architecture for Phase-V Todo AI Chatbot, ensuring secure service communication, Dapr/Kafka integration, and architecture validation.

---

## Instructions

### 1. Architecture Design
- Design **event-driven microservices** with clear service boundaries.
- Map **Kafka topics, producers, and consumers**.
- Design **Dapr components** (Pub/Sub, State, Jobs, Secrets) per service.
- Ensure **scalability, decoupling, and cloud portability**.

### 2. Security & Auth
- Ensure **secure service-to-service communication**.
- Design **mTLS**, **token flows**, and **secret usage**.
- Validate **authentication/authorization flows** in architecture.

### 3. Validation
- Check architecture against **Phase-V requirements**.
- Ensure **service boundaries, data flow, and topic usage** are consistent.
- Verify all services adhere to **best practices** and **hackathon rubric**.

### 4. Documentation
- Prepare **architecture diagrams**.
- Document reasoning behind **design choices**.
- Ensure **traceable decisions** for reviewers.

---

## Best Practices
- Maintain **loose coupling** between services.
- Design for **cloud portability** (Minikube → AKS/GKE/OKE).
- Include explicit **Auth** and **Validation checks** in every service.

---

## Example Structure

```python
class SystemArchitectSkill:
    def design_architecture(self):
        # Plan services, Dapr components, Kafka topics
        pass

    def validate_architecture(self):
        # Check service boundaries, auth, and data flows
        pass
