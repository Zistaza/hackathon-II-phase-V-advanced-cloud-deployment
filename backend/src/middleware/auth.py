from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from ..utils.jwt import verify_token
from ..models.user import CurrentUser


security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    """
    FastAPI dependency to extract the current user from JWT token in Authorization header

    Args:
        credentials: HTTP authorization credentials from the Authorization header

    Returns:
        CurrentUser: Authenticated user information

    Raises:
        HTTPException: If token is invalid, expired, or missing required claims
    """
    token = credentials.credentials

    # Verify the token and extract user data
    token_data = verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create and return CurrentUser object
    current_user = CurrentUser(
        user_id=token_data.user_id,
        email=token_data.email,
        is_authenticated=True
    )

    return current_user


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[CurrentUser]:
    """
    FastAPI dependency to optionally extract the current user from JWT token

    Args:
        credentials: HTTP authorization credentials from the Authorization header (optional)

    Returns:
        CurrentUser if token is valid, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    token_data = verify_token(token)

    if token_data is None:
        return None

    # Create and return CurrentUser object
    current_user = CurrentUser(
        user_id=token_data.user_id,
        email=token_data.email,
        is_authenticated=True
    )

    return current_user