from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas, service
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    # the client never chooses its own role: create_user defaults to "viewer"
    return service.create_user(db, data.email, data.password)


@router.get("/me", response_model=schemas.UserOut)
def read_me(user: models.User = Depends(get_current_user)):
    return user
