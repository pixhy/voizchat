
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    username: str = Field(index=True)
    passwordhash: str
    is_verified: bool = False
    verification_code: str | None = None
    verification_code_expiration: int | None = None

class CreateUserRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserInfo(BaseModel):
    id: int
    email: str
    username: str