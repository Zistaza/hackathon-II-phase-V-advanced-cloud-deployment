# ADR-0002: Authentication Architecture for Todo Application

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-15
- **Feature:** 001-auth-identity
- **Context:** Need to establish a comprehensive authentication architecture for the Todo Full-Stack Web Application that balances security, scalability, and developer experience. The architecture must support multi-tenant isolation, ensure stateless operation, integrate seamlessly with Better Auth, and provide a foundation for future feature development while adhering to the project's security-by-default principle.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Frontend Authentication Layer**: Better Auth as the primary authentication provider for user registration, login, and session management
- **Token Strategy**: JWT-based authentication with stateless verification on the backend
- **Security Protocol**: HS256 algorithm with BETTER_AUTH_SECRET shared between frontend and backend
- **Backend Integration**: FastAPI dependency injection system for authentication middleware
- **Identity Management**: User identity propagation through CurrentUser model with user_id and email
- **API Protection**: Mandatory JWT validation for all user-specific endpoints with user_id verification
- **Multi-tenant Isolation**: URL-based user_id validation against JWT claims to prevent cross-user access
- **Error Handling**: Consistent HTTP 401 responses for all authentication failures

## Consequences

### Positive

- Scalable authentication system that supports horizontal scaling without shared session state
- Clear separation of concerns between frontend authentication management and backend verification
- Standardized JWT tokens that work across services and are compatible with industry tools
- Developer-friendly authentication flow with established libraries and community support
- Strong security posture with proper token validation and user isolation
- Future extensibility for additional authentication providers or security enhancements
- Compliance with stateless architecture requirements for cloud deployment

### Negative

- Increased complexity of token management on the client side
- Inability to revoke individual tokens before expiration (stateless limitation)
- Larger payload sizes compared to session-based authentication
- Dependency on shared secrets that require careful management and rotation
- Potential security risks if JWTs are stolen (valid until expiration)
- Client-side complexity for handling token expiration and refresh

## Alternatives Considered

Alternative A: Session-based authentication with server-side storage
- Components: Server sessions in Redis/database, cookie-based authentication, session middleware
- Why rejected: Violates stateless architecture requirement, introduces infrastructure complexity, creates scaling challenges, conflicts with cloud-native design principles

Alternative B: OAuth-only authentication with third-party providers
- Components: Google/Facebook/Apple OAuth integration, external identity providers
- Why rejected: Doesn't meet requirement for email/password registration, reduces user acquisition flexibility, adds external dependencies and potential vendor lock-in

Alternative C: Certificate-based authentication
- Components: PKI infrastructure, client certificates, mutual TLS
- Why rejected: Excessive complexity for web application, poor user experience, significant infrastructure requirements, limited browser support

Alternative D: API Key-based authentication
- Components: Static API keys per user, header-based authentication, key management system
- Why rejected: Keys are harder to manage than time-limited tokens, no built-in expiration, higher security risk if compromised, doesn't align with Better Auth integration

## References

- Feature Spec: /specs/001-auth-identity/spec.md
- Implementation Plan: /specs/001-auth-identity/plan.md
- Related ADRs: ADR-0001 (JWT Authentication Architecture)
- Research: /specs/001-auth-identity/research.md