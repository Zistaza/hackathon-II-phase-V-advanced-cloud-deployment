import logging
from typing import Optional
from datetime import datetime
import json


# Create logger for authentication operations
auth_logger = logging.getLogger("auth")
auth_logger.setLevel(logging.INFO)

# Create a handler for auth logs
if not auth_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    auth_logger.addHandler(handler)


def log_auth_success(user_id: str, email: str, action: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
    """
    Log successful authentication events

    Args:
        user_id: The ID of the authenticated user
        email: The email of the authenticated user
        action: The authentication action performed (login, register, etc.)
        ip_address: The IP address of the request (if available)
        user_agent: The user agent of the request (if available)
    """
    auth_logger.info(
        f"AUTH_SUCCESS - Action: {action}, UserID: {user_id}, Email: {email}"
        f"{f', IP: {ip_address}' if ip_address else ''}"
        f"{f', UserAgent: {user_agent}' if user_agent else ''}"
    )


def log_auth_failure(email: str, action: str, reason: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
    """
    Log failed authentication events

    Args:
        email: The email associated with the failed authentication
        action: The authentication action attempted
        reason: The reason for the failure
        ip_address: The IP address of the request (if available)
        user_agent: The user agent of the request (if available)
    """
    auth_logger.warning(
        f"AUTH_FAILURE - Action: {action}, Email: {email}, Reason: {reason}"
        f"{f', IP: {ip_address}' if ip_address else ''}"
        f"{f', UserAgent: {user_agent}' if user_agent else ''}"
    )


def log_token_validation(event: str, user_id: Optional[str] = None, email: Optional[str] = None,
                        token_status: Optional[str] = None, ip_address: Optional[str] = None):
    """
    Log token validation events

    Args:
        event: The token validation event (validated, expired, invalid, etc.)
        user_id: The user ID associated with the token (if available)
        email: The email associated with the token (if available)
        token_status: The status of the token (valid, expired, invalid, etc.)
        ip_address: The IP address of the request (if available)
    """
    auth_logger.info(
        f"TOKEN_{event.upper()} - "
        f"UserID: {user_id or 'unknown'}, "
        f"Email: {email or 'unknown'}, "
        f"Status: {token_status or 'unknown'}"
        f"{f', IP: {ip_address}' if ip_address else ''}"
    )


def log_unauthorized_access(attempted_endpoint: str, user_id: Optional[str] = None,
                           email: Optional[str] = None, ip_address: Optional[str] = None):
    """
    Log unauthorized access attempts

    Args:
        attempted_endpoint: The endpoint that was accessed without authorization
        user_id: The user ID (if any) associated with the request
        email: The email (if any) associated with the request
        ip_address: The IP address of the request
    """
    auth_logger.warning(
        f"UNAUTHORIZED_ACCESS - Endpoint: {attempted_endpoint}"
        f"{f', UserID: {user_id}' if user_id else ', UserID: none'}"
        f"{f', Email: {email}' if email else ', Email: none'}"
        f"{f', IP: {ip_address}' if ip_address else ''}"
    )


def log_privilege_violation(user_id: str, email: str, attempted_action: str,
                           required_permission: str, ip_address: Optional[str] = None):
    """
    Log privilege violations

    Args:
        user_id: The ID of the user attempting the action
        email: The email of the user attempting the action
        attempted_action: The action that was attempted without sufficient privileges
        required_permission: The permission required for the action
        ip_address: The IP address of the request
    """
    auth_logger.warning(
        f"PRIVILEGE_VIOLATION - UserID: {user_id}, Email: {email}, "
        f"Action: {attempted_action}, Required: {required_permission}"
        f"{f', IP: {ip_address}' if ip_address else ''}"
    )


def log_user_impersonation_attempt(attempted_user_id: str, requesting_user_id: str,
                                  requesting_email: str, ip_address: Optional[str] = None):
    """
    Log attempts to impersonate another user

    Args:
        attempted_user_id: The ID of the user being impersonated
        requesting_user_id: The ID of the user making the request
        requesting_email: The email of the user making the request
        ip_address: The IP address of the request
    """
    auth_logger.error(
        f"USER_IMPERSONATION_ATTEMPT - AttemptedUser: {attempted_user_id}, "
        f"RequestingUser: {requesting_user_id}, RequestingEmail: {requesting_email}"
        f"{f', IP: {ip_address}' if ip_address else ''}"
    )


def log_security_event(event_type: str, severity: str, details: dict,
                      user_id: Optional[str] = None, ip_address: Optional[str] = None):
    """
    Log general security events

    Args:
        event_type: The type of security event
        severity: The severity level (info, warning, error, critical)
        details: Additional details about the event
        user_id: The user ID associated with the event (if any)
        ip_address: The IP address associated with the event (if any)
    """
    auth_logger.log(
        getattr(logging, severity.upper(), logging.INFO),
        f"SECURITY_EVENT - Type: {event_type}, Severity: {severity}, "
        f"Details: {json.dumps(details)}, UserID: {user_id or 'none'}"
        f"{f', IP: {ip_address}' if ip_address else ''}"
    )


def setup_auth_logging():
    """
    Setup authentication logging configuration
    """
    # Ensure the auth logger is properly configured
    if not auth_logger.handlers:
        handler = logging.FileHandler("auth.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        auth_logger.addHandler(handler)

    auth_logger.info("Authentication logging initialized")


# Initialize the logging system
setup_auth_logging()