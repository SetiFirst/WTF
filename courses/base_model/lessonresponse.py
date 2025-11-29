from pydantic import BaseModel


class LessonResponse(BaseModel):
    id: int
    name: str
    course_id: int
    type_id: int
    description: str
    theory: str
    
    class Config:
        from_attributes = True