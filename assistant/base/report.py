from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from base.base import Base


class CourseReport(Base):
    __tablename__ = "CourseReports"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("Courses.id"))
    author_id = Column(Integer, ForeignKey("Users.id"))
    question = Column(Text)
    
    # Relationships
    course = relationship("Course", back_populates="reports")
    author = relationship("User", back_populates="reports")
    help_responses = relationship("CourseHelp", back_populates="report")