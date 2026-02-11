# Research: Authentication & Identity Implementation

## Decision 1: JWT Structure and Claims

### Decision:
JWT tokens will contain standard claims plus custom user identity claims required for the application.

### Rationale:
Standard JWT structure with required claims ensures compatibility with libraries and follows security best practices.

### Claims Structure:
- `iss`: Issuer (set to "better-auth")
- `sub`: Subject (user_id)
- `aud`: Audience (application-specific)
- `exp`: Expiration time (recommended 24 hours)
- `iat`: Issued at time
- `jti`: JWT ID (for potential future use)
- `user_email`: User's email address
- `user_id`: Unique user identifier

### Alternatives Considered:
- Minimal claims approach (just user_id) - rejected for lack of audit trail
- Extended claims with roles/permissions - rejected as out of scope per spec (no RBAC)

## Decision 2: JWT Signing and Verification Approach

### Decision:
Use HMAC SHA-256 (HS256) algorithm with BETTER_AUTH_SECRET as the shared secret for signing and verification.

### Rationale:
Better Auth integrates with JWT plugin that supports HS256 algorithm. Using the same BETTER_AUTH_SECRET ensures consistency between frontend and backend authentication.

### Implementation Details:
- Algorithm: HS256
- Secret: Retrieved from environment variable BETTER_AUTH_SECRET
- Backend verification: Using PyJWT library with the same secret

### Alternatives Considered:
- RSA public/private key pairs - rejected for complexity (stateless requirement)
- Different algorithms (RS256, ES256) - rejected for unnecessary complexity
- Separate secrets for signing/verification - rejected for operational overhead

## Decision 3: Backend JWT Verification Middleware Implementation

### Decision:
Implement FastAPI dependency and middleware to verify JWT tokens and extract user identity.

### Rationale:
FastAPI's dependency injection system provides clean way to enforce authentication on routes while extracting user identity for business logic.

### Implementation Structure:
- Custom dependency function: `get_current_user()`
- HTTPBearer scheme for token extraction
- JWT verification using PyJWT
- Exception handling for invalid/missing tokens

### Alternatives Considered:
- Global middleware approach - rejected for lack of granular control
- Decorator-based approach - rejected for less flexibility than dependencies

## Decision 4: Authenticated User Identity Exposure to Routes

### Decision:
Use FastAPI dependency injection with a `CurrentUser` Pydantic model to expose authenticated user identity to route handlers.

### Rationale:
Dependency injection provides type safety and automatic error handling while keeping route handlers clean and focused on business logic.

### Implementation:
- Define `CurrentUser` model with user_id, email
- Dependency function that decodes JWT and returns CurrentUser instance
- Route handlers accept CurrentUser as parameter

### Alternatives Considered:
- Manual token decoding in each route - rejected for duplication
- Global request context - rejected for testability concerns
- Thread-local storage - rejected for async safety concerns

## Decision 5: Error Handling Strategy for Invalid JWTs

### Decision:
Return HTTP 401 Unauthorized for all authentication failures with standardized error responses.

### Rationale:
Consistent error handling improves client experience and follows REST conventions. HTTP 401 is semantically correct for authentication failures.

### Error Scenarios:
- Missing Authorization header → HTTP 401
- Malformed token → HTTP 401
- Invalid signature → HTTP 401
- Expired token → HTTP 401
- Invalid claims → HTTP 401

### Alternatives Considered:
- HTTP 403 Forbidden - rejected as semantically incorrect (not authorization)
- Custom error codes - rejected for non-standard behavior

## Decision 6: Stateless JWT vs Server-Side Sessions

### Decision:
Use stateless JWT authentication as required by the specification.

### Rationale:
Specification explicitly requires stateless backend with no session storage. JWTs provide authentication without server-side state while enabling horizontal scaling.

### Tradeoffs:
**Pros:**
- Stateless operation (no server-side session storage)
- Horizontal scalability
- Self-contained tokens with user identity
- No session cleanup requirements

**Cons:**
- Cannot invalidate individual tokens before expiration
- Larger token size than session IDs
- Tokens remain valid even if user changes password

### Justification:
Stateless approach aligns with cloud-native design principles and meets explicit specification requirements.

## Decision 7: Better Auth Integration Pattern

### Decision:
Use Better Auth on the frontend to handle user registration/login and token issuance, with backend-only JWT verification.

### Rationale:
Specification requires Better Auth on frontend and backend JWT verification without calling frontend services. This pattern provides clean separation of concerns.

### Integration Flow:
1. Frontend: Better Auth handles registration/login
2. Frontend: Receives JWT from Better Auth
3. Frontend: Attaches JWT to API requests in Authorization header
4. Backend: Verifies JWT locally using BETTER_AUTH_SECRET
5. Backend: Extracts user identity for business logic

### Alternatives Considered:
- Backend-initiated authentication - rejected as violates spec
- Custom token format - rejected for reinvention of standards

## Decision 8: Token Expiration Strategy

### Decision:
Set JWT expiration to 24 hours (86400 seconds) with no refresh tokens.

### Rationale:
Balances security (reasonable validity window) with usability (day-long session). No refresh tokens as they're explicitly out of scope.

### Considerations:
- Shorter expiration increases security but degrades UX
- Longer expiration improves UX but increases risk window
- 24 hours aligns with typical "day session" expectation

### Alternatives Considered:
- 1-hour tokens - rejected for poor UX
- 7-day tokens - rejected for excessive validity window
- Sliding expiration - rejected as refresh tokens are out of scope

## Decision 9: Frontend-Backend Secret Sharing

### Decision:
Share BETTER_AUTH_SECRET between frontend (Better Auth) and backend (JWT verification) through environment variables.

### Rationale:
Specification requires using BETTER_AUTH_SECRET exclusively. Both frontend and backend need access to the same secret for token signing/verification.

### Security Measures:
- Store in environment variables, not code
- Use different variables for different environments
- Rotate regularly in production

### Alternatives Considered:
- Separate secrets for signing/verification - rejected as incompatible with Better Auth
- Dynamic secret exchange - rejected as violates stateless requirement

## Decision 10: API Route Protection Strategy

### Decision:
Apply JWT authentication to all backend routes that handle user-specific data, following the locked REST API contract.

### Rationale:
All routes in the locked contract require user_id in path, which must match the authenticated user's identity. This enforces multi-tenant isolation.

### Implementation:
- Create authentication dependency
- Apply to all routes that access user-specific data
- Verify user_id in URL matches JWT user_id for data isolation

### Alternatives Considered:
- Selective protection - rejected as violates security-by-default
- Role-based protection - rejected as RBAC is out of scope