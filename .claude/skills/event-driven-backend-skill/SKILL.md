# Event-Driven Backend Skill

**Name:** `event-driven-backend-skill`  
**Description:** Implement asynchronous workflows for Phase-V Todo AI Chatbot using Kafka via Dapr Pub/Sub, ensuring idempotent, validated, and secure event processing.

---

## Instructions

### 1. Event Schema Management
- Define **versioned event schemas** for `task-events`, `reminders`, `task-updates`.
- Ensure **schema consistency** across producers and consumers.

### 2. Event Handling
- Publish events via **Dapr Pub/Sub**; avoid direct Kafka clients.
- Consume events **idempotently** for recurring tasks, audit logs, and notifications.
- Handle **retries and failure scenarios** gracefully.

### 3. Auth & Validation
- Ensure only **authenticated services** can publish/consume events.
- Validate **event payloads, timestamps, and user IDs**.
- Prevent **invalid or inconsistent task/event states**.

### 4. Performance & Reliability
- Implement **asynchronous flows efficiently**.
- Avoid **blocking main service operations**.
- Monitor **event delivery success and failures**.

---

## Best Practices
- Always **validate event schemas before publishing**.
- Ensure **idempotency** in consumers to prevent duplicates.
- Keep events **loosely coupled** from services.

---

## Example Structure

```python
class EventDrivenBackendSkill:
    def publish_event(self, topic, payload):
        # Use Dapr Pub/Sub to send event
        pass

    def consume_event(self, topic):
        # Consume and process event idempotently
        pass

    def validate_event(self, payload):
        # Ensure schema correctness
        pass
