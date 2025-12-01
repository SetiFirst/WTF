
from typing import List
from fastapi import HTTPException, Depends, Request
from api_tools import app
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from base.course import Course
from base.coursetype import CourseType
from base.lesson import Lesson
from base.test import Test
from base.user import User
from base.lessontype import LessonType
from db import init_db, get_db
from base_model.coursecreate import CourseCreate
from base_model.coursedetailresponse import CourseDetailResponse
from base_model.courseresponse import CourseResponse
from base_model.coursesimpleresponse import CourseSimpleResponse
from base_model.coursetypecreate import CourseTypeCreate
from base_model.coursetyperesponse import CourseTypeResponse
from base_model.lessoncreate import LessonCreate
from base_model.lessonresponse import LessonResponse
from base_model.lessonsimpleresponse import LessonSimpleResponse
from base_model.lessontypecreate import LessonTypeCreate
from base_model.lessontyperesponse import LessonTypeResponse
from base_model.testanswercheck import TestAnswerCheck
from base_model.testcreate import TestCreate
from base_model.testresponse import TestResponse
from base_model.testresultresponse import TestResultResponse
from base_model.coursetypeupdate import CourseTypeUpdate
from base_model.courseupdate import CourseUpdate
from base_model.lessontypeupdate import LessonTypeUpdate
from base_model.lessonupdate import LessonUpdate
from base_model.testupdate import TestUpdate
from db_tools import get_current_user


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

@app.post("/courses/lessons/types/create", response_model=LessonTypeResponse)
async def create_lesson_type(
    lesson_type: LessonTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

@app.get("/courses/types", response_model=List[CourseTypeResponse])
async def get_all_course_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    course_types = db.query(CourseType).offset(skip).limit(limit).all()
    return course_types

@app.get("/courses/lessons/types", response_model=List[LessonTypeResponse])
async def get_all_lesson_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    lesson_types = db.query(LessonType).offset(skip).limit(limit).all()
    return lesson_types

@app.post("/users/me/courses/{course_id}/add")
async def subscribe_to_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course in current_user.subscribed_courses:
        raise HTTPException(status_code=400, detail="Already subscribed to this course")
    current_user.subscribed_courses.append(course)
    try:
        db.commit()
        return {"message": "Successfully subscribed to course"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error subscribing to course")

@app.get("/users/me/courses", response_model=List[CourseSimpleResponse])
async def get_my_subscribed_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return current_user.subscribed_courses

@app.get("/users/{user_id}/courses", response_model=List[CourseSimpleResponse])
async def get_user_subscribed_courses(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.subscribed_courses

@app.get("/courses", response_model=List[CourseSimpleResponse])
async def get_all_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@app.get("/courses/{course_id}", response_model=CourseDetailResponse)
async def get_course_detail(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.get("/courses/{course_id}/lessons", response_model=List[LessonSimpleResponse])
async def get_course_lessons(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.lessons

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

@app.get("/courses/{course_id}/lessons/{lesson_id}/test", response_model=TestResponse)
async def get_lesson_test(
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
    test = db.query(Test).filter(Test.lesson_id == lesson_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found for this lesson")
    return test

@app.get("/courses/{course_id}/lessons/{lesson_id}/test/correct-answers")
async def get_correct_test_answers(
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
    test = db.query(Test).filter(Test.lesson_id == lesson_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found for this lesson")
    correct_answers = {key: value for key, value in test.answers.items() if value is True}
    return {"correct_answers": correct_answers}
@app.post("/courses/{course_id}/lessons/{lesson_id}/test/check", response_model=TestResultResponse)
async def check_test_answers(
    course_id: int,
    lesson_id: int,
    user_answers: TestAnswerCheck,
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id, 
        Lesson.course_id == course_id
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    test = db.query(Test).filter(Test.lesson_id == lesson_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found for this lesson")
    correct_answers = test.answers
    if user_answers.answers == correct_answers:
        return TestResultResponse(correct=True, message="All answers are correct!")
    else:
        return TestResultResponse(correct=False, message="Some answers are incorrect")

@app.post("/courses/types/create", response_model=CourseTypeResponse)
async def create_course_type(
    course_type: CourseTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
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

@app.post("/courses/{course_id}/lessons/tests/create", response_model=TestResponse)
async def create_test(
    course_id: int,
    test: TestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

@app.patch("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this course")
    if course_update.type_id is not None:
        course_type = db.query(CourseType).filter(CourseType.id == course_update.type_id).first()
        if not course_type:
            raise HTTPException(status_code=404, detail="Course type not found")
    update_data = course_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    try:
        db.commit()
        db.refresh(course)
        return course
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating course")

@app.patch("/courses/types/{type_id}", response_model=CourseTypeResponse)
async def update_course_type(
    type_id: int,
    course_type_update: CourseTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course_type = db.query(CourseType).filter(CourseType.id == type_id).first()
    if not course_type:
        raise HTTPException(status_code=404, detail="Course type not found")
    update_data = course_type_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course_type, field, value)
    try:
        db.commit()
        db.refresh(course_type)
        return course_type
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Course type with this name already exists")

@app.patch("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    course_id: int,
    lesson_id: int,
    lesson_update: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id, 
        Lesson.course_id == course_id
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    if course.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update lessons in this course")
    if lesson_update.type_id is not None:
        lesson_type = db.query(LessonType).filter(LessonType.id == lesson_update.type_id).first()
        if not lesson_type:
            raise HTTPException(status_code=404, detail="Lesson type not found")
    update_data = lesson_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lesson, field, value)
    try:
        db.commit()
        db.refresh(lesson)
        return lesson
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating lesson")
@app.patch("/courses/lessons/types/{type_id}", response_model=LessonTypeResponse)
async def update_lesson_type(
    type_id: int,
    lesson_type_update: LessonTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lesson_type = db.query(LessonType).filter(LessonType.id == type_id).first()
    if not lesson_type:
        raise HTTPException(status_code=404, detail="Lesson type not found")
    update_data = lesson_type_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lesson_type, field, value)
    try:
        db.commit()
        db.refresh(lesson_type)
        return lesson_type
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Lesson type with this name already exists")
@app.patch("/courses/{course_id}/lessons/{lesson_id}/test", response_model=TestResponse)
async def update_test(
    course_id: int,
    lesson_id: int,
    test_update: TestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id, 
        Lesson.course_id == course_id
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    test = db.query(Test).filter(Test.lesson_id == lesson_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found for this lesson")
    if course.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update tests in this course")
    update_data = test_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test, field, value)
    try:
        db.commit()
        db.refresh(test)
        return test
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating test")
