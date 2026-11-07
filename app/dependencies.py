from fastapi import Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, service
from app.database import get_db
from app.errors import (
    AppError,
    FileTooLargeError,
    NotFoundError,
    UnsupportedFileTypeError,
)
from app.uploads import ALLOWED_TYPES, MAX_UPLOAD_BYTES, UploadedFile

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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


async def get_student_or_404(
    student_id: int, db: AsyncSession = Depends(get_db)
) -> models.Student:
    student = await service.get_student(db, student_id)
    if student is None:
        raise NotFoundError("Student")
    return student


async def get_file_or_404(
    file_id: int,
    student: models.Student = Depends(get_student_or_404),
    db: AsyncSession = Depends(get_db),
) -> models.StudentFile:
    record = await service.get_student_file(db, student.id, file_id)
    if record is None:
        raise NotFoundError("File")
    return record


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> models.User:
    user = await service.user_from_token(db, token)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(*roles: str):
    def checker(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Not allowed for your role")
        return user

    return checker


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def read_upload(file: UploadFile = File(...)) -> UploadedFile:
    """Check an upload and read it into memory, up to the size limit."""
    extension = ALLOWED_TYPES.get(file.content_type or "")
    if extension is None:
        raise UnsupportedFileTypeError(", ".join(sorted(ALLOWED_TYPES)))
    # Read one byte more than allowed. If it arrives, the file is too big.
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise FileTooLargeError(MAX_UPLOAD_BYTES)
    if not data:
        raise AppError("The file is empty")
    # Keep only the last part of the name, so "../../x.png" becomes "x.png"
    name = (file.filename or "").replace("\\", "/").split("/")[-1][:255] or "file"
    return UploadedFile(
        original_name=name,
        content_type=file.content_type,
        extension=extension,
        data=data,
    )
