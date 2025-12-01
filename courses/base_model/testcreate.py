from pydantic import BaseModel
from typing import Dict


class TestCreate(BaseModel):
    question: str
    lesson_id: int
    answers: Dict[str, bool]