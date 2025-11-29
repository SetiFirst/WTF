from pydantic import BaseModel


class TestResultResponse(BaseModel):
    correct: bool
    message: str