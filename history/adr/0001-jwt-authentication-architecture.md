# ADR-0001: JWT Authentication Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-15
- **Feature:** 001-auth-identity
- **Context:** Need to implement secure authentication and identity layer for the Todo Full-Stack Web Application that ensures every backend request has a verified, trusted user identity available for multi-tenant data isolation. The solution must be stateless, scalable, and compliant with the project's security-by-default principle.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- Authentication Provider: Better Auth for frontend user registration/login
- JWT Algorithm: HS256 (HMAC SHA-256) with shared secret
- Secret Management: BETTER_AUTH_SECRET stored in environment variables
- Backend Verification: FastAPI dependency with PyJWT for token validation
- Token Claims: Standard claims (iss, sub, aud, exp, iat, jti) + custom claims (user_email, user_id)
- Token Expiration: 24 hours (86400 seconds)
- Identity Propagation: FastAPI dependency injection with CurrentUser model
- Error Handling: HTTP 401 for all authentication failures
- Multi-tenant Isolation: Verify user_id in URL matches JWT user_id

## Consequences

### Positive

- Stateless backend operation with no session storage requirements
- Horizontal scalability without shared session state
- Self-contained tokens with user identity embedded
- No session cleanup or synchronization needed
- Consistent authentication flow between frontend and backend
- Strong security with proper token validation and expiration
- Clean separation of concerns between frontend authentication and backend verification

### Negative

- Cannot invalidate individual tokens before expiration
- Larger token size compared to session IDs
- Tokens remain valid even if user changes password
- Potential for token theft and replay until expiration
- Complexity of secret rotation in production
- Need to handle token expiration on client side

## Alternatives Considered

Alternative A: Session-based authentication with server-side storage
- Components: Server sessions stored in Redis/database, session cookies
- Why rejected: Violates stateless backend requirement, adds infrastructure complexity, harder to scale horizontally

Alternative B: RSA public/private key pairs for JWT
- Components: Asymmetric cryptography, public key distribution
- Why rejected: Adds complexity for key management, unnecessary for this use case, harder to implement with Better Auth

Alternative C: Custom authentication protocol
- Components: Proprietary token format, custom verification logic
- Why rejected: Reinvents standards, security risks, incompatibility with established tools

Alternative D: OAuth/Social login providers
- Components: Google/Facebook/Apple OAuth integration
- Why rejected: Out of scope per specification, adds external dependencies

## References

- Feature Spec: /specs/001-auth-identity/spec.md
- Implementation Plan: /specs/001-auth-identity/plan.md
- Related ADRs: none
- Evaluator Evidence: /history/prompts/001-auth-identity/0002-auth-identity-plan-complete.plan.prompt.md
