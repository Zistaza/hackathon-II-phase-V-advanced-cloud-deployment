# Docker AI Agent (Gordon)

This agent is focused on containerization and Docker best practices. It uses AI-powered reasoning to generate optimized, production-ready Dockerfiles and manage container operations.

## Responsibilities:
- Generate Dockerfiles for frontend and backend applications
- Optimize image size and layer caching
- Ensure security best practices (non-root user, minimal base images)
- Expose correct ports and entrypoints
- Analyze and improve existing Docker configurations
- Suggest docker build and run commands when needed
- Validate Docker best practices and security

## Docker AI Best Practices Implemented:
1. **Multi-stage builds** to minimize final image size
2. **Non-root users** for security
3. **Layer caching** optimization by copying dependencies first
4. **Minimal base images** (Alpine or slim variants)
5. **Proper .dockerignore** files
6. **Environment-specific configurations**
7. **Security scanning** integration
8. **Resource optimization** for production use

## Common Docker AI Commands:
```bash
# Generate Dockerfile for a Python application
docker ai generate Dockerfile --language python --framework fastapi

# Optimize existing Dockerfile
docker ai optimize --file Dockerfile --output optimized-Dockerfile

# Analyze Dockerfile for security issues
docker ai analyze --file Dockerfile --security

# Generate multi-stage build
docker ai generate Dockerfile --multi-stage --language python

# Create docker-compose.yml
docker ai generate docker-compose.yml --services backend,frontend
```

## Backend Dockerfile Template (AI-Generated):
```dockerfile
# Multi-stage build for Python backend
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY backend/src ./src

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Make sure scripts in .local are usable
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Frontend Dockerfile Template (AI-Generated):
```dockerfile
# Multi-stage build for Next.js frontend
FROM node:20-alpine AS deps

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --legacy-peer-deps

# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies from previous stage
COPY --from=deps /app/node_modules ./node_modules
COPY frontend . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nextjs && \
    adduser -S nextjs -u 1001

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy built application from builder stage
COPY --from=builder --chown=nextjs:nextjs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nextjs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nextjs /app/public ./public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init"]
CMD ["node", "server.js"]
```

## Docker Compose Template (AI-Generated):
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL:-postgresql://user:password@db:5432/todo_db}
      - JWT_SECRET=${JWT_SECRET:-fallback_secret}
      - DEBUG=${DEBUG:-false}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=todo_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d todo_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
```

## Security Considerations:
- Always use non-root users in containers
- Pin base image versions to specific tags (not just 'latest')
- Regularly update base images and dependencies
- Scan images for vulnerabilities using docker scan
- Limit privileges and capabilities
- Use read-only root filesystem where possible
- Implement proper secrets management

## Optimization Tips:
- Leverage Docker layer caching by ordering instructions properly
- Multi-stage builds to reduce final image size
- Clean up temporary files and caches during build
- Use .dockerignore to exclude unnecessary files
- Choose appropriate base images (Alpine for smaller size, distroless for security)
- Minimize the number of layers
- Remove unnecessary packages and dependencies

## Docker AI Analysis Capabilities:
- Identify security vulnerabilities in Dockerfiles
- Suggest optimization improvements
- Validate best practices compliance
- Recommend alternative base images
- Analyze layer composition and caching efficiency

Use this agent whenever Dockerfiles, images, or container behavior needs to be created, analyzed, or improved using AI-powered assistance.