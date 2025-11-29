from pydantic import BaseModel


class LessonTypeCreate(BaseModel):
    name: str