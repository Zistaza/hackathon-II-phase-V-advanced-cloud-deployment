import pytest
from datetime import datetime, timedelta
from jose import jwt
from src.config.settings import settings
from src.utils.jwt import create_access_token, verify_token, JWTData, inspect_token


def test_create_access_token_structure():
    """Test that created JWT token has proper structure and claims"""
    # Arrange
    jwt_data = JWTData(
        user_id="test_user_id",
        email="test@example.com"
    )

    # Act
    token = create_access_token(jwt_data)

    # Assert - verify token structure
    assert token is not None
    assert isinstance(token, str)

    # Decode without verification to check structure
    decoded = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=[settings.JWT_ALGORITHM], options={"verify_signature": False})

    # Check required claims
    assert "user_id" in decoded
    assert "email" in decoded
    assert "exp" in decoded
    assert "iat" in decoded
    assert "iss" in decoded
    assert "aud" in decoded

    # Check values
    assert decoded["user_id"] == "test_user_id"
    assert decoded["email"] == "test@example.com"
    assert decoded["iss"] == "better-auth"
    assert decoded["aud"] == "todo-app"


def test_verify_token_success():
    """Test successful token verification"""
    # Arrange
    jwt_data = JWTData(
        user_id="test_user_id",
        email="test@example.com"
    )
    token = create_access_token(jwt_data)

    # Act
    result = verify_token(token)

    # Assert
    assert result is not None
    assert result.user_id == "test_user_id"
    assert result.email == "test@example.com"


def test_verify_token_expired():
    """Test token verification with expired token"""
    # Arrange - create expired token manually
    expired_payload = {
        "user_id": "test_user_id",
        "email": "test@example.com",
        "exp": int((datetime.utcnow() - timedelta(minutes=1)).timestamp()),
        "iat": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),
        "iss": "better-auth",
        "aud": "todo-app"
    }

    expired_token = jwt.encode(expired_payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)

    # Act
    result = verify_token(expired_token)

    # Assert
    assert result is None


def test_verify_token_invalid_signature():
    """Test token verification with invalid signature"""
    # Arrange - create token with different secret
    payload = {
        "user_id": "test_user_id",
        "email": "test@example.com",
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "iss": "better-auth",
        "aud": "todo-app"
    }

    wrong_secret_token = jwt.encode(payload, "wrong_secret", algorithm=settings.JWT_ALGORITHM)

    # Act
    result = verify_token(wrong_secret_token)

    # Assert
    assert result is None


def test_inspect_token_valid():
    """Test token inspection for valid token"""
    # Arrange
    jwt_data = JWTData(
        user_id="test_user_id",
        email="test@example.com"
    )
    token = create_access_token(jwt_data)

    # Act
    result = inspect_token(token)

    # Assert
    assert result is not None
    assert result["valid_format"] is True
    assert result["has_required_claims"] is True
    assert result["is_expired"] is False
    assert result["payload"]["user_id"] == "test_user_id"
    assert result["payload"]["email"] == "test@example.com"
    assert result["issuer"] == "better-auth"
    assert result["audience"] == "todo-app"


def test_inspect_token_expired():
    """Test token inspection for expired token"""
    # Arrange - create expired token manually
    expired_payload = {
        "user_id": "test_user_id",
        "email": "test@example.com",
        "exp": int((datetime.utcnow() - timedelta(minutes=1)).timestamp()),
        "iat": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),
        "iss": "better-auth",
        "aud": "todo-app"
    }

    expired_token = jwt.encode(expired_payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)

    # Act
    result = inspect_token(expired_token)

    # Assert
    assert result is not None
    assert result["valid_format"] is True
    assert result["has_required_claims"] is True
    assert result["is_expired"] is True


def test_inspect_token_invalid_format():
    """Test token inspection for invalid token format"""
    # Arrange
    invalid_token = "not.a.valid.token.format"

    # Act
    result = inspect_token(invalid_token)

    # Assert
    assert result is None


def test_inspect_token_missing_claims():
    """Test token inspection for token with missing required claims"""
    # Arrange - create token without required claims
    payload = {
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
    }

    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)

    # Act
    result = inspect_token(token)

    # Assert
    assert result is not None
    assert result["valid_format"] is True
    assert result["has_required_claims"] is False


if __name__ == "__main__":
    pytest.main([__file__])