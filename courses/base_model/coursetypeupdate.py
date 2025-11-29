from pydantic import BaseModel


class CourseTypeUpdate(BaseModel):
    name: str | None = None