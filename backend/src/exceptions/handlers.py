from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
import logging


# Set up logger
logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions globally
    """
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle validation errors from Pydantic models
    """
    logger.error(f"Validation Error: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "status_code": 422
        }
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """
    Handle database integrity errors
    """
    logger.error(f"Integrity Error: {str(exc)}")

    return JSONResponse(
        status_code=409,
        content={
            "detail": "Data integrity violation",
            "status_code": 409
        }
    )


async def general_exception_handler(request: Request, exc: Union[Exception, BaseException]):
    """
    Handle general exceptions
    """
    logger.error(f"General Exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500
        }
    )


# Error handling for authentication failures specifically
async def auth_exception_handler(request: Request, exc: HTTPException):
    """
    Handle authentication-specific exceptions
    """
    if exc.status_code == 401:
        logger.info(f"Authentication failed: {exc.detail}")
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Authentication required",
                "status_code": 401,
                "error_type": "unauthorized"
            }
        )

    # For other HTTP exceptions, use the general handler
    return await http_exception_handler(request, exc)