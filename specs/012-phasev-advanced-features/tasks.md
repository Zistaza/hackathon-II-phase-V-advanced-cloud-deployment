# Tasks: Phase-V Advanced & Intermediate Features

**Input**: Design documents from `/specs/012-phasev-advanced-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Infrastructure**: `infrastructure/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Verify backend project structure exists per plan.md (backend/src/models/, backend/src/mcp/, backend/src/services/, backend/src/events/, backend/src/api/)
- [X] T002 Verify frontend project structure exists per plan.md (frontend/src/components/, frontend/src/services/, frontend/src/hooks/)
- [X] T003 [P] Install Python dependencies in backend/requirements.txt (FastAPI, SQLModel, Pydantic, Dapr SDK, Alembic)
- [X] T004 [P] Install frontend dependencies in frontend/package.json (OpenAI ChatKit, WebSocket client)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema & Migration

- [X] T005 Create Alembic migration script backend/src/db/migrations/002_advanced_features.py with new columns (priority, tags, due_date, recurrence_pattern, reminder_time, search_vector)
- [X] T006 Add database indexes in migration script (idx_tasks_priority, idx_tasks_tags, idx_tasks_search, idx_tasks_due_date, idx_tasks_status_priority)
- [X] T007 Add full-text search trigger in migration script (tasks_search_vector_update)
- [ ] T008 Run migration to apply schema changes (alembic upgrade head)
- [ ] T009 Verify migration rollback works (alembic downgrade -1, then upgrade head)

### Extended Task Model

- [X] T010 [P] Add TaskPriority enum to backend/src/models/task.py (LOW, MEDIUM, HIGH, URGENT)
- [X] T011 [P] Add RecurrencePattern enum to backend/src/models/task.py (NONE, DAILY, WEEKLY, MONTHLY)
- [X] T012 Extend Task model in backend/src/models/task.py with new fields (priority, tags, due_date, recurrence_pattern, reminder_time)
- [X] T013 Add Pydantic validation models in backend/src/models/task.py (TaskCreate, TaskUpdate with validators)

### Event Models & Infrastructure

- [X] T014 [P] Create EventType enum in backend/src/models/events.py (TASK_CREATED, TASK_UPDATED, TASK_COMPLETED, TASK_DELETED, REMINDER_SCHEDULED, REMINDER_TRIGGERED)
- [X] T015 [P] Create TaskEvent base model in backend/src/models/events.py with Pydantic (event_id, event_type, user_id, timestamp, payload)
- [X] T016 [P] Create event payload models in backend/src/models/events.py (TaskCreatedPayload, TaskUpdatedPayload, TaskCompletedPayload, TaskDeletedPayload, ReminderTriggeredPayload)
- [X] T017 Create event publisher utility in backend/src/events/publisher.py (publish_task_event function using Dapr client)
- [X] T018 Create idempotency checker in backend/src/events/idempotency.py (check_and_mark_processed function using Dapr State Store with 7-day TTL)
- [X] T019 Create base event consumer class in backend/src/events/consumer.py with idempotency handling

### Dapr Components Configuration

- [X] T020 [P] Create Dapr Pub/Sub component config in infrastructure/dapr/components/kafka-pubsub.yaml for Kafka/Redpanda
- [X] T021 [P] Create Dapr State Store component config in infrastructure/dapr/components/postgres-statestore.yaml for Neon PostgreSQL
- [X] T022 [P] Create Dapr Jobs API component config in infrastructure/dapr/components/jobs-api.yaml
- [X] T023 [P] Create Dapr Secrets component config in infrastructure/dapr/components/kubernetes-secrets.yaml
- [X] T024 [P] Create Kafka topic configurations (task-events, reminders, task-updates) in infrastructure/kafka/topics.yaml

### Query Builders

- [X] T025 [P] Create search query builder in backend/src/db/queries.py (build_search_query function using PostgreSQL full-text search)
- [X] T026 [P] Create filter query builder in backend/src/db/queries.py (build_filter_query function for priority, tags, status, due_date)
- [X] T027 [P] Create sort query builder in backend/src/db/queries.py (build_sort_query function for multiple fields and directions)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Due Dates & Reminder Notifications (Priority: P1) 🎯 MVP

**Goal**: Users can set due dates on tasks and receive timely reminder notifications before tasks are due

**Independent Test**: Create a task with a due date and reminder time (e.g., "Remind me 1 hour before"), wait for the reminder time, and verify the reminder notification is delivered

### Implementation for User Story 1

- [X] T028 [P] [US1] Extend add_task MCP tool schema in backend/src/mcp/schemas.py to accept due_date and reminder_time parameters
- [X] T029 [P] [US1] Extend update_task MCP tool schema in backend/src/mcp/schemas.py to accept due_date and reminder_time parameters
- [X] T030 [US1] Create reminder scheduler utility in backend/src/services/reminder_scheduler.py (schedule_reminder, cancel_reminder, parse_reminder_time functions)
- [X] T031 [US1] Update add_task implementation in backend/src/mcp/tools.py to schedule reminder job via Dapr Jobs API when due_date and reminder_time provided
- [X] T032 [US1] Update update_task implementation in backend/src/mcp/tools.py to cancel old reminder and schedule new one when due_date or reminder_time changes
- [X] T033 [US1] Update complete_task implementation in backend/src/mcp/tools.py to cancel pending reminder jobs
- [X] T034 [US1] Update delete_task implementation in backend/src/mcp/tools.py to cancel pending reminder jobs
- [X] T035 [US1] Create reminder job handler endpoint in backend/src/api/reminders.py (POST /api/reminders/trigger) that publishes reminder.triggered event
- [X] T036 [US1] Create Notification Service in backend/src/services/notification.py that consumes reminders topic and delivers notifications
- [X] T037 [US1] Implement idempotent reminder event handling in Notification Service using event_id deduplication
- [X] T038 [US1] Add due_date and reminder display to TaskMessage component in frontend/src/components/TaskMessage.tsx
- [X] T039 [US1] Add validation for due_date (must be in future) and reminder_time (must match pattern) in backend/src/models/task.py

**Checkpoint**: User Story 1 complete - users can create tasks with due dates and receive reminders

---

## Phase 4: User Story 2 - Task Priorities (Priority: P1)

**Goal**: Users can assign priority levels (low, medium, high, urgent) to tasks and filter/sort by priority

**Independent Test**: Create tasks with different priority levels, then filter by priority "urgent" and verify only urgent tasks are displayed, then sort by priority and verify correct ordering

### Implementation for User Story 2

- [X] T040 [P] [US2] Extend add_task MCP tool schema in backend/src/mcp/schemas.py to accept priority parameter (default: medium)
- [X] T041 [P] [US2] Extend update_task MCP tool schema in backend/src/mcp/schemas.py to accept priority parameter
- [X] T042 [P] [US2] Extend list_tasks MCP tool schema in backend/src/mcp/schemas.py to accept priority filter parameter
- [X] T043 [US2] Update add_task implementation in backend/src/mcp/tools.py to store priority value
- [X] T044 [US2] Update update_task implementation in backend/src/mcp/tools.py to update priority and emit task-updated event
- [X] T045 [US2] Update list_tasks implementation in backend/src/mcp/tools.py to filter by priority using indexed query
- [X] T046 [US2] Add priority sorting to list_tasks implementation in backend/src/mcp/tools.py (urgent → high → medium → low)
- [X] T047 [US2] Add priority badge display to TaskMessage component in frontend/src/components/TaskMessage.tsx with color coding
- [X] T048 [US2] Add CSS styling for priority badges in frontend/src/components/TaskMessage.tsx (urgent=red, high=orange, medium=yellow, low=gray)

**Checkpoint**: User Story 2 complete - users can assign priorities and filter/sort by priority

---

## Phase 5: User Story 3 - Full-Text Search (Priority: P2)

**Goal**: Users can quickly find tasks by searching for keywords in task titles and descriptions

**Independent Test**: Create multiple tasks with varied titles and descriptions, search for a specific keyword, and verify all matching tasks are returned in under 2 seconds

### Implementation for User Story 3

- [X] T049 [P] [US3] Extend list_tasks MCP tool schema in backend/src/mcp/schemas.py to accept search parameter
- [X] T050 [US3] Update list_tasks implementation in backend/src/mcp/tools.py to perform full-text search using search_vector column
- [X] T051 [US3] Implement case-insensitive search matching in backend/src/db/queries.py using PostgreSQL to_tsquery
- [X] T052 [US3] Add search result ranking by relevance in backend/src/db/queries.py using ts_rank
- [X] T053 [US3] Handle empty search query (return all tasks) in backend/src/mcp/tools.py
- [X] T054 [US3] Add search performance optimization (pagination for large result sets) in backend/src/mcp/tools.py
- [ ] T055 [US3] Verify search query performance meets <500ms target for 10,000 tasks using EXPLAIN ANALYZE

**Checkpoint**: User Story 3 complete - users can search tasks by keyword with fast results

---

## Phase 6: User Story 4 - Advanced Filtering & Sorting (Priority: P2)

**Goal**: Users can filter tasks by multiple criteria (status, priority, tags, due date) and sort by various fields

**Independent Test**: Create diverse tasks with various attributes, apply multiple filters (e.g., status=incomplete AND priority=urgent AND due this week), verify correct results, then sort by due date and verify ordering

### Implementation for User Story 4

- [X] T056 [P] [US4] Extend list_tasks MCP tool schema in backend/src/mcp/schemas.py to accept status filter parameter
- [X] T057 [P] [US4] Extend list_tasks MCP tool schema in backend/src/mcp/schemas.py to accept due_date_filter parameter (overdue, today, this_week, this_month)
- [X] T058 [P] [US4] Extend list_tasks MCP tool schema in backend/src/mcp/schemas.py to accept sort_by and sort_order parameters
- [X] T059 [US4] Update list_tasks implementation in backend/src/mcp/tools.py to apply status filter
- [X] T060 [US4] Update list_tasks implementation in backend/src/mcp/tools.py to apply due_date_filter with date range calculations
- [X] T061 [US4] Update list_tasks implementation in backend/src/mcp/tools.py to combine multiple filters with AND logic
- [X] T062 [US4] Update list_tasks implementation in backend/src/mcp/tools.py to apply sorting by created_at, due_date, priority, or status
- [X] T063 [US4] Update list_tasks implementation in backend/src/mcp/tools.py to support both ascending and descending sort orders
- [ ] T064 [US4] Verify combined filter + sort query performance meets <1s target for 10,000 tasks using EXPLAIN ANALYZE

**Checkpoint**: User Story 4 complete - users can filter and sort tasks by multiple criteria

---

## Phase 7: User Story 5 - Task Tags (Priority: P3)

**Goal**: Users can organize tasks with multiple tags for flexible categorization

**Independent Test**: Create tasks with multiple tags, filter by single tag "work" and verify all tasks with that tag are displayed, then filter by multiple tags "work" AND "urgent" and verify only tasks with both tags are displayed

### Implementation for User Story 5

- [X] T065 [P] [US5] Extend add_task MCP tool schema in backend/src/mcp/schemas.py to accept tags parameter (array of strings, max 20 tags)
- [X] T066 [P] [US5] Extend update_task MCP tool schema in backend/src/mcp/schemas.py to accept tags parameter (replaces existing tags)
- [X] T067 [P] [US5] Extend list_tasks MCP tool schema in backend/src/mcp/schemas.py to accept tags filter parameter (AND logic)
- [X] T068 [US5] Update add_task implementation in backend/src/mcp/tools.py to store tags as JSONB array
- [X] T069 [US5] Update update_task implementation in backend/src/mcp/tools.py to update tags and emit task-updated event
- [X] T070 [US5] Update list_tasks implementation in backend/src/mcp/tools.py to filter by tags using JSONB containment operator (@>)
- [X] T071 [US5] Add tag validation (max 20 tags, max 50 chars per tag) in backend/src/models/task.py
- [X] T072 [US5] Add tag display to TaskMessage component in frontend/src/components/TaskMessage.tsx with badge styling
- [ ] T073 [US5] Verify tag filter query performance meets <200ms target for 10,000 tasks using EXPLAIN ANALYZE

**Checkpoint**: User Story 5 complete - users can organize tasks with tags and filter by tags

---

## Phase 8: User Story 6 - Recurring Tasks (Priority: P3)

**Goal**: Users can create tasks that automatically repeat on a schedule (daily, weekly, monthly)

**Independent Test**: Create a recurring task with pattern "weekly", complete the task, and verify the next instance is automatically generated within 5 seconds with the same title, description, priority, and tags but with next week's due date

### Implementation for User Story 6

- [X] T074 [P] [US6] Extend add_task MCP tool schema in backend/src/mcp/schemas.py to accept recurrence_pattern parameter (none, daily, weekly, monthly)
- [X] T075 [P] [US6] Extend update_task MCP tool schema in backend/src/mcp/schemas.py to accept recurrence_pattern parameter
- [X] T076 [US6] Update add_task implementation in backend/src/mcp/tools.py to store recurrence_pattern
- [X] T077 [US6] Update complete_task implementation in backend/src/mcp/tools.py to include recurrence_pattern and original_task data in task-completed event payload
- [X] T078 [US6] Create Recurring Task Service in backend/src/services/recurring_tasks.py as separate microservice
- [X] T079 [US6] Implement Dapr subscription to task-events topic in Recurring Task Service
- [X] T080 [US6] Implement task-completed event handler in Recurring Task Service that filters for recurrence_pattern != "none"
- [X] T081 [US6] Implement next due date calculation logic in Recurring Task Service (daily: +1 day, weekly: +7 days, monthly: +30 days)
- [X] T082 [US6] Implement next task instance creation in Recurring Task Service by calling add_task MCP tool with same title, description, priority, tags, and calculated next due date
- [X] T083 [US6] Implement idempotent event handling in Recurring Task Service using event_id deduplication
- [X] T084 [US6] Handle edge case: skip backfill for past due dates, generate next valid future instance
- [X] T085 [US6] Add recurrence pattern display to TaskMessage component in frontend/src/components/TaskMessage.tsx (show "Repeats: daily/weekly/monthly")

**Checkpoint**: User Story 6 complete - users can create recurring tasks that auto-generate next instances

---

## Phase 9: User Story 7 - Real-Time Multi-Client Sync (Priority: P2)

**Goal**: Users working across multiple devices or browser tabs see task updates in real-time without manual refresh

**Independent Test**: Open application in two browser tabs, create a task in tab 1, and verify it appears in tab 2 within 2 seconds without refresh

### Implementation for User Story 7

- [X] T086 [P] [US7] Update add_task implementation in backend/src/mcp/tools.py to publish task-created event to task-updates topic
- [X] T087 [P] [US7] Update update_task implementation in backend/src/mcp/tools.py to publish task-updated event to task-updates topic
- [X] T088 [P] [US7] Update complete_task implementation in backend/src/mcp/tools.py to publish task-completed event to task-updates topic
- [X] T089 [P] [US7] Update delete_task implementation in backend/src/mcp/tools.py to publish task-deleted event to task-updates topic
- [X] T090 [US7] Create WebSocket service in backend/src/services/websocket.py that subscribes to task-updates topic for authenticated user
- [X] T091 [US7] Implement WebSocket connection handler in backend/src/api/websocket.py (GET /ws/{user_id})
- [X] T092 [US7] Implement JWT authentication for WebSocket connections in backend/src/api/websocket.py
- [X] T093 [US7] Create WebSocket client in frontend/src/services/websocket.ts that connects to backend WebSocket endpoint
- [X] T094 [US7] Create useTaskSync React hook in frontend/src/hooks/useTaskSync.ts that manages WebSocket connection and task list updates
- [ ] T095 [US7] Update TaskMessage component in frontend/src/components/TaskMessage.tsx to use useTaskSync hook for real-time updates
- [X] T096 [US7] Implement task list update logic in frontend (add for task-created, update for task-updated, remove for task-deleted)
- [X] T097 [US7] Handle WebSocket reconnection logic in frontend/src/services/websocket.ts with exponential backoff
- [ ] T098 [US7] Verify multi-client sync latency meets <2s target from state change to display update

**Checkpoint**: User Story 7 complete - users see real-time updates across all connected clients

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T099 [P] Add comprehensive error handling for all MCP tool operations in backend/src/mcp/tools.py
- [X] T100 [P] Add logging for all task operations in backend/src/mcp/tools.py (user_id, operation, task_id, timestamp, result)
- [X] T101 [P] Add logging for all event publications in backend/src/events/publisher.py (event_id, event_type, topic, timestamp)
- [X] T102 [P] Add logging for all event consumptions in backend/src/events/consumer.py (event_id, consumer, timestamp, result)
- [X] T103 [P] Add logging for all reminder operations in backend/src/services/reminder_scheduler.py (job_id, task_id, scheduled_time, status)
- [X] T104 [P] Configure Prometheus metrics collection in backend/src/api/metrics.py (task operations/sec, event processing latency, reminder delivery rate)
- [X] T105 [P] Create Grafana dashboards in infrastructure/monitoring/grafana/dashboards/ (task-operations.json, event-processing.json, reminders.json)
- [X] T106 [P] Configure alerting rules in infrastructure/monitoring/prometheus/alerts.yaml (search latency >1s, event errors >1%, reminder failures >5%)
- [X] T107 [P] Update Helm chart in infrastructure/helm/todo-app/values.yaml with new services (recurring-task-service, notification-service)
- [X] T108 [P] Create Helm templates for new services in infrastructure/helm/todo-app/templates/ (recurring-task-service.yaml, notification-service.yaml)
- [X] T109 [P] Update API documentation in backend/docs/api.md with extended MCP tool schemas
- [X] T110 [P] Update event schema documentation in backend/docs/events.md with all event types and payloads
- [ ] T111 Run quickstart.md validation (follow all 7 implementation phases and verify each checkpoint)
- [ ] T112 Perform end-to-end testing of all user stories in sequence
- [ ] T113 Perform performance testing (search, filter, sort latency with 10,000 tasks)
- [ ] T114 Perform idempotency testing (duplicate events, concurrent processing)
- [ ] T115 Perform security testing (JWT validation, user authorization, cross-user access prevention)
- [ ] T116 Deploy to Minikube for local validation
- [ ] T117 Deploy to cloud cluster (AKS/GKE/OKE) for production validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US7 → US3 → US4 → US5 → US6)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Integrates with US2 (priority filter) and US5 (tag filter) but independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 (due dates) and US2 (priorities) but independently testable
- **User Story 7 (P2)**: Can start after Foundational (Phase 2) - Works with all other stories but independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Tasks within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch schema extensions in parallel:
Task T028: "Extend add_task MCP tool schema in backend/src/mcp/schemas.py"
Task T029: "Extend update_task MCP tool schema in backend/src/mcp/schemas.py"

# Then implement reminder scheduler (depends on schemas):
Task T030: "Create reminder scheduler utility in backend/src/services/reminder_scheduler.py"

# Then update MCP tools (depends on scheduler):
Task T031: "Update add_task implementation in backend/src/mcp/tools.py"
Task T032: "Update update_task implementation in backend/src/mcp/tools.py"
Task T033: "Update complete_task implementation in backend/src/mcp/tools.py"
Task T034: "Update delete_task implementation in backend/src/mcp/tools.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch all schema extensions in parallel:
Task T040: "Extend add_task MCP tool schema in backend/src/mcp/schemas.py"
Task T041: "Extend update_task MCP tool schema in backend/src/mcp/schemas.py"
Task T042: "Extend list_tasks MCP tool schema in backend/src/mcp/schemas.py"

# Then implement MCP tool updates (depends on schemas):
Task T043: "Update add_task implementation in backend/src/mcp/tools.py"
Task T044: "Update update_task implementation in backend/src/mcp/tools.py"
Task T045: "Update list_tasks implementation in backend/src/mcp/tools.py"
Task T046: "Add priority sorting to list_tasks implementation"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Due Dates & Reminders)
4. Complete Phase 4: User Story 2 (Priorities)
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo if ready

**Rationale**: User Stories 1 and 2 are both P1 priority and provide the most critical value - due dates with reminders and priority management. Together they form a complete MVP for advanced task management.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 7 (Multi-Client Sync) → Test independently → Deploy/Demo
5. Add User Story 3 (Search) → Test independently → Deploy/Demo
6. Add User Story 4 (Filtering & Sorting) → Test independently → Deploy/Demo
7. Add User Story 5 (Tags) → Test independently → Deploy/Demo
8. Add User Story 6 (Recurring Tasks) → Test independently → Deploy/Demo
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Due Dates & Reminders)
   - Developer B: User Story 2 (Priorities)
   - Developer C: User Story 7 (Multi-Client Sync)
3. After P1 and P2 stories complete:
   - Developer A: User Story 3 (Search)
   - Developer B: User Story 4 (Filtering & Sorting)
   - Developer C: User Story 5 (Tags)
4. After P2 stories complete:
   - Developer A: User Story 6 (Recurring Tasks)
5. Stories complete and integrate independently

---

## Summary

**Total Tasks**: 117
**Task Count by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 23 tasks
- Phase 3 (US1 - Due Dates & Reminders): 12 tasks
- Phase 4 (US2 - Priorities): 9 tasks
- Phase 5 (US3 - Search): 7 tasks
- Phase 6 (US4 - Filtering & Sorting): 9 tasks
- Phase 7 (US5 - Tags): 9 tasks
- Phase 8 (US6 - Recurring Tasks): 12 tasks
- Phase 9 (US7 - Multi-Client Sync): 13 tasks
- Phase 10 (Polish): 19 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Create task with due date and reminder, verify notification delivered on time
- US2: Create tasks with different priorities, filter and sort by priority
- US3: Create multiple tasks, search by keyword, verify results in <2s
- US4: Create diverse tasks, apply multiple filters and sort, verify correct results
- US5: Create tasks with tags, filter by single and multiple tags
- US6: Create recurring task, complete it, verify next instance auto-generated
- US7: Open app in two tabs, update task in one, verify appears in other within 2s

**Suggested MVP Scope**: User Stories 1 & 2 (Due Dates & Reminders + Priorities)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks follow strict checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
