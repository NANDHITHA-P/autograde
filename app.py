import os
import shutil
import streamlit as st
from sqlalchemy.orm import Session
from utils.file_processing import extract_text_from_pdf
from utils.grading import grade_assignment
from database import get_db
from models import Assignment, Result
from pgc.pgc import check_plagiarism  # Ensure correct import
from typing import List

# Folder setup
UPLOAD_FOLDER_ASSIGNMENTS = "uploads/assignments"
UPLOAD_FOLDER_SUBMISSIONS = "uploads/student_submissions"
os.makedirs(UPLOAD_FOLDER_ASSIGNMENTS, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_SUBMISSIONS, exist_ok=True)

# Streamlit UI
st.title("Subjective Assignment Grading System")
st.sidebar.header("Navigation")
panel = st.sidebar.radio("Select Panel", ["Professor", "Student"])

# Streamlit: Database session handling within the context of user interaction
@st.cache_resource
def get_database_session():
    return next(get_db())  # Assuming get_db() is a generator function returning a session

# Function to check plagiarism
def check_plagiarism_function(files):
    file_paths = []
    file_names = []
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER_SUBMISSIONS, file.name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file, buffer)  # Save file locally
        file_paths.append(file_path)
        file_names.append(file.name)  # Store the name of the file

    try:
        report = check_plagiarism(file_paths)  # Assuming check_plagiarism works with file paths
        # Assuming report is a list of dictionaries with 'similarity', 'file_1', 'file_2' keys
        return report, file_names  # Return both report and file names
    except Exception as e:
        return f"Error during plagiarism check: {e}", []

# Main logic for Professor and Student Panels
if panel == "Professor":
    st.header("Professor Panel: Upload 2 files to check for Plagiarism")
    
    # File upload for plagiarism check
    plagiarism_files = st.file_uploader("Upload Files for Plagiarism Check", type=["pdf"], accept_multiple_files=True)
    
    if st.button("Check Plagiarism"):
        if plagiarism_files:
            try:
                report, file_names = check_plagiarism_function(plagiarism_files)
                if isinstance(report, list):  # Assuming the report is a list of dictionaries with plagiarism data
                    st.write("Plagiarism Report:")
                    # Format and display results in a more readable way
                    for item in report:
                        file_1_name = file_names[0] if item['file_1'] == file_names[0] else file_names[1]
                        file_2_name = file_names[1] if item['file_2'] == file_names[1] else file_names[0]
                        
                        st.subheader(f"Plagiarism Report between **{file_1_name}** and **{file_2_name}**")
                        st.markdown(f"**Similarity**: {item['similarity']}%")
                else:
                    st.error(f"Error during plagiarism check: {report}")
            except Exception as e:
                st.error(f"Error during plagiarism check: {e}")
        else:
            st.error("Please upload files to check for plagiarism.")

    st.header("Professor Panel: Create Assignment")
    
    # File upload and form inputs
    question_pdf = st.file_uploader("Upload Question PDF", type=["pdf"])
    key_pdf = st.file_uploader("Upload Key PDF", type=["pdf"])
    total_marks = st.number_input("Enter Total Marks", min_value=1, step=1)
    technical = st.checkbox("Include Technical Content")
    grammar = st.checkbox("Include Grammar")
    spelling = st.checkbox("Include Spelling")

    if st.button("Create Assignment"):
        if question_pdf and key_pdf:
            # Save files
            question_pdf_path = os.path.join(UPLOAD_FOLDER_ASSIGNMENTS, question_pdf.name)
            key_pdf_path = os.path.join(UPLOAD_FOLDER_ASSIGNMENTS, key_pdf.name)
            
            with open(question_pdf_path, "wb") as buffer:
                shutil.copyfileobj(question_pdf, buffer)
            with open(key_pdf_path, "wb") as buffer:
                shutil.copyfileobj(key_pdf, buffer)
            
            # Get database session
            db: Session = get_database_session()

            # Save assignment details in the database
            new_assignment = Assignment(
                question_pdf=question_pdf_path,
                key_pdf=key_pdf_path,
                technical=technical,
                grammar=grammar,
                spelling=spelling,
                total_marks=total_marks
            )
            
            try:
                db.add(new_assignment)
                db.commit()
                st.success(f"Assignment created successfully! Assignment ID: {new_assignment.id}")
            except Exception as e:
                db.rollback()
                st.error(f"Error adding assignment: {e}")
        else:
            st.error("Please upload both Question and Key PDFs.")

elif panel == "Student":
    st.header("Student Panel: Submit Assignment")
    
    # File upload and form inputs
    assignment_pdf = st.file_uploader("Upload Assignment PDF", type=["pdf"])
    assignment_id = st.number_input("Enter Assignment ID", min_value=1, step=1)

    if st.button("Submit Assignment"):
        if assignment_pdf:
            # Save student submission
            assignment_pdf_path = os.path.join(UPLOAD_FOLDER_SUBMISSIONS, assignment_pdf.name)
            with open(assignment_pdf_path, "wb") as buffer:
                shutil.copyfileobj(assignment_pdf, buffer)

            # Extract text from PDF
            student_text = extract_text_from_pdf(assignment_pdf_path)
            
            # Get database session
            db: Session = get_database_session()

            # Retrieve the assignment details
            assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
            if not assignment:
                st.error("Assignment ID not found.")
            else:
                key_text = extract_text_from_pdf(assignment.key_pdf)
                technical = assignment.technical
                grammar = assignment.grammar
                spelling = assignment.spelling

                # Determine weight x for grading
                if technical and grammar and spelling:
                    x = 8
                elif technical and not grammar and not spelling:
                    x = 2
                elif grammar and not technical and not spelling:
                    x = 3
                elif spelling and not technical and not grammar:
                    x = 4
                elif technical and grammar and not spelling:
                    x = 5
                elif technical and spelling and not grammar:
                    x = 6
                elif grammar and spelling and not technical:
                    x = 7
                else:
                    x = 1

                # Grade the assignment
                marks_obtained = grade_assignment(student_text, key_text, assignment.total_marks, x)
                percentage = (marks_obtained / assignment.total_marks) * 100
                
                # Save the result in the database
                new_result = Result(
                    student_id=1,  # Example student ID
                    assignment_id=assignment_id,
                    marks_obtained=marks_obtained,
                    percentage=percentage
                )
                db.add(new_result)
                db.commit()

                st.success(f"Marks Obtained: {marks_obtained}")
                st.info(f"Percentage: {percentage:.2f}%")
