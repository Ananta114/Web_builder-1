from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import LoginRecord, User
from app.utils.security import hash_password


def create_user(
    db: Session,
    *,
    username: str,
    email: str,
    phone_number: str,
    password: str,
    ip_address: str,
    login_method: str,
):
    user = User(
        username=username,
        email=email,
        phone_number=phone_number,
        password_hash=hash_password(password),
        ip_address=ip_address,
        login_method=login_method,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_login_record(
    db: Session,
    *,
    user_id: int,
    username: str,
    email: str,
    login_method: str,
    ip_address: str | None,
    is_active: bool,
):
    record = LoginRecord(
        user_id=user_id,
        username=username,
        email=email,
        login_method=login_method,
        ip_address=ip_address,
        is_active=is_active,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_active_login_record(db: Session, user_id: int):
    return db.query(LoginRecord).filter(
        LoginRecord.user_id == user_id,
        LoginRecord.is_active == True
    ).order_by(LoginRecord.created_at.desc()).first()


def logout_user(db: Session, user_id: int):
    # Mark all active sessions for this user as logged out
    active_records = db.query(LoginRecord).filter(
        LoginRecord.user_id == user_id,
        LoginRecord.is_active == True
    ).all()
    
    for record in active_records:
        record.is_active = False
        record.logged_out_at = func.now()
    
    db.commit()
    return len(active_records)  # Return number of sessions closed


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()


def get_login_record_by_id(db: Session, *, id: str) -> LoginRecord | None:
    return db.query(LoginRecord).filter(LoginRecord.id == id).first()


def set_login_record_status(
    db: Session,
    *,
    id: str,
    is_active: bool,
    ip_address: str | None = None,
) -> LoginRecord | None:
    record = get_login_record_by_id(db, id=id)
    if not record:
        return None
    record.is_active = is_active
    if ip_address is not None:
        record.ip_address = ip_address
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
