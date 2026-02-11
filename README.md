# Phase IV: Local Kubernetes Deployment

## Overview
Phase IV focuses on deploying the **Phase III Todo Chatbot** on a **local Kubernetes cluster**.  
This includes containerizing the apps, creating Helm charts, and using AI-assisted DevOps tools.

## Objective
- Deploy the Todo Chatbot on **Minikube** locally.  
- Use AI-assisted tooling to automate Docker and Kubernetes operations.  
- Follow the **Agentic Dev Stack workflow**: Write spec → Generate plan → Break into tasks → Implement via Claude Code.  
  *(No manual coding allowed.)*

## Requirements
- Containerize frontend and backend applications (**Gordon AI agent**).  
- Create Helm charts for deployment (**kubectl-ai** or **Kagent**).  
- Deploy and manage the app on **Minikube**.  
- Use AI agents for intelligent operations:
  - **Docker AI Agent (Gordon)**
  - **kubectl-ai**
  - **Kagent**

> **Note:** If Docker AI (Gordon) is unavailable, use standard Docker CLI or have Claude Code generate equivalent commands.

## Technology Stack
| Component         | Technology / Tool                        |
|------------------|-----------------------------------------|
| Containerization   | Docker (Docker Desktop), Gordon AI       |
| Orchestration      | Kubernetes (Minikube)                   |
| Package Manager    | Helm Charts                              |
| AI DevOps          | kubectl-ai, Kagent                       |
| Application        | Phase III Todo Chatbot                    |

## AI DevOps Usage
**Docker AI (Gordon):**
```bash
docker ai "What can you do?"
