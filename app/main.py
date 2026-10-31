from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app import models
from app.database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="My API", description="A simple API built with FastAPI")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

#POST
@app.post("/students/")
def create_student(student: schemas.studentcreate, db: Session = Depends(get_db)):
    db_student = models.Student(name=student.name, age=student.age, email=student.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

#GET
@app.get("/students/", response_model=list[schemas.studentoutput])
def list_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return students