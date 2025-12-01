from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from base.base import Base


class Lesson(Base):
    __tablename__ = "Lessons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    course_id = Column(Integer, ForeignKey("Courses.id"))
    description = Column(Text)
    theory = Column(Text)
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    tests = relationship("Test", back_populates="lesson")