
from typing import Annotated
from fastapi import HTTPException, Depends, status, Request
from api_tools import app, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi.responses import JSONResponse
from base.user import User
from db import init_db, get_db
from base_model.token import Token
from base_model.usercreate import UserCreate
from base_model.userresponse import UserResponse
from db_tools import get_current_user, hash_password, authenticate_user, create_access_token


# Создание таблиц в базе данных
init_db()

# Инициализация базы данных
get_db()


# Роуты API
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "message": "Ресурс не найден"}
    )


@app.get("/")
async def test():
    return {"status": "work"}


@app.post("/register/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = User(
        login=user.login,
        hashed_password=hashed_password,
        email=user.email
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback() 
        raise HTTPException(status_code=400, detail="Login already registered")

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@app.put("/users/me/update", response_model=UserResponse)
async def update_current_user(
    user_update: UserCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Обновление данных текущего пользователя
    """
    # Проверяем, не пытается ли пользователь изменить логин на уже существующий
    if user_update.login != current_user.login:
        existing_user = db.query(User).filter(User.login == user_update.login).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Login already registered"
            )
    
    # Обновляем данные пользователя
    current_user.login = user_update.login
    current_user.email = user_update.email
    
    # Если предоставлен новый пароль, хешируем и обновляем его
    if user_update.password:
        current_user.hashed_password = hash_password(user_update.password)
    
    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Update failed")

from sqlalchemy import text

@app.get("/database/users-table-info")
async def get_users_table_info(db: Session = Depends(get_db)):
    # Выполняем запрос PRAGMA через SQLAlchemy
    result = db.execute(text("""SELECT 
        column_name,
        data_type,
        character_maximum_length,
        is_nullable,
        column_default
    FROM information_schema.columns 
    WHERE table_name = 'CourseHelp'
    ORDER BY ordinal_position;"""))
    columns_info = []
    
    for row in result:
        columns_info.append({
            "name": row[0],
            "type": row[1],
            "max_length": row[2],
            "not_null": bool(row[3]),
            "default_value": row[4]
        })
    
    return columns_info
