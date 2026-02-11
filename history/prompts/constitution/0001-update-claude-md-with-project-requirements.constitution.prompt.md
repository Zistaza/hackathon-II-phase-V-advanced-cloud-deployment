---
id: 0001
title: Update CLAUDE.md with Project Requirements
stage: constitution
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: unknown
command: /sp.phr
labels: ["claude.md", "project-requirements", "configuration", "agents"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - /home/emizee/Hackathon-II-phase-II-todo-full-stack/CLAUDE.md
tests:
 - none
---

## Prompt

Update the claude.md file based on my project requirements. In this file:

Use Auth Agent for authentication
Use Frontend Agent for frontend development (e.g., Next.js)
Use DB Agent for database design and operations
Use Backend Agent for FastAPI development


Below are my project requirements:

____
Phase II: Todo Full-Stack Web Application
Basic Level Functionality
Objective: Using Claude Code and Spec-Kit Plus transform the console app into a modern
multi-user web application with persistent storage.
Requirements
• Implement all 5 Basic Level features as a web application
• Create RESTful API endpoints
• Build responsive frontend interface
• Store data in Neon Serverless PostgreSQL database
• Authentication – Implement user signup/signin using Better Auth
Technology Stack
Layer Technology
Frontend Next.js 16+ (App Router)
Backend Python FastAPI
ORM SQLModel
Database Neon Serverless PostgreSQL
Spec-Driven Claude Code + Spec-Kit Plus
Authentication Better Auth

API Endpoints
Method Endpoint Description
GET /api/{user_id}/tasks List all tasks
POST /api/{user_id}/tasks Create a new task
GET /api/{user_id}/tasks/{id} Get task details
PUT /api/{user_id}/tasks/{id} Update a task
DELETE /api/{user_id}tasks/{id} Delete a task
PATCH /api/{user_id}tasks/{id}/complete Toggle completion

Better Auth can be configured to issue JWT (JSON Web Token) tokens when users log in.
These tokens are self-contained credentials that include user information and can be verified
by any service that knows the secret key.
Page 7 of 38

Hackathon II: Spec-Driven Development
How It Works
● User logs in on Frontend → Better Auth creates a session and issues a JWT token
● Frontend makes API call → Includes the JWT token in the Authorization: Bearer
<token> header
● Backend receives request → Extracts token from header, verifies signature using
shared secret
● Backend identifies user → Decodes token to get user ID, email, etc. and matches it
with the user ID in the URL
● Backend filters data → Returns only tasks belonging to that user

| Component              | Changes Required                                      |
|------------------------|-------------------------------------------------------|
| Better Auth Config     | Enable JWT plugin to issue tokens                     |
| Frontend API Client    | Attach JWT token to every API request header          |
| FastAPI Backend        | Add middleware to verify JWT and extract user         |
| API Routes             | Filter all queries by the authenticated user's ID     |



## Response snapshot

I've successfully updated the CLAUDE.md file to reflect your project requirements. The file now includes:

1. **Agent Specializations** - Clearly defined roles for Auth Agent, Frontend Agent, DB Agent, and Backend Agent
2. **Technology Stack** - Detailed table showing the tech stack (Next.js, FastAPI, SQLModel, Neon PostgreSQL, Better Auth)
3. **API Endpoints** - Complete list of required endpoints for the todo application
4. **Authentication Flow** - Details on how Better Auth with JWT tokens will work
5. **Project-Specific Guidelines** - Best practices for implementing the solution

All changes have been implemented as requested, aligning the CLAUDE.md file with your Phase II Todo Full-Stack Web Application requirements. The file now serves as a comprehensive guide for developing the multi-user web application with persistent storage using the specified technology stack.

## Outcome

- ✅ Impact: Updated CLAUDE.md to reflect project requirements with agent specializations, technology stack, and API endpoints
- 🧪 Tests: none
- 📁 Files: /home/emizee/Hackathon-II-phase-II-todo-full-stack/CLAUDE.md
- 🔁 Next prompts: none
- 🧠 Reflection: Successfully integrated project-specific requirements into the foundational CLAUDE.md file to guide future development

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A