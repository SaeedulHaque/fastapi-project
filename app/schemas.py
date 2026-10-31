from pydantic import BaseModel, ConfigDict

class studentcreate(BaseModel):
    name: str
    age: int
    email: str

class studentoutput(BaseModel):

    id: int
    name: str
    age: int

    model_config = ConfigDict(from_attributes=True)