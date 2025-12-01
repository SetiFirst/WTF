from pydantic import BaseModel
from typing import Dict


class TestAnswerCheck(BaseModel):
    answers: Dict[str, bool]