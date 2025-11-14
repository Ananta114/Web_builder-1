from fastapi import APIRouter, Depends, Request, status, HTTPException
import jwt
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.models.login_record import LoginRecord
from app.schemas.other import TokenRefresh
from app.core.response import success_response, error_response
from app.crud import auth as crud_auth, other as crud_other
from app.core.dependencies import get_current_user
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter(tags=["Auth"])


@router.post("/refresh")
def refresh_token(
    request: Request,
    db: Session = Depends(get_db),
    payload: TokenRefresh = Depends()
):
    # Get the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return error_response("Missing or invalid Authorization header", "AUTH_HEADER_MISSING", 401)
    
    # Extract the token from the header
    token = auth_header.split(" ")[1]
    
    try:
        # Decode the refresh token
        payload_data = decode_token(token)
        
        # Verify token type
        if payload_data.get("type") != "refresh":
            return error_response("Invalid token type", "INVALID_TOKEN", 401)
        
        # Get user ID from token
        user_id = payload_data.get("sub")
        if not user_id:
            return error_response("Invalid token", "INVALID_TOKEN", 401)
        
        # Get user from database
        user = crud_auth.get_user_by_id(db, int(user_id))
        if not user:
            return error_response("User not found", "USER_NOT_FOUND", 404)

        # Check for an active session (logout should disable refresh as well)
        active_record = crud_other.get_active_login_record(db, user.user_id)
        if not active_record:
            return error_response("No active session found", "NO_ACTIVE_SESSIONS", 401)

        # Create new tokens
        access_token, _ = create_access_token(str(user.user_id))
        refresh_token = create_refresh_token(str(user.user_id))
        
        return success_response(
            message="Tokens refreshed successfully",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
        )
        
    except jwt.ExpiredSignatureError:
        return error_response("Refresh token has expired", "TOKEN_EXPIRED", 401)
    except jwt.InvalidTokenError:
        return error_response("Invalid refresh token", "INVALID_TOKEN", 401)


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_data(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current authenticated user's data.
    Requires a valid access token in the Authorization header.
    """
    # Get the full user data from the database
    user = crud_auth.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get the user's active login records
    active_sessions = db.query(LoginRecord).filter(
        LoginRecord.user_id == user.user_id,
        LoginRecord.is_active == True
    ).all()
    
    # Prepare the response with serializable data types
    user_data = {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "login_method": user.login_method,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "active_sessions": len(active_sessions),
        "last_login": active_sessions[0].created_at.isoformat() if active_sessions else None
    }
    
    return success_response(
        message="User data retrieved successfully",
        data=user_data
    )
