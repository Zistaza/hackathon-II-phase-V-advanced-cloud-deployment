import os
from typing import Optional
from pydantic import BaseModel, validator


class AuthConfig(BaseModel):
    """
    Configuration for authentication system
    """
    # Shared secret used for JWT signing and verification
    better_auth_secret: str

    # JWT configuration
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = 86400  # 24 hours

    # Token issuer and audience
    jwt_issuer: str = "better-auth"
    jwt_audience: str = "todo-app"

    @validator('better_auth_secret')
    def validate_secret(cls, v):
        """
        Validate that the secret meets security requirements
        """
        if not v:
            raise ValueError('BETTER_AUTH_SECRET must be set')

        if len(v) < 32:
            raise ValueError('BETTER_AUTH_SECRET should be at least 32 characters long for security')

        return v


def get_auth_config() -> AuthConfig:
    """
    Create and return authentication configuration from environment variables
    """
    better_auth_secret = os.getenv("BETTER_AUTH_SECRET")

    if not better_auth_secret:
        raise ValueError("BETTER_AUTH_SECRET environment variable must be set")

    return AuthConfig(better_auth_secret=better_auth_secret)


# Create global instance of auth config
auth_config = get_auth_config()


def validate_auth_config():
    """
    Validate that the authentication configuration is properly set up
    """
    try:
        config = get_auth_config()
        # Additional validation can be added here
        return True
    except ValueError as e:
        print(f"Auth configuration validation failed: {e}")
        return False