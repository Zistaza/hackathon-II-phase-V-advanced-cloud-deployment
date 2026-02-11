from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
from sqlmodel import Session, select
from pydantic import BaseModel
from passlib.context import CryptContext
from ..models.user_model import User, UserCreate, UserPublic
from ..models.user import UserRegistrationRequest
from ..utils.jwt import create_access_token, JWTData
from ..config.settings import settings
from ..database import get_session

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_BCRYPT_LEN = 72  # bcrypt limitation

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthResponse(BaseModel):
    token: str
    user: UserPublic


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserRegistrationRequest, session: Session = Depends(get_session)) -> AuthResponse:
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Truncate password to bcrypt max byte length (72 bytes)
    password_bytes = user_data.password.encode('utf-8')[:MAX_BCRYPT_LEN]
    password_to_hash = password_bytes.decode('utf-8', errors='ignore')

    # Hash the password
    hashed_password = pwd_context.hash(password_to_hash)

    # Create new user with hashed password
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password=hashed_password,
    )

    # Add to session and commit
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create JWT token
    jwt_data = JWTData(user_id=new_user.id, email=new_user.email)
    token = create_access_token(jwt_data)

    # Return token and user info
    return AuthResponse(
        token=token,
        user=UserPublic.from_orm(new_user) if hasattr(UserPublic, 'from_orm') else UserPublic(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: LoginRequest, session: Session = Depends(get_session)) -> AuthResponse:
    # Find user by email
    user = session.exec(select(User).where(User.email == login_data.email)).first()

    # Truncate password to bcrypt max byte length (72 bytes)
    password_bytes = login_data.password.encode('utf-8')[:MAX_BCRYPT_LEN]
    password_to_verify = password_bytes.decode('utf-8', errors='ignore')

    if not user or not pwd_context.verify(password_to_verify, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create JWT token
    jwt_data = JWTData(user_id=user.id, email=user.email)
    token = create_access_token(jwt_data)

    # Return token and user info
    return AuthResponse(
        token=token,
        user=UserPublic.from_orm(user) if hasattr(UserPublic, 'from_orm') else UserPublic(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    )


@router.post("/logout")
async def logout_user():
    return {"message": "Successfully logged out"}
