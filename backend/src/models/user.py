from pydantic import BaseModel
from typing import Optional


class CurrentUser(BaseModel):
    """
    Represents the authenticated user identity extracted from JWT for use in backend operations.

    Fields:
    - user_id: Unique identifier of the authenticated user
    - email: Email address of the authenticated user
    - is_authenticated: Flag indicating authentication status
    """
    user_id: str
    email: str
    is_authenticated: bool = True


class UserRegistrationRequest(BaseModel):
    """
    Request model for user registration
    """
    email: str
    password: str
    name: Optional[str] = None


class UserLoginRequest(BaseModel):
    """
    Request model for user login
    """
    email: str
    password: str


class UserResponse(BaseModel):
    """
    Response model for user data
    """
    id: str
    email: str
    name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None