from typing import Annotated
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from api_tools import oauth2_scheme, SECRET_KEY, ALGORITHM, pwd_context
from base.user import User
from db import get_db
from base_model.tokendata import TokenData
from datetime import datetime, timedelta, timezone


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, login: str, password: str):
    """Аутентификация пользователя"""
    user = db.query(User).filter(User.login == login).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = TokenData(username=login)
    except InvalidTokenError:
        raise credentials_exception
    user = db.query(User).filter(User.login == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user