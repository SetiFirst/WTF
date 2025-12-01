from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from base.base import Base


class CourseHelp(Base):
    __tablename__ = "CourseHelp"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("CourseReports.id"))
    answer = Column(Text)
    
    # Relationships
    report = relationship("CourseReport", back_populates="help_responses")