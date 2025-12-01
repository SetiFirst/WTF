from pydantic import BaseModel


class CourseCreate(BaseModel):
    name: str
    type_id: int
    description: str