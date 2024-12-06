from fastapi import APIRouter, UploadFile, File, Form, Depends
from utils.file_processing import extract_text_from_pdf
from utils.grading import grade_assignment
from sqlalchemy.orm import Session
from database import get_db
from models import Assignment, Result
import shutil
import os

router = APIRouter()

UPLOAD_FOLDER = "uploads/student_submissions"

# Ensure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/submit_assignment", tags=["Student"])
def submit_assignment(
    assignment_pdf: UploadFile = File(...),
    assignment_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Save the student's assignment PDF to the system
    assignment_pdf_path = os.path.join(UPLOAD_FOLDER, assignment_pdf.filename)
    
    with open(assignment_pdf_path, "wb") as buffer:
        shutil.copyfileobj(assignment_pdf.file, buffer)
    
    # Extract text from the student's assignment PDF
    student_text = extract_text_from_pdf(assignment_pdf_path)
    
    # Retrieve the corresponding key PDF for the assignment from the database
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    print(assignment)
    key_text = extract_text_from_pdf(assignment.key_pdf)
    
    technical = assignment.technical
    grammar = assignment.grammar
    spelling = assignment.spelling
    
    #Test cases
    if(technical and grammar and spelling):
        x = 8
    elif(technical and not grammar and not spelling):
        x = 2
    elif(grammar and not technical and not spelling):
        x = 3
    elif(spelling and not technical and not grammar):
        x = 4
    elif(technical and grammar and not spelling):
        x = 5
    elif(technical and spelling and not grammar):
        x = 6
    elif(grammar and spelling and not technical):
        x = 7
    else:
        x = 1
    
    marks_obtained = grade_assignment(student_text, key_text, assignment.total_marks, x)
    percentage = (marks_obtained / assignment.total_marks) * 100
    
    # Save the result in the database
    new_result = Result(
        student_id=1,  # Student ID would be dynamic in a real app
        assignment_id=assignment_id,
        marks_obtained=marks_obtained,
        percentage=percentage
    )
    db.add(new_result)
    db.commit()
    
    return {"marks_obtained": marks_obtained, "percentage": percentage}
