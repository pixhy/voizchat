
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    username: str = Field(index=True)
    passwordhash: str

class CreateUserRequest(BaseModel):
    email: str
    username: str
    password: str

class UserInfo(BaseModel):
    id: int
    email: str
    username: str