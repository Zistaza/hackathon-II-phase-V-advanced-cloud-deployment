# ADR-0003: Frontend Technology Stack and Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-19
- **Feature:** 003-frontend-todo-app
- **Context:** Need to establish a comprehensive frontend architecture for the Todo Full-Stack Web Application that balances developer experience, security, performance, and maintainability. The architecture must integrate seamlessly with the existing backend API contracts, implement secure authentication flows with JWT tokens, provide responsive UI for task management, and follow modern React/Next.js best practices while adhering to the project's security-by-default principle.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- **Frontend Framework**: Next.js 16.1.3 with App Router for modern React development and file-based routing
- **UI Framework**: React 19.2.3 with TypeScript 5.x for type safety and modern React patterns
- **Authentication Integration**: Better Auth with HttpOnly cookies for secure JWT storage and Context API for state management
- **API Integration**: Centralized API service with Axios and interceptors for consistent request/response handling
- **Route Protection**: Combined Next.js middleware and server component checks for multi-layered security
- **State Management**: Context API with useReducer for global state management without external dependencies
- **Project Structure**: Route groups with separate (auth) and (dashboard) sections for clear separation of concerns
- **Styling**: Tailwind CSS with CSS Modules for utility-first styling approach
- **Deployment**: Standard Next.js deployment patterns compatible with Vercel or other platforms

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

- Unified and consistent routing architecture with Next.js App Router
- Enhanced security through HttpOnly cookies preventing XSS attacks on JWT tokens
- Centralized API management with automatic JWT attachment and consistent error handling
- Multi-layered route protection combining edge and server-side validation
- Maintainable state management without external dependencies like Redux/Zustand
- Clear separation between public and protected routes improving user experience
- Strong type safety with TypeScript reducing runtime errors
- Modern React patterns with hooks and Context API for familiar development experience
- Compatible with existing backend API contracts ensuring seamless integration

### Negative

- Learning curve for developers unfamiliar with Next.js App Router conventions
- Potential bundle size increase with Axios compared to native fetch
- Additional complexity with multi-layered route protection requiring coordination
- Context API may face performance issues with very large applications (though suitable for this scope)
- Dependency on Next.js ecosystem limiting flexibility for alternative deployment options
- HttpOnly cookies require additional server-side handling compared to localStorage
- More complex debugging for JWT-related issues due to cookie-based storage

## Alternatives Considered

Alternative Stack A: React + Vite + React Router + Custom Authentication
- Components: Vite bundler, React Router DOM, custom authentication implementation
- Why rejected: Would require building authentication from scratch, lacks Next.js integrated features, more complex SEO and SSR setup

Alternative Stack B: Remix + its built-in authentication
- Components: Remix framework, built-in data loading, form handling
- Why rejected: Less mature ecosystem than Next.js, different mental model for routing, smaller community and resources

Alternative Stack C: React + Create React App + Third-party auth library
- Components: CRA, React Router, Auth0 or Firebase Auth
- Why rejected: Missing Next.js benefits like file-based routing, SSR, API routes; dependency on external auth providers

Alternative Stack D: Vanilla JavaScript + Custom framework
- Components: Plain JS, custom routing, custom auth implementation
- Why rejected: Significant development overhead, reinventing standard solutions, lack of modern React patterns

## References

- Feature Spec: /specs/003-frontend-todo-app/spec.md
- Implementation Plan: /specs/003-frontend-todo-app/plan.md
- Related ADRs: ADR-0001 (JWT Authentication Architecture), ADR-0002 (Authentication Architecture)
- Evaluator Evidence: /specs/003-frontend-todo-app/research.md
