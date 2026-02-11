---
description: "Task list for Backend API & Database implementation"
---

# Tasks: Backend API & Database for Todo Full-Stack Web Application

**Input**: Design documents from `/specs/002-backend-api-database/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths adjusted for the current project structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in backend/src/
- [X] T002 Initialize Python project with FastAPI, SQLModel, Pydantic, PyJWT dependencies in backend/requirements.txt
- [X] T003 [P] Configure linting and formatting tools in backend/

---
## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Setup database schema and migrations framework in backend/src/database.py
- [X] T005 [P] Implement authentication/authorization framework using Better Auth in backend/src/middleware/auth.py
- [X] T006 [P] Setup API routing and middleware structure in backend/src/main.py
- [X] T007 Create base models/entities that all stories depend on in backend/src/models/user_model.py and backend/src/models/task_model.py
- [X] T008 Configure error handling and logging infrastructure in backend/src/exceptions/
- [X] T009 Setup environment configuration management in backend/src/config/settings.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Management API (Priority: P1) 🎯 MVP

**Goal**: Implement CRUD API endpoints for tasks so that the frontend can create, read, update, and delete tasks for authenticated users

**Independent Test**: Can be fully tested by making API calls to create, retrieve, update, and delete tasks and verifying the responses match expected outcomes

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Contract test for GET /api/{user_id}/tasks in backend/tests/contract/test_tasks_contract.py
- [X] T011 [P] [US1] Contract test for POST /api/{user_id}/tasks in backend/tests/contract/test_tasks_contract.py
- [X] T012 [P] [US1] Contract test for GET /api/{user_id}/tasks/{id} in backend/tests/contract/test_tasks_contract.py
- [X] T013 [P] [US1] Contract test for PUT /api/{user_id}/tasks/{id} in backend/tests/contract/test_tasks_contract.py
- [X] T014 [P] [US1] Contract test for DELETE /api/{user_id}/tasks/{id} in backend/tests/contract/test_tasks_contract.py
- [X] T015 [P] [US1] Contract test for PATCH /api/{user_id}/tasks/{id}/complete in backend/tests/contract/test_tasks_contract.py
- [X] T016 [P] [US1] Integration test for task creation journey in backend/tests/integration/test_task_integration.py
- [X] T017 [P] [US1] Integration test for task retrieval journey in backend/tests/integration/test_task_integration.py

### Implementation for User Story 1

- [X] T018 [P] [US1] Create Task model in backend/src/models/task_model.py
- [X] T019 [P] [US1] Create TaskCreate model in backend/src/models/task_model.py
- [X] T020 [P] [US1] Create TaskUpdate model in backend/src/models/task_model.py
- [X] T021 [P] [US1] Create TaskPublic model in backend/src/models/task_model.py
- [X] T022 [US1] Implement GET /api/{user_id}/tasks endpoint in backend/src/api/tasks.py
- [X] T023 [US1] Implement POST /api/{user_id}/tasks endpoint in backend/src/api/tasks.py
- [X] T024 [US1] Implement GET /api/{user_id}/tasks/{id} endpoint in backend/src/api/tasks.py
- [X] T025 [US1] Implement PUT /api/{user_id}/tasks/{id} endpoint in backend/src/api/tasks.py
- [X] T026 [US1] Implement DELETE /api/{user_id}/tasks/{id} endpoint in backend/src/api/tasks.py
- [X] T027 [US1] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/src/api/tasks.py
- [X] T028 [US1] Add validation and error handling for all task endpoints in backend/src/api/tasks.py
- [X] T029 [US1] Add logging for task operations in backend/src/api/tasks.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - User-Based Filtering & Multi-Tenant Isolation (Priority: P2)

**Goal**: Implement user-based filtering so that each user can only access their own tasks and maintain multi-tenant isolation

**Independent Test**: Can be fully tested by creating tasks for different users and verifying that each user can only access their own tasks through API endpoints

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [X] T030 [P] [US2] Unit test for user-based filtering logic in backend/tests/contract/test_tasks_contract.py
- [X] T031 [P] [US2] Integration test for multi-tenant isolation in backend/tests/contract/test_tasks_contract.py
- [X] T032 [P] [US2] Security test for cross-user data access prevention in backend/tests/contract/test_tasks_contract.py

### Implementation for User Story 2

- [X] T033 [P] [US2] Enhance Task model with user relationship in backend/src/models/task_model.py
- [X] T034 [US2] Implement user ID validation in URL against JWT token in backend/src/api/tasks.py
- [X] T035 [US2] Add database query filtering by user_id in backend/src/api/tasks.py
- [X] T036 [US2] Add proper error responses for unauthorized access attempts in backend/src/api/tasks.py
- [X] T037 [US2] Add logging for access control checks in backend/src/api/tasks.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Database Integration with Neon PostgreSQL (Priority: P3)

**Goal**: Integrate the application with Neon Serverless PostgreSQL database using SQLModel so that tasks and user data can be persisted reliably

**Independent Test**: Can be fully tested by creating tasks through the API and verifying they persist in the database, survive application restarts, and can be retrieved consistently

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [X] T038 [P] [US3] Unit test for database connection in backend/tests/contract/test_tasks_contract.py
- [X] T039 [P] [US3] Integration test for Neon PostgreSQL integration in backend/tests/integration/test_task_integration.py
- [X] T040 [P] [US3] Performance test for database operations in backend/tests/contract/test_tasks_contract.py

### Implementation for User Story 3

- [X] T041 [P] [US3] Configure Neon PostgreSQL connection in backend/src/config/settings.py
- [X] T042 [US3] Implement database session management in backend/src/database.py
- [X] T043 [US3] Create database initialization function in backend/src/database.py
- [X] T044 [US3] Add database migration setup in backend/src/database.py
- [X] T045 [US3] Optimize database queries for performance in backend/src/api/tasks.py
- [X] T046 [US3] Add connection pooling configuration for Neon in backend/src/database.py

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - JWT Authentication & Authorization (Priority: P4)

**Goal**: Implement JWT verification using the authentication logic from Spec 1 so that all API endpoints are properly secured with authorization checks

**Independent Test**: Can be fully tested by attempting API calls with valid and invalid JWT tokens and verifying that only authorized requests succeed

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

- [X] T047 [P] [US4] Unit test for JWT token validation in backend/tests/contract/test_tasks_contract.py
- [X] T048 [P] [US4] Integration test for JWT-based authentication in backend/tests/contract/test_tasks_contract.py
- [X] T049 [P] [US4] Security test for unauthorized access attempts in backend/tests/contract/test_tasks_contract.py

### Implementation for User Story 4

- [X] T050 [P] [US4] Implement JWT utility functions in backend/src/utils/jwt.py
- [X] T051 [P] [US4] Create authentication middleware in backend/src/middleware/auth.py
- [X] T052 [US4] Integrate JWT verification with task endpoints in backend/src/api/tasks.py
- [X] T053 [US4] Add proper error responses for invalid JWT tokens in backend/src/api/tasks.py
- [X] T054 [US4] Add logging for authentication events in backend/src/logging/auth.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T055 [P] Documentation updates in docs/backend_api.md
- [X] T056 Code cleanup and refactoring across all modules
- [X] T057 Performance optimization across all stories
- [X] T058 [P] Additional unit tests (if requested) in backend/tests/contract/test_tasks_contract.py
- [X] T059 Security hardening across all endpoints
- [X] T060 Run quickstart.md validation
- [X] T061 Database migration and versioning implementation in backend/src/database.py
- [X] T062 Error logging and monitoring setup in backend/src/logging/
- [X] T063 API documentation generation in backend/docs/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 models and basic endpoints
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 models and endpoints
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US1, US2, US3 for full functionality

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for GET /api/{user_id}/tasks in backend/tests/contract/test_tasks_contract.py"
Task: "Contract test for POST /api/{user_id}/tasks in backend/tests/contract/test_tasks_contract.py"

# Launch all models for User Story 1 together:
Task: "Create Task model in backend/src/models/task_model.py"
Task: "Create TaskCreate model in backend/src/models/task_model.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence