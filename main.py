from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, status, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import os

# Создание объекта FastAPI
# app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
app = FastAPI(redoc_url=None)

# Настройка базы данных SQLite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
# SQLALCHEMY_DATABASE_URL = "sqlite:///db.db"
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # in seconds

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модели базы данных
class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(15), unique=True)
    email = Column(String(100), nullable=True)
    hashed_password = Column(String(100))

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic модели
class UserCreate(BaseModel):
    login: str
    password: str
    email: str

class UserLogin(BaseModel):
    login: str
    password: str

class UserResponse(BaseModel):
    id: int
    login: str
    email: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Вспомогательные функции
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

async def get_current_user_or_raise_if_banned(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Session = Depends(get_db)
):
    user = await get_current_user(token, db)
    
    return user

# Роуты API
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "message": "Ресурс не найден"}
    )

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
async def read_users_me(current_user: Annotated[User, Depends(get_current_user_or_raise_if_banned)]):
    return current_user

@app.put("/users/me/update", response_model=UserResponse)
async def update_current_user(
    user_update: UserCreate,
    current_user: Annotated[User, Depends(get_current_user_or_raise_if_banned)],
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