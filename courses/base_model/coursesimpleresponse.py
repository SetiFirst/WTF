from pydantic import BaseModel


class CourseSimpleResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True