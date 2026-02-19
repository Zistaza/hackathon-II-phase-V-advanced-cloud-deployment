# Research & Architectural Decisions: Phase-V Infrastructure

**Feature**: 013-phasev-infra-deployment
**Date**: 2026-02-14
**Status**: Complete

## Overview

This document captures all architectural decisions made during the research phase for the Phase-V Infrastructure, Deployment & Cloud Architecture feature. Each decision includes the selected option, rationale, and alternatives considered.

---

## Decision 1: Message Broker Selection

**Decision**: Use **Redpanda Cloud** (free tier) as primary message broker with Dapr Pub/Sub abstraction

**Rationale**:
- Redpanda Cloud offers a generous free tier (10GB storage, 100MB/s throughput) compatible with Oracle Cloud Always Free constraints
- Kafka-compatible API ensures seamless migration if needed
- Managed service reduces operational overhead compared to self-hosted Kafka
- Dapr Pub/Sub abstraction allows fallback to alternative brokers (Redis Streams, RabbitMQ) if Redpanda unavailable
- Lower resource consumption than self-hosted Kafka (no need for Zookeeper/KRaft)
- Better performance than Kafka for small-to-medium workloads

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Self-hosted Kafka (Strimzi) | Full control, no external dependencies | High resource usage (Zookeeper + brokers), complex operations, exceeds Always Free limits | ❌ Rejected - too resource-intensive |
| Confluent Cloud | Mature, well-supported, generous free tier | Requires credit card, potential cost overruns, vendor lock-in | ⚠️ Backup option if Redpanda unavailable |
| Redis Streams (via Dapr) | Lightweight, simple, can run in-cluster | Not designed for event streaming, limited retention, no partitioning | ⚠️ Fallback for local development only |
| RabbitMQ (via Dapr) | Mature, reliable, can run in-cluster | Not optimized for event streaming, higher latency | ❌ Rejected - not event-stream native |

**Implementation Notes**:
- Configure Dapr Pub/Sub component with Redpanda Cloud connection string
- Use separate Dapr component configurations for local (Redis Streams) and cloud (Redpanda Cloud)
- Implement retry logic and dead-letter queues in Dapr configuration
- Monitor message retention and throughput to stay within free tier limits

---

## Decision 2: Oracle Cloud Kubernetes Platform

**Decision**: Use **k3s on Oracle Cloud Compute instances** (Always Free tier)

**Rationale**:
- OKE (Oracle Kubernetes Engine) is NOT available in Always Free tier - requires paid subscription
- k3s is a lightweight Kubernetes distribution designed for resource-constrained environments
- Runs efficiently on 2 OCPUs and 12GB RAM (Always Free limits)
- Full Kubernetes API compatibility ensures Helm charts and manifests work without modification
- Single binary installation simplifies setup and maintenance
- Built-in Traefik ingress controller reduces resource overhead
- Supports all required features (Dapr, Helm, kubectl)

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| OKE (Oracle Kubernetes Engine) | Fully managed, production-grade, Oracle support | NOT available in Always Free tier, requires paid subscription | ❌ Rejected - not free tier compatible |
| MicroK8s | Lightweight, snap-based, easy setup | Higher resource usage than k3s, snap dependency | ⚠️ Backup option if k3s issues |
| Minikube on Compute | Familiar for developers, easy setup | Not designed for production, higher overhead | ❌ Rejected - development tool only |
| Docker Swarm | Lightweight, simple orchestration | Limited ecosystem, no Helm support, not Kubernetes-compatible | ❌ Rejected - incompatible with requirements |

**Implementation Notes**:
- Provision 2x Oracle Cloud Compute instances (Always Free: 2 OCPUs, 12GB RAM each)
- Install k3s on both instances (1 server, 1 agent for HA)
- Configure k3s with embedded etcd for high availability
- Use k3s built-in Traefik ingress controller
- Document manual cluster provisioning steps in quickstart.md
- Test resource usage to ensure compliance with Always Free limits

---

## Decision 3: Ingress Controller

**Decision**: Use **k3s built-in Traefik** ingress controller

**Rationale**:
- Traefik comes pre-installed with k3s, reducing resource overhead
- Automatic SSL/TLS certificate management via Let's Encrypt integration
- Lower memory footprint than Nginx Ingress (~50MB vs ~150MB)
- Native Kubernetes Ingress resource support
- Built-in dashboard for monitoring and debugging
- Sufficient for Always Free tier resource constraints

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Nginx Ingress | Most popular, mature, extensive documentation | Higher resource usage, requires separate installation | ❌ Rejected - unnecessary overhead |
| Oracle Cloud Load Balancer | Fully managed, native Oracle integration | Requires paid tier, not available in Always Free | ❌ Rejected - not free tier compatible |
| Istio Ingress Gateway | Advanced traffic management, service mesh features | Very high resource usage (>1GB memory), complex setup | ❌ Rejected - too resource-intensive |
| HAProxy Ingress | High performance, low resource usage | Less mature Kubernetes integration, smaller community | ⚠️ Backup option if Traefik issues |

**Implementation Notes**:
- Use k3s default Traefik installation (no additional setup required)
- Configure Traefik IngressRoute for HTTP/HTTPS routing
- Enable Let's Encrypt certificate resolver for automatic SSL/TLS
- Configure HTTP to HTTPS redirect
- Set up Traefik dashboard for monitoring (optional, disable in production)

---

## Decision 4: Secret Management Strategy

**Decision**: Use **Kubernetes Secrets** with Dapr Secrets component abstraction

**Rationale**:
- Kubernetes Secrets are built-in, no additional infrastructure required
- Dapr Secrets component provides abstraction layer for future migration to Oracle Cloud Vault
- Sufficient security for Always Free tier deployment (secrets encrypted at rest in etcd)
- Simple rotation process using kubectl
- No additional cost or resource overhead
- Compatible with CI/CD pipeline (GitHub Secrets → Kubernetes Secrets)

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Oracle Cloud Vault | Enterprise-grade, centralized management, audit logs | Requires paid tier, not available in Always Free | ❌ Rejected - not free tier compatible |
| HashiCorp Vault | Industry standard, dynamic secrets, advanced features | High resource usage, complex setup, operational overhead | ❌ Rejected - too complex for Always Free |
| Sealed Secrets | GitOps-friendly, encrypted in Git | Additional controller required, rotation complexity | ⚠️ Consider for future GitOps workflow |
| External Secrets Operator | Syncs from external secret stores | Requires external secret store, additional complexity | ❌ Rejected - unnecessary for current scope |

**Implementation Notes**:
- Create Kubernetes Secrets for database credentials, API keys, JWT secrets
- Configure Dapr Secrets component to reference Kubernetes Secrets
- Use GitHub Secrets for CI/CD pipeline secrets
- Implement secret rotation procedure in documentation
- Enable encryption at rest in k3s etcd configuration
- Never commit secrets to Git (use .env.example templates)

---

## Decision 5: CI/CD Deployment Strategy

**Decision**: Use **push-based deployment** with GitHub Actions and kubectl

**Rationale**:
- Simpler setup than pull-based (ArgoCD/Flux) - no additional controllers required
- GitHub Actions free tier sufficient for deployment frequency (2000 minutes/month)
- Direct kubectl apply provides immediate feedback and faster iteration
- Easier rollback using kubectl rollout undo
- Lower resource usage on cluster (no GitOps controller pods)
- Sufficient for Always Free tier constraints

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| ArgoCD (pull-based) | GitOps best practices, automatic sync, drift detection | Requires cluster resources (~500MB memory), complex setup | ❌ Rejected - too resource-intensive for Always Free |
| Flux (pull-based) | Lightweight GitOps, Helm support | Still requires cluster resources, additional complexity | ⚠️ Consider for future production deployment |
| Jenkins | Mature, extensive plugin ecosystem | Requires dedicated server, high resource usage | ❌ Rejected - too heavy for Always Free |
| GitLab CI/CD | Integrated with GitLab, powerful features | Requires GitLab (not using GitHub), additional infrastructure | ❌ Rejected - not using GitLab |

**Implementation Notes**:
- Create GitHub Actions workflows for CI (build, test) and CD (deploy)
- Use kubectl apply for deployment updates
- Implement rollback using kubectl rollout undo
- Store kubeconfig in GitHub Secrets
- Use GitHub Actions caching for Docker layers and dependencies
- Implement deployment health checks before marking workflow as successful

---

## Decision 6: Monitoring Stack Location

**Decision**: Use **in-cluster Prometheus and Grafana** with resource limits

**Rationale**:
- Full control over data retention and alerting
- No external dependencies or costs
- Prometheus and Grafana can run within Always Free limits with proper resource constraints
- Dapr metrics integration requires in-cluster Prometheus
- Sufficient for development and demo purposes
- Can migrate to managed monitoring later if needed

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Oracle Cloud Monitoring | Fully managed, native integration, no cluster resources | Limited free tier, requires paid tier for advanced features | ⚠️ Consider for future production |
| Grafana Cloud | Generous free tier, managed service | External dependency, potential cost overruns | ⚠️ Backup option if in-cluster too resource-intensive |
| Datadog | Comprehensive monitoring, APM, logs | Expensive, overkill for Always Free tier | ❌ Rejected - too expensive |
| New Relic | Good free tier, easy setup | Limited retention, vendor lock-in | ❌ Rejected - prefer open-source |

**Implementation Notes**:
- Deploy Prometheus with resource limits (CPU: 200m, Memory: 512Mi)
- Deploy Grafana with resource limits (CPU: 100m, Memory: 256Mi)
- Configure Prometheus to scrape Dapr metrics and application metrics
- Create Grafana dashboards for task operations, event processing, reminders
- Set up alerting rules for critical metrics
- Configure metric retention to 7 days to reduce storage usage
- Use Prometheus node exporter for cluster resource monitoring

---

## Decision 7: Event Processing Architecture

**Decision**: Use **multiple specialized consumers** pattern with idempotency

**Rationale**:
- Clear separation of concerns (recurring tasks, reminders, audit logging)
- Independent scaling of each consumer based on load
- Easier debugging and monitoring (separate metrics per consumer)
- Simpler than event sourcing (no need for event store and projections)
- Idempotency handled via event_id and Dapr State Store
- Aligns with microservices architecture principles

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Single event processor | Simpler deployment, fewer pods | Tight coupling, harder to scale, single point of failure | ❌ Rejected - violates separation of concerns |
| Event sourcing | Complete audit trail, time travel, replay capability | High complexity, requires event store, overkill for requirements | ❌ Rejected - unnecessary complexity |
| CQRS with event sourcing | Optimized read/write models, scalability | Very high complexity, steep learning curve, resource-intensive | ❌ Rejected - over-engineering |
| Saga pattern | Distributed transactions, compensation logic | Complex orchestration, not needed for current requirements | ❌ Rejected - requirements don't need distributed transactions |

**Implementation Notes**:
- Create separate consumers: RecurringTaskConsumer, ReminderConsumer, AuditConsumer
- Each consumer subscribes to relevant Kafka topics via Dapr Pub/Sub
- Implement idempotency using event_id stored in Dapr State Store
- Use Pydantic models for event schema validation
- Implement retry logic with exponential backoff (3 retries, 1s, 2s, 4s)
- Route failed events to dead-letter queue after max retries
- Monitor consumer lag and processing latency

---

## Decision 8: Dapr State Store Backend

**Decision**: Use **PostgreSQL** (existing Neon DB) as Dapr State Store

**Rationale**:
- Reuse existing Neon Serverless PostgreSQL database (no additional infrastructure)
- Strong consistency guarantees for idempotency tracking
- ACID transactions for reliable state management
- No additional cost (already using Neon for application data)
- Sufficient performance for event processing state (<1000 ops/sec)
- Dapr PostgreSQL state store component is mature and well-tested

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Redis | Very fast, low latency, popular for state store | Requires separate Redis instance, persistence concerns, additional resource usage | ⚠️ Consider for future if performance bottleneck |
| Oracle Cloud Object Storage | Cheap, scalable, durable | High latency, not designed for transactional state, complex setup | ❌ Rejected - too slow for state store |
| In-memory (no persistence) | Fastest, no external dependency | State lost on pod restart, not suitable for idempotency tracking | ❌ Rejected - violates reliability requirements |
| etcd | Kubernetes-native, strong consistency | Additional cluster resources, complex operations | ❌ Rejected - unnecessary complexity |

**Implementation Notes**:
- Configure Dapr State Store component to use Neon PostgreSQL connection string
- Create separate schema/table for Dapr state (dapr_state)
- Enable TTL for ephemeral state (event processing state expires after 7 days)
- Monitor state store performance (query latency, connection pool usage)
- Implement state cleanup job for expired entries
- Use Dapr State Store transactions for atomic operations

---

## Summary of Architectural Decisions

| Decision Area | Selected Option | Key Rationale |
|---------------|----------------|---------------|
| Message Broker | Redpanda Cloud (free tier) | Kafka-compatible, managed, generous free tier |
| Kubernetes Platform | k3s on Oracle Compute | Only free tier option, lightweight, full K8s compatibility |
| Ingress Controller | Traefik (k3s built-in) | Pre-installed, low resource usage, automatic SSL/TLS |
| Secret Management | Kubernetes Secrets + Dapr | Built-in, sufficient security, no additional cost |
| CI/CD Strategy | Push-based (GitHub Actions) | Simple, fast feedback, low resource usage |
| Monitoring Stack | In-cluster Prometheus/Grafana | Full control, Dapr integration, within resource limits |
| Event Processing | Multiple specialized consumers | Separation of concerns, independent scaling, clear boundaries |
| Dapr State Store | PostgreSQL (Neon DB) | Reuse existing DB, strong consistency, no additional cost |

---

## Resource Allocation Plan

### Oracle Cloud Always Free Tier Limits
- **Compute**: 2 OCPUs, 12GB RAM (across all instances)
- **Storage**: 100GB block storage
- **Network**: 10TB outbound data transfer/month

### Planned Resource Allocation

**Compute Instance 1 (k3s server)**:
- k3s server: 1 OCPU, 4GB RAM
- Frontend: 0.2 OCPU, 512MB RAM
- Backend: 0.3 OCPU, 1GB RAM
- Event Processor: 0.2 OCPU, 512MB RAM
- Prometheus: 0.2 OCPU, 512MB RAM
- **Total**: 1.9 OCPU, 6.5GB RAM

**Compute Instance 2 (k3s agent)**:
- k3s agent: 0.5 OCPU, 2GB RAM
- Reminder Scheduler: 0.2 OCPU, 512MB RAM
- Notification Service: 0.2 OCPU, 512MB RAM
- WebSocket Service: 0.2 OCPU, 512MB RAM
- Grafana: 0.1 OCPU, 256MB RAM
- **Total**: 1.2 OCPU, 3.8GB RAM

**Combined Total**: 3.1 OCPU, 10.3GB RAM (within 2 OCPU, 12GB limit with overcommit)

**Note**: Kubernetes allows resource overcommit. Actual usage will be lower than requested limits. Monitor and adjust as needed.

---

## Risk Assessment

### High-Priority Risks

1. **Resource Exhaustion**: Cluster may exceed Always Free limits under load
   - **Mitigation**: Implement resource limits, horizontal pod autoscaling with max replicas, monitoring alerts

2. **Redpanda Cloud Free Tier Limits**: May hit message retention or throughput limits
   - **Mitigation**: Monitor usage, implement fallback to Redis Streams for local dev, document upgrade path

3. **k3s Stability**: Self-managed Kubernetes may have operational challenges
   - **Mitigation**: Document troubleshooting procedures, implement health checks, test failure scenarios

### Medium-Priority Risks

4. **SSL Certificate Provisioning**: Let's Encrypt may fail on Oracle Cloud
   - **Mitigation**: Document manual certificate installation, test renewal process, provide HTTP fallback

5. **Network Latency**: Oracle Cloud to Redpanda Cloud latency may impact performance
   - **Mitigation**: Choose same region, implement retry logic, monitor latency metrics

6. **GitHub Actions Minutes**: May exceed free tier (2000 minutes/month)
   - **Mitigation**: Optimize builds, cache dependencies, consider self-hosted runners

### Low-Priority Risks

7. **Monitoring Resource Usage**: Prometheus/Grafana may consume too much memory
   - **Mitigation**: Configure retention limits, use lightweight exporters, consider Grafana Cloud

8. **Dapr Sidecar Overhead**: Sidecars may consume significant resources
   - **Mitigation**: Optimize Dapr config, disable unnecessary features, monitor usage

---

## Next Steps

1. ✅ Research complete - all architectural decisions documented
2. ⏭️ Proceed to Phase 1: Design event schemas, Dapr components, Kubernetes resources
3. ⏭️ Create data-model.md with event schemas
4. ⏭️ Create contracts/ directory with component configurations
5. ⏭️ Create quickstart.md with deployment guide
6. ⏭️ Run `/sp.tasks` to generate implementation tasks

**Status**: Ready for Phase 1 (Design & Contracts)
