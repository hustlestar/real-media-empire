"""Error handlers for FastAPI application."""

import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.exceptions import APIException

logger = logging.getLogger(__name__)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: dict = None,
    request_id: str = None
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        error_code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
        request_id: Request ID for tracking

    Returns:
        JSONResponse with error information
    """
    content = {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
        }
    }

    if request_id:
        content["request_id"] = request_id

    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handle custom API exceptions.

    Args:
        request: FastAPI request object
        exc: APIException instance

    Returns:
        JSONResponse with error details
    """
    request_id = request.headers.get("X-Request-ID")

    logger.error(
        f"API Exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "request_id": request_id,
            "path": request.url.path
        }
    )

    return create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        request_id=request_id
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: RequestValidationError instance

    Returns:
        JSONResponse with validation error details
    """
    request_id = request.headers.get("X-Request-ID")

    # Format validation errors
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(
        "Validation error",
        extra={
            "errors": errors,
            "request_id": request_id,
            "path": request.url.path
        }
    )

    return create_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"errors": errors},
        request_id=request_id
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: FastAPI request object
        exc: HTTPException instance

    Returns:
        JSONResponse with error details
    """
    request_id = request.headers.get("X-Request-ID")

    # For 500 errors, log full traceback
    if exc.status_code >= 500:
        logger.error(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "request_id": request_id,
                "path": request.url.path,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        # Also print to console for immediate visibility
        print(f"\n{'='*80}")
        print(f"HTTP {exc.status_code} ERROR at {request.url.path}")
        print(f"Detail: {exc.detail}")
        print(f"{'='*80}")
        traceback.print_exc()
        print(f"{'='*80}\n")
    else:
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "request_id": request_id,
                "path": request.url.path
            }
        )

    error_codes = {
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }

    return create_error_response(
        error_code=error_codes.get(exc.status_code, "HTTP_ERROR"),
        message=exc.detail,
        status_code=exc.status_code,
        request_id=request_id
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with generic error message
    """
    request_id = request.headers.get("X-Request-ID")

    # Log full traceback for debugging
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "error_type": type(exc).__name__,
            "request_id": request_id,
            "path": request.url.path,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )

    # Also print to console for immediate visibility
    print(f"\n{'='*80}")
    print(f"UNHANDLED EXCEPTION at {request.url.path}")
    print(f"Type: {type(exc).__name__}")
    print(f"Message: {str(exc)}")
    print(f"{'='*80}")
    traceback.print_exc()
    print(f"{'='*80}\n")

    # Don't expose internal error details to clients
    return create_error_response(
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"error_type": type(exc).__name__} if logger.isEnabledFor(logging.DEBUG) else {},
        request_id=request_id
    )


def register_error_handlers(app):
    """
    Register all error handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Error handlers registered")
