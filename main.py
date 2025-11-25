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
app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
# app = FastAPI(redoc_url=None)

# Настройка базы данных SQLite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
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

class LessonType(Base):
    __tablename__ = "LessonTypes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    
    # Relationships
    lessons = relationship("Lesson", back_populates="lesson_type")

class Lesson(Base):
    __tablename__ = "Lessons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    course_id = Column(Integer, ForeignKey("Courses.id"))
    type_id = Column(Integer, ForeignKey("LessonTypes.id"), nullable=True)
    description = Column(Text)
    theory = Column(Text)
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    lesson_type = relationship("LessonType", back_populates="lessons")
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

# Модели для курсов
class CourseTypeCreate(BaseModel):
    name: str

class CourseTypeResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    name: str
    type_id: int
    description: str

class CourseResponse(BaseModel):
    id: int
    name: str
    type_id: int
    description: str
    author_id: int
    
    class Config:
        from_attributes = True

class CourseSimpleResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class CourseDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    author_id: int
    type_id: int
    
    class Config:
        from_attributes = True

# Модели для типов уроков
class LessonTypeCreate(BaseModel):
    name: str

class LessonTypeResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class LessonCreate(BaseModel):
    name: str
    type_id: int  # Добавлено поле для типа урока
    description: str
    theory: str

class LessonResponse(BaseModel):
    id: int
    name: str
    course_id: int
    type_id: int
    description: str
    theory: str
    
    class Config:
        from_attributes = True

class LessonSimpleResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

# Измененные модели для тестов
class TestCreate(BaseModel):
    question: str
    lesson_id: int
    answers: Dict[str, bool]  # JSON: {"1a": true, "2a": false}

class TestResponse(BaseModel):
    id: int
    lesson_id: int
    question: str
    answers: Dict[str, bool]
    
    class Config:
        from_attributes = True

class TestAnswerCheck(BaseModel):
    answers: Dict[str, bool]

class TestResultResponse(BaseModel):
    correct: bool
    message: str

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

# Новые эндпоинты для типов уроков

# 1) Добавить тип урока
@app.post("/courses/lessons/types/create", response_model=LessonTypeResponse)
async def create_lesson_type(
    lesson_type: LessonTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise_if_banned)
):
    db_lesson_type = LessonType(name=lesson_type.name)
    try:
        db.add(db_lesson_type)
        db.commit()
        db.refresh(db_lesson_type)
        return db_lesson_type
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Lesson type already exists")

# 2) Получить все типы курсов
@app.get("/courses/types", response_model=List[CourseTypeResponse])
async def get_all_course_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    course_types = db.query(CourseType).offset(skip).limit(limit).all()
    return course_types

# 3) Получить все типы уроков
@app.get("/courses/lessons/types", response_model=List[LessonTypeResponse])
async def get_all_lesson_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    lesson_types = db.query(LessonType).offset(skip).limit(limit).all()
    return lesson_types

# Существующие эндпоинты для подписок на курсы

# 4) Подписаться на курс
@app.post("/users/me/courses/{course_id}/add")
async def subscribe_to_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise_if_banned)
):
    # Проверяем существование курса
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Проверяем, не подписан ли уже пользователь
    if course in current_user.subscribed_courses:
        raise HTTPException(status_code=400, detail="Already subscribed to this course")
    
    # Добавляем подписку
    current_user.subscribed_courses.append(course)
    try:
        db.commit()
        return {"message": "Successfully subscribed to course"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error subscribing to course")

# 5) Получить мои курсы из подписок
@app.get("/users/me/courses", response_model=List[CourseSimpleResponse])
async def get_my_subscribed_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise_if_banned)
):
    return current_user.subscribed_courses

# 6) Получить курсы пользователя из подписок
@app.get("/users/{user_id}/courses", response_model=List[CourseSimpleResponse])
async def get_user_subscribed_courses(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.subscribed_courses

# 7) Получить все курсы
@app.get("/courses", response_model=List[CourseSimpleResponse])
async def get_all_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

# 8) Получить детальную информацию о курсе
@app.get("/courses/{course_id}", response_model=CourseDetailResponse)
async def get_course_detail(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course

# 9) Получить уроки курса
@app.get("/courses/{course_id}/lessons", response_model=List[LessonSimpleResponse])
async def get_course_lessons(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course.lessons

# 10) Получить детальную информацию об уроке
@app.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson_detail(
    course_id: int,
    lesson_id: int,
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id, 
        Lesson.course_id == course_id
    ).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    return lesson

# 11) Получить тест урока
@app.get("/courses/{course_id}/lessons/{lesson_id}/test", response_model=TestResponse)
async def get_lesson_test(
    course_id: int,
    lesson_id: int,
    db: Session = Depends(get_db)
):
    # Проверяем существование курса и урока
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id, 
        Lesson.course_id == course_id
    ).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Получаем тест урока
    test = db.query(Test).filter(Test.lesson_id == lesson_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found for this lesson")
    
    return test

# 12) Получить только правильные ответы на тест
@app.get("/courses/{course_id}/lessons/{lesson_id}/test/correct-answers")
async def get_correct_test_answers(
    course_id: int,
    lesson_id: int,
    db: Session = Depends(get_db)
):
    # Проверяем существование курса и урока
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id, 
        Lesson.course_id == course_id
    ).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Получаем тест урока
    test = db.query(Test).filter(Test.lesson_id == lesson_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found for this lesson")
    
    # Фильтруем правильные ответы из JSON
    correct_answers = {key: value for key, value in test.answers.items() if value is True}
    
    return {"correct_answers": correct_answers}

# 13) Проверить ответы пользователя на тест
@app.post("/courses/{course_id}/lessons/{lesson_id}/test/check", response_model=TestResultResponse)
async def check_test_answers(
    course_id: int,
    lesson_id: int,
    user_answers: TestAnswerCheck,
    db: Session = Depends(get_db)
):
    # Проверяем существование курса и урока
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id, 
        Lesson.course_id == course_id
    ).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Получаем тест урока
    test = db.query(Test).filter(Test.lesson_id == lesson_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found for this lesson")
    
    # Получаем правильные ответы из теста
    correct_answers = test.answers
    
    # Сравниваем ответы пользователя с правильными
    if user_answers.answers == correct_answers:
        return TestResultResponse(correct=True, message="All answers are correct!")
    else:
        return TestResultResponse(correct=False, message="Some answers are incorrect")

# Существующие эндпоинты создания (с изменениями для тестов)
@app.post("/courses/types/create", response_model=CourseTypeResponse)
async def create_course_type(
    course_type: CourseTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise_if_banned)
):
    db_course_type = CourseType(name=course_type.name)
    try:
        db.add(db_course_type)
        db.commit()
        db.refresh(db_course_type)
        return db_course_type
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Course type already exists")

@app.post("/courses/create", response_model=CourseResponse)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise_if_banned)
):
    course_type = db.query(CourseType).filter(CourseType.id == course.type_id).first()
    if not course_type:
        raise HTTPException(status_code=404, detail="Course type not found")
    
    db_course = Course(
        name=course.name,
        type_id=course.type_id,
        description=course.description,
        author_id=current_user.id
    )
    try:
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        return db_course
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating course")

@app.post("/courses/{course_id}/lessons/create", response_model=LessonResponse)
async def create_lesson(
    course_id: int,
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise_if_banned)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Проверяем существование типа урока
    lesson_type = db.query(LessonType).filter(LessonType.id == lesson.type_id).first()
    if not lesson_type:
        raise HTTPException(status_code=404, detail="Lesson type not found")
    
    if course.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add lessons to this course")
    
    db_lesson = Lesson(
        name=lesson.name,
        course_id=course_id,
        type_id=lesson.type_id,  # Добавляем тип урока
        description=lesson.description,
        theory=lesson.theory
    )
    try:
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        return db_lesson
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating lesson")

# Измененный эндпоинт создания теста
@app.post("/courses/{course_id}/lessons/tests/create", response_model=TestResponse)
async def create_test(
    course_id: int,
    test: TestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_raise_if_banned)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    lesson = db.query(Lesson).filter(Lesson.id == test.lesson_id, Lesson.course_id == course_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found in this course")
    
    if course.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add tests to this course")
    
    db_test = Test(
        lesson_id=test.lesson_id,
        question=test.question,
        answers=test.answers  # Сохраняем JSON с ответами
    )
    try:
        db.add(db_test)
        db.commit()
        db.refresh(db_test)
        return db_test
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating test")