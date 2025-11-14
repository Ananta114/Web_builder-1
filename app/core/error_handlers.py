from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import json
from datetime import datetime
from typing import Any

from .response import error_response
from .exceptions import AppException

def register_exception_handlers(app):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return error_response(error=exc.message, code=exc.code, status_code=exc.status_code, details=exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # You can format as you prefer
        details = exc.errors()
        return error_response(error="Validation error", code="VALIDATION_ERROR", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)

    @app.exception_handler(IntegrityError)
    async def sqlalchemy_integrity_error(request: Request, exc: IntegrityError):
        # Don't leak DB internals, return generic message
        return error_response(error="Database integrity error", code="DB_INTEGRITY_ERROR", status_code=status.HTTP_400_BAD_REQUEST)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return error_response(
            error=exc.detail,
            code=getattr(exc, "code", "HTTP_ERROR"),
            status_code=exc.status_code,
            details=getattr(exc, "details", None)
        )
        
    @app.exception_handler(TypeError)
    async def json_encode_error_handler(request: Request, exc: TypeError):
        if "Object of type.*is not JSON serializable" in str(exc):
            return error_response(
                error="Error encoding response data",
                code="JSON_ENCODE_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=str(exc)
            )
        raise exc  # Re-raise if it's not a JSON serialization error
        
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        return error_response(
            error="Database error occurred",
            code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(exc)
        )
        
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return error_response(
            error="An unexpected error occurred",
            code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(exc) if str(exc) else None
        )
