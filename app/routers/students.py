from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas, service
from app.database import get_db
from app.dependencies import (
    Pagination,
    get_current_user,
    get_student_or_404,
    log_request,
    require_admin,
)

router = APIRouter(
    prefix="/students",
    tags=["students"],
    dependencies=[Depends(log_request), Depends(get_current_user)],
    responses={
        401: {"model": schemas.ErrorOut, "description": "Missing or wrong credentials"},
        404: {"model": schemas.ErrorOut, "description": "Student not found"},
        409: {"model": schemas.ErrorOut, "description": "Email already exists"},
    },
)


# CREATE (admin only)
@router.post(
    "",
    response_model=schemas.StudentOut,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return service.create_student(db, student)


# READ: list, with paging and a name search (any logged-in user)
@router.get("", response_model=schemas.StudentPage)
def list_students(
    page: Pagination = Depends(),
    q: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_students(db, page.skip, page.limit, q)


# READ: a short list, same table, fewer fields
# (declared before /{student_id}, or "directory" would be read as an id)
@router.get("/directory", response_model=list[schemas.StudentSummary])
def student_directory(db: Session = Depends(get_db)):
    return service.student_directory(db)


# READ: one
@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student: models.Student = Depends(get_student_or_404)):
    return student
