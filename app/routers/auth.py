from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, service
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
async def register(data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # the client never chooses its own role: create_user defaults to "viewer"
    return await service.create_user(db, data.email, data.password)


@router.post("/login", response_model=schemas.Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    # the form field is called "username"; in this project it holds the email
    token = await service.login(db, form.username, form.password)
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
async def read_me(user: models.User = Depends(get_current_user)):
    return user
