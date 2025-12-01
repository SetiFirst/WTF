from pydantic import BaseModel


class CourseHelpResponse(BaseModel):
    id: int
    report_id: int
    answer: str
    
    class Config:
        from_attributes = True