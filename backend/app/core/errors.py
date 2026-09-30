"""
Standardized error formatting and domain exceptions.
Conforms to FR-16 specification:
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Human-readable message",
    "request_id": "uuid"
  }
}
"""
from typing import Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.telemetry import get_request_id


class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(code="RESOURCE_NOT_FOUND", message=message, status_code=status.HTTP_404_NOT_FOUND)


class AuthenticationException(AppException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(code="AUTHENTICATION_FAILED", message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(AppException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(code="PERMISSION_DENIED", message=message, status_code=status.HTTP_403_FORBIDDEN)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def create_error_response(code: str, message: str, status_code: int, request_id: Optional[str] = None) -> JSONResponse:
    req_id = request_id or get_request_id()
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": req_id
            }
        }
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        request_id=getattr(request.state, "request_id", None)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    msg = errors[0]["msg"] if errors else "Invalid request body or parameters"
    loc = " -> ".join([str(l) for l in errors[0].get("loc", [])]) if errors else ""
    full_msg = f"{loc}: {msg}" if loc else msg
    return create_error_response(
        code="INVALID_REQUEST",
        message=full_msg,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        request_id=getattr(request.state, "request_id", None)
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return create_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=getattr(request.state, "request_id", None)
    )
