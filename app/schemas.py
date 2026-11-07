from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StudentBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str
    age: int | None = Field(default=None, ge=5, le=100)
    phone: str | None = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: str | None = None
    age: int | None = Field(default=None, ge=5, le=100)
    phone: str | None = None

    @field_validator("name", "email")
    @classmethod
    def required_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("cannot be null")
        return value


class StudentOut(StudentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudentSummary(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class StudentPage(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[StudentOut]


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorOut(BaseModel):
    error: ErrorBody


class StudentFileOut(BaseModel):
    id: int
    student_id: int
    original_name: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
