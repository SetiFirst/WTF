from pydantic import BaseModel


class CourseHelpCreate(BaseModel):
    answer: str