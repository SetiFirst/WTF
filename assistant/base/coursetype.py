from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from base.base import Base


class CourseType(Base):
    __tablename__ = "CourseTypes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True)
    
    # Relationships
    courses = relationship("Course", back_populates="course_type")