"""Custom exceptions for the API."""

from typing import Optional, Dict, Any


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIException):
    """Validation error (400)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(APIException):
    """Resource not found (404)."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} with ID '{resource_id}' not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "id": resource_id}
        )


class ConflictError(APIException):
    """Resource conflict (409)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details
        )


class RateLimitError(APIException):
    """Rate limit exceeded (429)."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )


class ExternalServiceError(APIException):
    """External service error (502)."""

    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"Error from {service}: {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


class BudgetExceededError(APIException):
    """Budget limit exceeded (402)."""

    def __init__(self, current_cost: float, budget_limit: float):
        super().__init__(
            message=f"Budget exceeded: ${current_cost:.2f} exceeds limit of ${budget_limit:.2f}",
            status_code=402,
            error_code="BUDGET_EXCEEDED",
            details={"current_cost": current_cost, "budget_limit": budget_limit}
        )


class ProcessingError(APIException):
    """Processing/generation error (500)."""

    def __init__(self, task: str, message: str):
        super().__init__(
            message=f"Processing failed for {task}: {message}",
            status_code=500,
            error_code="PROCESSING_ERROR",
            details={"task": task}
        )
