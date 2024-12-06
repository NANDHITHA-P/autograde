from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer)
    question_pdf = Column(String)
    key_pdf = Column(String)
    technical = Column(Boolean)
    grammar = Column(Boolean)
    spelling = Column(Boolean)
    total_marks = Column(Integer)

class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    marks_obtained = Column(Integer)
    percentage = Column(Integer)

    assignment = relationship("Assignment")
