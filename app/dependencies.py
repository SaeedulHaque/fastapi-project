from fastapi import Depends, HTTPException, Query, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app import models, service
from app.database import get_db
from app.errors import NotFoundError

security = HTTPBasic()


def log_request(request: Request):
    print(f"{request.method} {request.url.path}")


class Pagination:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
    ):
        self.skip = skip
        self.limit = limit


def get_student_or_404(
    student_id: int, db: Session = Depends(get_db)
) -> models.Student:
    student = service.get_student(db, student_id)
    if student is None:
        raise NotFoundError("Student")
    return student


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    user = service.authenticate(db, credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
