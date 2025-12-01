from pydantic import BaseModel


class CourseResponse(BaseModel):
    id: int
    name: str
    type_id: int
    description: str
    author_id: int
    
    class Config:
        from_attributes = True