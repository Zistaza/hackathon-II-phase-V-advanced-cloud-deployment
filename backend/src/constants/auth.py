from enum import Enum
from typing import Final


# JWT-related constants
JWT_ALGORITHM: Final[str] = "HS256"
DEFAULT_JWT_EXPIRATION_SECONDS: Final[int] = 86400  # 24 hours
JWT_ISSUER: Final[str] = "better-auth"
JWT_AUDIENCE: Final[str] = "todo-app"

# Token-related constants
MIN_SECRET_LENGTH: Final[int] = 32
TOKEN_PREFIX: Final[str] = "Bearer "

# HTTP status codes for auth
HTTP_401_UNAUTHORIZED: Final[int] = 401
HTTP_403_FORBIDDEN: Final[int] = 403
HTTP_409_CONFLICT: Final[int] = 409

# Error messages
INVALID_CREDENTIALS_ERROR: Final[str] = "Invalid credentials"
TOKEN_EXPIRED_ERROR: Final[str] = "Token has expired"
INVALID_TOKEN_ERROR: Final[str] = "Invalid token"
MISSING_TOKEN_ERROR: Final[str] = "Missing authentication token"
INSUFFICIENT_PERMISSIONS_ERROR: Final[str] = "Insufficient permissions"
USER_NOT_FOUND_ERROR: Final[str] = "User not found"
USER_INACTIVE_ERROR: Final[str] = "User account is inactive"
DUPLICATE_USER_ERROR: Final[str] = "User already exists"

# User-related constants
MAX_EMAIL_LENGTH: Final[int] = 255
MAX_NAME_LENGTH: Final[int] = 255
MIN_PASSWORD_LENGTH: Final[int] = 6

# Session-related constants (though stateless in this implementation)
SESSION_COOKIE_NAME: Final[str] = "auth-session"
SESSION_MAX_AGE: Final[int] = 86400  # 24 hours in seconds


class AuthTokenType(Enum):
    """
    Enum for different types of authentication tokens
    """
    ACCESS = "access"
    REFRESH = "refresh"  # Though refresh tokens are out of scope for this spec


class AuthProvider(Enum):
    """
    Enum for different authentication providers
    """
    BETTER_AUTH = "better_auth"
    CUSTOM = "custom"


class Permission(Enum):
    """
    Enum for different permission levels
    """
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class UserRole(Enum):
    """
    Enum for different user roles (though RBAC is out of scope for this spec)
    """
    USER = "user"
    ADMIN = "admin"
    GUEST = "guest"