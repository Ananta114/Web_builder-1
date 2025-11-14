from typing import Any, Optional
from fastapi import status
from fastapi.responses import JSONResponse

def success_response(message: str, data: Optional[Any] = None, status_code: int = status.HTTP_200_OK):
    payload = {"status": True, "message": message}
    if data is not None:
        payload["data"] = data
    return JSONResponse(status_code=status_code, content=payload)

def error_response(error: str, code: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: Optional[Any] = None):
    payload = {"status": False, "error": error, "code": code}
    if details is not None:
        payload["details"] = details
    return JSONResponse(status_code=status_code, content=payload)
