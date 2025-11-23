from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, List, Dict
from fastapi import FastAPI, HTTPException, Depends, status, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Table, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.responses import JSONResponse
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

# Таблица для подписок на курсы
user_course_subscription = Table(
    'user_course_subscription',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('Users.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('Courses.id'), primary_key=True)
)

# Модели базы данных
class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(15), unique=True)
    email = Column(String(100), nullable=True)
    hashed_password = Column(String(100))
    
    # Relationships
    courses = relationship("Course", back_populates="author")
    reports = relationship("CourseReport", back_populates="author")
    subscribed_courses = relationship("Course", secondary=user_course_subscription, back_populates="subscribers")

class CourseType(Base):
    __tablename__ = "CourseTypes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    
    # Relationships
    courses = relationship("Course", back_populates="course_type")

class Course(Base):
    __tablename__ = "Courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    type_id = Column(Integer, ForeignKey("CourseTypes.id"))
    description = Column(Text)
    author_id = Column(Integer, ForeignKey("Users.id"))
    
    # Relationships
    course_type = relationship("CourseType", back_populates="courses")
    author = relationship("User", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course")
    reports = relationship("CourseReport", back_populates="course")
    subscribers = relationship("User", secondary=user_course_subscription, back_populates="subscribed_courses")

class Lesson(Base):
    __tablename__ = "Lessons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    course_id = Column(Integer, ForeignKey("Courses.id"))
    description = Column(Text)
    theory = Column(Text)
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    tests = relationship("Test", back_populates="lesson")

class Test(Base):
    __tablename__ = "Tests"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("Lessons.id"))
    question = Column(Text)
    answers = Column(JSON)  # Изменено: теперь храним ответы в формате JSON
    
    # Relationships
    lesson = relationship("Lesson", back_populates="tests")

class CourseReport(Base):
    __tablename__ = "CourseReports"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("Courses.id"))
    author_id = Column(Integer, ForeignKey("Users.id"))
    question = Column(Text)
    
    # Relationships
    course = relationship("Course", back_populates="reports")
    author = relationship("User", back_populates="reports")
    help_responses = relationship("CourseHelp", back_populates="report")

class CourseHelp(Base):
    __tablename__ = "CourseHelp"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("CourseReports.id"))
    answer = Column(Text)
    
    # Relationships
    report = relationship("CourseReport", back_populates="help_responses")

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic модели

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class CourseReportCreate(BaseModel):
    question: str

class CourseReportResponse(BaseModel):
    id: int
    course_id: int
    author_id: int
    question: str
    
    class Config:
        from_attributes = True

class CourseHelpCreate(BaseModel):
    answer: str

class CourseHelpResponse(BaseModel):
    id: int
    report_id: int
    answer: str
    
    class Config:
        from_attributes = True

# Вспомогательные функции
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# 11) Получить все вопросы по курсу для ассистента
@app.get("/courses/{course_id}/reports", response_model=List[CourseReportResponse])
async def get_course_reports(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course.reports

# 12) Получить конкретный вопрос по курсу для ассистента
@app.get("/courses/{course_id}/reports/{report_id}", response_model=CourseReportResponse)
async def get_course_report(
    course_id: int,
    report_id: int,
    db: Session = Depends(get_db)
):
    report = db.query(CourseReport).filter(
        CourseReport.id == report_id,
        CourseReport.course_id == course_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report

@app.post("/courses/{course_id}/reports/create", response_model=CourseReportResponse)
async def create_course_report(
    course_id: int,
    report: CourseReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise_if_banned)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db_report = CourseReport(
        course_id=course_id,
        author_id=current_user.id,
        question=report.question
    )
    try:
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating course report")

@app.post("/courses/{course_id}/reports/{report_id}/help", response_model=CourseHelpResponse)
async def create_course_help(
    course_id: int,
    report_id: int,
    help_data: CourseHelpCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise_if_banned)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    report = db.query(CourseReport).filter(CourseReport.id == report_id, CourseReport.course_id == course_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found in this course")
    
    if course.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to provide help for this course")
    
    db_help = CourseHelp(
        report_id=report_id,
        answer=help_data.answer
    )
    try:
        db.add(db_help)
        db.commit()
        db.refresh(db_help)
        return db_help
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating course help")