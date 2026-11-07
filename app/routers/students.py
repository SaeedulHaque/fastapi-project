from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, service
from app.database import get_db
from app.dependencies import (
    Pagination,
    get_current_user,
    get_file_or_404,
    get_student_or_404,
    log_request,
    read_upload,
    require_admin,
    require_role,
)
from app.errors import NotFoundError
from app.uploads import UploadedFile

router = APIRouter(
    prefix="/students",
    tags=["students"],
    dependencies=[Depends(log_request), Depends(get_current_user)],
    responses={
        401: {"model": schemas.ErrorOut, "description": "Missing or invalid token"},
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
async def create_student(
    student: schemas.StudentCreate, db: AsyncSession = Depends(get_db)
):
    return await service.create_student(db, student)


# READ: list, with paging and a name search (any logged-in user)
@router.get("", response_model=schemas.StudentPage)
async def list_students(
    page: Pagination = Depends(),
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await service.list_students(db, page.skip, page.limit, q)


# READ: a short list, same table, fewer fields
# (declared before /{student_id}, or "directory" would be read as an id)
@router.get("/directory", response_model=list[schemas.StudentSummary])
async def student_directory(db: AsyncSession = Depends(get_db)):
    return await service.student_directory(db)


# READ: one
@router.get("/{student_id}", response_model=schemas.StudentOut)
async def get_student(student: models.Student = Depends(get_student_or_404)):
    return student


# UPDATE: replace the whole record (admin only)
@router.put(
    "/{student_id}",
    response_model=schemas.StudentOut,
    dependencies=[Depends(require_admin)],
)
async def replace_student(
    data: schemas.StudentCreate,
    student: models.Student = Depends(get_student_or_404),
    db: AsyncSession = Depends(get_db),
):
    return await service.replace_student(db, student, data)


# UPDATE: change only the fields that were sent (admin or teacher)
@router.patch(
    "/{student_id}",
    response_model=schemas.StudentOut,
    dependencies=[Depends(require_role("admin", "teacher"))],
)
async def update_student(
    data: schemas.StudentUpdate,
    student: models.Student = Depends(get_student_or_404),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_student(db, student, data)


# DELETE (admin only)
@router.delete(
    "/{student_id}",
    status_code=204,
    dependencies=[Depends(require_admin)],
)
async def delete_student(
    student: models.Student = Depends(get_student_or_404),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_student(db, student)


# FILES: upload one file for a student (admin or teacher)
@router.post(
    "/{student_id}/files",
    response_model=schemas.StudentFileOut,
    status_code=201,
    dependencies=[Depends(require_role("admin", "teacher"))],
    responses={
        413: {"model": schemas.ErrorOut, "description": "File is too large"},
        415: {"model": schemas.ErrorOut, "description": "File type is not allowed"},
    },
)
async def upload_student_file(
    upload: UploadedFile = Depends(read_upload),
    student: models.Student = Depends(get_student_or_404),
    db: AsyncSession = Depends(get_db),
):
    return await service.add_student_file(db, student, upload)


# FILES: list a student's files (any logged-in user)
@router.get("/{student_id}/files", response_model=list[schemas.StudentFileOut])
async def list_student_files(
    student: models.Student = Depends(get_student_or_404),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_student_files(db, student)


# FILES: download one (any logged-in user)
@router.get(
    "/{student_id}/files/{file_id}",
    response_class=FileResponse,
    responses={404: {"model": schemas.ErrorOut, "description": "Student or file not found"}},
)
async def download_student_file(record: models.StudentFile = Depends(get_file_or_404)):
    if not await service.file_exists(record):
        raise NotFoundError("File")  # a row without a file on disk
    return FileResponse(
        service.file_path(record),
        media_type=record.content_type,
        filename=record.original_name,
    )
