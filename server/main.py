import hashlib
import os
from contextlib import asynccontextmanager
from typing import Union
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query

from sqlmodel import Field, Session, SQLModel, create_engine, select

from model.user import User, CreateUserRequest, UserInfo
from base64 import b64encode, b64decode

sqlite_url = f"sqlite:///data/voizchat.db"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def hash_password(password: str):
    salt = os.urandom(32)
    hash = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1)
    return f"1${b64encode(salt).decode('utf-8')}${b64encode(hash).decode('utf-8')}"

def verify_password_hash(password_hash, password):
    version, salt, expected_hash = password_hash.split('$')
    if version != "1": return False
    salt = b64decode(salt)
    expected_hash = b64decode(expected_hash)
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1) == expected_hash


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Cleanup
    pass

app = FastAPI(lifespan=lifespan)

@app.post("/users/")
def create_user(user_request: CreateUserRequest, session: SessionDep) -> int:
    user = User(email=user_request.email, username=user_request.username)
    user.passwordhash = hash_password(user_request.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.id

@app.get("/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[UserInfo]:
    return [
        UserInfo(id=user.id, email=user.email, username=user.username)
             for user in session.exec(select(User).offset(offset).limit(limit)).all()
    ]

@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> UserInfo:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfo(id=user.id, email=user.email, username=user.username)

@app.delete("/user/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}