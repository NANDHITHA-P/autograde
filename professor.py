from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from pgc.pgc import check_plagiarism  # Ensure this is the correct path to your plagiarism checking module
import os
import shutil
from typing import List

router = APIRouter()

# Directory for uploading files
UPLOAD_FOLDER = "uploads/plagiarism"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/create_assignment", tags=["Professor"])
async def create_assignment(
    question_pdf: UploadFile = File(...),
    key_pdf: UploadFile = File(...),
    technical: bool = False,
    grammar: bool = False,
    spelling: bool = False,
    total_marks: int = 100,
    db: Session = Depends(get_db),
):
    """Endpoint for creating an assignment with question and key PDFs."""
    try:
        # Save the question PDF
        question_pdf_path = os.path.join(UPLOAD_FOLDER, question_pdf.filename)
        with open(question_pdf_path, "wb") as buffer:
            shutil.copyfileobj(question_pdf.file, buffer)

        # Save the key PDF
        key_pdf_path = os.path.join(UPLOAD_FOLDER, key_pdf.filename)
        with open(key_pdf_path, "wb") as buffer:
            shutil.copyfileobj(key_pdf.file, buffer)

        # Save assignment details to the database
        new_assignment = Assignment(
            question_pdf=question_pdf_path,
            key_pdf=key_pdf_path,
            technical=technical,
            grammar=grammar,
            spelling=spelling,
            total_marks=total_marks
        )
        db.add(new_assignment)
        db.commit()

        return {"message": "Assignment created successfully", "assignment_id": new_assignment.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating assignment: {e}")


@router.post("/check_plagiarism", tags=["Professor"])
async def check_plagiarism_endpoint(
    files: List[UploadFile] = File(...),
):
    """Endpoint to check plagiarism among selected files."""
    file_paths = []

    try:
        # Save each uploaded file to the uploads directory
        for file in files:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_paths.append(file_path)

        # Run plagiarism check
        plagiarism_report = check_plagiarism(file_paths)  # Adjust function to handle multiple file paths
        return {"plagiarism_report": plagiarism_report}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during plagiarism check: {e}")
