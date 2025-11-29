from typing import List
from fastapi import HTTPException, Depends, Request
from api_tools import app
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from base.user import User
from base.course import Course
from base.report import CourseReport
from base.help import CourseHelp
from db import init_db, get_db
from base_model.coursereportcreate import CourseReportCreate
from base_model.coursereportresponse import CourseReportResponse
from base_model.coursehelpcreate import CourseHelpCreate
from base_model.coursehelpresponse import CourseHelpResponse
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

@app.get("/courses/{course_id}/reports", response_model=List[CourseReportResponse])
async def get_course_reports(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return course.reports

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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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