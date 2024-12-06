from pydantic import BaseModel

class AssignmentUploadSchema(BaseModel):
    question_pdf: str
    key_pdf: str
    technical: bool
    grammar: bool
    spelling: bool
    total_marks: int
    

class AssignmentResultSchema(BaseModel):
    student_id: int
    assignment_id: int
    marks_obtained: int
    percentage: float
