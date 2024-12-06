from fastapi import FastAPI
from routers import professor, student, plagiarism
from database import Base, engine

# Create the SQLite database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers
app.include_router(professor.router, prefix="/professor")
app.include_router(student.router, prefix="/student")
app.include_router(plagiarism.router, prefix="/plagiarism", tags=["plagiarism"])

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
