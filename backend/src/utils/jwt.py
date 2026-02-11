import jwt
import os
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel
from ..config.settings import settings


class JWTData(BaseModel):
    """Data structure for JWT claims"""
    user_id: str
    email: str
    exp: Optional[int] = None
    iat: Optional[int] = None
    iss: Optional[str] = "better-auth"
    aud: Optional[str] = "todo-app"


def create_access_token(data: JWTData) -> str:
    """
    Create a new JWT access token with the given data

    Args:
        data: JWTData containing user information

    Returns:
        Encoded JWT token string
    """
    to_encode = data.dict()

    # Set expiration time
    expire = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION_DELTA)
    to_encode.update({"exp": int(expire.timestamp())})

    # Set issued at time
    to_encode.update({"iat": int(datetime.utcnow().timestamp())})

    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[JWTData]:
    """
    Verify a JWT token and return the decoded data

    Args:
        token: JWT token string to verify

    Returns:
        JWTData if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience="todo-app"  # Specify the expected audience
        )

        # Validate required claims
        if "user_id" not in payload or "email" not in payload:
            return None

        return JWTData(**payload)

    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token format or signature
        return None
    except Exception:
        # Any other error during verification
        return None


def decode_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without verifying the signature (for debugging purposes)

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary with token claims if valid format, None otherwise
    """
    try:
        # Decode without verification (for debugging)
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception:
        return None


def inspect_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Inspect a JWT token to extract all information without full verification

    Args:
        token: JWT token string to inspect

    Returns:
        Dictionary with token information including header, payload, and metadata
    """
    try:
        # Split the token to get header and payload
        parts = token.split('.')
        if len(parts) != 3:
            return None

        # Decode header
        header_b64 = parts[0] + '=' * (4 - len(parts[0]) % 4)  # Add padding if needed
        header_json = base64.b64decode(header_b64).decode('utf-8')
        header = json.loads(header_json)

        # Decode payload without verification
        payload = decode_token_without_verification(token)

        if payload is None:
            return None

        # Create inspection result
        inspection_result = {
            "header": header,
            "payload": payload,
            "valid_format": True,
            "has_required_claims": all(key in payload for key in ['user_id', 'email']),
            "is_expired": is_token_expired(payload),
            "time_until_expiry": get_time_until_expiry(payload),
            "issuer": payload.get('iss'),
            "audience": payload.get('aud'),
            "subject": payload.get('sub'),
            "issued_at": payload.get('iat'),
            "expires_at": payload.get('exp')
        }

        return inspection_result
    except Exception:
        return None


def is_token_expired(payload: Dict[str, Any]) -> bool:
    """
    Check if a token payload indicates an expired token

    Args:
        payload: JWT payload dictionary

    Returns:
        Boolean indicating if token is expired
    """
    exp = payload.get('exp')
    if exp is None:
        return False

    current_time = int(datetime.utcnow().timestamp())
    return exp < current_time


def get_time_until_expiry(payload: Dict[str, Any]) -> Optional[int]:
    """
    Get the time in seconds until token expiry

    Args:
        payload: JWT payload dictionary

    Returns:
        Number of seconds until expiry, or None if no expiry claim
    """
    exp = payload.get('exp')
    if exp is None:
        return None

    current_time = int(datetime.utcnow().timestamp())
    return max(0, exp - current_time)