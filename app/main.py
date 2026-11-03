from fastapi import FastAPI

from app.errors import register_error_handlers
from app.routers import auth, students

app = FastAPI(title="Student API")

register_error_handlers(app)
app.include_router(auth.router)
app.include_router(students.router)


@app.get("/")
def root():
    return {"message": "Student API is running"}