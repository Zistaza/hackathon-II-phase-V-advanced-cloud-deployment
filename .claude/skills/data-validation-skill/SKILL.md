# Data & Validation Skill

**Name:** `data-validation-skill`  
**Description:** Ensure correctness, consistency, and integrity of data and events in Phase-V Todo AI Chatbot, validating all schemas and stored state.

---

## Instructions

### 1. Schema Validation
- Validate **API requests and responses**.
- Enforce **event schema contracts** for `task-events`, `reminders`, and `task-updates`.

### 2. State Validation
- Ensure **stored task and conversation state** is consistent.
- Check **recurrence rules, due dates, and reminders**.

### 3. Auth Integration
- Verify **user identity** before any data mutation.
- Ensure that only **authorized users** can access or modify data.

### 4. Edge-Case Handling
- Prevent **invalid or corrupted task/conversation state**.
- Validate **date, recurrence, and reminder logic**.

---

## Best Practices
- Always **validate inputs** before storage or processing.
- Maintain **strict versioning** for events and data schemas.
- Use **automated tests** for data integrity.

---

## Example Structure

```python
class DataValidationSkill:
    def validate_api_request(self, request):
        # Check request against schema
        pass

    def validate_state(self, state):
        # Ensure data consistency
        pass

    def check_user_auth(self, user, action):
        # Verify authorization before data mutation
        pass
