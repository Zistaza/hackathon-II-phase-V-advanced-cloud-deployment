from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from typing import Callable, Awaitable
import logging


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Process the request
        response: Response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"

        # For auth-related responses, we may want additional headers
        if request.url.path.startswith('/api/v1/auth'):
            # Prevent caching of auth responses to avoid storing sensitive data in browser cache
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response


def add_security_headers(response: Response, is_auth_endpoint: bool = False):
    """
    Helper function to add security headers to a response

    Args:
        response: The response object to add headers to
        is_auth_endpoint: Whether this is an auth-related endpoint
    """
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    if is_auth_endpoint:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


def get_secure_response(content: dict, status_code: int = 200, is_auth_endpoint: bool = False):
    """
    Create a response with security headers applied

    Args:
        content: The content to include in the response
        status_code: The HTTP status code
        is_auth_endpoint: Whether this is an auth-related endpoint

    Returns:
        JSONResponse with security headers
    """
    response = JSONResponse(content=content, status_code=status_code)
    return add_security_headers(response, is_auth_endpoint)