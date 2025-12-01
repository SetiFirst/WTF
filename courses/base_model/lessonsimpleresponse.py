from pydantic import BaseModel


class LessonSimpleResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True