from pydantic import BaseModel


class LessonTypeResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True