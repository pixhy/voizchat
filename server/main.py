import hashlib
import os
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlmodel import Session, SQLModel, create_engine, select
from model.user import User, CreateUserRequest, UserInfo, LoginRequest
from base64 import b64encode, b64decode
import jwt
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import time
from email_service import send_verification_email

sqlite_url = os.getenv("DATABASE_URL") or "sqlite:///data/voizchat.db"

print(f"Using database: {sqlite_url}")
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def hash_password(password: str):
    salt = os.urandom(32)
    passwordhash = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1)
    return f"1${b64encode(salt).decode('utf-8')}${b64encode(passwordhash).decode('utf-8')}"

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
async def lifespan(_app: FastAPI):
    # Startup
    hash(_app)
    create_db_and_tables()
    yield
    # Cleanup
    pass

app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:5173",  # Vite's default dev server
    "http://127.0.0.1:5173"  # Alternative localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


jwt_public_key = os.getenv("AUTH_JWT_PUBKEY")
if jwt_public_key:
    jwt_public_key = f'-----BEGIN PUBLIC KEY-----\n{jwt_public_key}\n-----END PUBLIC KEY-----\n'
else:
    with open("public_key.pem", "r") as public_file:
        jwt_public_key = public_file.read()

jwt_private_key = os.getenv("AUTH_JWT_PRIVKEY")
if jwt_private_key:
    jwt_private_key = f'-----BEGIN PRIVATE KEY-----\n{jwt_private_key}\n-----END PRIVATE KEY-----\n'
else:
    with open("private_key.pem", "r") as private_file:
        jwt_private_key = private_file.read()

@app.post("/api/users/register")
def create_user(user_request: CreateUserRequest, session: SessionDep) -> dict[str, str]:
    user = User(email=user_request.email, username=user_request.username)
    user.passwordhash = hash_password(user_request.password)
    user.verification_code = os.urandom(20).hex()
    user.verification_code_expiration = int(time.time()) + 60*60*24 #one day
    send_verification_email(user_request.email, user.verification_code)
    session.add(user)
    session.commit()
    session.refresh(user)
    one_week_in_seconds = 60*60*24*7
    expiration = int(time.time()) + one_week_in_seconds
    payload = {"sub": user.id, "exp": expiration}
    token = jwt.encode(payload, jwt_private_key, algorithm="EdDSA")
    return jsonable_encoder({"token": token})

@app.get("/api/users/verify/{verification_code}")
def verify_user(verification_code: str, session: SessionDep):
    user = session.exec(select(User).where(User.verification_code == verification_code)).first()
    if user:
        user.is_verified = True
        user.verification_code = None
        user.verification_code_expiration = None
        user.verification_code_expiration = None
        session.commit()
        session.refresh(user)
        return Response(status_code=204)
    
    raise HTTPException(status_code=404, detail="Verification code not found")


@app.post("/api/users/login")
def login_user(user_request: LoginRequest, session: SessionDep) -> dict[str, str]:
    user = session.exec(select(User).where(User.email == user_request.email)).first()
    if not user or not verify_password_hash(user.passwordhash, user_request.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    one_week_in_seconds = 60*60*24*7
    expiration = int(time.time()) + one_week_in_seconds
    payload = {"sub": user.id, "exp": expiration}
    token = jwt.encode(payload, jwt_private_key, algorithm="EdDSA")
    return jsonable_encoder({"token": token})

@app.get("/api/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[UserInfo]:
    return [
        UserInfo(id=user.id, email=user.email, username=user.username)
             for user in session.exec(select(User).offset(offset).limit(limit)).all()
    ]

@app.get("/api/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> UserInfo:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfo(id=user.id, email=user.email, username=user.username)

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
