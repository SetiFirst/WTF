from pydantic import BaseModel


class CourseReportCreate(BaseModel):
    question: str