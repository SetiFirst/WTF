from pydantic import BaseModel


class CourseReportResponse(BaseModel):
    id: int
    course_id: int
    author_id: int
    question: str
    
    class Config:
        from_attributes = True