from pydantic import BaseModel
from typing import Dict


class TestResponse(BaseModel):
    id: int
    lesson_id: int
    question: str
    answers: Dict[str, bool]
    
    class Config:
        from_attributes = True