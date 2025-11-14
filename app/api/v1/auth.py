from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import UserCreate, UserLogin, UserLogout
from app.core.response import success_response, error_response
from app.crud import auth as crud_auth, other as crud_other
from app.core.dependencies import get_current_user
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)

router = APIRouter(tags=["Auth"])

@router.post("/signup")
def signup(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    # Check for existing email/username
    if crud_auth.get_user_by_email(db, payload.email):
        return error_response("Email already exists", "EMAIL_EXISTS", 400)
    if crud_auth.get_user_by_username(db, payload.username):
        return error_response("Username already exists", "USERNAME_EXISTS", 400)

    # Extract client IP address
    client_ip = request.client.host

    user = crud_auth.create_user(
        db,
        username=payload.username,
        email=payload.email,
        phone_number=payload.phone_number,
        password=payload.password,
        ip_address=client_ip,
        login_method=payload.login_method,
    )

    access_token, _ = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    crud_other.create_login_record(
        db,
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        login_method=payload.login_method,
        ip_address=client_ip,
        is_active=True,
    )

    return success_response(
        message="User created successfully",
        data={
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        status_code=201,
    )


@router.post("/login")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    user = crud_auth.get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        return error_response("Invalid credentials", "INVALID_CREDENTIALS", 401)

    # Create tokens
    access_token, _ = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))

    client_ip = request.client.host if request.client else None

    # Create login record
    crud_other.create_login_record(
        db,
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        login_method=payload.login_method,
        ip_address=client_ip,
        is_active=True,
    )

    return success_response(
        message="Login successful",
        data={
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mark all active sessions for this user as logged out
    sessions_closed = crud_other.logout_user(db, current_user["user_id"])
    
    if sessions_closed == 0:
        return error_response(
            "No active sessions found",
            "NO_ACTIVE_SESSIONS",
            status.HTTP_400_BAD_REQUEST
        )
        
    return success_response(
        message="Successfully logged out"
    )
