from pydantic import BaseModel


class CourseDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    author_id: int
    type_id: int
    
    class Config:
        from_attributes = True