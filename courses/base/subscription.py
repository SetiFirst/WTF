from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from base.base import Base


class UserCourseSubscription(Base):
    __tablename__ = 'user_course_subscription'
    user_id = Column(Integer, ForeignKey('Users.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('Courses.id'), primary_key=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    course = relationship("Course", back_populates="subscriptions")
