from pydantic import BaseModel


class LessonCreate(BaseModel):
    name: str
    type_id: int
    description: str
    theory: str