from pydantic import BaseModel


class CourseTypeCreate(BaseModel):
    name: str