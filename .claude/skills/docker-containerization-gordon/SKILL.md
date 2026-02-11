---
name: docker-containerization-gordon
description: Containerize frontend and backend applications using Docker AI Agent (Gordon) with optimized, production-ready Dockerfiles.
---

# Docker Containerization with Gordon

## Instructions

1. **Application Analysis**
   - Identify frontend and backend entry points
   - Detect runtime requirements (Node.js, Python, etc.)
   - Determine exposed ports and environment variables

2. **Dockerfile Generation**
   - Use minimal and official base images
   - Apply multi-stage builds when applicable
   - Ensure proper WORKDIR and COPY order
   - Define clear CMD or ENTRYPOINT

3. **Optimization**
   - Minimize image size
   - Optimize layer caching
   - Remove unnecessary dependencies
   - Avoid running containers as root

4. **Docker AI (Gordon) Usage**
   - Prefer Docker AI for Dockerfile creation
   - Ask Gordon for image optimization suggestions
   - Validate Docker best practices via AI feedback

## Best Practices
- One container per service
- Use `.dockerignore` to reduce build context
- Keep Dockerfiles readable and minimal
- Expose only required ports
- Tag images clearly (app-name:version)

## Example Commands
```bash
docker ai "Generate an optimized Dockerfile for the backend service"
docker build -t todo-backend:latest .
docker run -p 7860:7860 todo-backend:latest
