from sqlalchemy.orm import Session

from app import models, repository, schemas, security


def create_student(db: Session, data: schemas.StudentCreate) -> models.Student:
    values = data.model_dump()
    values["email"] = values["email"].strip().lower()  # one email, one spelling
    return repository.add_student(db, models.Student(**values))


def list_students(
    db: Session, skip: int, limit: int, q: str | None = None
) -> dict:
    return {
        "total": repository.count_students(db, q),
        "skip": skip,
        "limit": limit,
        "items": repository.list_students(db, skip, limit, q),
    }


def student_directory(db: Session) -> list[models.Student]:
    return repository.list_students_by_name(db)


def get_student(db: Session, student_id: int) -> models.Student | None:
    return repository.get_student(db, student_id)


def create_user(
    db: Session, email: str, password: str, role: str = "viewer"
) -> models.User:
    user = models.User(
        email=email.strip().lower(),
        hashed_password=security.hash_password(password),
        role=role,
    )
    return repository.add_user(db, user)


def authenticate(db: Session, email: str, password: str) -> models.User | None:
    user = repository.get_user_by_email(db, email.strip().lower())
    # Always run one password check, even when the email is unknown
    hashed = user.hashed_password if user else security.DUMMY_HASH
    password_ok = security.verify_password(password, hashed)
    return user if user and password_ok else None
