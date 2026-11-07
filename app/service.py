import asyncio
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app import models, repository, schemas, security, storage
from app.uploads import UploadedFile


async def create_student(db: AsyncSession, data: schemas.StudentCreate) -> models.Student:
    values = data.model_dump()
    values["email"] = values["email"].strip().lower()  # one email, one spelling
    return await repository.add_student(db, models.Student(**values))


async def list_students(
    db: AsyncSession, skip: int, limit: int, q: str | None = None
) -> dict:
    return {
        "total": await repository.count_students(db, q),
        "skip": skip,
        "limit": limit,
        "items": await repository.list_students(db, skip, limit, q),
    }


async def student_directory(db: AsyncSession) -> list[models.Student]:
    return await repository.list_students_by_name(db)


async def get_student(db: AsyncSession, student_id: int) -> models.Student | None:
    return await repository.get_student(db, student_id)


async def replace_student(
    db: AsyncSession, student: models.Student, data: schemas.StudentCreate
) -> models.Student:
    changes = data.model_dump()
    changes["email"] = changes["email"].strip().lower()
    return await repository.update_student(db, student, changes)


async def update_student(
    db: AsyncSession, student: models.Student, data: schemas.StudentUpdate
) -> models.Student:
    changes = data.model_dump(exclude_unset=True)
    if "email" in changes:
        changes["email"] = changes["email"].strip().lower()
    return await repository.update_student(db, student, changes)


async def delete_student(db: AsyncSession, student: models.Student) -> None:
    # The database deletes the file rows (ON DELETE CASCADE). The files on disk are ours to remove.
    stored_names = await repository.list_stored_names(db, student.id)
    await repository.delete_student(db, student)
    for stored_name in stored_names:
        await storage.delete(stored_name)


async def create_user(
    db: AsyncSession, email: str, password: str, role: str = "viewer"
) -> models.User:
    # Argon2 is slow on purpose and blocks the thread it runs in. Keep it off the event loop.
    hashed = await asyncio.to_thread(security.hash_password, password)
    user = models.User(email=email.strip().lower(), hashed_password=hashed, role=role)
    return await repository.add_user(db, user)


async def authenticate(
    db: AsyncSession, email: str, password: str
) -> models.User | None:
    user = await repository.get_user_by_email(db, email.strip().lower())
    # Always run one password check, even when the email is unknown
    hashed = user.hashed_password if user else security.DUMMY_HASH
    password_ok = await asyncio.to_thread(security.verify_password, password, hashed)
    return user if user and password_ok else None


async def login(db: AsyncSession, email: str, password: str) -> str | None:
    """Check the password once, then hand back a token."""
    user = await authenticate(db, email, password)
    return security.create_access_token(user.id) if user else None


async def user_from_token(db: AsyncSession, token: str) -> models.User | None:
    """Check the signature and expiry, then load the user. No password check."""
    user_id = security.read_access_token(token)
    return await repository.get_user(db, user_id) if user_id is not None else None


async def add_student_file(
    db: AsyncSession, student: models.Student, upload: UploadedFile
) -> models.StudentFile:
    # The name on disk is ours. The client's name is only kept as a label.
    stored_name = f"{uuid.uuid4().hex}{upload.extension}"
    await storage.save(stored_name, upload.data)
    record = models.StudentFile(
        student_id=student.id,
        original_name=upload.original_name,
        stored_name=stored_name,
        content_type=upload.content_type,
        size_bytes=len(upload.data),
    )
    try:
        return await repository.add_file(db, record)
    except Exception:
        await storage.delete(stored_name)  # no row, so no file left behind
        raise


async def list_student_files(
    db: AsyncSession, student: models.Student
) -> list[models.StudentFile]:
    return await repository.list_files(db, student.id)


async def get_student_file(
    db: AsyncSession, student_id: int, file_id: int
) -> models.StudentFile | None:
    return await repository.get_file(db, student_id, file_id)


async def file_exists(record: models.StudentFile) -> bool:
    return await storage.exists(record.stored_name)


def file_path(record: models.StudentFile) -> Path:
    return storage.path_for(record.stored_name)
