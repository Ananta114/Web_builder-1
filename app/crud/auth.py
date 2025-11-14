from sqlalchemy.orm import Session

from app.models.user import User
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


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()
