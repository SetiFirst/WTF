from pydantic import BaseModel
from typing import Dict


class TestUpdate(BaseModel):
    question: str | None = None
    answers: Dict[str, bool] | None = None