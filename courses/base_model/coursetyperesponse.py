from pydantic import BaseModel


class CourseTypeResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True