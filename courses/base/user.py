from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from base.base import Base
from base.coursetype import CourseType


class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(Text, unique=True)
    email = Column(Text, nullable=True)
    hashed_password = Column(Text)
    
    # Relationships
    courses = relationship("Course", back_populates="author")
    reports = relationship("CourseReport", back_populates="author")
    subscribed_courses = relationship("UserCourseSubscription", back_populates="user")