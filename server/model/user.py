from sqlmodel import Field, SQLModel, Column
from pydantic import BaseModel
from server.util.ulidtype import ULIDType
from ulid import ULID

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    userid: ULID = Field(default_factory=ULID, sa_column=Column(ULIDType, unique=True, index=True))
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

class PrivateUserInfo(BaseModel):
    userid: str
    email: str
    username: str
    @staticmethod
    def from_user(user: User):
        return PrivateUserInfo(userid=str(user.userid), email=user.email, username=user.username)
class UserInfo(BaseModel):
    userid: str
    username: str
    @staticmethod
    def from_user(user: User):
        return UserInfo(userid=str(user.userid), username=user.username)