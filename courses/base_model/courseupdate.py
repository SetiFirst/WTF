from pydantic import BaseModel


class CourseUpdate(BaseModel):
    name: str | None = None
    type_id: int | None = None
    description: str | None = None