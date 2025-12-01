from sqlalchemy import Column, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from base.base import Base


class Test(Base):
    __tablename__ = "Tests"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("Lessons.id"))
    question = Column(Text)
    answers = Column(JSON)  # Изменено: теперь храним ответы в формате JSON
    
    # Relationships
    lesson = relationship("Lesson", back_populates="tests")