from fastapi import HTTPException, status
from typing import Optional


class AuthException(HTTPException):
    """
    Base authentication exception
    """
    def __init__(self, detail: str = "Authentication error", headers: Optional[dict] = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


class InvalidCredentialsException(AuthException):
    """
    Raised when invalid credentials are provided during login
    """
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail)


class TokenExpiredException(AuthException):
    """
    Raised when a JWT token has expired
    """
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail)


class InvalidTokenException(AuthException):
    """
    Raised when a JWT token is invalid (malformed, wrong signature, etc.)
    """
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(detail=detail)


class MissingTokenException(AuthException):
    """
    Raised when no authentication token is provided
    """
    def __init__(self, detail: str = "Missing token"):
        super().__init__(detail=detail)


class InsufficientPermissionsException(HTTPException):
    """
    Raised when authenticated user doesn't have sufficient permissions
    """
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UserNotFoundException(AuthException):
    """
    Raised when a user is not found
    """
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail=detail, headers={"WWW-Authenticate": "Bearer"})


class UserInactiveException(AuthException):
    """
    Raised when a user account is inactive
    """
    def __init__(self, detail: str = "User account is inactive"):
        super().__init__(detail=detail, headers={"WWW-Authenticate": "Bearer"})


class DuplicateUserException(HTTPException):
    """
    Raised when attempting to create a user that already exists
    """
    def __init__(self, detail: str = "User already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


def handle_auth_error(error_message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
    """
    Generic function to handle authentication errors

    Args:
        error_message: The error message to return
        status_code: The HTTP status code to return (default 401)

    Returns:
        HTTPException with the specified error message and status code
    """
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return AuthException(detail=error_message)
    elif status_code == status.HTTP_403_FORBIDDEN:
        return InsufficientPermissionsException(detail=error_message)
    elif status_code == status.HTTP_409_CONFLICT:
        return DuplicateUserException(detail=error_message)
    else:
        return HTTPException(status_code=status_code, detail=error_message)