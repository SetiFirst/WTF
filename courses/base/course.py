from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from base.base import Base


class Course(Base):
    __tablename__ = "Courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True)
    type_id = Column(Integer, ForeignKey("CourseTypes.id"))
    description = Column(Text)
    author_id = Column(Integer, ForeignKey("Users.id"))
    
    # Relationships
    course_type = relationship("CourseType", back_populates="courses")
    author = relationship("User", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course")
    reports = relationship("CourseReport", back_populates="course")
    subscribers = relationship("UserCourseSubscription", back_populates="course")