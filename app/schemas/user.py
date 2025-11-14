from pydantic import BaseModel, EmailStr, constr, validator
from typing import Any

# Constrained types
UsernameStr = constr(min_length=3, max_length=50)
PhoneStr = constr(min_length=7, max_length=30)
PasswordStr = constr(min_length=8, max_length=128)
LoginMethodStr = constr(min_length=1, max_length=50)


class UserCreate(BaseModel):
    username: UsernameStr
    email: EmailStr
    phone_number: PhoneStr
    password: PasswordStr
    confirm_password: str
    login_method: LoginMethodStr

    @validator("confirm_password")
    def passwords_match(cls, v: str, values: dict[str, Any], **kwargs) -> str:
        pw = values.get("password")
        if pw != v:
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: PasswordStr
    login_method: LoginMethodStr


class UserLogout(BaseModel):
    email: EmailStr
    login_method: LoginMethodStr
    access_token: str


class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    phone_number: str
    login_method: str
    created_at: Any
    updated_at: Any

    class Config:
        from_attributes = True


class TokenRefresh(BaseModel):
    pass  # Empty class since we'll use Authorization header
