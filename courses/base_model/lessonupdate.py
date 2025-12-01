from pydantic import BaseModel


class LessonUpdate(BaseModel):
    name: str | None = None
    type_id: int | None = None
    description: str | None = None
    theory: str | None = None