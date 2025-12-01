from typing import Annotated
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from api_tools import oauth2_scheme, SECRET_KEY, ALGORITHM
from base.user import User
from db import get_db
from base_model.tokendata import TokenData


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