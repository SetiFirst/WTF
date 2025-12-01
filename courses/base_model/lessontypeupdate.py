from pydantic import BaseModel


class LessonTypeUpdate(BaseModel):
    name: str | None = None