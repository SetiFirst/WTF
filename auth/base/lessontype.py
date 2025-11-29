from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from base.base import Base


class LessonType(Base):
    __tablename__ = "LessonTypes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True)
    
    # Relationships
    lessons = relationship("Lesson", back_populates="lesson_type")