from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str
    age: int | None = Field(default=None, ge=5, le=100)
    phone: str | None = None


class StudentCreate(StudentBase):
    pass


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


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorOut(BaseModel):
    error: ErrorBody
