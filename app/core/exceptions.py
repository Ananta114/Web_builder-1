from typing import Optional

class AppException(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 400, details: Optional[dict] = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

class EmailExists(AppException):
    def __init__(self, message: str = "Email already exists"):
        super().__init__(message=message, code="EMAIL_EXISTS", status_code=409)

class PhoneExists(AppException):
    def __init__(self, message: str = "Phone number already exists"):
        super().__init__(message=message, code="PHONE_EXISTS", status_code=409)

class UsernameExists(AppException):
    def __init__(self, message: str = "Username already exists"):
        super().__init__(message=message, code="USERNAME_EXISTS", status_code=409)
