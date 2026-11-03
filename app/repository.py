from sqlalchemy.orm import Session

from app import models


def _commit(db: Session) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def _save(db: Session, obj):
    db.add(obj)
    _commit(db)
    db.refresh(obj)
    return obj


def add_student(db: Session, student: models.Student) -> models.Student:
    return _save(db, student)


def get_student(db: Session, student_id: int) -> models.Student | None:
    return db.get(models.Student, student_id)


def _search(db: Session, q: str | None):
    query = db.query(models.Student)
    if q:
        query = query.filter(models.Student.name.ilike(f"%{q}%"))
    return query


def list_students(
    db: Session, skip: int, limit: int, q: str | None = None
) -> list[models.Student]:
    return _search(db, q).order_by(models.Student.id).offset(skip).limit(limit).all()


def count_students(db: Session, q: str | None = None) -> int:
    return _search(db, q).count()


def list_students_by_name(db: Session) -> list[models.Student]:
    return db.query(models.Student).order_by(models.Student.name).all()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def add_user(db: Session, user: models.User) -> models.User:
    return _save(db, user)
