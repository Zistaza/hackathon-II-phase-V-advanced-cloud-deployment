<!-- SYNC IMPACT REPORT:
Version change: 2.0.0 -> 3.0.0
Modified principles: Phase III – Todo AI Chatbot (Agentic MCP Architecture) → Phase IV – Local Kubernetes Deployment of Todo AI Chatbot (Containerization and Orchestration)
Added sections: Spec-Driven Infrastructure Development, Agentic DevOps First, Zero Application Logic Changes, Reproducible Local Cloud-Native Deployment, Infrastructure Standards, AI Operations (AIOps) Standards, Containerization requirements, Kubernetes requirements, Helm requirements, Docker AI (Gordon), kubectl-ai, Kagent
Removed sections: Previous Phase III implementation details (retained core security and architecture principles)
Templates requiring updates: ⚠ pending - .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md
Follow-up TODOs: None
-->

# Phase IV – Local Kubernetes Deployment of Todo AI Chatbot (Containerization and Orchestration) Constitution

## Core Principles

### Spec-Driven Infrastructure Development
All infrastructure work must originate from written specifications before execution; every deployment component starts with a clear spec document that defines requirements, acceptance criteria, and test cases before any infrastructure is provisioned

### Agentic DevOps First
All containerization and Kubernetes operations must be performed using AI agents wherever possible (Docker AI, kubectl-ai, Kagent); human-written YAML or Dockerfiles are discouraged unless explicitly required by the AI agents

### Zero Application Logic Changes
No backend, frontend, MCP tool, database, or authentication logic may be altered in Phase IV; the application code is locked and only infrastructure, containerization, deployment, and operations are in scope

### Reproducible Local Cloud-Native Deployment
The system must be deployable from scratch on a local machine using Minikube and documented commands; all deployment steps must be repeatable and verifiable on any development machine

### Spec-Driven Development
All implementation must originate from written specifications; every feature starts with a clear spec document that defines requirements, acceptance criteria, and test cases before any code is written

### Separation of Concerns
UI, agent logic, MCP tooling, and persistence responsibilities are isolated; each layer has clear boundaries and interfaces without cross-contamination of concerns

### Security by Default (NON-NEGOTIABLE)
Every request is authenticated and authorized via JWT; backend must reject unauthenticated requests with HTTP 401; all database queries must be filtered by authenticated user ID

### Multi-Tenant Isolation
Users can only access and modify their own data; user ID in the URL must match the user ID in the JWT; cross-user data access is strictly forbidden

### Agentic-first Design
AI agent reasoning drives all task operations; the system must be designed around the OpenAI Agents SDK and its decision-making capabilities; all user interactions flow through the AI agent

### Statelessness
No server-side memory between requests; all state must be persisted in the database; the backend must be horizontally scalable and restart-safe with full conversation context reconstruction from database

### Tool-based Interaction
AI must interact with the application exclusively via MCP (Model Context Protocol) tools; no direct API calls from agents; all operations must occur through the defined MCP tool interface

### Deterministic APIs
Backend behavior must be predictable, validated, and testable; the single chat endpoint must follow the defined contract with appropriate response handling

### Cloud-Native Design
Stateless backend, serverless-friendly database usage; minimal viable implementations avoiding premature optimization

## Infrastructure Standards

### Containerization
Frontend and backend must be containerized separately; Docker AI Agent (Gordon) must be preferred for Dockerfile generation, image optimization, and best practice validation; images must be buildable via Docker Desktop

### Kubernetes
Target environment: Local Minikube cluster; Deployments must use Kubernetes Deployments and Services; No raw Pod definitions allowed; Resource requests and limits must be defined

### Helm
All Kubernetes resources must be packaged as Helm charts; Charts must include Chart.yaml, values.yaml, deployment templates, and service templates; Configuration must be parameterized via values.yaml

## AI Operations (AIOps) Standards

### Docker AI (Gordon)
Must be used for Docker-related reasoning and optimization; CLI usage should be demonstrated via `docker ai` commands

### kubectl-ai
Must be used for Deployments, Scaling, and Debugging pod or service failures

### Kagent
Must be used for Cluster health analysis, Resource optimization recommendations, and Post-deployment operational insights

## Technology Standards

Frontend: OpenAI ChatKit; Backend: Python FastAPI; AI Framework: OpenAI Agents SDK; MCP Server: Official MCP SDK only; ORM: SQLModel; Database: Neon Serverless PostgreSQL; Authentication: Better Auth with JWT; Environment secrets must be managed via environment variables; Shared JWT secret must be configured via BETTER_AUTH_SECRET; Containerization: Docker AI Agent (Gordon); Orchestration: Kubernetes with Minikube; Packaging: Helm charts; Operations: kubectl-ai and Kagent

## Development Workflow

All features must be implemented according to written specs; The system must support conversation resumption after server restarts; The chatbot must fully manage todos through natural language; All task operations performed exclusively through MCP tools; Infrastructure must be deployed using AI agents (Docker AI, kubectl-ai, Kagent)

## Governance

All implementation must follow the defined API contracts and MCP tool schemas; All infrastructure must follow the defined containerization and orchestration standards.

### REST API Contract (LOCKED)

All implementations must conform to the following REST API contract:
- POST /api/{user_id}/chat — Single chat endpoint handles all AI interactions

No endpoint renaming, path restructuring, or contract deviation is allowed without a constitution amendment.

### MCP Tooling Standards (LOCKED)

All implementations must conform to the following MCP tools contract:
- add_task — Creates a new task in the database
- list_tasks — Lists all tasks for the authenticated user
- complete_task — Marks a task as completed
- delete_task — Deletes a task from the database
- update_task — Updates task properties

No tool renaming, schema modification, or contract deviation is allowed without a constitution amendment.

### Infrastructure Constraints

No cloud providers (AWS, GCP, Azure); No production clusters; No manual YAML editing unless generated by AI agents; No Helm charts copied from external repositories; No changes to Phase III REST API or MCP contracts

No hardcoded secrets or credentials in code; Backend must remain stateless; No direct database access from frontend; MCP tools must not contain conversational logic; Infrastructure must be deployed using AI agents only.

## Success Criteria

- Frontend and backend images build successfully using Docker AI Agent
- Helm charts install cleanly on Minikube
- Application runs correctly in Kubernetes
- kubectl-ai commands demonstrate deployment and scaling
- Kagent provides cluster health and optimization insights
- Entire process is spec-driven, agent-assisted, and reproducible
- Deployment is demo-ready and judge-verifiable
- All API endpoints require valid JWT authentication
- Users can only access and modify their own tasks
- Tasks persist reliably in Neon PostgreSQL
- Conversation history is replayable after server restart
- MCP tools validate user ownership and handle errors gracefully
- Agent demonstrates correct tool usage and confirmations
- Chatbot fully manages todos through natural language

## Authority Hierarchy

Phase III Constitution → Phase IV Constitution → Phase IV Specifications → Phase IV Plans → Phase IV Tasks → Execution

Any conflict must be resolved in favor of the higher authority document.

**Version**: 3.0.0 | **Ratified**: 2026-01-24 | **Last Amended**: 2026-02-07