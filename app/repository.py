from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def _commit(db: AsyncSession) -> None:
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise


async def _save(db: AsyncSession, obj):
    db.add(obj)
    await _commit(db)
    await db.refresh(obj)
    return obj


async def add_student(db: AsyncSession, student: models.Student) -> models.Student:
    return await _save(db, student)


async def get_student(db: AsyncSession, student_id: int) -> models.Student | None:
    return await db.get(models.Student, student_id)


def _search(statement, q: str | None):
    if q:
        statement = statement.where(models.Student.name.ilike(f"%{q}%"))
    return statement


async def list_students(
    db: AsyncSession, skip: int, limit: int, q: str | None = None
) -> list[models.Student]:
    statement = _search(select(models.Student), q)
    statement = statement.order_by(models.Student.id).offset(skip).limit(limit)
    return list((await db.scalars(statement)).all())


async def count_students(db: AsyncSession, q: str | None = None) -> int:
    statement = _search(select(func.count()).select_from(models.Student), q)
    return await db.scalar(statement)


async def list_students_by_name(db: AsyncSession) -> list[models.Student]:
    statement = select(models.Student).order_by(models.Student.name)
    return list((await db.scalars(statement)).all())


async def update_student(
    db: AsyncSession, student: models.Student, changes: dict
) -> models.Student:
    for field, value in changes.items():
        setattr(student, field, value)
    return await _save(db, student)


async def delete_student(db: AsyncSession, student: models.Student) -> None:
    await db.delete(student)
    await _commit(db)


async def get_user(db: AsyncSession, user_id: int) -> models.User | None:
    return await db.get(models.User, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> models.User | None:
    statement = select(models.User).where(models.User.email == email)
    return await db.scalar(statement)


async def add_user(db: AsyncSession, user: models.User) -> models.User:
    return await _save(db, user)


async def add_file(db: AsyncSession, record: models.StudentFile) -> models.StudentFile:
    return await _save(db, record)


async def list_files(db: AsyncSession, student_id: int) -> list[models.StudentFile]:
    statement = (
        select(models.StudentFile)
        .where(models.StudentFile.student_id == student_id)
        .order_by(models.StudentFile.id)
    )
    return list((await db.scalars(statement)).all())


async def get_file(
    db: AsyncSession, student_id: int, file_id: int
) -> models.StudentFile | None:
    statement = select(models.StudentFile).where(
        models.StudentFile.id == file_id,
        models.StudentFile.student_id == student_id,
    )
    return await db.scalar(statement)


async def list_stored_names(db: AsyncSession, student_id: int) -> list[str]:
    statement = select(models.StudentFile.stored_name).where(
        models.StudentFile.student_id == student_id
    )
    return list((await db.scalars(statement)).all())
