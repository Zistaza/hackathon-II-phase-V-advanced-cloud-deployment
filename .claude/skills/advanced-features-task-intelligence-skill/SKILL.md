# Advanced Features & Task Intelligence Skill

**Name:** `advanced-features-task-intelligence-skill`  
**Description:** Implement Phase-V-A Advanced Features (recurring tasks, due dates, reminders) and Intermediate Features (priorities, tags, search/filter/sort) for Todo AI Chatbot.

---

## Instructions

### 1. Task Schema Extension
- Add **recurrence rules**, `due_at`, `remind_at`, **priorities**, and **tags**.
- Ensure schema is **backward-compatible**.

### 2. Recurring Tasks
- Emit **task.completed events**.
- Consume events to **auto-generate next recurring task**.

### 3. Reminders
- Schedule reminders via **Dapr Jobs API**.
- Publish **reminder events** to the `reminders` topic.

### 4. Search, Filter, Sort
- Implement **indexed, efficient queries**.
- Avoid **brute-force scanning** of task lists.

### 5. Auth & Validation
- Ensure only **authorized users** can mutate tasks.
- Validate all **task data, recurrence rules, reminders, and queries**.

---

## Best Practices
- Maintain **consistent schema** for all task types.
- Use **Dapr Jobs API** for exact-time scheduling.
- Optimize **search queries** for performance.

---

## Example Structure

```python
class AdvancedFeaturesTaskIntelligenceSkill:
    def extend_task_schema(self):
        # Add recurrence, due_at, remind_at, tags, priorities
        pass

    def handle_recurring_task(self, task):
        # Emit event and generate next task
        pass

    def schedule_reminder(self, task):
        # Use Dapr Jobs API to trigger reminder
        pass

    def implement_search_filter_sort(self, query):
        # Execute indexed queries efficiently
        pass
